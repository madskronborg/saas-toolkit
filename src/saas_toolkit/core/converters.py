import orjson


def convert_value_to_list(v: str | list) -> list:

    if isinstance(v, list):
        return v

    if isinstance(v, str):

        if v.startswith("["):
            return orjson.loads(v)

        return [i.strip() for i in v.split(",")]

    raise ValueError(v)
