## PostgreSQL and Authentication

Project structure:

project/
│──.git/
│──.gitignore
│──rabbitmq_test/
│──auth/
│──tasks_mservice/
│──README.md
└──pyproject.toml

auth/
├── containers/
│ └── Dockerfile
│── src/
│ │── \_\_init\_\_.py
│ ├── app/
│ │ │── \_\_init\_\_.py
│ │ └── main.py
│ ├── db/
│ │ │── \_\_init\_\_.py
│ │ │── database.py
│ │ │── models.py
│ │ └── schemas.py
│ ├── router/
│ │ │── \_\_init\_\_.py
│ │ └── posts.py
│ └── .env
├── requirements.txt
├── docker-compose.yml
└── README.md

[docker-compose.yml](docker-compose.yml)

```yaml
services:
  postgres:
    image: postgres:latest
    container_name: pg-test
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    ports:
      - "5432:5432"

    volumes:
      - ./postgres/data:/var/lib/postgresql/data

  app:
    build:
      context: .
      dockerfile: containers/Dockerfile
    ports:
      - "8000:80"
    depends_on:
      - postgres
    volumes:
      - ./:/src:ro
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}

volumes:
  postgres:
```

## Configuration

### .env

Before deploying this setup, you need to configure the following values in the .env file.

```.env
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

POSTGRES_USER=viole
POSTGRES_DB=pg-test
POSTGRES_PASSWORD=passwd
```

## Deploy with docker compose

```bash
docker-compose up
```
