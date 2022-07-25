from kitman.kits.templating import dependency_resolvers, templating

from .fixtures import template_child, template, template_standalone, template_group

from kitman.kits.templating.dependency_resolvers import TemplateDependencyResolver
from kitman.kits.templating import TemplateBuilder

from pprint import pprint


def test_resolve_without_variables():

    builder = TemplateBuilder()

    builder.set_group(template_group)
    builder.add_user_template(template_standalone)

    structure = builder._get_structure()

    dependency_resolver = builder._get_dependency_resolver(structure)

    item = structure.items[1]

    result = dependency_resolver.resolve(item)

    print("Result is:", result)

    assert (
        result == item
    ), "TemplateDependencyResolver.resolve does not work with items without variables"


def test_resolve_with_variables():

    builder = TemplateBuilder()

    builder.set_group(template_group)
    builder.add_user_template(template_standalone)

    structure = builder._get_structure()

    dependency_resolver = builder._get_dependency_resolver(structure)

    item = structure.items[0]

    result = dependency_resolver.resolve(item)

    print("Result is:")
    pprint(result.dict())

    assert (
        result != item
    ), "TemplateDependencyResolver.resolve does not work with items with variables"
