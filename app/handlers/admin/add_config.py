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
# 📨 ذخیره V2Ray (پشتیبانی چندخطی)
# =====================================================
@router.message(AddConfigState.waiting_for_link)
async def save_v2ray_config(message: Message, state: FSMContext):

    raw_text = (message.text or "").strip()

    if not raw_text:
        await message.answer("❌ لینک نامعتبر است.")
        return

    # جدا کردن بر اساس خط
    lines = [
        line.strip()
        for line in raw_text.splitlines()
        if line.strip()
    ]

    if not lines:
        await message.answer("❌ هیچ کانفیگ معتبری یافت نشد.")
        return

    added_count = 0

    async with AsyncSessionLocal() as session:

        for link in lines:

            # فقط لینک‌هایی که شبیه کانفیگ هستند
            if not link.lower().startswith(
                ("vless://", "vmess://", "trojan://", "ss://")
            ):
                continue

            new_config = Config(
                type="v2ray",
                title="TEMP",
                value=link,
                is_active=True
            )

            session.add(new_config)
            await session.commit()
            await session.refresh(new_config)

            config_id = new_config.id

            # ری‌نیم بر اساس سیستم جدید
            final_link = rename_config_link(link, config_id)

            tag = f"@ConfigFreeRbot | 🟢 کانفیگ رایگان | {config_id}"

            new_config.value = final_link
            new_config.title = tag

            await session.commit()

            added_count += 1

    if added_count == 0:
        await message.answer("❌ هیچ کانفیگ معتبری ذخیره نشد.")
    else:
        await message.answer(
            f"✅ {added_count} کانفیگ با موفقیت اضافه شد."
        )

    await state.clear()


# =====================================================
# 📂 ذخیره فایل NPV (با Rename حرفه‌ای)
# =====================================================
@router.message(AddConfigState.waiting_for_npv_file, F.document)
async def save_npv_file(message: Message, state: FSMContext):

    document: Document = message.document

    if not document.file_name.lower().endswith(".npvt"):
        await message.answer("❌ فقط فایل با پسوند .npvt مجاز است.")
        return

    os.makedirs("storage/npv", exist_ok=True)

    # مرحله 1: ذخیره موقت
    temp_path = f"storage/npv/temp_{document.file_unique_id}.npvt"

    await message.bot.download(
        document,
        destination=temp_path
    )

    async with AsyncSessionLocal() as session:

        # مرحله 2: ساخت رکورد برای گرفتن ID
        new_config = Config(
            type="npv",
            title="TEMP",
            value=temp_path,
            is_active=True
        )

        session.add(new_config)
        await session.commit()
        await session.refresh(new_config)

        config_id = new_config.id

        # مرحله 3: ساخت نام نهایی فایل
        final_filename = f"{config_id}_@ConfigFreeRbot.npvt"
        final_path = f"storage/npv/{final_filename}"

        # Rename واقعی فایل
        os.rename(temp_path, final_path)

        # آپدیت دیتابیس
        new_config.title = final_filename
        new_config.value = final_path

        await session.commit()

    await message.answer(
        f"✅ فایل NPV با موفقیت ذخیره شد.\n\n"
        f"📌 نام فایل: {final_filename}"
    )

    await state.clear()
