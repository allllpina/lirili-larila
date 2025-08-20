## PostgreSQL and pgAdmin

More details on how to customize the installation and the compose file can be found [here (PostgreSQL)](https://hub.docker.com/_/postgres) and [here (pgAdmin)](https://www.pgadmin.org/docs/pgadmin4/latest/container_deployment.html).

Project structure:

```
.
├── .env
├── docker_compose.yml
└── README.md
```

[docker*compose.yml*](docker_compose.yml)

```yaml
services:
  postgres:
    container_name: postgres
    image: postgres:latest
    environment:
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PW}
      - POSTGRES_DB=${POSTGRES_DB} #optional (specify default database instead of $POSTGRES_DB)
    ports:
      - "5432:5432"
    restart: always
    volumes:
      # - ./db/init:/docker-entrypoint-initdb.d  # SQL скрипти чи .sh файли виконуються на старті
      - postgres-data:/var/lib/postgresql/data

volumes:
  postgres-data:
```

## Configuration

### .env

Before deploying this setup, you need to configure the following values in the [.env](.env) file.

- POSTGRES_USER
- POSTGRES_PW
- POSTGRES_DB (can be default value)

## Deploy with docker compose

```shell
$ docker compose up
Starting postgres ... done
```

## Expected result

Check containers are running:

```
$ docker ps
CONTAINER ID   IMAGE                           COMMAND                  CREATED             STATUS                 PORTS                                                                                  NAMES
849c5f48f784   postgres:latest                 "docker-entrypoint.s…"   9 minutes ago       Up 9 minutes           0.0.0.0:5432->5432/tcp, :::5432->5432/tcp                                              postgres
```

Stop the containers with

```shell
$ docker compose down
# To delete all data run:
$ docker compose down -v
```
