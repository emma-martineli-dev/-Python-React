from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import STORAGE_DIR
from src.models import StoredFile
from src.repositories import files as file_repo

MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB hard limit
ALLOWED_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".gif", ".webp",
    ".pdf", ".txt", ".csv", ".json", ".xml",
    ".zip", ".tar", ".gz",
    ".exe", ".bat", ".cmd", ".sh", ".js",  # allowed but flagged by scanner
}


async def list_files(session: AsyncSession, offset: int, limit: int) -> tuple[list[StoredFile], int]:
    return await file_repo.get_all(session, offset=offset, limit=limit)


async def get_file(session: AsyncSession, file_id: str) -> StoredFile:
    file_item = await file_repo.get_by_id(session, file_id)
    if not file_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    return file_item


async def create_file(session: AsyncSession, title: str, upload_file: UploadFile) -> StoredFile:
    if not upload_file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Filename is required")

    ext = Path(upload_file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"File extension '{ext}' is not allowed",
        )

    content = await upload_file.read()
    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File is empty")
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File exceeds maximum allowed size of 100 MB",
        )

    return await file_repo.create_from_bytes(session, title=title, upload_file=upload_file, content=content)


async def update_file(session: AsyncSession, file_id: str, title: str) -> StoredFile:
    return await file_repo.update_title(session, await get_file(session, file_id), title)


async def delete_file(session: AsyncSession, file_id: str) -> None:
    await file_repo.delete(session, await get_file(session, file_id))


async def get_file_path(session: AsyncSession, file_id: str) -> tuple[StoredFile, Path]:
    file_item = await get_file(session, file_id)
    stored_path = STORAGE_DIR / file_item.stored_name
    if not stored_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stored file not found")
    return file_item, stored_path
