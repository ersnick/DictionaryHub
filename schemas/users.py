from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    fullname: str | None
    bio: str | None
    photo_path: str | None

    class Config:
        orm_mode = True
