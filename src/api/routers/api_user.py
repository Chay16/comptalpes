from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from api.repository import load_users, save_users
from comptalpes.model.entities import User

router = APIRouter()


class UserPayload(BaseModel):
    name: str


def get_user_from_user_id(users: list[User], user_id: UUID) -> User:
    for user in users:
        if user.id == user_id:
            return user
    raise HTTPException(status_code=404, detail=f"User {user_id} not found.")


@router.get("/user/", tags=["users"])
def get_users():
    return load_users()


@router.post("/user/", tags=["users"])
def add_user(payload: UserPayload):
    user = User(name=payload.name)
    users = load_users()
    users.append(user)
    save_users(users)
    return user


@router.patch("/user/{user_id}", tags=["users"])
def update_user(user_id: UUID, payload: UserPayload):
    users = load_users()
    user = get_user_from_user_id(users, user_id)
    updated = User(id=user.id, name=payload.name)
    users[users.index(user)] = updated
    save_users(users)
    return updated


@router.delete("/user/{user_id}", tags=["users"])
def delete_user(user_id: UUID):
    users = load_users()
    user = get_user_from_user_id(users, user_id)
    users.remove(user)
    save_users(users)
    return user
