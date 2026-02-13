from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy import select

from app.database.session import AsyncSessionLocal
from app.database.models import User

router = Router()


# =====================================================
# 🧠 States
# =====================================================
class BanUserState(StatesGroup):
    waiting_for_ban_id = State()
    waiting_for_unban_id = State()


# =====================================================
# 🚫 شروع بن کاربر
# =====================================================
@router.message(F.text == "🚫 بن کاربر")
async def start_ban_user(message: Message, state: FSMContext):
    await message.answer("🔢 لطفاً آیدی عددی کاربر را ارسال کنید:")
    await state.set_state(BanUserState.waiting_for_ban_id)


# =====================================================
# 🚫 دریافت آیدی و بن
# =====================================================
@router.message(BanUserState.waiting_for_ban_id)
async def process_ban_user(message: Message, state: FSMContext):

    if not message.text.isdigit():
        await message.answer("❌ فقط عدد ارسال کنید.")
        return

    telegram_id = int(message.text)

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            await message.answer("❌ کاربر یافت نشد.")
            await state.clear()
            return

        user.is_banned = True
        await session.commit()

    await message.answer("✅ کاربر با موفقیت بن شد.")
    await state.clear()


# =====================================================
# ♻️ شروع رفع بن
# =====================================================
@router.message(F.text == "♻️ رفع بن کاربر")
async def start_unban_user(message: Message, state: FSMContext):
    await message.answer("🔢 لطفاً آیدی عددی کاربر را ارسال کنید:")
    await state.set_state(BanUserState.waiting_for_unban_id)


# =====================================================
# ♻️ دریافت آیدی و رفع بن
# =====================================================
@router.message(BanUserState.waiting_for_unban_id)
async def process_unban_user(message: Message, state: FSMContext):

    if not message.text.isdigit():
        await message.answer("❌ فقط عدد ارسال کنید.")
        return

    telegram_id = int(message.text)

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            await message.answer("❌ کاربر یافت نشد.")
            await state.clear()
            return

        user.is_banned = False
        await session.commit()

    await message.answer("✅ کاربر رفع بن شد.")
    await state.clear()
