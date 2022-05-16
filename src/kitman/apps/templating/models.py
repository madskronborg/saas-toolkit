from kitman.db.models import BaseModel, BaseMeta, ormar


class TemplateVariable(BaseModel):
    class Meta(BaseMeta):
        abstract = True

    name: str = ormar.String(max_length=255)
    value: str = ormar.String(max_length=1024, nullable=True)
    required: bool = ormar.Boolean(default=False)
    template: "Template" = ormar.ForeignKey(
        Template,
    )
