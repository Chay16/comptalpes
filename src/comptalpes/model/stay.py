from datetime import date

from pydantic import BaseModel, model_validator


class Stay(BaseModel):
    start: date
    end: date

    @model_validator(mode="after")
    def verify_date_order(self) -> "Stay":
        if self.start > self.end:
            raise ValueError(
                f"Start Date ({self.start}) can't be posterior to End Date ({self.end})"
            )
        return self
