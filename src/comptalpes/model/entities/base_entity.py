from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class BaseEntity(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
        use_enum_values=False,
    )

    id: UUID = Field(default_factory=uuid4, frozen=True)
