from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import STORAGE_DIR
from src.models import StoredFile
from src.repositories import files as file_repo


async def list_files(session: AsyncSession, offset: int, limit: int) -> tuple[list[StoredFile], int]:
    return await file_repo.get_all(session, offset=offset, limit=limit)


async def get_file(session: AsyncSession, file_id: str) -> StoredFile:
    file_item = await file_repo.get_by_id(session, file_id)
    if not file_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    return file_item


async def create_file(session: AsyncSession, title: str, upload_file: UploadFile) -> StoredFile:
    content = await upload_file.read()
    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File is empty")
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
