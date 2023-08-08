FROM python:3.10
LABEL maintainer = "jwis02202@gmail.com"

COPY ./app /app

WORKDIR /app

RUN pip install -r requirements/dev.txt

COPY ./docker/dev/python/entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

ENTRYPOINT  ["/entrypoint.sh"]

