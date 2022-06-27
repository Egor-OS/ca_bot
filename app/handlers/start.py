from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import BotCommand

class Start_Bot():

    def __init__(self, db, bot, conf):
        self.db_prov = db
        self.bot = bot
        self.config = conf

    class StartState(StatesGroup):
        registration = State()
        reg_fio = State()
        reg_confirm = State()

    async def set_commands(self):
        commands = [
            BotCommand(command="/start", description="Перезапуск"),
            BotCommand(command="/info", description="Помощь")
        ]
        await self.bot.set_my_commands(commands)

    async def cmd_start(self, message: types.Message, state: FSMContext):
        await state.finish()
        await state.update_data(mess=[])
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
        if self.db_prov.get_student_id(message.chat.id):
            obj_id = self.db_prov.get_student_id(message.chat.id)
            if obj_id:
                await state.update_data(obj_id=obj_id)
                for name in ['📝 Документы', '🔏 Личные данные']:
                    keyboard.add(name)
                await message.answer('Главное меню:', reply_markup=keyboard)
                await self.StudStates.stud_menu.set()
            else:
                await message.answer('Ошибка авторизации!')
        elif self.db_prov.get_teacher_id(message.chat.id):
            obj_id = self.db_prov.get_teacher_id(message.chat.id)
            if obj_id:
                await state.update_data(obj_id=obj_id)
                for name in ['📝 Документы', '⏳ Непроверенные документы', '🔏 Личные данные']:
                    keyboard.add(name)
                await message.answer('Главное меню:', reply_markup=keyboard)
                await self.TeachStates.teach_menu.set()
            else:
                await message.answer('Ошибка авторизации!')
        elif str(message.chat.id) in self.config.ADMINS:
            for name in ['👩🏼‍🏫 Управление преподавателями', '🧑🏼‍💻 Управление студентами', '🗂 Управление документами','👋🏼 Выход из панели администратора']:
                    keyboard.add(name)
            await message.answer('Главное меню: ', reply_markup=keyboard)
            await self.AdminStates.admin_menu.set()
        else:
            await self.bot.send_sticker(message.from_user.id,
                                   'CAACAgIAAxkBAAEFF8disgvQU-FuX_nxFIr4c9IdaDkWkgACERoAAlhVkElPAZiRutJ0mykE',
                                   reply_markup=types.ReplyKeyboardRemove())
            mess = await message.answer("Введите ваучер:")
            await state.update_data(mess=[message.chat.id, mess.message_id])
            await self.RegStates.registration.set()

    async def help(self, message: types.Message):
        if str(message.chat.id) in self.config.ADMINS:
            await message.answer('https://teletype.in/@ca_bot/spXLNWxGRWt')
        if self.db_prov.get_student_id(message.chat.id):
            await message.answer('https://teletype.in/@ca_bot/7nkyd_5IPWX')
        elif self.db_prov.get_teacher_id(message.chat.id):
            await message.answer('https://teletype.in/@ca_bot/AgvOJ1_aQX8')



    def register_handlers_start(self, dp: Dispatcher):
        dp.register_message_handler(self.cmd_start, commands="start", state="*")
        dp.register_message_handler(self.help, commands="help", state='*')