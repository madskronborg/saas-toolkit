from kitman.core import configs


class IAMModelsConfig(configs.BaseConfig):

    user: configs.ModelConfig
    customer: configs.ModelConfig
    membership: configs.ModelConfig
    invitation: configs.ModelConfig


class IAMServicesConfig(configs.BaseConfig):
    pass


class IAMConfig(configs.AppConfig[IAMModelsConfig, IAMServicesConfig]):

    name = "iam"
    namespace = "iam"
