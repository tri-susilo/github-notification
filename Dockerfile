# Stage 1: Build dependencies
FROM python:3.11-alpine AS builder

WORKDIR /app

# Install alat build (wajib untuk compile package C)
RUN apk add --no-cache gcc musl-dev libffi-dev

COPY requirments.txt .

# Install dependencies ke folder terpisah
RUN pip install --no-cache-dir --prefix=/install -r requirments.txt


# Stage 2: Final minimal image
FROM python:3.11-alpine

WORKDIR /app

# Copy hasil install dari builder stage
COPY --from=builder /install /usr/local

# Copy source code
COPY main.py .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
