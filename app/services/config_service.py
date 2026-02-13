import base64
import json

from app.config import settings


def rename_config_link(link: str, number: int) -> str:
    """
    تغییر نام کانفیگ بر اساس فرمت تعیین شده در settings
    """

    if not link:
        return link

    link = link.strip().replace("\ufeff", "")

    tag = settings.CONFIG_TAG_FORMAT.format(
        bot_name=settings.BOT_NAME,
        number=number
    )

    # اگر VMESS بود
    if link.lower().startswith("vmess://"):
        return _rename_vmess(link, tag)

    # سایر پروتکل‌ها (vless, trojan, ss, ...)
    return _rename_standard(link, tag)


def _rename_standard(link: str, tag: str) -> str:
    """
    تغییر نام برای پروتکل‌های معمولی که بعد از # نام دارند
    """

    if "#" in link:
        base = link.split("#", 1)[0]
        return f"{base}#{tag}"

    return f"{link}#{tag}"


def _rename_vmess(link: str, tag: str) -> str:
    """
    تغییر نام برای vmess
    (decode → تغییر ps → encode)
    """

    try:
        raw = link.replace("vmess://", "").strip()

        # اصلاح padding در صورت نبود =
        missing_padding = len(raw) % 4
        if missing_padding:
            raw += "=" * (4 - missing_padding)

        decoded = base64.b64decode(raw).decode("utf-8")
        data = json.loads(decoded)

        # تغییر ps
        data["ps"] = tag

        new_encoded = base64.b64encode(
            json.dumps(
                data,
                separators=(",", ":"),
                ensure_ascii=False
            ).encode("utf-8")
        ).decode("utf-8")

        return f"vmess://{new_encoded}"

    except Exception as e:
        print("VMESS RENAME ERROR:", e)

        # fallback اگر خراب بود
        return _rename_standard(link, tag)
