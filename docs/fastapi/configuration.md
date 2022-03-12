# Configuration

The `saas_toolkit.fastapi.config` module contains a collection of setting classes that can be used to configure the FastAPI app.

## App Settings (required)

The default setting class.

**Environment variables** <br>

- PROEJCT_NAME (str) - The name of your project / title of the `FastAPI` instance
- ENV (str) - Can be used to configure different environments like `development`, `staging` and `production`
- SECRET (str) - A Base64 key used to encrypt secrets

## CorsSettings

Configure cors.

**Environment variables** <br>

- BACKEND_CORS_ORIGINS (str) - A comma-separated string of CORS Origins including the protocol e.g. `"http://localhost,http://127.0.0.1"`

## PostgresSettings

Configure Postgres database

**Environment variables** <br>

- POSTGRES_SERVER (str) - The hostname of your Postgres database
- POSTGRES_USER (str) - The Postgres database user
- POSTGRES_PASSWORD (str) - The Postgres database user's password
- POSTGRES_DB (str) - The name of the Postgres database
