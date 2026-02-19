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

PROMO_TEXT = "\n\n⭐️ کانفیگ های رایگان بیشتر در :\n🟢 @ConfigFreeRbot"


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

        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()

        if user and user.is_banned:
            await message.answer("⛔ شما از استفاده از ربات مسدود شده‌اید.")
            return

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
# 📡 کانفیگ V2Ray
# =========================
@router.message(F.text == "📡 کانفیگ V2Ray")
async def get_v2ray_configs(message: Message, state: FSMContext):
    await send_configs_by_type(message, state, "v2ray")


# =========================
# 🛰 کانفیگ NPV (فایل واقعی - صفحه‌بندی شده)
# =========================
@router.message(F.text == "🛰 کانفیگ NPV")
async def get_npv_configs(message: Message, state: FSMContext):

    async with AsyncSessionLocal() as session:

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

    await state.update_data(
        npv_configs=[(c.id, c.value) for c in configs],
        offset=0
    )

    await send_npv_page(message, state)


async def send_npv_page(message: Message, state: FSMContext, edit=False):

    data = await state.get_data()
    configs = data.get("npv_configs", [])
    offset = data.get("offset", 0)

    per_page = settings.ITEMS_PER_PAGE
    next_offset = offset + per_page
    page = configs[offset:next_offset]

    if not page:
        text = "❌ فایل بیشتری موجود نیست."
        if edit:
            await message.edit_text(text)
        else:
            await message.answer(text)
        await state.clear()
        return

    for config_id, file_path in page:

        if not os.path.exists(file_path):
            await message.answer("❌ فایل روی سرور یافت نشد.")
            continue

        try:
            file = FSInputFile(file_path)

            await message.answer_document(
                file,
                caption=(
                    f"🛰 {settings.BOT_NAME} — فایل NPV شما\n"
                    f"{PROMO_TEXT}"
                )
            )

        except Exception:
            await message.answer("❌ خطا در ارسال فایل.")

    await state.update_data(offset=next_offset)

    if next_offset < len(configs):
        await message.answer(
            "⬇️ برای دریافت فایل‌های بعدی:",
            reply_markup=config_pagination_keyboard()
        )


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


@router.callback_query(F.data == "next_configs")
async def next_configs(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await send_configs_page(callback.message, state, edit=True)


async def send_configs_page(message: Message, state: FSMContext, edit=False):

    data = await state.get_data()
    configs = data.get("configs", [])
    offset = data.get("offset", 0)

    per_page = settings.ITEMS_PER_PAGE
    next_offset = offset + per_page
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

    text += PROMO_TEXT

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
