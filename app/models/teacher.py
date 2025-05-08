from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field, EmailStr, GetJsonSchemaHandler
from bson import ObjectId
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema


class PyObjectId(ObjectId):
    # Supprimer les anciennes méthodes de validation
    # @classmethod
    # def __get_validators__(cls):
    #     yield cls.validate
    #
    # @classmethod
    # def validate(cls, v):
    #     if not ObjectId.is_valid(v):
    #         raise ValueError("Invalid ObjectId")
    #     return ObjectId(v)

    # Utiliser cette méthode pour Pydantic v2
    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type, _handler):
        return core_schema.union_schema([
            core_schema.is_instance_schema(ObjectId),
            core_schema.chain_schema([
                core_schema.str_schema(),
                core_schema.no_info_plain_validator_function(cls.validate_from_str),
            ]),
        ])

    @staticmethod
    def validate_from_str(value: str) -> ObjectId:
        if not ObjectId.is_valid(value):
            raise ValueError("Invalid ObjectId")
        return ObjectId(value)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema, **kwargs):
        field_schema.update(type="string")
        return field_schema

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