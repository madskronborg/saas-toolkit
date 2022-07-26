from pydantic import AnyHttpUrl, BaseModel, validator
from kitman import Plugin, Kitman, InstallableManager
from kitman.core.converters import convert_value_to_list
from fastapi.middleware.cors import CORSMiddleware


class CorsConf(BaseModel):

    ORIGINS: list[AnyHttpUrl] = []
    ALLOW_CREDENTIALS: bool = True
    ALLOW_METHODS: list[str] = ["*"]
    ALLOW_HEADERS: list[str] = ["*"]

    # Validators
    _assemble_origins = validator("ORIGINS", pre=True)(convert_value_to_list)


class CorsPluginManager(InstallableManager["CorsPlugin", CorsConf]):
    def install(self, kitman: Kitman, conf: CorsConf | None = None) -> None:
        super().install(kitman, conf)

        if self.conf:
            kitman.fastapi.add_middleware(
                CORSMiddleware,
                allow_origins=[str(origin) for origin in self.conf.ORIGINS],
                allow_credentials=self.conf.ALLOW_CREDENTIALS,
                allow_methods=self.conf.ALLOW_METHODS,
                allow_headers=self.conf.ALLOW_HEADERS,
            )


class CorsPlugin(Plugin[CorsConf]):

    name = "cors"
    description = "A plugin for adding cors headers to FastAPI"
    manager = CorsPluginManager()
