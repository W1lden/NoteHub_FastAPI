from typing import Annotated

from pydantic import Field

ID = Annotated[int, Field(gt=0)]
