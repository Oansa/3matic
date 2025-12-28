from pydantic import BaseModel, EmailStr, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema
from typing import Optional, List, Dict, Any, Annotated
from datetime import datetime
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: Any
    ) -> core_schema.CoreSchema:
        def validate(value: Any) -> ObjectId:
            if isinstance(value, ObjectId):
                return value
            if isinstance(value, str):
                if ObjectId.is_valid(value):
                    return ObjectId(value)
                raise ValueError("Invalid ObjectId string")
            raise ValueError("Invalid ObjectId")

        return core_schema.no_info_plain_validator_function(validate)

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        return {"type": "string"}

class User(BaseModel):
    id: Optional[PyObjectId] = None
    email: EmailStr
    name: Optional[str] = None
    provider: str  # google, github
    provider_id: str
    created_at: Optional[datetime] = None

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class Community(BaseModel):
    id: Optional[PyObjectId] = None
    userId: PyObjectId
    name: Optional[str] = None
    telegram_token: str
    telegram_chat_id: str
    status: str = "inactive"  # inactive, active, deploying
    purpose: Optional[str] = None
    rules: List[str] = []
    moderationLevel: str = "medium"  # low, medium, high
    engagementStyle: str = "friendly"  # formal, friendly, casual
    postingFrequency: str = "moderate"  # low, moderate, high
    documents: List[Dict[str, Any]] = []
    scheduledPosts: List[Dict[str, Any]] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class Document(BaseModel):
    filename: str
    size: int
    content_type: str
    uploaded_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class OAuthCallback(BaseModel):
    code: str
    state: Optional[str] = None

