import pytest
from kitman.conf import settings
from kitman.core import converters


def test_convert_value_to_list(db):

    from kitman import core

    # Convert list to list
    assert converters.convert_value_to_list([1]) == [
        1
    ], "Converter failed to convert list to list"

    # Convert "[1]" to list
    assert converters.convert_value_to_list("[1]") == [
        1
    ], "Converter failed to convert string wrapped list to list"

    # Convert comma-separated string to list
    assert converters.convert_value_to_list("123,1234") == [
        "123",
        "1234",
    ], "Converter failed to convert comma-separated string to list"

    # Value error
    with pytest.raises(ValueError):

        converters.convert_value_to_list(1234)
