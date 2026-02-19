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
    await message.answer("✍️ لطفاً پیام همگانی را ارسال کنید:")
    await state.set_state(BroadcastState.waiting_for_message)


# =====================================================
# 📤 ارسال به همه کاربران (با حفظ کامل فرمت)
# =====================================================
@router.message(BroadcastState.waiting_for_message)
async def process_broadcast(message: Message, state: FSMContext):

    sent = 0
    failed = 0

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.is_banned == False)
        )
        users = result.scalars().all()

    for user in users:
        try:
            # 👇 این خط جادویی است
            await message.bot.copy_message(
                chat_id=user.telegram_id,
                from_chat_id=message.chat.id,
                message_id=message.message_id
            )
            sent += 1
        except Exception:
            failed += 1

    await message.answer(
        f"✅ ارسال انجام شد.\n\n"
        f"📤 موفق: {sent}\n"
        f"❌ ناموفق: {failed}"
    )

    await state.clear()
