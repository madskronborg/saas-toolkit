from typing import TYPE_CHECKING
from kitman.core import configs
from . import domain

if TYPE_CHECKING:
    from .auth import AuthenticationBackend


class IAMModelsConfig(configs.BaseConfig):

    user: configs.ModelConfig
    customer: configs.ModelConfig
    membership: configs.ModelConfig
    invitation: configs.ModelConfig


class IAMServicesConfig(configs.BaseConfig):

    users: domain.IUserService


class IAMDependencyConfig(configs.DependencyConfig):

    get_user_service: domain.UserServiceDependency


class IAMConfig(
    configs.AppConfig[IAMModelsConfig, IAMServicesConfig, IAMDependencyConfig]
):

    name = "iam"
    namespace = "iam"

    backends: list[AuthenticationBackend]
