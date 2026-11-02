import pytest
from pydantic import ValidationError

from comptalpes.model.entities import User


def test_user() -> None:
    user = User(name="Alice")
    assert user.name == "Alice"


def test_user_requires_name() -> None:
    with pytest.raises(ValidationError):
        User()
