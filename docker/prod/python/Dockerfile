FROM python:3.10-alpine
LABEL maintainer = "jwis02202@gmail.com"

# Musl-dev, a general C compiler necessary
RUN apk update && \
    apk add --no-cache musl-dev libpq-dev gcc

COPY ./app /app

WORKDIR /app

RUN pip install --no-cache-dir -r requirements/prod.txt

COPY ./docker/prod/python/entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

ENTRYPOINT  ["/entrypoint.sh"]

