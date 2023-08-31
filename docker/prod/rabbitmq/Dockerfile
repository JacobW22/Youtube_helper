FROM python:3.10-alpine AS builder

RUN apk update && \
    apk add --no-cache musl-dev libpq-dev gcc

RUN python -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

COPY /app/requirements/requirements.txt .

RUN pip install --no-cache -r requirements.txt

FROM python:3.10-alpine

RUN apk update && \
    apk add --no-cache libpq-dev

COPY --from=builder /opt/venv /opt/venv

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTOHNUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

COPY ./docker/prod/rabbitmq/entrypoint.sh .
RUN ["chmod", "+x", "entrypoint.sh"]

WORKDIR /app

ADD app /app

EXPOSE 8000 5432

ENTRYPOINT  ["/entrypoint.sh"]


