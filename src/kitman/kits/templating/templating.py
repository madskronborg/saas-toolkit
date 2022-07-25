from __future__ import annotations
from . import domain
from . import generics


class TemplateVariable(domain.BaseTemplateVariable):
    pass


class TemplateItem(domain.BaseTemplateItem["Template"]):
    pass


class Template(domain.BaseTemplate["Template", TemplateItem, TemplateVariable]):
    pass


class TemplateGroup(
    domain.BaseTemplateGroup["TemplateGroup", Template, TemplateVariable]
):
    pass


class TemplateStructure(
    domain.BaseTemplateStructure[Template, TemplateItem, TemplateVariable]
):
    pass


class TemplateBuild(domain.BaseTemplateBuild[TemplateItem, TemplateStructure]):
    pass


class TemplateBuilder(
    generics.BaseTemplateBuilder[
        TemplateGroup,
        Template,
        TemplateItem,
        TemplateVariable,
        TemplateStructure,
        TemplateBuild,
    ]
):
    class Config:
        template_structure_model = TemplateStructure
        template_build_model = TemplateBuild
