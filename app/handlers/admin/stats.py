from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy import select, func
from datetime import datetime

from app.database.session import AsyncSessionLocal
from app.database.models import User, Config, AdChannel
from app.services.admin_service import is_admin

router = Router()


@router.message(F.text == "📊 آمار کاربران")
async def admin_stats(message: Message):

    async with AsyncSessionLocal() as session:

        # 🔐 چک ادمین
        if not await is_admin(session, message.from_user.id):
            await message.answer("❌ دسترسی غیرمجاز.")
            return

        total_users = (
            await session.execute(select(func.count()).select_from(User))
        ).scalar() or 0

        today_start = datetime.utcnow().replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        today_users = (
            await session.execute(
                select(func.count())
                .select_from(User)
                .where(User.joined_at >= today_start)
            )
        ).scalar() or 0

        active_today = (
            await session.execute(
                select(func.count())
                .select_from(User)
                .where(User.last_active >= today_start)
            )
        ).scalar() or 0

        total_configs = (
            await session.execute(
                select(func.count())
                .select_from(Config)
                .where(Config.type != "proxy")
            )
        ).scalar() or 0

        total_proxies = (
            await session.execute(
                select(func.count())
                .select_from(Config)
                .where(Config.type == "proxy")
            )
        ).scalar() or 0

        total_ads = (
            await session.execute(
                select(func.count()).select_from(AdChannel)
            )
        ).scalar() or 0

    text = (
        "📊 <b>آمار کلی بات</b>\n\n"
        f"👥 کل کاربران: <b>{total_users}</b>\n"
        f"📅 کاربران جدید امروز: <b>{today_users}</b>\n"
        f"🟢 فعال امروز: <b>{active_today}</b>\n\n"
        f"📦 تعداد کانفیگ‌ها: <b>{total_configs}</b>\n"
        f"🌐 تعداد پروکسی‌ها: <b>{total_proxies}</b>\n"
        f"📢 کانال‌های تبلیغاتی: <b>{total_ads}</b>"
    )

    await message.answer(text)
