from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy import select

from app.database.session import AsyncSessionLocal
from app.database.models import Admin
from app.services.admin_service import is_admin
from app.keyboards.admin_kb import (
    admin_main_keyboard,
    admin_users_keyboard,
    admin_configs_keyboard,
    admin_ads_keyboard,
    admin_add_config_keyboard,
    admin_manage_config_keyboard,
    admin_manage_proxy_keyboard,
)
from app.keyboards.user_kb import user_main_keyboard
from app.config import settings

router = Router()


async def admin_check(message: Message):
    async with AsyncSessionLocal() as session:
        return await is_admin(session, message.from_user.id)


@router.message(F.text == "/panel")
async def admin_panel(message: Message):

    if not await admin_check(message):
        await message.answer("❌ دسترسی غیرمجاز.")
        return

    text = f"""
<b>🛠 پنل مدیریت {settings.BOT_NAME}</b>

از منوی زیر بخش مورد نظر را انتخاب کنید.
"""
    await message.answer(text, reply_markup=admin_main_keyboard())


@router.message(F.text == "👥 مدیریت کاربران")
async def manage_users(message: Message):
    if not await admin_check(message):
        return
    await message.answer(
        "<b>👥 مدیریت کاربران</b>\n\nعملیات مورد نظر را انتخاب کنید.",
        reply_markup=admin_users_keyboard()
    )


@router.message(F.text == "🗂 مدیریت کانفیگ و پروکسی")
async def manage_configs(message: Message):
    if not await admin_check(message):
        return
    await message.answer(
        "<b>🗂 مدیریت کانفیگ و پروکسی</b>\n\nعملیات مورد نظر را انتخاب کنید.",
        reply_markup=admin_configs_keyboard()
    )


@router.message(F.text == "📢 مدیریت تبلیغات")
async def manage_ads(message: Message):
    if not await admin_check(message):
        return
    await message.answer(
        "<b>📢 مدیریت تبلیغات</b>\n\nبخش مورد نظر را انتخاب کنید.",
        reply_markup=admin_ads_keyboard()
    )


@router.message(F.text == "➕ افزودن کانفیگ")
async def add_config_menu(message: Message):
    if not await admin_check(message):
        return
    await message.answer(
        "<b>➕ افزودن کانفیگ</b>\n\nنوع کانفیگ را انتخاب کنید.",
        reply_markup=admin_add_config_keyboard()
    )


@router.message(F.text == "🛠 مدیریت کانفیگ")
async def manage_config_menu(message: Message):
    if not await admin_check(message):
        return
    await message.answer(
        "<b>🛠 مدیریت کانفیگ</b>\n\nعملیات مورد نظر را انتخاب کنید.",
        reply_markup=admin_manage_config_keyboard()
    )


@router.message(F.text == "🛠 مدیریت پروکسی")
async def manage_proxy_menu(message: Message):
    if not await admin_check(message):
        return
    await message.answer(
        "<b>🛠 مدیریت پروکسی</b>\n\nعملیات مورد نظر را انتخاب کنید.",
        reply_markup=admin_manage_proxy_keyboard()
    )


@router.message(F.text == "🔙 بازگشت به مدیریت")
async def back_to_manage_menu(message: Message):
    if not await admin_check(message):
        return
    await message.answer(
        "<b>🗂 مدیریت کانفیگ و پروکسی</b>\n\nعملیات مورد نظر را انتخاب کنید.",
        reply_markup=admin_configs_keyboard()
    )


@router.message(F.text == "🔙 بازگشت به پنل")
async def back_to_admin_panel(message: Message):
    if not await admin_check(message):
        return
    await message.answer(
        "<b>🛠 پنل مدیریت</b>\n\nاز منوی زیر بخش مورد نظر را انتخاب کنید.",
        reply_markup=admin_main_keyboard()
    )


@router.message(F.text == "🔙 بازگشت به منوی کاربر")
async def back_to_user_menu(message: Message):
    text = f"""
<b>{settings.BRAND_TITLE}</b>

{settings.BRAND_DESCRIPTION}

{settings.START_MESSAGE_FOOTER}
"""
    await message.answer(
        text,
        reply_markup=user_main_keyboard()
    )
