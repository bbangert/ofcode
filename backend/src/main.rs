mod settings;

use actix_session::{storage::CookieSessionStore, Session, SessionMiddleware};
use actix_web::{
    cookie, delete, error, get,
    http::{header::ContentType, StatusCode},
    post, web,
    web::Data,
    App, HttpResponse, HttpServer, Responder, Result,
};
use derive_more::{Display, Error};
use mobc::Pool;
use mobc_redis::redis::{AsyncCommands, FromRedisValue};
use mobc_redis::{redis, RedisConnectionManager};
use nanoid::nanoid;
use serde::{Deserialize, Serialize};

use settings::Settings;

#[derive(Serialize, Deserialize)]
struct CodeBody {
    code: String,
    language: String,
}

#[derive(Serialize, Deserialize)]
struct CodeStorage {
    code: String,
    language: String,
    session_id: String,
}

impl FromRedisValue for CodeStorage {
    fn from_redis_value(v: &redis::Value) -> redis::RedisResult<Self> {
        let s: String = redis::from_redis_value(v)?;
        let data = serde_json::from_str(&s).map_err(|error| -> redis::RedisError {
            (
                redis::ErrorKind::TypeError,
                "Could not deserialize data from Redis",
                format!("{:?}", error),
            )
                .into()
        })?;
        Ok(data)
    }
}

impl From<CodeStorage> for CodeBody {
    fn from(c: CodeStorage) -> Self {
        CodeBody {
            code: c.code,
            language: c.language,
        }
    }
}

#[derive(Serialize, Deserialize)]
struct CodeId {
    id: String,
}

#[derive(Debug, Display, Error)]
enum PasteError {
    #[display(fmt = "Code not found.")]
    CodeNotFound,

    #[display(fmt = "Unauthorized.")]
    Unauthorized,
}

impl error::ResponseError for PasteError {
    fn error_response(&self) -> HttpResponse {
        HttpResponse::build(self.status_code())
            .insert_header(ContentType::html())
            .body(self.to_string())
    }

    fn status_code(&self) -> StatusCode {
        match *self {
            PasteError::CodeNotFound => StatusCode::NOT_FOUND,
            PasteError::Unauthorized => StatusCode::UNAUTHORIZED,
        }
    }
}

fn get_session_id(session: &Session) -> Result<String, error::Error> {
    let session_id = session.get::<String>("id")?.unwrap_or_else(|| {
        let id = nanoid!();
        session.insert("id", &id).unwrap();
        id
    });
    Ok(session_id)
}

async fn get_con(
    pool: &Pool<RedisConnectionManager>,
) -> Result<mobc::Connection<mobc_redis::RedisConnectionManager>, error::Error> {
    pool.get().await.map_err(error::ErrorInternalServerError)
}

#[get("/v1/code/{code_id}")]
async fn fetch_code(
    pool: Data<Pool<RedisConnectionManager>>,
    code_id: web::Path<String>,
) -> Result<impl Responder> {
    let mut con = get_con(&pool).await?;
    let stored_code: CodeStorage = con
        .get(code_id.into_inner())
        .await
        .map_err(|_e| PasteError::CodeNotFound)?;
    let code: CodeBody = stored_code.into();
    Ok(web::Json(code))
}

#[post("/v1/code")]
async fn create_code(
    pool: Data<Pool<RedisConnectionManager>>,
    code: web::Json<CodeBody>,
    session: Session,
) -> Result<impl Responder> {
    let key = nanoid!();
    let session_id = get_session_id(&session)?;
    let code_storage = CodeStorage {
        code: code.code.clone(),
        language: code.language.clone(),
        session_id,
    };
    let mut con = get_con(&pool).await?;
    con.set(&key, serde_json::to_string(&code_storage).unwrap())
        .await
        .map_err(error::ErrorInternalServerError)?;
    Ok(web::Json(CodeId { id: key }))
}

#[delete("/v1/code/{code_id}")]
async fn delete_code(
    pool: Data<Pool<RedisConnectionManager>>,
    code_id: web::Path<String>,
    session: Session,
) -> Result<impl Responder> {
    let session_id = get_session_id(&session)?;
    let mut con = get_con(&pool).await?;
    let key = code_id.into_inner();
    let stored_code: CodeStorage = con.get(&key).await.map_err(|_e| PasteError::CodeNotFound)?;
    if stored_code.session_id != session_id {
        return Err(PasteError::Unauthorized.into());
    }
    con.del(&key)
        .await
        .map_err(error::ErrorInternalServerError)?;
    Ok(HttpResponse::Ok().finish())
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let settings = Settings::new().unwrap();

    // Setup Redis connection pool
    let client =
        redis::Client::open(settings.redis_url.clone()).expect("Failed to connect to Redis");
    let manager = RedisConnectionManager::new(client);
    let pool = Pool::builder().max_open(20).build(manager);
    let data = Data::new(pool);

    let cookie_key = cookie::Key::derive_from(&base64::decode(settings.session_secret).unwrap());

    HttpServer::new(move || {
        App::new()
            .wrap(
                SessionMiddleware::builder(CookieSessionStore::default(), cookie_key.clone())
                    .cookie_secure(false)
                    .build(),
            )
            .app_data(Data::clone(&data))
            .service(fetch_code)
            .service(create_code)
            .service(delete_code)
    })
    .bind(("0.0.0.0", settings.port))?
    .run()
    .await
}
