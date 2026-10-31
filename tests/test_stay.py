from datetime import date

import pytest
from pydantic import ValidationError

from comptalpes.model import Stay


def test_stay() -> None:
    stay = Stay(start=date(1970, 1, 1), end=date(1970, 1, 2))
    assert stay.start == date(1970, 1, 1)
    assert stay.end == date(1970, 1, 2)

    with pytest.raises(ValidationError):
        Stay(start=date(1970, 1, 2), end=date(1970, 1, 1))
