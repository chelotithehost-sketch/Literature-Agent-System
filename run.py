#!/usr/bin/env python3
import asyncio
import yaml
import os
from bot.telegram_bot import TelegramBot
from web.server import app
import uvicorn
from loguru import logger

async def main():
    # Load config
    with open("config/default.yaml", "r") as f:
        config = yaml.safe_load(f)
    # Substitute env vars
    for provider, cfg in config["routing"]["providers"].items():
        if "api_key" in cfg and cfg["api_key"].startswith("${"):
            env_var = cfg["api_key"][2:-1]
            cfg["api_key"] = os.environ.get(env_var)

    # Start Telegram bot in background
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        logger.error("TELEGRAM_BOT_TOKEN not set")
        return
    bot = TelegramBot(bot_token, config)
    asyncio.create_task(bot.run_async())

    # Start web server
    config_server = uvicorn.Config(app, host="127.0.0.1", port=8000, log_level="info")
    server = uvicorn.Server(config_server)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())
