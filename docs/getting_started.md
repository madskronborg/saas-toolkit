# Getting Started

To get started with Saas Toolkit, you will first need to install the library:

In a shell run: <br>
`pip install git+https://github.com/madskronborg/saas-toolkit`

## Configuration

In your `main.py` file (where your FastAPI app is), you will need to configure Saas Toolkit. <br>
You can enable / disable logging, add a custom `SQLAlchemy` `MetaData` class and much more.

**Important** <br>
The configuration has to be made before any other part of the library is imported.

```py
# In main.py
from saas_toolkit import configure, Settings


# First we configure sass_toolkit
configure(
    Settings(
        logging = {
            "enable": True # Enable / Disable logging
        }
    )
)

```

After we have configured the library, we can import anything we need.

## FastAPI

The next step is to decide how we want to configure our FastAPI app. <br>
Typically, we will use Pydantic's `BaseSettings` class, so we can change configuration settings via Environment Variables.

You have several settings options at your disposal:

- `AppSettings` (_required_) - The base settings class. Subclass Pydantic's `BaseSettings` class and adds a few generic attributes like `PROJECT_NAME`, `ENV` and `SECRET`.
- `CorsSettings` - A mixin to configure CORS. Will automatically enable `FastAPI`'s `CorsMiddleware`.
- `PostgresSettings` - A mixin to configure postgres. If a database is not provided to the `setup` function, a database will automatically be made. If `metadata` is not provided when configuring Saas Toolkit, a `MetaData` instance will be created automatically.

Each of these settings can be combined at will. The only required

```py
# in config.py
from saas_toolkit.fastapi.config import AppSettings, CorsSettings, PostgresSettings

class Settings(AppSettings, CorsSettings, PostgresSettings):
    pass

settings = Settings()

```

You can now configure your project using environment variables or `.env` file.

Full list of environment variables can be found [here.](fastapi/configuration.md)

---

The next step is to setup the FastAPI `app` instance, so it works with all the goodies from Saas Toolkit such as automatic error responses + starting and stopping of database etc.

```py
# In main.py
# ... code from above

from fastapi import FastAPI
from .config import settings # Import the settings variable we created before
from sass_toolkit.fastapi import import setup
app = FastAPI()

setup(app, settings) # Notice we don't pass the `db` kwarg, since we wan't Saas Toolkit to auto create our database.
```

Voilà! Our FastAPI app now have:

- CORS enabled
- A Postgres database connection which will be started and stopped automatically on app start and shutdown
- Error responses whenever we raise an error that subclasses `saas_toolkit.errors.Error`.
