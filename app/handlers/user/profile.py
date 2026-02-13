from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy import select
from datetime import datetime
from zoneinfo import ZoneInfo

from app.config import settings
from app.database.session import AsyncSessionLocal
from app.database.models import User, Admin


router = Router()

TEHRAN_TZ = ZoneInfo("Asia/Tehran")


@router.message(F.text.contains("پروفایل"))
async def user_profile(message: Message):
    async with AsyncSessionLocal() as session:

        # گرفتن اطلاعات کاربر
        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()

        # بررسی ادمین بودن
        admin_result = await session.execute(
            select(Admin).where(Admin.telegram_id == message.from_user.id)
        )
        is_admin = admin_result.scalar_one_or_none()

        if not user:
            await message.answer("خطا در دریافت اطلاعات کاربر.")
            return

        # آپدیت فقط last_active (نه joined_at)
        user.last_active = datetime.utcnow()
        await session.commit()

        # تبدیل ساعت‌ها به تایم تهران
        joined_tehran = user.joined_at.replace(tzinfo=ZoneInfo("UTC")).astimezone(TEHRAN_TZ)
        last_active_tehran = user.last_active.replace(tzinfo=ZoneInfo("UTC")).astimezone(TEHRAN_TZ)

        role = "👑 Admin" if is_admin else "👤 User"

        text = f"""
✨ <b>{settings.BOT_NAME}</b> — پروفایل کاربری

━━━━━━━━━━━━━━
🆔 <b>Telegram ID:</b> <code>{user.telegram_id}</code>
📅 <b>عضویت از:</b> {joined_tehran.strftime('%Y-%m-%d %H:%M')}
⏱ <b>آخرین فعالیت:</b> {last_active_tehran.strftime('%Y-%m-%d %H:%M')}
🛡 <b>نقش:</b> {role}
💠 <b>وضعیت حساب:</b> Active
━━━━━━━━━━━━━━
        """

        await message.answer(text)
