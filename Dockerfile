FROM python:2

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN apt-get update && apt-get install -yy libev-dev
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir pastescript
COPY . .
RUN python setup.py install

CMD ["paster", "serve", "prod.ini"]
