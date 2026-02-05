FROM python:3.11-slim

WORKDIR /app

COPY . /app

CMD ["/app/start.sh"]