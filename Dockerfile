FROM python:3.12-slim

LABEL org.opencontainers.image.title="Software FJ"
LABEL org.opencontainers.image.description="Sistema de reservas orientado a objetos - UNAD 213023_466"
LABEL org.opencontainers.image.authors="Julián Cano, Leo Diaz, John Arroyo, Camilo, Santiago"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
