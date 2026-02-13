from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy import select
import os

from app.database.session import AsyncSessionLocal
from app.database.models import Config, User
from app.services.ad_service import is_user_member_all, get_active_channels
from app.keyboards.user_kb import config_submenu_keyboard, user_main_keyboard
from app.keyboards.user_config_kb import config_pagination_keyboard
from app.keyboards.ad_kb import ad_channels_keyboard
from app.config import settings

router = Router()

CONFIGS_PER_PAGE = 5


# =========================
# 🧠 Pagination State
# =========================
class ConfigPagination(StatesGroup):
    offset = State()


# =========================
# 📥 منوی دریافت کانفیگ
# =========================
@router.message(F.text == "📥 دریافت کانفیگ")
async def config_menu(message: Message):

    async with AsyncSessionLocal() as session:

        # 🔴 چک بن
        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()

        if user and user.is_banned:
            await message.answer("⛔ شما از استفاده از ربات مسدود شده‌اید.")
            return

        # ✅ چک عضویت لحظه‌ای تبلیغات
        is_member = await is_user_member_all(
            message.bot,
            session,
            message.from_user.id
        )

        if not is_member:
            channels = await get_active_channels(session)

            await message.answer(
                "❌ برای استفاده از ربات ابتدا باید عضو کانال‌های زیر باشید:",
                reply_markup=ad_channels_keyboard(channels)
            )
            return

    await message.answer(
        "نوع کانفیگ مورد نظر را انتخاب کنید:",
        reply_markup=config_submenu_keyboard()
    )


# =========================
# 📡 کانفیگ V2Ray (لینکی + صفحه‌بندی)
# =========================
@router.message(F.text == "📡 کانفیگ V2Ray")
async def get_v2ray_configs(message: Message, state: FSMContext):
    await send_configs_by_type(message, state, "v2ray")


# =========================
# 🛰 کانفیگ NPV (فایل واقعی)
# =========================
@router.message(F.text == "🛰 کانفیگ NPV")
async def get_npv_configs(message: Message):

    async with AsyncSessionLocal() as session:

        # 🔴 چک بن
        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()

        if user and user.is_banned:
            await message.answer("⛔ شما از استفاده از ربات مسدود شده‌اید.")
            return

        # ✅ چک عضویت تبلیغات
        is_member = await is_user_member_all(
            message.bot,
            session,
            message.from_user.id
        )

        if not is_member:
            channels = await get_active_channels(session)

            await message.answer(
                "❌ ابتدا عضو کانال‌ها شوید:",
                reply_markup=ad_channels_keyboard(channels)
            )
            return

        result = await session.execute(
            select(Config)
            .where(
                Config.type == "npv",
                Config.is_active == True
            )
            .order_by(Config.id.desc())
        )

        configs = result.scalars().all()

    if not configs:
        await message.answer("❌ فایل NPV موجود نیست.")
        return

    for config in configs:

        file_path = config.value

        if not os.path.exists(file_path):
            await message.answer("❌ فایل روی سرور یافت نشد.")
            continue

        try:
            file = FSInputFile(file_path)
            await message.answer_document(
                file,
                caption=f"🛰 {settings.BOT_NAME} — فایل NPV شما"
            )
        except Exception:
            await message.answer("❌ خطا در ارسال فایل.")


# =========================
# 🔙 بازگشت
# =========================
@router.message(F.text == "🔙 بازگشت")
async def back_to_main(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        settings.WELCOME_TEXT.strip(),
        reply_markup=user_main_keyboard()
    )


# =========================
# 📤 گرفتن کانفیگ‌های لینکی
# =========================
async def send_configs_by_type(message: Message, state: FSMContext, config_type: str):

    async with AsyncSessionLocal() as session:

        # 🔴 چک بن
        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()

        if user and user.is_banned:
            await message.answer("⛔ شما از استفاده از ربات مسدود شده‌اید.")
            return

        # ✅ چک عضویت تبلیغات
        is_member = await is_user_member_all(
            message.bot,
            session,
            message.from_user.id
        )

        if not is_member:
            channels = await get_active_channels(session)

            await message.answer(
                "❌ ابتدا عضو کانال‌ها شوید:",
                reply_markup=ad_channels_keyboard(channels)
            )
            return

        result = await session.execute(
            select(Config)
            .where(
                Config.type == config_type,
                Config.is_active == True
            )
            .order_by(Config.id.desc())
        )

        configs = result.scalars().all()

    if not configs:
        await message.answer(settings.NO_CONFIG_TEXT)
        return

    await state.update_data(
        configs=[c.value for c in configs],
        offset=0
    )

    await send_configs_page(message, state)


# =========================
# ➡️ صفحه بعد
# =========================
@router.callback_query(F.data == "next_configs")
async def next_configs(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await send_configs_page(callback.message, state, edit=True)


# =========================
# 📄 ارسال صفحه
# =========================
async def send_configs_page(message: Message, state: FSMContext, edit=False):

    data = await state.get_data()
    configs = data.get("configs", [])
    offset = data.get("offset", 0)

    next_offset = offset + CONFIGS_PER_PAGE
    page = configs[offset:next_offset]

    if not page:
        text = "❌ کانفیگ بیشتری موجود نیست."
        if edit:
            await message.edit_text(text)
        else:
            await message.answer(text)
        await state.clear()
        return

    text = f"✨ <b>{settings.BOT_NAME}</b> — لیست کانفیگ‌ها\n\n"

    for idx, link in enumerate(page, start=offset + 1):
        text += "━━━━━━━━━━━━━━\n"
        text += f"🔹 کانفیگ {idx}\n"
        text += f"<code>{link}</code>\n\n"

    await state.update_data(offset=next_offset)

    if edit:
        await message.edit_text(
            text,
            reply_markup=config_pagination_keyboard()
        )
    else:
        await message.answer(
            text,
            reply_markup=config_pagination_keyboard()
        )
