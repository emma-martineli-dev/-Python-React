from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.db import get_session
from src.schemas import FileItem, FileUpdate, Page
from src.services import files as file_service
from src.workers.tasks import scan_file_for_threats

router = APIRouter(prefix="/files", tags=["files"])


@router.get("", response_model=Page[FileItem])
async def list_files(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
):
    items, total = await file_service.list_files(session, offset=offset, limit=limit)
    return Page(items=items, total=total, offset=offset, limit=limit)


@router.post("", response_model=FileItem, status_code=status.HTTP_201_CREATED)
async def create_file(
    title: str = Form(..., min_length=1, max_length=255),
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
):
    file_item = await file_service.create_file(session, title=title.strip(), upload_file=file)
    scan_file_for_threats.delay(file_item.id)
    return file_item


@router.get("/{file_id}", response_model=FileItem)
async def get_file(file_id: str, session: AsyncSession = Depends(get_session)):
    return await file_service.get_file(session, file_id)


@router.patch("/{file_id}", response_model=FileItem)
async def update_file(
    file_id: str,
    payload: FileUpdate,
    session: AsyncSession = Depends(get_session),
):
    return await file_service.update_file(session, file_id=file_id, title=payload.title)


@router.get("/{file_id}/download")
async def download_file(file_id: str, session: AsyncSession = Depends(get_session)):
    file_item, stored_path = await file_service.get_file_path(session, file_id)
    return FileResponse(
        path=stored_path,
        media_type=file_item.mime_type,
        filename=file_item.original_name,
    )


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(file_id: str, session: AsyncSession = Depends(get_session)):
    await file_service.delete_file(session, file_id)
