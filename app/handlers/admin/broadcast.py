from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy import select

from app.database.session import AsyncSessionLocal
from app.database.models import User

router = Router()


# =====================================================
# 🧠 State
# =====================================================
class BroadcastState(StatesGroup):
    waiting_for_message = State()


# =====================================================
# 📢 شروع پیام همگانی
# =====================================================
@router.message(F.text == "📢 ارسال همگانی")
async def start_broadcast(message: Message, state: FSMContext):
    await message.answer("✍️ لطفاً متن پیام همگانی را ارسال کنید:")
    await state.set_state(BroadcastState.waiting_for_message)


# =====================================================
# 📤 ارسال به همه کاربران
# =====================================================
@router.message(BroadcastState.waiting_for_message)
async def process_broadcast(message: Message, state: FSMContext):

    broadcast_text = message.text

    if not broadcast_text:
        await message.answer("❌ پیام خالی است.")
        return

    sent = 0
    failed = 0

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.is_banned == False)
        )
        users = result.scalars().all()

    for user in users:
        try:
            await message.bot.send_message(
                user.telegram_id,
                broadcast_text
            )
            sent += 1
        except:
            failed += 1

    await message.answer(
        f"✅ ارسال انجام شد.\n\n"
        f"📤 موفق: {sent}\n"
        f"❌ ناموفق: {failed}"
    )

    await state.clear()
