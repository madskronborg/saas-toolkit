import pytest
from kitman.plugins import redis
from kitman.core import dynamic


def test_redis_settings():

    callable_types = dynamic.get_callable_types(redis.Redis.__init__)

    settings = redis.RedisConf()

    for parameter in callable_types.parameters.values():

        # Assert attr exists
        attr_name = f"REDIS_{parameter.name.upper()}"
        assert hasattr(
            redis.RedisConf,
            attr_name,
        ), f"Attribute {attr_name} does not exist on RedisSettings. Please add {str(parameter)} to RedisSettings"

        attr = getattr(settings, attr_name)

        assert (
            attr == parameter.default
        ), f"Attribute {attr_name} has wrong default value"

    # Test generic options
    options = settings.get_redis_options()

    for name, value in options.items():

        assert name.islower(), "Redis options are not lowercase"

        assert hasattr(
            settings, f"REDIS_{name.upper()}"
        ), "get_redis_options returned key that does not exist"

        assert value == getattr(
            settings, f"REDIS_{name.upper()}"
        ), "Redis option value is not correct"

    # Test custom kwarg to get_redis_options
    custom_options = settings.get_redis_options(db=1)

    assert custom_options["db"] == 1, "get_redis_options does not use kwargs"
