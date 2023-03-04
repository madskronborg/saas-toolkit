from fastapi.middleware.cors import CORSMiddleware
from pydantic import AnyHttpUrl, BaseModel, validator

from kitman import InstallableManager, Kitman, Plugin
from kitman.core.converters import convert_value_to_list


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

        if self.settings:
            kitman.api.add_middleware(
                CORSMiddleware,
                allow_origins=[str(origin) for origin in self.settings.ORIGINS],
                allow_credentials=self.settings.ALLOW_CREDENTIALS,
                allow_methods=self.settings.ALLOW_METHODS,
                allow_headers=self.settings.ALLOW_HEADERS,
            )


class CorsPlugin(Plugin[CorsConf]):

    name = "cors"
    description = "A plugin for adding cors headers to FastAPI"
    manager = CorsPluginManager()
