## PostgreSQL and Authentication

Project structure:

```
project/
│──.git/
│──.gitignore
│──rabbitmq_test/
│──auth/
│──tasks_mservice/
│──README.md
└──pyproject.toml
```

```
auth/
├─ containers/
│  └─ auth.Dockerfile
├─ alembic/
│  ├─ README
│  ├─ env.py
│  └─ script.py.mako
├─ app/
│  ├─ __init__.py
│  ├─ main.py
│  ├─ core/
│  │  ├─ __init__.py
│  │  ├─ config.py
│  │  ├─ database.py
│  │  ├─ dependency.py
│  │  ├─ exceptions.py
│  │  ├─ hash.py
│  │  └─ jwt.py
│  ├─ models/
│  │  ├─ __init__.py
│  │  └─ models.py
│  ├─ routers/
│  │  ├─ __init__.py
│  │  └─ routers.py
│  ├─ schemas/
│  │  ├─ __init__.py
│  │  └─ schemas.py
│  └─ utils/
│     ├─ __init__.py
│     ├─ mail.py
│     └─ time_utc_now.py
├─ docker-compose.yml
├─ start.sh
├─ alembic.ini
├─ README.md
└─ requirements.txt

```

[docker-compose.yml](docker-compose.yml)

```yaml
services:
  postgres:
    container_name: postgres
    image: "postgres:15"
    restart: always
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5
    ports:
      - "5432:5432"
    env_file:
      - ./.env
    volumes:
      - "./pgsql:/var/lib/postgresql/data"
    networks:
      - default

  backend:
    container_name: auth
    build:
      context: .
      dockerfile: ./containers/auth.Dockerfile
    restart: always
    env_file:
      - .env
    ports:
      - "8000:8000"
    links:
      - postgres
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - default

networks:
  default:
    driver: bridge

volumes:
  pgsql:
    driver: local
```

## Configuration

### .env

Before deploying this setup, you need to configure the following values in the .env file.

```.env
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=test-db
POSTGRES_USER=viole
POSTGRES_PASSWORD=passwd
DATABASE_URL=postgresql+asyncpg://viole:passwd@postgres:5432/test-db

SECRET_KEY=725f2afa914ec7e08650a8b837f1d3ac6da3a5aeb9fa11ca0b007ee2fce75794
```

## Deploy with docker compose

```bash
docker-compose up -d build
```
