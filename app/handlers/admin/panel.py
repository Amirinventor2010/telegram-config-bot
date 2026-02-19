from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy import select

from app.database.session import AsyncSessionLocal
from app.database.models import Admin
from app.services.admin_service import is_admin, is_super_admin
from app.keyboards.admin_kb import (
    admin_main_keyboard,
    admin_users_keyboard,
    admin_configs_keyboard,
    admin_ads_keyboard,
    admin_manage_admins_keyboard,
)
from app.keyboards.user_kb import user_main_keyboard
from app.config import settings

router = Router()


# =========================
# 🧠 FSM برای مدیریت ادمین
# =========================
class ManageAdminState(StatesGroup):
    waiting_for_add_id = State()
    waiting_for_remove_id = State()


async def admin_check(message: Message):
    async with AsyncSessionLocal() as session:
        return await is_admin(session, message.from_user.id)


# =========================
# 🛠 پنل اصلی
# =========================
@router.message(F.text == "/panel")
async def admin_panel(message: Message):

    if not await admin_check(message):
        await message.answer("❌ دسترسی غیرمجاز.")
        return

    text = f"""
<b>{settings.ADMIN_PANEL_TITLE}</b>

{settings.ADMIN_PANEL_DESCRIPTION}

{settings.ADMIN_PANEL_FOOTER}
"""

    if await is_super_admin(message.from_user.id):
        keyboard = admin_main_keyboard(include_admin_manage=True)
    else:
        keyboard = admin_main_keyboard()

    await message.answer(text, reply_markup=keyboard)


# =========================
# 👥 مدیریت کاربران
# =========================
@router.message(F.text == "👥 مدیریت کاربران")
async def manage_users(message: Message):
    if not await admin_check(message):
        return

    await message.answer(
        "<b>👥 مدیریت کاربران</b>\n\nعملیات مورد نظر را انتخاب کنید.",
        reply_markup=admin_users_keyboard()
    )


# =========================
# 👑 مدیریت ادمین‌ها
# =========================
@router.message(F.text == "👑 مدیریت ادمین‌ها")
async def manage_admins(message: Message):

    if not await is_super_admin(message.from_user.id):
        await message.answer("❌ فقط سوپر ادمین دسترسی دارد.")
        return

    await message.answer(
        "<b>👑 مدیریت ادمین‌ها</b>\n\nعملیات مورد نظر را انتخاب کنید.",
        reply_markup=admin_manage_admins_keyboard()
    )


# =========================
# ➕ درخواست افزودن ادمین
# =========================
@router.message(F.text == "➕ افزودن ادمین")
async def request_add_admin(message: Message, state: FSMContext):

    if not await is_super_admin(message.from_user.id):
        return

    await state.set_state(ManageAdminState.waiting_for_add_id)
    await message.answer("🆔 آیدی عددی کاربر جدید را ارسال کنید.")


@router.message(ManageAdminState.waiting_for_add_id)
async def add_admin_handler(message: Message, state: FSMContext):

    if not message.text.isdigit():
        await message.answer("❌ فقط آیدی عددی ارسال کنید.")
        return

    new_admin_id = int(message.text)

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Admin).where(Admin.telegram_id == new_admin_id)
        )
        existing = result.scalar_one_or_none()

        if existing:
            await message.answer("⚠️ این کاربر قبلاً ادمین است.")
            await state.clear()
            return

        session.add(Admin(telegram_id=new_admin_id))
        await session.commit()

    await message.answer("✅ ادمین جدید با موفقیت اضافه شد.")
    await state.clear()


# =========================
# ➖ درخواست حذف ادمین
# =========================
@router.message(F.text == "➖ حذف ادمین")
async def request_remove_admin(message: Message, state: FSMContext):

    if not await is_super_admin(message.from_user.id):
        return

    await state.set_state(ManageAdminState.waiting_for_remove_id)
    await message.answer("🆔 آیدی عددی ادمینی که می‌خواهید حذف شود را ارسال کنید.")


@router.message(ManageAdminState.waiting_for_remove_id)
async def remove_admin_handler(message: Message, state: FSMContext):

    if not message.text.isdigit():
        await message.answer("❌ فقط آیدی عددی ارسال کنید.")
        return

    admin_id = int(message.text)

    # جلوگیری از حذف سوپر ادمین اصلی
    if admin_id in settings.ADMIN_IDS:
        await message.answer("⛔ امکان حذف سوپر ادمین وجود ندارد.")
        await state.clear()
        return

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Admin).where(Admin.telegram_id == admin_id)
        )
        admin = result.scalar_one_or_none()

        if not admin:
            await message.answer("❌ چنین ادمینی وجود ندارد.")
            await state.clear()
            return

        await session.delete(admin)
        await session.commit()

    await message.answer("✅ ادمین با موفقیت حذف شد.")
    await state.clear()


# =========================
# 🗂 مدیریت کانفیگ
# =========================
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


@router.message(F.text == "🔙 بازگشت به پنل")
async def back_to_admin_panel(message: Message):
    await admin_panel(message)


@router.message(F.text == "🔙 بازگشت به منوی کاربر")
async def back_to_user_menu(message: Message):
    text = f"""
<b>{settings.BRAND_TITLE}</b>

{settings.BRAND_DESCRIPTION}

{settings.START_MESSAGE_FOOTER}
"""
    await message.answer(text, reply_markup=user_main_keyboard())
