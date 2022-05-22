from typing import Type
from kitman.core import configs
from . import models


class TemplatingModelConfig(configs.BaseModelConfig):

    TemplateVariable: Type[models.TTemplateVariable] = models.TemplateVariable
