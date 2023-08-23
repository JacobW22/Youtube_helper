FROM python:3.10-alpine AS builder

RUN apk update && \
    apk add musl-dev libpq-dev gcc

RUN python -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

COPY /app/requirements/dev.txt .

RUN pip install -r dev.txt

FROM python:3.10-alpine

RUN apk update && \
    apk add libpq-dev

COPY --from=builder /opt/venv /opt/venv

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTOHNUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

COPY ./docker/dev/python/entrypoint.sh .
RUN ["chmod", "+x", "entrypoint.sh"]

WORKDIR /app

ADD app /app

EXPOSE 8000 5432

ENTRYPOINT  ["/entrypoint.sh"]
