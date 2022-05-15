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
            name="Item without variables",
            value={"name": "no_variables", "content": "no_variables"},
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
