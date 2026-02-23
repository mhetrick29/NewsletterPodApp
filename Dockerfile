FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DISABLE_INTERACTIVE_AUTH=true

WORKDIR /app

COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

COPY backend /app/backend
COPY parsers /app/parsers

WORKDIR /app/backend
RUN chmod +x /app/backend/start_server.sh
CMD ["/app/backend/start_server.sh"]
