# ref: https://github.com/astral-sh/uv-docker-example/blob/main/multistage.Dockerfile
FROM ghcr.io/astral-sh/uv:python3.13-alpine AS builder

WORKDIR /app
COPY . ./
RUN uv sync --frozen --no-dev

FROM python:3.13-alpine

WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY . ./

ENV PATH="/app/.venv/bin:$PATH"

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

CMD ["python", "main.py"]
