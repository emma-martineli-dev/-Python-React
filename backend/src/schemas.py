from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field, field_validator

T = TypeVar("T")

MAX_TITLE_LEN = 255
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_MIME_PREFIXES = ("image/", "text/", "application/pdf", "application/octet-stream")


class FileItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    original_name: str
    mime_type: str
    size: int
    processing_status: str
    scan_status: str | None
    scan_details: str | None
    metadata_json: dict | None
    requires_attention: bool
    created_at: datetime
    updated_at: datetime


class FileCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=MAX_TITLE_LEN, strip_whitespace=True)


class FileUpdate(BaseModel):
    title: str = Field(..., min_length=1, max_length=MAX_TITLE_LEN, strip_whitespace=True)


class AlertItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    file_id: str
    level: str
    message: str
    created_at: datetime


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int
    offset: int
    limit: int
