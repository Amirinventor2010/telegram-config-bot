from aiogram import Router, F
from aiogram.types import Message, Document
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select
import os

from app.database.session import AsyncSessionLocal
from app.database.models import Config
from app.services.config_service import rename_config_link
from app.config import settings


router = Router()


# =========================
# 🧠 FSM States
# =========================
class AddConfigState(StatesGroup):
    waiting_for_link = State()
    waiting_for_npv_file = State()


# =====================================================
# 📡 افزودن V2Ray
# =====================================================
@router.message(F.text == "📡 افزودن V2Ray")
async def choose_v2ray(message: Message, state: FSMContext):
    await state.update_data(config_type="v2ray")

    await message.answer(
        "📨 لطفاً لینک کانفیگ V2Ray را ارسال کنید:\n\n"
        "پروتکل‌های پشتیبانی‌شده:\n"
        "vless / vmess / trojan / ss"
    )

    await state.set_state(AddConfigState.waiting_for_link)


# =====================================================
# 🛰 افزودن NPV (دریافت فایل)
# =====================================================
@router.message(F.text == "🛰 افزودن NPV")
async def choose_npv(message: Message, state: FSMContext):
    await state.update_data(config_type="npv")

    await message.answer(
        "📁 لطفاً فایل .npvt را ارسال کنید:"
    )

    await state.set_state(AddConfigState.waiting_for_npv_file)


# =====================================================
# 📨 ذخیره V2Ray
# =====================================================
@router.message(AddConfigState.waiting_for_link)
async def save_v2ray_config(message: Message, state: FSMContext):

    raw_link = (message.text or "").strip()

    if not raw_link:
        await message.answer("❌ لینک نامعتبر است.")
        return

    async with AsyncSessionLocal() as session:

        new_config = Config(
            type="v2ray",
            title="TEMP",
            value=raw_link,
            is_active=True
        )

        session.add(new_config)
        await session.commit()
        await session.refresh(new_config)

        config_id = new_config.id

        final_link = rename_config_link(raw_link, config_id)

        tag = settings.CONFIG_TAG_FORMAT.format(
            bot_name=settings.BOT_NAME,
            number=config_id
        )

        new_config.value = final_link
        new_config.title = tag

        await session.commit()

    await message.answer(
        "✅ کانفیگ V2Ray با موفقیت اضافه شد.\n\n"
        f"📌 عنوان: {tag}"
    )

    await state.clear()


# =====================================================
# 📂 ذخیره فایل NPV
# =====================================================
@router.message(AddConfigState.waiting_for_npv_file, F.document)
async def save_npv_file(message: Message, state: FSMContext):

    document: Document = message.document

    if not document.file_name.endswith(".npvt"):
        await message.answer("❌ فقط فایل با پسوند .npvt مجاز است.")
        return

    # ساخت پوشه اگر نبود
    os.makedirs("storage/npv", exist_ok=True)

    file_path = f"storage/npv/{document.file_unique_id}.npvt"

    await message.bot.download(
        document,
        destination=file_path
    )

    async with AsyncSessionLocal() as session:

        new_config = Config(
            type="npv",
            title=document.file_name,
            value=file_path,
            is_active=True
        )

        session.add(new_config)
        await session.commit()

    await message.answer("✅ فایل NPV با موفقیت ذخیره شد.")

    await state.clear()
