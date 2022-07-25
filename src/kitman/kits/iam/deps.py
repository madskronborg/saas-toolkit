from kitman.kits.iam.auth import Authenticator


def get_current_user_factory():

    from kitman.conf import settings

    authenticator = Authenticator(
        backends=settings.kits.iam.backends,
        get_user_service=settings.kits.iam.dependencies.get_user_service,
    )

    return authenticator.current_user
