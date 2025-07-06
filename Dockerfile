# Stage 1: Build dependencies
FROM python:3.11-alpine AS builder

WORKDIR /build

# Install alat build untuk package C
RUN apk add --no-cache gcc musl-dev libffi-dev

# Copy file requirements
COPY requirements.txt .

# Install dependencies ke folder terpisah
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Final minimal image
FROM python:3.11-alpine

WORKDIR /app

# Copy hasil instalasi dari builder
COPY --from=builder /install /usr/local

# Copy seluruh source code
COPY app/ ./app

EXPOSE 8000

# Jalankan FastAPI dari folder app/
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
