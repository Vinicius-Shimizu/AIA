from collections.abc import Callable

from pydantic import BaseModel, ConfigDict


class Tool(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str
    description: str
    args_schema: type[BaseModel]
    function: Callable
