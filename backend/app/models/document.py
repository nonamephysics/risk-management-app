from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict
from datetime import datetime
from bson import ObjectId


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")
        return field_schema


class ValidationError(BaseModel):
    column: str
    row: int
    value: str
    message: str


class Document(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    tag: str = Field(..., description="Document tag/name")
    filename: str = Field(..., description="Original filename")
    file_type: str = Field(..., description="File type (csv/xlsx)")
    data: List[Dict[str, Any]] = Field(..., description="Document data")
    validation_errors: List[ValidationError] = Field(default=[], description="Validation errors found")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = Field(default=None, description="User who created the document")
    updated_by: Optional[str] = Field(default=None, description="User who last updated the document")

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class DocumentCreate(BaseModel):
    tag: str = Field(..., description="Document tag/name")


class DocumentUpdate(BaseModel):
    tag: Optional[str] = None
    data: Optional[List[Dict[str, Any]]] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    updated_by: Optional[str] = None


class DocumentResponse(BaseModel):
    id: str
    tag: str
    filename: str
    file_type: str
    data: List[Dict[str, Any]]
    validation_errors: List[ValidationError]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    updated_by: Optional[str] = None


class DocumentListResponse(BaseModel):
    id: str
    tag: str
    filename: str
    file_type: str
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    updated_at: datetime
    error_count: int