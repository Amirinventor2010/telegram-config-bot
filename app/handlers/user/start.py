from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from datetime import datetime
from sqlalchemy import select

from app.database.session import AsyncSessionLocal
from app.database.models import User
from app.keyboards.user_kb import user_main_keyboard
from app.keyboards.ad_kb import ad_channels_keyboard
from app.services.ad_service import (
    get_active_channels,
    is_user_member_all
)
from app.config import settings


router = Router()


# =====================================================
# 🚀 دستور /start
# =====================================================
@router.message(lambda message: message.text == "/start")
async def start_handler(message: Message):

    async with AsyncSessionLocal() as session:

        # -------------------------
        # گرفتن یا ساخت کاربر
        # -------------------------
        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()

        if not user:
            user = User(
                telegram_id=message.from_user.id,
                joined_at=datetime.utcnow(),
                last_active=datetime.utcnow(),
                is_banned=False
            )
            session.add(user)
            await session.commit()
        else:
            user.last_active = datetime.utcnow()
            await session.commit()

        # -------------------------
        # گرفتن کانال‌های فعال
        # -------------------------
        channels = await get_active_channels(session)

        # اگر تبلیغی نداریم → مستقیم منو
        if not channels:
            await message.answer(
                settings.WELCOME_TEXT.strip(),
                reply_markup=user_main_keyboard()
            )
            return

        # -------------------------
        # چک لحظه‌ای عضویت
        # -------------------------
        is_member = await is_user_member_all(
            message.bot,
            session,
            message.from_user.id
        )

        if is_member:
            await message.answer(
                settings.WELCOME_TEXT.strip(),
                reply_markup=user_main_keyboard()
            )
            return

        # -------------------------
        # نمایش تبلیغات
        # -------------------------
        await message.answer(
            "📢 لطفاً در کانال‌های زیر عضو شوید و سپس تایید را بزنید:",
            reply_markup=ad_channels_keyboard(channels)
        )


# =====================================================
# ✅ تایید عضویت در کانال‌ها
# =====================================================
@router.callback_query(F.data == "confirm_ads")
async def confirm_ads(callback: CallbackQuery):

    async with AsyncSessionLocal() as session:

        is_member = await is_user_member_all(
            callback.bot,
            session,
            callback.from_user.id
        )

        # اگر هنوز عضو نیست
        if not is_member:
            await callback.answer(
                "❌ هنوز عضو همه کانال‌ها نیستید.",
                show_alert=True
            )
            return

        # حذف پیام تبلیغ
        try:
            await callback.message.delete()
        except:
            pass

        # نمایش منوی اصلی
        await callback.message.answer(
            settings.WELCOME_TEXT.strip(),
            reply_markup=user_main_keyboard()
        )

        await callback.answer()
