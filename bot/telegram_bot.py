# bot/telegram_bot.py
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from core.state import BookState, TaskStatus
from agents.orchestrator import Orchestrator
from core.routing import Router
import yaml
from loguru import logger

class ProjectStates(StatesGroup):
    waiting_for_title = State()
    waiting_for_genre = State()
    waiting_for_tone = State()

class TelegramBot:
    def __init__(self, token: str, config: dict):
        self.bot = Bot(token=token)
        self.dp = Dispatcher(storage=MemoryStorage())
        self.router = Router(config["routing"])
        self.orchestrator = Orchestrator(config["agents"], self.router)
        self.active_projects = {}
        self._setup_handlers()

    def _setup_handlers(self):
        self.dp.message(Command("start"))(self.cmd_start)
        self.dp.message(Command("new"))(self.cmd_new)
        self.dp.message(Command("status"))(self.cmd_status)
        self.dp.message(Command("pause"))(self.cmd_pause)
        self.dp.message(Command("resume"))(self.cmd_resume)
        self.dp.message(Command("export"))(self.cmd_export)

    async def cmd_start(self, message: types.Message):
        await message.answer("📚 Literature Agent Bot\nCommands:\n/new - Start new project\n/status - Show progress\n/pause - Pause generation\n/resume - Resume project\n/export - Get download link")

    async def cmd_new(self, message: types.Message, state: FSMContext):
        await state.set_state(ProjectStates.waiting_for_title)
        await message.answer("Enter book title:")

    # ... (implement state handlers for collecting title, genre, tone and then launching orchestrator)

    async def run_async(self):
        await self.dp.start_polling(self.bot)

    def run(self):
        asyncio.run(self.run_async())
