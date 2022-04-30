from kitman.core.templating import (
    TemplateGroup,
    Template,
    TemplateItem,
    TemplateVariable,
    TemplateBuilder,
    TemplateStructure,
)

from deepdiff import DeepDiff

# Data
template_child = Template(
    name="child",
    items=[
        TemplateItem(
            name="Item 2",
            value={
                "name": "2.{domain}",
                "content": "{domain}",
            },
        ),
        TemplateItem(
            name="Item 3",
            value={"name": "{subdomain}.test.com", "content": "my-redirect.test.com"},
        ),
        TemplateItem(
            name="Item 4",
            value={"name": "{subdomain}.{domain}", "content": "my-redirect.test.com"},
        ),
    ],
    variables=[
        TemplateVariable(name="domain", required=True),
        TemplateVariable(name="subdomain", value="sub"),
    ],
    unique_keys=["name", "content"],
)

template = Template(
    name="parent",
    items=[
        TemplateItem(name="1", value={"name": "{subsubdomain}.{subdomain}.test.com"}),
        TemplateItem(
            name="Item 2",
            value={
                "name": "2.{domain}",
                "content": "{domain}",
            },
        ),
    ],
    children=[template_child],
    unique_keys=["name"],
    variables=[TemplateVariable(name="subsubdomain", value="subsub")],
)


template_standalone = Template(
    name="standalone",
    category="networking",
    items=[
        TemplateItem(
            name="Item 2",
            value={
                "name": "2.{domain}",
                "content": "{domain}",
            },
        ),
        TemplateItem(value={"name": "2.test.com", "content": "{domain}"}),
    ],
)

template_group = TemplateGroup(
    name="Group",
    templates=[template, template_standalone],
    variables=[TemplateVariable(name="domain", value="group_domain.com")],
)


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

    assert structure.items == expected_items, "TemplateStructure items are not correct"
