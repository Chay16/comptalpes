from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from comptalpes.model.entities import BaseEntity


def test_base_entity_generates_uuid() -> None:
    entity = BaseEntity()
    assert isinstance(entity.id, UUID)


def test_base_entity_ids_are_unique() -> None:
    first = BaseEntity()
    second = BaseEntity()
    assert first.id != second.id


def test_base_entity_rejects_invalid_uuid() -> None:
    with pytest.raises(ValidationError):
        BaseEntity(id="not-a-uuid")


def test_base_entity_id_is_frozen() -> None:
    entity = BaseEntity()
    other_id = uuid4()
    with pytest.raises(ValidationError):
        entity.id = other_id
    assert entity.id != other_id
