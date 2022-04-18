from kitman.core.templating import (
    TemplateGroup,
    Template,
    TemplateItem,
    TemplateVariable,
    TemplateBuilder,
    TemplateStructure,
)

# Data
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
    unique_keys=["name"],
    variables=[TemplateVariable(name="subsubdomain", value="subsub")],
)

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
    extends=template,
    unique_keys=["name", "content"],
)

template_standalone = Template(
    name="standalone",
    category="networking",
    items=[TemplateItem(value={"name": "2.test.com", "content": "{domain}"})],
)

template_group = TemplateGroup(
    name="Group",
    templates=[template, template_child, template_standalone],
    variables=[TemplateVariable(name="domain", value="group_domain.com")],
)

structure_without_standalone = TemplateStructure(
    templates=template_group.templates,
    items=[
        TemplateItem(
            name="1",
            value={"name": "{subsubdomain}.{subdomain}.test.com"},
            template="parent",
        ),
        TemplateItem(
            name="Item 2",
            value={
                "name": "2.{domain}",
                "content": "{domain}",
            },
            template="parent",
        ),
        TemplateItem(
            name="Item 3",
            value={"name": "{subdomain}.test.com", "content": "my-redirect.test.com"},
            template="child",
        ),
        TemplateItem(
            name="Item 4",
            value={"name": "{subdomain}.{domain}", "content": "my-redirect.test.com"},
            template="child",
        ),
        TemplateItem(
            value={"name": "2.test.com", "content": "{domain}"}, template="standalone"
        ),
    ],
    variables=[
        TemplateVariable(name="subsubdomain", value="subsub", template="parent"),
        TemplateVariable(name="domain", required=True, template="child"),
        TemplateVariable(name="subdomain", value="sub", template="child"),
    ],
)

# struture_with_standalone = TemplateStructure()


def test_template_structure():

    builder = TemplateBuilder().set_group(template_group)

    structure = builder._get_structure()

    assert (
        structure.templates == structure_without_standalone.templates
    ), "TemplateStructure does not have correct templates"

    assert (
        structure.items == structure_without_standalone.items
    ), "TemplateStructure does not have correct items"

    assert (
        structure.variables == structure_without_standalone.variables
    ), "TemplateStructure does not have correct variables"


left = [
    TemplateItem(
        name="1",
        value={"name": "{subsubdomain}.{subdomain}.test.com"},
        template="parent",
    ),
    TemplateItem(
        name="Item 2",
        value={"name": "2.{domain}", "content": "{domain}"},
        template="parent",
    ),
    TemplateItem(
        name=None,
        value={"name": "2.test.com", "content": "{domain}"},
        template="standalone",
    ),
]
right = [
    TemplateItem(
        name="1",
        value={"name": "{subsubdomain}.{subdomain}.test.com"},
        template="parent",
    ),
    TemplateItem(
        name="Item 2",
        value={"name": "2.{domain}", "content": "{domain}"},
        template="parent",
    ),
    TemplateItem(
        name="Item 3",
        value={"name": "{subdomain}.test.com", "content": "my-redirect.test.com"},
        template="child",
    ),
    TemplateItem(
        name="Item 4",
        value={"name": "{subdomain}.{domain}", "content": "my-redirect.test.com"},
        template="child",
    ),
    TemplateItem(
        name=None,
        value={"name": "2.test.com", "content": "{domain}"},
        template="standalone",
    ),
]
