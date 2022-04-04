use actix_web::cookie;
use base64;
use config::{Config, ConfigError, Environment};
use serde::{Deserialize, Serialize};
use std::env;

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Settings {
    /// Settings for connecting to Redis.
    pub redis_url: String,

    /// Server port to bind to.
    pub port: u16,

    // Session secret key
    pub session_secret: String,
}

impl Settings {
    pub fn new() -> Result<Self, ConfigError> {
        let run_mode = env::var("RUN_MODE").unwrap_or_else(|_| "development".into());

        let default_key = cookie::Key::generate();

        let s = Config::builder()
            .add_source(Environment::default())
            .set_default("redis_url", "redis://172.17.0.5/")?
            .set_default("port", 8080)?
            .set_default("session_secret", base64::encode(default_key.encryption()))?
            .build()?;

        // You can deserialize (and thus freeze) the entire configuration as
        s.try_deserialize()
    }
}
