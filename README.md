# Quick Start

```bash
uv sync --frozen && uv cache prune --ci && python manage.py collectstatic --noinput
```

## Docker

Build and run locally:

```bash
docker build -t django-pastebin .
docker run --rm -p 8000:8000 \
  -e MYSQL_URL='mysql://user:pass@host:3306/db' \
  -e DEBUG=false \
  django-pastebin
```

## Environment Variables

| Variable    | Required | Default | Description                                  |
|-------------|----------|---------|----------------------------------------------|
| `MYSQL_URL` | Yes      | —       | MySQL connection string (e.g. `mysql://user:pass@host:3306/db`) |
| `DEBUG`     | No       | `false` | Set to `true` for Django debug mode          |
