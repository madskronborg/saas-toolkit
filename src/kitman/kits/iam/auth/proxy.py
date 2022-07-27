from typing import Generic
from kitman.kitman import TInstallableConf
from kitman.kits.iam.auth.base import (
    BaseAuthenticationConf,
    BaseAuthenticationPlugin,
    HeaderLocationStrategy,
)
from kitman.kits.iam import domain


class ProxyAuthenticationConf(BaseAuthenticationConf, Generic[domain.TUser]):

    location = HeaderLocationStrategy(key="X-USER-ID")


class ProxyAuthenticationPlugin(
    BaseAuthenticationPlugin, Generic[TInstallableConf, domain.TUser]
):
    name = "Proxy Authentication"
    description = "A plugin for authenticating via an identity proxy. The proxy will determine the identity of the user and provide a user identifier to the downstream application. This will usually be in a header like X-USER-ID"
