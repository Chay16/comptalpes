from comptalpes.model import Stay
from datetime import date
from pydantic import ValidationError
import pytest

def test_stay() -> None:
    stay = Stay(start=date(1970,1,1), end=date(1970,1,2))
    assert stay.start == date(1970,1,1)
    assert stay.end == date(1970,1,2)

    with pytest.raises(ValidationError) as exc_info:
        Stay(start=date(1970, 1, 2), end=date(1970, 1, 1))