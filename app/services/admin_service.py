from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Admin
from app.config import settings


async def is_super_admin(telegram_id: int) -> bool:
    """
    بررسی می‌کند آیا کاربر سوپر ادمین است یا نه.
    """
    return telegram_id == settings.SUPER_ADMIN_ID


async def is_admin(session: AsyncSession, telegram_id: int) -> bool:
    """
    بررسی می‌کند آیا کاربر ادمین (معمولی یا سوپر) است یا نه.
    """

    # اگر سوپر ادمین باشد
    if await is_super_admin(telegram_id):
        return True

    result = await session.execute(
        select(Admin).where(Admin.telegram_id == telegram_id)
    )

    admin = result.scalar_one_or_none()

    return admin is not None
