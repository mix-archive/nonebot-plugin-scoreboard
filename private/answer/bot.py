import nonebot
from nonebot.adapters.onebot.v11 import Adapter as OneBotV11Adapter

nonebot.init()

driver = nonebot.get_driver()
driver.register_adapter(OneBotV11Adapter)


nonebot.load_from_toml("pyproject.toml")

#####################
# fix part
#####################

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, Any

from _string import formatter_field_name_split  # type: ignore
from nonebot.internal.adapter.template import MessageTemplate

if TYPE_CHECKING:

    def formatter_field_name_split(
        field_name: str,
    ) -> tuple[str, list[tuple[bool, str]]]: ...


def get_field(
    self: MessageTemplate,
    field_name: str,
    args: Sequence[Any],
    kwargs: Mapping[str, Any],
) -> tuple[Any, int | str]:
    first, rest = formatter_field_name_split(field_name)
    obj = self.get_value(first, args, kwargs)

    for is_attr, value in rest:
        if value.startswith("_"):
            raise ValueError("Cannot access private attribute")
        obj = getattr(obj, value) if is_attr else obj[value]

    return obj, first


MessageTemplate.get_field = get_field

#####################
# fix part end
#####################

if __name__ == "__main__":
    nonebot.run()
