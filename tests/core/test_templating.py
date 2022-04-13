from saas_toolkit.core.templating import (
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
                "name": "2.test.com",
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
    templates=[template, template_standalone],
    variables=[TemplateVariable(name="domain", value="group_domain.com")],
)


def test_template_structure():

    builder = TemplateBuilder.set_group(template_group).add_user_template(
        template_standalone
    )
