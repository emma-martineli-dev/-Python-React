import asyncio
import os

from celery import Celery
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.models import Alert, StoredFile
from src.config import STORAGE_DIR
from src.db import DB_URL
from src.services.scanner import scan, extract_metadata

REDIS_URL = os.environ.get("REDIS_URL", "redis://backend-redis:6379/0")

celery_app = Celery("file_tasks", broker=REDIS_URL, backend=REDIS_URL)

_engine = create_async_engine(DB_URL)
_session_maker = async_sessionmaker(_engine, expire_on_commit=False)


def _run(coro):
    """Run an async coroutine from a sync Celery task."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            raise RuntimeError
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


# ── async implementations ────────────────────────────────────────────────────

async def _do_scan(file_id: str) -> None:
    async with _session_maker() as session:
        file_item: StoredFile | None = await session.get(StoredFile, file_id)
        if not file_item:
            return

        file_item.processing_status = "processing"
        await session.commit()

        scan_status, scan_details, requires_attention = scan(
            file_item.original_name, file_item.size, file_item.mime_type
        )
        file_item.scan_status = scan_status
        file_item.scan_details = scan_details
        file_item.requires_attention = requires_attention
        await session.commit()

    extract_file_metadata.delay(file_id)


async def _do_extract_metadata(file_id: str) -> None:
    async with _session_maker() as session:
        file_item: StoredFile | None = await session.get(StoredFile, file_id)
        if not file_item:
            return

        stored_path = STORAGE_DIR / file_item.stored_name
        if not stored_path.exists():
            file_item.processing_status = "failed"
            file_item.scan_status = file_item.scan_status or "failed"
            file_item.scan_details = "stored file not found during metadata extraction"
            await session.commit()
            send_file_alert.delay(file_id)
            return

        file_item.metadata_json = extract_metadata(
            file_item.stored_name, file_item.original_name, file_item.size, file_item.mime_type
        )
        file_item.processing_status = "processed"
        await session.commit()

    send_file_alert.delay(file_id)


async def _do_send_alert(file_id: str) -> None:
    async with _session_maker() as session:
        file_item: StoredFile | None = await session.get(StoredFile, file_id)
        if not file_item:
            return

        if file_item.processing_status == "failed":
            level, message = "critical", "File processing failed"
        elif file_item.requires_attention:
            level = "warning"
            message = f"File requires attention: {file_item.scan_details}"
        else:
            level, message = "info", "File processed successfully"

        session.add(Alert(file_id=file_id, level=level, message=message))
        await session.commit()


# ── celery tasks ─────────────────────────────────────────────────────────────

@celery_app.task(name="workers.scan_file_for_threats")
def scan_file_for_threats(file_id: str) -> None:
    _run(_do_scan(file_id))


@celery_app.task(name="workers.extract_file_metadata")
def extract_file_metadata(file_id: str) -> None:
    _run(_do_extract_metadata(file_id))


@celery_app.task(name="workers.send_file_alert")
def send_file_alert(file_id: str) -> None:
    _run(_do_send_alert(file_id))
