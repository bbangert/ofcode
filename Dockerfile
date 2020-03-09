FROM pypy:2

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir pastescript
COPY . .

CMD ["paster", "serve", "prod.ini"]
