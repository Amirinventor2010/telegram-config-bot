from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def config_manage_keyboard(config_id: int, is_active: bool):
    status_text = "🔴 غیرفعال کن" if is_active else "🟢 فعال کن"

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=status_text,
                    callback_data=f"toggle_config:{config_id}"
                ),
                InlineKeyboardButton(
                    text="❌ حذف",
                    callback_data=f"delete_config:{config_id}"
                ),
            ]
        ]
    )


def config_pagination_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="➡️ صفحه بعد",
                    callback_data="next_admin_configs"
                )
            ]
        ]
    )
