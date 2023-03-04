from pydantic import BaseModel, SecretStr


class StripePluginSettings(BaseModel):
    secret_key: SecretStr
    publishable_key: str
    webhook_secret: SecretStr