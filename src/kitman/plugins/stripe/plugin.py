import stripe
from fastapi import APIRouter

from kitman import InstallableManager, Kitman, Plugin

from .api import create_router
from .domain import StripePluginSettings


class StripePluginManager(InstallableManager["StripePlugin", StripePluginSettings]):
	
	def install(self, kitman: Kitman, settings: StripePluginSettings) -> None:
		super().install(kitman, settings)
  
		# Configure stripe
		stripe.api_key = settings.secret_key
  
		# Create and install router
		self.parent.router = create_router(self.parent)

class StripePlugin(Plugin[StripePluginSettings]):
	name = "Stripe"
	description = "Easy setup of Stripe"
	manager = StripePluginManager()
	router: APIRouter | None = None
	
