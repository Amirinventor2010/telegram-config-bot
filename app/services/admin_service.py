from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Admin


async def is_admin(session: AsyncSession, telegram_id: int) -> bool:
    """
    بررسی می‌کند آیا کاربر ادمین است یا نه.
    """

    result = await session.execute(
        select(Admin).where(Admin.telegram_id == telegram_id)
    )

    admin = result.scalar_one_or_none()

    return admin is not None
