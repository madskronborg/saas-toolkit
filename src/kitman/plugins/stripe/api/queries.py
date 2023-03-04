from typing import TYPE_CHECKING, overload

import stripe
from pydantic import SecretStr

from kitman.core.queries import Query, QueryHandler

if TYPE_CHECKING:
    from ..plugin import StripePlugin


class GetStripeWebhook(Query):
    sig_header: str
    payload: str | bytes


class StripeQueryHandler(QueryHandler):
    handles = {
        GetStripeWebhook,
    }
    plugin: StripePlugin

    async def _on_get_stripe_webhook(self, message: GetStripeWebhook) -> stripe.Event:

        event = stripe.Webhook.construct_event(
            message.payload,
            message.sig_header,
            self.plugin.settings.secret_key.get_secret_value(),
        )

        return event

    @overload
    async def handle(self, message: GetStripeWebhook) -> stripe.Event:
        ...

    async def handle(self, message: GetStripeWebhook):

        if isinstance(message, GetStripeWebhook):
            return await self._on_get_stripe_webhook(message)

        return False
