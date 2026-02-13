from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest

from app.database.models import AdChannel


# =====================================================
# گرفتن تمام کانال‌های فعال
# =====================================================
async def get_active_channels(session: AsyncSession):
    result = await session.execute(
        select(AdChannel)
        .where(AdChannel.is_active == True)
        .order_by(AdChannel.id)
    )
    return result.scalars().all()


# =====================================================
# چک لحظه‌ای عضویت کاربر در تمام کانال‌ها
# =====================================================
async def is_user_member_all(
    bot: Bot,
    session: AsyncSession,
    telegram_id: int
) -> bool:

    channels = await get_active_channels(session)

    if not channels:
        return True  # اگر تبلیغی نداریم، آزاد است

    for ch in channels:
        try:
            member = await bot.get_chat_member(
                chat_id=ch.channel_id,
                user_id=telegram_id
            )

            if member.status in ["left", "kicked"]:
                return False

        except TelegramBadRequest:
            return False

    return True
