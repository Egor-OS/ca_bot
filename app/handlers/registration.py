from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup


class Registration():

    def __init__(self, db,bot):
        self.db_prov = db
        self.bot = bot

    class RegStates(StatesGroup):
        registration = State()
        reg_fio = State()
        reg_confirm = State()


    # Регистрация
    async def registration(self, message: types.Message, state: FSMContext):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
        data = await state.get_data()
        voucher = self.db_prov.check_voucher(message.text)
        if voucher:
            await state.update_data(voucher=voucher)
            await message.answer('Введите данные для регистрации в формате: \n\n<i><b>[Фамилия],[Имя],[Отчество]</b></i>',
                                 parse_mode=types.ParseMode.HTML)
            await self.RegStates.reg_fio.set()
        elif message.text:
            await message.answer('⛔ Неверный ваучер...')


    async def reg_fio(self, message: types.Message, state: FSMContext):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
        data = await state.get_data()
        if message.text:
            fio = message.text
            fio = fio.replace("[", '').replace(']', '').replace(' ', '').split(',')
            if len(fio) == 3:
                await state.update_data(fio=fio)
                keyboard.add('⬅ Назад', 'Принять')
                await message.answer(
                    f'Фамилия: <i><b>{fio[0]}</b></i>\nИмя: <i><b>{fio[1]}</b></i>\nОтчество: <i><b>{fio[2]}</b></i>',
                    reply_markup=keyboard, parse_mode=types.ParseMode.HTML)
                await self.RegStates.reg_confirm.set()
            else:
                await message.answer('Неверное количество параметров!')


    async def reg_confirm(self, message: types.Message, state: FSMContext):
        data = await state.get_data()
        if message.text == '⬅ Назад':
            await message.answer('Введите данные для регистрации в формате: \n\n<i><b>[Фамилия],[Имя],[Отчество]</b></i>',
                                 parse_mode=types.ParseMode.HTML)
            await self.RegStates.reg_fio.set()
        elif message.text == 'Принять':
            if self.db_prov.add_user(data['voucher'], data['fio'], message.chat.id):
                await self.bot.send_sticker(message.from_user.id,
                                       'CAACAgIAAxkBAAEFF8VisgdVZPQU2uzPdzZvS1mDVmwJ1gACfhwAAv8pkUl_ZIxgcvPuGykE',
                                       reply_markup=types.ReplyKeyboardRemove())
                await message.answer('Регистрация успешна! Введите /start для начала работы.')
            else:
                await message.answer('Ошибка! Вероятнее всего пользователь с таким ФИО уже существует, в вашей группе.')


    def register_handlers_reg(self, dp: Dispatcher):
        dp.register_message_handler(self.registration, state=self.RegStates.registration)
        dp.register_message_handler(self.reg_fio, state=self.RegStates.reg_fio)
        dp.register_message_handler(self.reg_confirm, state=self.RegStates.reg_confirm)
