# Migrations

Generate an Alembic revision after setting `APIX_DATABASE_URL` to the TimescaleDB instance. The application creates the prototype schema at startup; production deployments should apply reviewed migrations and then run the `create_hypertable` statement for `fare_quotes`.
