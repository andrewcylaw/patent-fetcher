from typing import Any

from pydantic_core import PydanticUseDefault


def default_if_none(value: Any) -> Any:
    # From https://docs.pydantic.dev/latest/concepts/validators/#special-types under 'PydanticUseDefault '
    if value is None:
        raise PydanticUseDefault()
    return value
