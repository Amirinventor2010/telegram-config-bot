from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User


async def get_user_by_telegram_id(
    session: AsyncSession,
    telegram_id: int
):
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    return result.scalar_one_or_none()


async def is_user_banned(
    session: AsyncSession,
    telegram_id: int
) -> bool:

    user = await get_user_by_telegram_id(session, telegram_id)

    if not user:
        return False

    return user.is_banned
