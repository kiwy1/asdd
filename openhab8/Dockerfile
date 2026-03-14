# Multi-stage Dockerfile — OpenHAB virtual simulator
# Stage 1: builder (dependencies)
FROM python:3.12-alpine AS builder
WORKDIR /build
RUN pip install --no-cache-dir --user requests

# Stage 2: runtime (minimal image)
FROM python:3.12-alpine AS runtime
WORKDIR /app
RUN adduser -D appuser && chown -R appuser /app
USER appuser
COPY --from=builder /root/.local /home/appuser/.local
ENV PATH=/home/appuser/.local/bin:$PATH
COPY --chown=appuser:appuser simulator/ ./
ENTRYPOINT ["python", "-u", "simulate.py"]
