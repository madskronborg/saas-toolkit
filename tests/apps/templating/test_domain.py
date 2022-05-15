from .fixtures import template_child

item = template_child.items[0]


def test_template_item_depends_on():

    print("Item value:", item.value)

    assert item.depends_on == set(["domain"]), "TemplateItem.depends_on is not correct"
