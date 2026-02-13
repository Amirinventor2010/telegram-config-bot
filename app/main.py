import asyncio
import sys

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession

from app.config import settings
from app.database.session import engine, AsyncSessionLocal
from app.database.models import Base, Admin

# =========================
# Routers
# =========================
from app.handlers.user.start import router as start_router
from app.handlers.user.profile import router as profile_router
from app.handlers.user.get_config import router as get_config_router
from app.handlers.user.get_proxy import router as proxy_router

from app.handlers.admin.panel import router as admin_panel_router
from app.handlers.admin.add_config import router as add_config_router
from app.handlers.admin.add_proxy import router as add_proxy_router
from app.handlers.admin.manage_config import router as manage_config_router
from app.handlers.admin.manage_proxy import router as manage_proxy_router
from app.handlers.admin.manage_users import router as manage_users_router
from app.handlers.admin.stats import router as stats_router
from app.handlers.admin.broadcast import router as broadcast_router
from app.handlers.admin.manage_ads import router as manage_ads_router
from app.handlers.admin.add_app_file import router as add_app_file_router

PROXY_URL = None


# =========================
# Init DB
# =========================
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            Admin.__table__.select().where(
                Admin.telegram_id == settings.ADMIN_ID
            )
        )
        admin = result.first()

        if not admin:
            session.add(Admin(telegram_id=settings.ADMIN_ID))
            await session.commit()


# =========================
# Main
# =========================
async def main():
    try:
        session = (
            AiohttpSession()
            if not PROXY_URL
            else AiohttpSession(proxy=PROXY_URL)
        )

        bot = Bot(
            token=settings.BOT_TOKEN,
            session=session,
            default=DefaultBotProperties(
                parse_mode=ParseMode.HTML
            )
        )

        dp = Dispatcher()

        # -------------------------
        # User Routers
        # -------------------------
        dp.include_router(start_router)
        dp.include_router(profile_router)
        dp.include_router(get_config_router)
        dp.include_router(proxy_router)
        
        # -------------------------
        # Admin Routers
        # -------------------------
        dp.include_router(admin_panel_router)
        dp.include_router(add_config_router)
        dp.include_router(add_proxy_router)
        dp.include_router(manage_config_router)
        dp.include_router(manage_proxy_router)
        dp.include_router(manage_users_router)
        dp.include_router(stats_router)
        dp.include_router(broadcast_router)
        dp.include_router(manage_ads_router)
        dp.include_router(add_app_file_router)

        await init_db()

        await bot.delete_webhook(
            drop_pending_updates=True
        )

        await dp.start_polling(bot)

    except Exception as e:
        print("Bot crashed:", e, flush=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
