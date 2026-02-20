from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from app.database.session import AsyncSessionLocal
from app.database.models import Config
from app.config import settings


router = Router()


# =========================
# 🧠 FSM State
# =========================
class AddProxyState(StatesGroup):
    waiting_for_proxy = State()


# =========================
# ➕ شروع افزودن پروکسی
# =========================
@router.message(F.text == "➕ افزودن پروکسی")
async def start_add_proxy(message: Message, state: FSMContext):

    await message.answer(
        "📨 لطفاً متن پروکسی را ارسال کنید:\n\n"
        "مثال:\n"
        "tg://proxy?server=1.1.1.1&port=443&secret=abcdef"
    )

    await state.set_state(AddProxyState.waiting_for_proxy)

# =========================
# 📥 دریافت و ذخیره پروکسی (چندخطی بدون محدودیت)
# =========================
@router.message(AddProxyState.waiting_for_proxy)
async def save_proxy(message: Message, state: FSMContext):

    raw_text = (message.text or "").strip()

    if not raw_text:
        await message.answer("❌ پروکسی نامعتبر است.")
        return

    # جدا کردن خطوط
    lines = [
        line.strip()
        for line in raw_text.splitlines()
        if line.strip()
    ]

    if not lines:
        await message.answer("❌ هیچ مورد معتبری یافت نشد.")
        return

    added_count = 0

    async with AsyncSessionLocal() as session:

        for proxy in lines:

            # هر خط یک رکورد مستقل
            new_proxy = Config(
                type="proxy",
                title=None,
                value=proxy,
                is_active=True
            )

            session.add(new_proxy)
            await session.commit()

            added_count += 1

    await message.answer(
        f"✅ {added_count} مورد با موفقیت اضافه شد."
    )

    await state.clear()