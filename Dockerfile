# syntax=docker/dockerfile:1.7

FROM python:3.14-slim AS builder
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY . .
RUN uv sync --frozen --no-dev

FROM python:3.14-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings \
    PORT=8000 \
    PATH="/app/.venv/bin:$PATH"
WORKDIR /app

RUN useradd --create-home --shell /bin/bash app

# Copy the full builder output (source code + .venv) in one shot,
# owned by root so collectstatic can write to /app/staticfiles.
COPY --from=builder /app /app

# collectstatic is run at build time as root (before USER app) so it can
# create /app/staticfiles, then we hand ownership off to the app user.
RUN python manage.py collectstatic --noinput && \
    chown -R app:app /app

USER app

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]