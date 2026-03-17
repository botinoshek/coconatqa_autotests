from pydantic import BaseModel, Field, field_validator
from typing import Optional
import datetime
import re
from typing import List
from pydantic import BaseModel, Field, field_validator
from constans.roles import Roles

class BaseUser(BaseModel):
    id: str | None = None
    email: str
    fullName: str
    password: str
    passwordRepeat: str = Field(..., min_length=1, max_length=20)

    @field_validator("passwordRepeat")
    def check_password_repeat(cls, value: str, info) -> str:
        if "password" in info.data and value != info.data["password"]:
            raise ValueError("Пароли не совпадают")
        return value

class TestUser(BaseUser):
    roles: list[Roles] = [Roles.USER]
    verified: Optional[bool] = None
    banned: Optional[bool] = None

    class Config:
        json_encoders = {Roles: lambda v: v.value}

# ---------- Register ----------

class RegisterUserRequest(BaseUser):
    """Данные для регистрации пользователя"""
    pass

class RegisterUserResponse(BaseModel):
    id: str
    email: str = Field(pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", description="Email пользователя")
    fullName: str = Field(min_length=1, max_length=100, description="Полное имя пользователя")
    verified: bool
    banned: Optional[bool] = None
    roles: List[Roles]
    createdAt: str = Field(description="Дата и время создания пользователя в формате ISO 8601")

    @field_validator("createdAt")
    def validate_created_at(cls, value: str) -> str:
        # Валидатор для проверки формата даты и времени (ISO 8601).
        try:
            datetime.datetime.fromisoformat(value)
        except ValueError:
            raise ValueError("Некорректный формат даты и времени. Ожидается формат ISO 8601.")
        return value
# ---------- Login ----------
class LoginUserRequest(BaseModel):
    email: str = Field(pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", description="Email пользователя")
    password: str

class LoginUserInfo(BaseModel):
    id: str
    email: str
    fullName: str
    roles: list[Roles]

class LoginUserResponse(BaseModel):
    user: LoginUserInfo
    accessToken: str
    refreshToken: str | None = None
    expiresIn: int

# ---------- Create User ----------
class CreateUserRequests(BaseUser):
    passwordRepeat:  str | None = Field(default=None, exclude=True)
    verified: Optional[bool] = None
    banned: Optional[bool] = None

class CreateUserResponse(RegisterUserResponse):
    """Данные для проверки созданного пользователя"""
    pass
# ---------- Delete User ----------
class DeleteUserResponse(RegisterUserResponse):
    pass