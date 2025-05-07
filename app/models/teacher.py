from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field, EmailStr, GetJsonSchemaHandler
from bson import ObjectId
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class TeacherBase(BaseModel):
    firstName: str
    lastName: str
    email: EmailStr
    profilePicture: Optional[str] = None
    school: str

class TeacherCreate(TeacherBase):
    password: str

class TeacherUpdate(BaseModel):
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    email: Optional[EmailStr] = None
    profilePicture: Optional[str] = None
    school: Optional[str] = None
    password: Optional[str] = None

class TeacherInDBBase(TeacherBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    lastLogin: Optional[datetime] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class Teacher(TeacherInDBBase):
    pass

class TeacherInDB(TeacherInDBBase):
    hashed_password: str