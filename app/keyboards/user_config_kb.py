from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def config_pagination_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="➡️ دریافت کانفیگ بعدی",
                    callback_data="next_configs"
                )
            ]
        ]
    )
