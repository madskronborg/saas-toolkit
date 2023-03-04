from typing import TYPE_CHECKING

from fastapi import APIRouter, Body, Header, Response, status

from . import queries, schemas

if TYPE_CHECKING:
    from ..plugin import StripePlugin


def create_router(plugin: StripePlugin):

    router = APIRouter()

    if not plugin.settings:
        raise ValueError("StripePlugin not configurated")

    @router.get("/config", response_model=schemas.PaymentConfigOut)
    async def get_config():

        return {"publishable_key": plugin.settings.publishable_key}

    @router.post(
        "/webhook", include_in_schema=False, status_code=status.HTTP_201_CREATED
    )
    async def on_webhook(payload=Body(), http_stripe_signature=Header()):
        print("Webhook payload is:", payload, "sig_header is:", http_stripe_signature)

        stripe_queries = plugin.kitman.inject(queries.StripeQueryHandler)

        try:
            event = await stripe_queries.handle(
                queries.GetStripeWebhook(
                    sig_header=http_stripe_signature, payload=payload
                )
            )
        except:
            return Response(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"message": "Invalid request"},
            )

        return {"status": "ok"}

    return router
