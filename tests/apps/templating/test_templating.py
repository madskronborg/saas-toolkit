from kitman.apps.templating import (
    TemplateGroup,
    Template,
    TemplateItem,
    TemplateVariable,
    TemplateBuilder,
    TemplateStructure,
)

from deepdiff import DeepDiff

# Data
from .fixtures import template_child, template, template_standalone, template_group


def test_get_item_index():

    builder = TemplateBuilder()

    index = builder._get_item_index(
        template_child.items,
        template_standalone.items[0],
        search_keys={
            "name",
        },
    )

    assert index == 0, "_get_item_index could not find item"


def test_get_tree():

    builder = TemplateBuilder()

    template_tree = builder._get_tree(template)

    assert template_tree == [
        template_child,
        template,
    ], "get_tree does not return correct tree for templates"

    group_tree = builder._get_tree(template_group)

    assert group_tree == [
        template_group
    ], "get_tree does rteturn correct tree for groups"


def test_get_structure():

    builder = TemplateBuilder()

    builder.set_group(template_group)
    builder.add_user_template(template_standalone)

    structure = builder._get_structure()

    assert structure.templates == [
        template_child,
        template,
        template_standalone,
    ], "TemplateStructure templates are not correct"

    from pprint import pprint

    for item in structure.items:
        print("Item:", item.name, "Is:", pprint(item))

    expected_items: list[TemplateItem] = []

    expected_items.extend(template_child.items[1:])

    expected_items.extend(template.items)

    expected_items.extend(template_standalone.items)

    if not structure.items == expected_items:

        print("Differences is:")
        pprint(
            DeepDiff(
                structure.items,
                expected_items,
            )
        )

        assert (
            structure.items == expected_items
        ), "TemplateStructure items are not correct"


def test_build():

    builder = TemplateBuilder()

    builder.set_group(template_group)
    builder.add_user_template(template_standalone)

    build = builder.build()

    print("Build is:", build.data)
