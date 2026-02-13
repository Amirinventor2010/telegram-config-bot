# Telegram Config Bot

A professional Telegram bot for managing V2Ray configs, NPV app files,
proxies, ads system, and admin panel.

Built with Aiogram 3, PostgreSQL, Redis, and Docker.

------------------------------------------------------------------------

## Features

### User Side

- Join-channel verification system
- V2Ray config delivery
- NPV (.npvt) file delivery
- Proxy pagination
- Profile system
- Ban detection
- Real-time ad membership validation

### Admin Panel

- Add V2Ray configs
- Upload NPV app files
- Manage configs (activate / deactivate / delete)
- Manage proxies
- Broadcast messaging
- User management (ban / unban)
- Ads channel management (join & view)

------------------------------------------------------------------------

## Tech Stack

- Python 3.11
- Aiogram 3
- PostgreSQL
- Redis
- Docker & Docker Compose
- Async SQLAlchemy

------------------------------------------------------------------------

## Installation (Docker)

``` bash
git clone https://github.com/yourusername/telegram-config-bot.git
cd telegram-config-bot
cp .env.example .env
```

Edit `.env` with your credentials.

Then run:

``` bash
docker compose up --build
```

------------------------------------------------------------------------

## Project Structure

    app/
     ├── handlers/
     ├── services/
     ├── keyboards/
     ├── database/
     ├── config.py
    run.py
    docker-compose.yml

------------------------------------------------------------------------

## Security Notes

- `.env` is ignored
- Uploaded NPV files are stored locally (not committed)
- Real-time Telegram membership validation
- Admin-only access protection

------------------------------------------------------------------------

## Author

**AmirGame**

Telegram: <https://t.me/MR_Amirr_00>

------------------------------------------------------------------------

## License

MIT License
