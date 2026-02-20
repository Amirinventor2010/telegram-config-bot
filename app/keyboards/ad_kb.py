from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def ad_channels_keyboard(channels):

    buttons = []

    for ch in channels:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"📢 {ch.channel_name}",
                    url=ch.invite_link
                )
            ]
        )

    buttons.append(
        [
            InlineKeyboardButton(
                text="✅ تایید عضویت",
                callback_data="confirm_ads"
            )
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons)
