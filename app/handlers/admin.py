import random
import string
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup



class AdminPanel():

    def __init__(self, db, bot, cloud_mail):
        self.db_prov = db
        self.bot = bot
        self.cloud_mail = cloud_mail

    class AdminStates(StatesGroup):
        admin_menu = State()
        admin_choice_teach = State()
        admin_choice_group = State()
        admin_add_stud = State()
        admin_add_gr_to_coll = State()
        admin_add_teacher = State()
        admin_action_teach = State()
        admin_del_teach = State()
        admin_add_coll = State()
        admin_act_coll = State()
        admin_del_coll = State()
        admin_update_stud = State()
        admin_del_stud = State()
        admin_del_group = State()
        admin_del_gr_from_coll = State()
        admin_doc_menu = State()
        admin_choice_type = State()
        admin_update_type = State()
        get_voucher = State()
    
    # Методист
    # Глвное меню
    async def admin_menu(self, message: types.Message, state: FSMContext):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
        data = await state.get_data()
        if message.text == '👩🏼‍🏫 Управление преподавателями':
            teachers_list = self.db_prov.get_list_teacher()
            await state.update_data(teachers_list = teachers_list)
            for name in teachers_list.keys():
                keyboard.add(name)
            keyboard.add('🆕 Добавить преподавателя')
            keyboard.add('⬅ Назад')
            await message.answer('Гл.меню/👩🏼‍🏫 Управление преподавателями:', reply_markup=keyboard)
            await self.AdminStates.admin_choice_teach.set()
        elif message.text == '🧑🏼‍💻 Управление студентами':
            group_list = self.db_prov.get_group_list_adm()
            await state.update_data(group_list=group_list)
            for name in group_list.keys():
                keyboard.add(name)
            keyboard.add('⬅ Назад')
            await message.answer('Гл.меню/🧑🏼‍💻 Управление студентами:', reply_markup=keyboard)
            await message.answer('Для добавления новой группы пришлите название сообщением.')
            await self.AdminStates.admin_choice_group.set()
        elif message.text == '🗂 Управление документами':
            for name in ['📑 Управление типами','🧹 Запустить очистку','⬅ Назад']:
                keyboard.add(name)
            await message.answer('Гл.меню/Управление документами:', reply_markup=keyboard)
            await self.AdminStates.admin_doc_menu.set()
        elif message.text == '👋🏼 Выход из панели администратора':
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
            else:
                await message.answer('Доступ только для администрирования!')
                await self.AdminStates.admin_menu.set()
    
    # главное меню/управление пераодавателями
    async def admin_choice_teach(self, message: types.Message, state: FSMContext):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
        data = await state.get_data()
        if message.text == "⬅ Назад":
            for name in ['👩🏼‍🏫 Управление преподавателями', '🧑🏼‍💻 Управление студентами', '🗂 Управление документами','👋🏼 Выход из панели администратора']:
                keyboard.add(name)
            await message.answer('Главное меню: ', reply_markup=keyboard)
            await self.AdminStates.admin_menu.set()
        elif message.text == '🆕 Добавить преподавателя':
            keyboard.add('💳 Получить ваучер')
            keyboard.add('⬅ Назад','🏠 На главную')
            await message.answer('Получите ваучер и передайте его преподавателю, чтобы он мог смостоятельно зарегистрироваться в системе.\n\nИЛИ.....')
            await message.answer('Для ручного добавления перподавателя пришлите данные сообщением в формате: \n[Фамилия],[Имя],[Отчество],[Telegram-id]', reply_markup=keyboard)
            await self.AdminStates.admin_add_teacher.set()
        elif message.text in data['teachers_list'].keys():
            choice_teach = message.text
            path_list = self.db_prov.get_path_list(data['teachers_list'][choice_teach]['_id'])
            await state.update_data(path_list=path_list)
            for name in path_list.keys():
                keyboard.add(name)
            await state.update_data(choice_teach = message.text)
            keyboard.add('🆕 Добавить дисциплину')
            keyboard.add('🗑 Удалить преподавателя')
            keyboard.add('⬅ Назад','🏠 На главную')
            teach_info = self.db_prov.get_teach_info(data['teachers_list'][choice_teach]['_id'])
            await message.answer(
                f'Фамилия: <b>{teach_info["l_name"]}</b> \nИмя: <b>{teach_info["f_name"]}</b> \nОтчество: <b>{teach_info["m_name"]}</b> \nTelegram-id: <b>{teach_info["tg_id"]}</b>',
                parse_mode=types.ParseMode.HTML, reply_markup=keyboard)
            await message.answer(
                'Для редактирования перподавателя пришлите данные сообщением в формате: \n[Фамилия],[Имя],[Отчество],[Telegram-id]',
                reply_markup=keyboard)
            await self.AdminStates.admin_action_teach.set()
    
    # главное меню/🧑🏼‍💻 Управление студентами
    async def admin_choice_group(self, message: types.Message, state: FSMContext):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
        data = await state.get_data()
        if message.text == "⬅ Назад":
            for name in ['👩🏼‍🏫 Управление преподавателями', '🧑🏼‍💻 Управление студентами', '🗂 Управление документами','👋🏼 Выход из панели администратора']:
                keyboard.add(name)
            await message.answer('Главное меню: ', reply_markup=keyboard)
            await self.AdminStates.admin_menu.set()
        elif message.text in data['group_list'].keys():
            choice_group = message.text
            await state.update_data(choice_group=choice_group)
            list_stud_id = data['group_list'][choice_group]['list_students_id']
            list_stud = self.db_prov.get_stud_list_adm(list_stud_id)
            await state.update_data(list_stud=list_stud)
            for name in list_stud.keys():
                keyboard.add(name)
            keyboard.add('💳 Получить ваучер')
            keyboard.add('🗑 Удалить группу')
            keyboard.add('⬅ Назад','🏠 На главную')
            await message.answer(
                'Для добавления студента пришлите данные сообщением.\nФормат строки:\n\n<b>[Фамилия],[Имя],[Отчество],[Telegram-id]</b>',
                parse_mode=types.ParseMode.HTML, reply_markup=keyboard)
            await self.AdminStates.admin_add_stud.set()
        elif message.text:
            self.db_prov.add_group(message.text)
            await message.answer(f'✅ Группа {message.text} успешно добавлена!')
            group_list = self.db_prov.get_group_list_adm()
            await state.update_data(group_list=group_list)
            for name in group_list.keys():
                keyboard.add(name)
            keyboard.add('⬅ Назад','🏠 На главную')
            await message.answer('Гл.меню/🧑🏼‍💻 Управление студентами:', reply_markup=keyboard)
            await message.answer('❕ Для добавления новой группы пришлите название сообщением.')
            await self.AdminStates.admin_choice_group.set()
    
    # главное меню/🧑🏼‍💻 Управление студентами/[группа]
    async def admin_add_stud(self, message: types.Message, state: FSMContext):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
        data = await state.get_data()
        if message.text == "⬅ Назад":
            group_list = self.db_prov.get_group_list_adm()
            await state.update_data(group_list=group_list)
            for name in group_list.keys():
                keyboard.add(name)
            keyboard.add('⬅ Назад')
            await message.answer('Гл.меню/🧑🏼‍💻 Управление студентами:', reply_markup=keyboard)
            await self.AdminStates.admin_choice_group.set()
        elif message.text == "🏠 На главную":
            for name in ['👩🏼‍🏫 Управление преподавателями', '🧑🏼‍💻 Управление студентами', '🗂 Управление документами','👋🏼 Выход из панели администратора']:
                keyboard.add(name)
            await message.answer('Главное меню: ', reply_markup=keyboard)
            await self.AdminStates.admin_menu.set()
        elif message.text=='💳 Получить ваучер':
            await state.update_data(type_voucher='student')
            keyboard.add('⬅ Назад','🏠 На главную')
            await message.answer('Введите необходимое количество ваучеров:', reply_markup=keyboard)
            await self.AdminStates.get_voucher.set()
        elif message.text=='🗑 Удалить группу':
            captcha = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(8))
            await state.update_data(captcha=captcha)
            keyboard.add('⬅ Назад','🏠 На главную')
            await message.answer(f'Для подтверждения удаления введите: {captcha}', reply_markup=keyboard)
            await self.AdminStates.admin_del_group.set()
        elif message.text in data['list_stud'].keys():
            choice_stud = message.text
            await state.update_data(choice_stud=choice_stud)
            keyboard.add('🗑 Удалить студента')
            keyboard.add('⬅ Назад','🏠 На главную')
            stud_info = data['list_stud'][choice_stud]
            await message.answer(
                f'Фамилия: <b>{stud_info["l_name"]}</b> \nИмя: <b>{stud_info["f_name"]}</b> \nОтчество: <b>{stud_info["m_name"]}</b> \nTelegram-id: <b>{stud_info["tg_id"]}</b>',
                parse_mode=types.ParseMode.HTML, reply_markup=keyboard)
            await message.answer(
                'Для редактирования студента пришлите данные сообщением.\nФормат строки:\n\n<b>[Фамилия],[Имя],[Отчество],[Telegram-id]</b>',
                parse_mode=types.ParseMode.HTML, reply_markup=keyboard)
            await self.AdminStates.admin_update_stud.set()
        elif message.text:
            stud_info = message.text
            stud_info = stud_info.replace("[",'').replace(']','').replace(' ', '').split(',')
            if len(stud_info) == 4:
                if self.db_prov.add_student(stud_info[0], stud_info[1], stud_info[2], stud_info[3],data['group_list'][data['choice_group']]['_id']):
                    await message.answer('✅ Студент успешно добавлен!')
                    group_list = self.db_prov.get_group_list_adm()
                    await state.update_data(group_list=group_list)
                    list_stud_id = group_list[data['choice_group']]['list_students_id']
                    list_stud = self.db_prov.get_stud_list_adm(list_stud_id)
                    await state.update_data(list_stud=list_stud)
                    for name in list_stud.keys():
                        keyboard.add(name)
                    keyboard.add('💳 Получить ваучер')
                    keyboard.add('⬅ Назад','🏠 На главную')
                    await message.answer(
                        'Для добавления студента пришлите данные сообщением.\nФормат строки:\n\n<b>[Фамилия],[Имя],[Отчество],[Telegram-id]</b>',
                        parse_mode=types.ParseMode.HTML, reply_markup=keyboard)
                    await self.AdminStates.admin_add_stud.set()
                else:
                    await message.answer('🚫 Ошибка добавления!')
            else:
                await message.answer('🚫 Неверное количество параметров!')
    
    async def admin_del_group(self, message: types.Message, state: FSMContext):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
        data = await state.get_data()
        if message.text == '⬅ Назад':
            list_stud_id = data['group_list'][data['choice_group']]['list_students_id']
            list_stud = self.db_prov.get_stud_list_adm(list_stud_id)
            await state.update_data(list_stud=list_stud)
            for name in list_stud.keys():
                keyboard.add(name)
            keyboard.add('🗑 Удалить группу')
            keyboard.add('💳 Получить ваучер')
            keyboard.add('⬅ Назад','🏠 На главную')
            await message.answer(
                'Для добавления студента пришлите данные сообщением.\nФормат строки:\n\n<b>[Фамилия],[Имя],[Отчество],[Telegram-id]</b>',
                parse_mode=types.ParseMode.HTML, reply_markup=keyboard)
            await self.AdminStates.admin_add_stud.set()
        elif message.text == "🏠 На главную":
            for name in ['👩🏼‍🏫 Управление преподавателями', '🧑🏼‍💻 Управление студентами', '🗂 Управление документами','👋🏼 Выход из панели администратора']:
                keyboard.add(name)
            await message.answer('Главное меню: ', reply_markup=keyboard)
            await self.AdminStates.admin_menu.set()
        elif message.text==data['captcha']:
            if self.db_prov.del_group(data['group_list'][data['choice_group']]['_id']):
                await message.answer('✅ Успешно удалено!')
            else:
                await message.answer('🚫 Ошибка удаления!')
            group_list = self.db_prov.get_group_list_adm()
            await state.update_data(group_list=group_list)
            for name in group_list.keys():
                keyboard.add(name)
            keyboard.add('⬅ Назад')
            await message.answer('Гл.меню/🧑🏼‍💻 Управление студентами:', reply_markup=keyboard)
            await message.answer('❕ Для добавления новой группы пришлите название сообщением.')
            await self.AdminStates.admin_choice_group.set()
    
    async def admin_update_stud(self, message: types.Message, state: FSMContext):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
        data = await state.get_data()
        if message.text == '⬅ Назад':
            list_stud_id = data['group_list'][data['choice_group']]['list_students_id']
            list_stud = self.db_prov.get_stud_list_adm(list_stud_id)
            await state.update_data(list_stud=list_stud)
            for name in list_stud.keys():
                keyboard.add(name)
            keyboard.add('🗑 Удалить группу')
            keyboard.add('💳 Получить ваучер')
            keyboard.add('⬅ Назад','🏠 На главную')
            await message.answer(
                'Для добавления студента пришлите данные сообщением.\nФормат строки:\n\n<b>[Фамилия],[Имя],[Отчество],[Telegram-id]</b>',
                parse_mode=types.ParseMode.HTML, reply_markup=keyboard)
            await self.AdminStates.admin_add_stud.set()
        elif message.text == "🏠 На главную":
            for name in ['👩🏼‍🏫 Управление преподавателями', '🧑🏼‍💻 Управление студентами', '🗂 Управление документами','👋🏼 Выход из панели администратора']:
                keyboard.add(name)
            await message.answer('Главное меню: ', reply_markup=keyboard)
            await self.AdminStates.admin_menu.set()
        elif message.text=='🗑 Удалить студента':
            captcha = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(8))
            await state.update_data(captcha=captcha)
            keyboard.add('⬅ Назад','🏠 На главную')
            await message.answer(f'Для подтверждения удаления введите: {captcha}', reply_markup=keyboard)
            await self.AdminStates.admin_del_stud.set()
        elif message.text:
            stud_info = message.text
            stud_info = stud_info.replace("[",'').replace(']','').replace(' ', '').split(',')
            if len(stud_info) == 4:
                if self.db_prov.update_stud(data['list_stud'][data['choice_stud']]['_id'],stud_info[0], stud_info[1], stud_info[2], stud_info[3]):
                    await message.answer('✅ Данные обновлены!')
                    group_list = self.db_prov.get_group_list_adm()
                    await state.update_data(group_list=group_list)
                    list_stud_id = group_list[data['choice_group']]['list_students_id']
                    list_stud = self.db_prov.get_stud_list_adm(list_stud_id)
                    await state.update_data(list_stud=list_stud)
                    for name in list_stud.keys():
                        keyboard.add(name)
                    keyboard.add('🗑 Удалить группу')
                    keyboard.add('💳 Получить ваучер')
                    keyboard.add('⬅ Назад','🏠 На главную')
                    await message.answer(
                        'Для добавления студента пришлите данные сообщением.\nФормат строки:\n\n<b>[Фамилия],[Имя],[Отчество],[Telegram-id]</b>',
                        parse_mode=types.ParseMode.HTML, reply_markup=keyboard)
                    await self.AdminStates.admin_add_stud.set()
                else:
                    await message.answer('🚫 Ошибка редактирования!')
            else:
                await message.answer('🚫 Неверное количество параметров!')
    
    async def admin_del_stud(self, message: types.Message, state: FSMContext):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
        data = await state.get_data()
        if message.text == '⬅ Назад':
            keyboard.add('🗑 Удалить студента')
            keyboard.add('⬅ Назад','🏠 На главную')
            stud_info = data['list_stud'][data['choices_stud']]
            await message.answer(
                f'Фамилия: <b>{stud_info["l_name"]}</b> \nИмя: <b>{stud_info["f_name"]}</b> \nОтчество: <b>{stud_info["m_name"]}</b> \nTelegram-id: <b>{stud_info["tg_id"]}</b>',
                parse_mode=types.ParseMode.HTML, reply_markup=keyboard)
            await message.answer(
                'Для редактирования студента пришлите данные сообщением.\nФормат строки:\n\n<b>[Фамилия],[Имя],[Отчество],[Telegram-id]</b>',
                parse_mode=types.ParseMode.HTML, reply_markup=keyboard)
            await self.AdminStates.admin_update_stud.set()
        elif message.text==data['captcha']:
            self.db_prov.del_stud(data['list_stud'][data['choice_stud']]['_id'])
            await message.answer('✅ Успешно удалено!')
            group_list = self.db_prov.get_group_list_adm()
            await state.update_data(group_list=group_list)
            list_stud_id = group_list[data['choice_group']]['list_students_id']
            list_stud = self.db_prov.get_stud_list_adm(list_stud_id)
            await state.update_data(list_stud=list_stud)
            for name in list_stud.keys():
                keyboard.add(name)
            keyboard.add('🗑 Удалить группу')
            keyboard.add('💳 Получить ваучер')
            keyboard.add('⬅ Назад','🏠 На главную')
            await message.answer(
                'Для добавления студента пришлите данные сообщением.\nФормат строки:\n\n<b>[Фамилия],[Имя],[Отчество],[Telegram-id]</b>',
                parse_mode=types.ParseMode.HTML, reply_markup=keyboard)
            await self.AdminStates.admin_add_stud.set()
    
    # главное меню/👩🏼‍🏫 Управление преподавателями/Добавить преподавателя
    async def admin_add_teacher(self, message: types.Message, state: FSMContext):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
        data = await state.get_data()
        if message.text == '⬅ Назад':
            teachers_list = self.db_prov.get_list_teacher()
            await state.update_data(teachers_list=teachers_list)
            for name in teachers_list.keys():
                keyboard.add(name)
            keyboard.add('🆕 Добавить преподавателя')
            keyboard.add('⬅ Назад')
            await message.answer('Гл.меню/👩🏼‍🏫 Управление преподавателями:', reply_markup=keyboard)
            await self.AdminStates.admin_choice_teach.set()
        elif message.text == "🏠 На главную":
            for name in ['👩🏼‍🏫 Управление преподавателями', '🧑🏼‍💻 Управление студентами', '🗂 Управление документами','👋🏼 Выход из панели администратора']:
                keyboard.add(name)
            await message.answer('Главное меню: ', reply_markup=keyboard)
            await self.AdminStates.admin_menu.set()
        elif message.text == '💳 Получить ваучер':
            await state.update_data(type_voucher= 'teacher')
            keyboard.add('⬅ Назад')
            await message.answer('Введите необходимое количество ваучеров:', reply_markup=keyboard)
            await self.AdminStates.get_voucher.set()
        elif message.text:
            teach_info = message.text
            teach_info = teach_info.replace("[",'').replace(']','').replace(' ', '').split(',')
            if len(teach_info)==4:
                if self.db_prov.add_teacher(teach_info[0],teach_info[1],teach_info[2],teach_info[3]):
                    await message.answer('✅ Преподаватель успешно добавлен!')
                else:
                    await message.answer('🚫 Ошибка добавления!')
            else:
                await message.answer('🚫 Неверное количество параметров!')
    
    async def get_voucher(self, message: types.Message, state: FSMContext):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
        data = await state.get_data()
        if message.text=='⬅ Назад':
            if data['type_voucher'] == 'teacher':
                keyboard.add('💳 Получить ваучер')
                keyboard.add('⬅ Назад','🏠 На главную')
                await message.answer(
                    'Получите ваучер и передайте его преподавателю, чтобы он мог смостоятельно зарегистрироваться в системе.\n\nИЛИ.....')
                await message.answer(
                    'Для ручного добавления перподавателя пришлите данные сообщением в формате: \n[Фамилия],[Имя],[Отчество],[Telegram-id]',
                    reply_markup=keyboard)
                await self.AdminStates.admin_add_teacher.set()
            else:
                choice_group = data['choice_group']
                list_stud_id = data['group_list'][choice_group]['list_students_id']
                list_stud = self.db_prov.get_stud_list_adm(list_stud_id)
                await state.update_data(list_stud=list_stud)
                for name in list_stud.keys():
                    keyboard.add(name)
                keyboard.add('💳 Получить ваучер')
                keyboard.add('🗑 Удалить группу')
                keyboard.add('⬅ Назад','🏠 На главную')
                await message.answer(
                    'Для добавления студента пришлите данные сообщением.\nФормат строки:\n\n<b>[Фамилия],[Имя],[Отчество],[Telegram-id]</b>',
                    parse_mode=types.ParseMode.HTML, reply_markup=keyboard)
                await self.AdminStates.admin_add_stud.set()
        elif message.text == "🏠 На главную":
            for name in ['👩🏼‍🏫 Управление преподавателями', '🧑🏼‍💻 Управление студентами', '🗂 Управление документами','👋🏼 Выход из панели администратора']:
                keyboard.add(name)
            await message.answer('Главное меню: ', reply_markup=keyboard)
            await self.AdminStates.admin_menu.set()
        elif message.text:
            try:
                count_voucher = int(message.text)
                if count_voucher <= 30:
                    txt = ''
                    for i in range(count_voucher):
                        letters_and_digits = string.ascii_letters + string.digits
                        rand_string = ''.join(random.sample(letters_and_digits, 15))
                        if data['type_voucher']=='teacher':
                            self.db_prov.add_voucher(rand_string,'','teacher')
                        else:
                            if txt=='':
                                txt += f"******* {data['choice_group']} *******\n"
                            self.db_prov.add_voucher(rand_string, data['group_list'][data['choice_group']]['_id'], 'student')
                        txt += f'{i+1}. {rand_string}\n'
                    await message.answer(txt)
            except Exception:
                pass
    
    # главное меню/управление пераодавателями/[преподаватель]
    async def admin_action_teach(self, message: types.Message, state: FSMContext):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
        data = await state.get_data()
        if message.text == '⬅ Назад':
            teachers_list = self.db_prov.get_list_teacher()
            await state.update_data(teachers_list=teachers_list)
            for name in teachers_list.keys():
                keyboard.add(name)
            keyboard.add('🆕 Добавить преподавателя')
            keyboard.add('⬅ Назад')
            await message.answer('Гл.меню/👩🏼‍🏫 Управление преподавателями:', reply_markup=keyboard)
            await self.AdminStates.admin_choice_teach.set()
        elif message.text == "🏠 На главную":
            for name in ['👩🏼‍🏫 Управление преподавателями', '🧑🏼‍💻 Управление студентами', '🗂 Управление документами','👋🏼 Выход из панели администратора']:
                keyboard.add(name)
            await message.answer('Главное меню: ', reply_markup=keyboard)
            await self.AdminStates.admin_menu.set()
        elif message.text == '🆕 Добавить дисциплину':
            keyboard.add('⬅ Назад','🏠 На главную')
            await message.answer('Введите название дисциплины в формате: \n\n[Полное название],[Сокращеное название]',reply_markup=keyboard)
            await self.AdminStates.admin_add_coll.set()
        elif message.text == '🗑 Удалить преподавателя':
            captcha = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(8))
            await state.update_data(captcha=captcha)
            keyboard.add('⬅ Назад','🏠 На главную')
            await message.answer(f'Для подтверждения удаления введите: {captcha}', reply_markup=keyboard)
            await self.AdminStates.admin_del_teach.set()
        elif message.text in data['path_list'].keys():
            choice_path = message.text
            await state.update_data(choice_path=choice_path)
            groups = self.db_prov.get_group_in_coll(data['path_list'][choice_path]['group_list_id'])
            await state.update_data(groups=groups)
            for name in groups.keys():
                keyboard.add(name)
            keyboard.add('🆕 Добавить группу')
            keyboard.add('🗑 Удалить дисциплину')
            keyboard.add('⬅ Назад','🏠 На главную')
            await message.answer(f'*/{data["choice_teach"]}/{choice_path}', reply_markup=keyboard)
            await self.AdminStates.admin_act_coll.set()
        elif message.text:
            teach_info = message.text
            teach_info = teach_info.replace("[",'').replace(']','').replace(' ', '').split(',')
            teach_id = data['teachers_list'][data['choice_teach']]['_id']
            if len(teach_info) == 4:
                if self.db_prov.update_teacher(teach_id, teach_info[0], teach_info[1], teach_info[2], teach_info[3]):
                    await message.answer('✅ Преподаватель успешно изменен!')
                else:
                    await message.answer('🚫 Ошибка изменения!')
            else:
                await message.answer('🚫 Неверное количество параметров!')
    
    # главное меню/управление пераодавателями/[преподаватель]/удалить преподавателя
    async def admin_del_teach(self, message: types.Message, state: FSMContext):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
        data = await state.get_data()
        if message.text == '⬅ Назад':
            choice_teach = data['choice_teach']
            path_list = self.db_prov.get_path_list(data['teachers_list'][choice_teach]['_id'])
            await state.update_data(path_list=path_list)
            for name in path_list.keys():
                keyboard.add(name)
            keyboard.add('🆕 Добавить дисциплину')
            keyboard.add('🗑 Удалить преподавателя')
            keyboard.add('⬅ Назад', '🏠 На главную')
            teach_info = self.db_prov.get_teach_info(data['teachers_list'][choice_teach]['_id'])
            await message.answer(
                f'Фамилия: <b>{teach_info["l_name"]}</b> \nИмя: <b>{teach_info["f_name"]}</b> \nОтчество: <b>{teach_info["m_name"]}</b> \nTelegram-id: <b>{teach_info["tg_id"]}</b>',
                parse_mode=types.ParseMode.HTML, reply_markup=keyboard)
            await message.answer(
                'Для редактирования перподавателя пришлите данные сообщением в формате: \n[Фамилия],[Имя],[Отчество],[Telegram-id]',
                reply_markup=keyboard)
            await self.AdminStates.admin_action_teach.set()
        elif message.text == "🏠 На главную":
            for name in ['👩🏼‍🏫 Управление преподавателями', '🧑🏼‍💻 Управление студентами', '🗂 Управление документами','👋🏼 Выход из панели администратора']:
                keyboard.add(name)
            await message.answer('Главное меню: ', reply_markup=keyboard)
            await self.AdminStates.admin_menu.set()
        elif message.text == data['captcha']:
            if self.db_prov.del_teacher(data['teachers_list'][data['choice_teach']]['_id']):
                await message.answer('✅ Успешно удалено!')
                teachers_list = self.db_prov.get_list_teacher()
                await state.update_data(teachers_list=teachers_list)
                for name in teachers_list.keys():
                    keyboard.add(name)
                keyboard.add('🆕 Добавить преподавателя')
                keyboard.add('⬅ Назад')
                await message.answer('Гл.меню/👩🏼‍🏫 Управление преподавателями:', reply_markup=keyboard)
                await self.AdminStates.admin_choice_teach.set()
            else:
                await message.answer('🚫 Ошибка удаления!')
    
    # главное меню/управление пераодавателями/[преподаватель]/добавить дисциплину
    async def admin_add_coll(self, message: types.Message, state: FSMContext):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
        data = await state.get_data()
        if message.text == '⬅ Назад':
            path_list = self.db_prov.get_path_list(data['teachers_list'][data['choice_teach']]['_id'])
            await state.update_data(path_list=path_list)
            for name in path_list.keys():
                keyboard.add(name)
            keyboard.add('🆕 Добавить дисциплину')
            keyboard.add('🗑 Удалить преподавателя')
            keyboard.add('⬅ Назад','🏠 На главную')
            teach_info = self.db_prov.get_teach_info(data['teachers_list'][data['choice_teach']]['_id'])
            await message.answer(
                f'Фамилия: <b>{teach_info["l_name"]}</b> \nИмя: <b>{teach_info["f_name"]}</b> \nОтчество: <b>{teach_info["m_name"]}</b> \nTelegram-id: <b>{teach_info["tg_id"]}</b>',
                parse_mode=types.ParseMode.HTML, reply_markup=keyboard)
            await message.answer(
                'Для редактирования перподавателя пришлите данные сообщением в формате: \n[Фамилия],[Имя],[Отчество],[Telegram-id]',
                reply_markup=keyboard)
            await self.AdminStates.admin_action_teach.set()
        elif message.text == "🏠 На главную":
            for name in ['👩🏼‍🏫 Управление преподавателями', '🧑🏼‍💻 Управление студентами', '🗂 Управление документами','👋🏼 Выход из панели администратора']:
                keyboard.add(name)
            await message.answer('Главное меню: ', reply_markup=keyboard)
            await self.AdminStates.admin_menu.set()
        elif message.text:
            mess_ = message.text
            mess_ = mess_.replace('[','').replace(']','').split(',')
            if len(mess_) == 2:
                if self.db_prov.add_coll(mess_[0],mess_[1], data['teachers_list'][data['choice_teach']]['_id']):
                    await message.answer(f'✅ Дисциплина успешно добавлена!')
                else:
                    await message.answer(f'Ошибка! Вероятнее всего дисциплина или ее сокращенное название уже сущесвует!')
            else:
                await message.answer('🚫 Неверное количество параметров!')
    
    # главное меню/управление пераодавателями/[преподаватель]/дисциплина/
    async def admin_act_coll(self, message: types.Message, state: FSMContext):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
        data = await state.get_data()
        if message.text == '⬅ Назад':
            path_list = self.db_prov.get_path_list(data['teachers_list'][data['choice_teach']]['_id'])
            await state.update_data(path_list=path_list)
            for name in path_list.keys():
                keyboard.add(name)
            keyboard.add('🆕 Добавить дисциплину')
            keyboard.add('🗑 Удалить преподавателя')
            keyboard.add('⬅ Назад','🏠 На главную')
            teach_info = self.db_prov.get_teach_info(data['teachers_list'][data['choice_teach']]['_id'])
            await message.answer(
                f'Фамилия: <b>{teach_info["l_name"]}</b> \nИмя: <b>{teach_info["f_name"]}</b> \nОтчество: <b>{teach_info["m_name"]}</b> \nTelegram-id: <b>{teach_info["tg_id"]}</b>',
                parse_mode=types.ParseMode.HTML, reply_markup=keyboard)
            await message.answer(
                'Для редактирования перподавателя пришлите данные сообщением в формате: \n[Фамилия],[Имя],[Отчество],[Telegram-id]',
                reply_markup=keyboard)
            await self.AdminStates.admin_action_teach.set()
        elif message.text == "🏠 На главную":
            for name in ['👩🏼‍🏫 Управление преподавателями', '🧑🏼‍💻 Управление студентами', '🗂 Управление документами','👋🏼 Выход из панели администратора']:
                keyboard.add(name)
            await message.answer('Главное меню: ', reply_markup=keyboard)
            await self.AdminStates.admin_menu.set()
        elif message.text == '🆕 Добавить группу':
            list_group = self.db_prov.get_group_list_adm()
            await state.update_data(list_group=list_group)
            for name in list_group.keys():
                keyboard.add(name)
            keyboard.add('⬅ Назад','🏠 На главную')
            await message.answer('Выберите группу', reply_markup=keyboard)
            await self.AdminStates.admin_add_gr_to_coll.set()
        elif message.text == '🗑 Удалить дисциплину':
            captcha = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(8))
            await state.update_data(captcha=captcha)
            keyboard.add('⬅ Назад','🏠 На главную')
            await message.answer(f'Для подтверждения удаления введите: {captcha}', reply_markup=keyboard)
            await self.AdminStates.admin_del_coll.set()
        elif message.text in data['groups']:
            choice_group = message.text
            await state.update_data(choice_group=choice_group)
            captcha = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(8))
            await state.update_data(captcha=captcha)
            keyboard.add('⬅ Назад','🏠 На главную')
            await message.answer(f'Для подтверждения удаления введите: {captcha}', reply_markup=keyboard)
            await self.AdminStates.admin_del_gr_from_coll.set()
    
    async def admin_del_gr_from_coll(self, message: types.Message, state: FSMContext):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
        data = await state.get_data()
        if message.text == '⬅ Назад':
            path_list = self.db_prov.get_path_list(data['teachers_list'][data['choice_teach']]['_id'])
            await state.update_data(path_list=path_list)
            choice_path = data['choice_path']
            await state.update_data(choice_path=choice_path)
            groups = self.db_prov.get_group_in_coll(path_list[choice_path]['group_list_id'])
            await state.update_data(groups=groups)
            for name in groups.keys():
                keyboard.add(name)
            keyboard.add('🆕 Добавить группу')
            keyboard.add('🗑 Удалить дисциплину')
            keyboard.add('⬅ Назад','🏠 На главную')
            await message.answer(f'*/{data["choice_teach"]}/{data["choice_path"]}', reply_markup=keyboard)
            await self.AdminStates.admin_act_coll.set()
        elif message.text == "🏠 На главную":
            for name in ['👩🏼‍🏫 Управление преподавателями', '🧑🏼‍💻 Управление студентами', '🗂 Управление документами','👋🏼 Выход из панели администратора']:
                keyboard.add(name)
            await message.answer('Главное меню: ', reply_markup=keyboard)
            await self.AdminStates.admin_menu.set()
        elif message.text == data['captcha']:
            if self.db_prov.del_gr_from_coll(data['groups'][data['choice_group']]['_id'],data['path_list'][data['choice_path']]['_id']):
                path_list = self.db_prov.get_path_list(data['teachers_list'][data['choice_teach']]['_id'])
                await state.update_data(path_list=path_list)
                choice_path = data['choice_path']
                await state.update_data(choice_path=choice_path)
                groups = self.db_prov.get_group_in_coll(path_list[choice_path]['group_list_id'])
                await state.update_data(groups=groups)
                for name in groups.keys():
                    keyboard.add(name)
                keyboard.add('🆕 Добавить группу')
                keyboard.add('🗑 Удалить дисциплину')
                keyboard.add('⬅ Назад','🏠 На главную')
                await message.answer(f'*/{data["choice_teach"]}/{data["choice_path"]}', reply_markup=keyboard)
                await self.AdminStates.admin_act_coll.set()
            else:
                await message.answer('Ошибка удаления!')
    
    async def admin_add_gr_to_coll(self, message: types.Message, state: FSMContext):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
        data = await state.get_data()
        if message.text == '⬅ Назад':
            path_list = self.db_prov.get_path_list(data['teachers_list'][data['choice_teach']]['_id'])
            await state.update_data(path_list=path_list)
            choice_path = data['choice_path']
            await state.update_data(choice_path=choice_path)
            groups = self.db_prov.get_group_in_coll(path_list[choice_path]['group_list_id'])
            await state.update_data(groups=groups)
            for name in groups.keys():
                keyboard.add(name)
            keyboard.add('🆕 Добавить группу')
            keyboard.add('🗑 Удалить дисциплину')
            keyboard.add('⬅ Назад','🏠 На главную')
            await message.answer(f'*/{data["choice_teach"]}/{data["choice_path"]}', reply_markup=keyboard)
            await self.AdminStates.admin_act_coll.set()
        elif message.text == "🏠 На главную":
            for name in ['👩🏼‍🏫 Управление преподавателями', '🧑🏼‍💻 Управление студентами', '🗂 Управление документами','👋🏼 Выход из панели администратора']:
                keyboard.add(name)
            await message.answer('Главное меню: ', reply_markup=keyboard)
            await self.AdminStates.admin_menu.set()
        elif message.text in data['list_group'].keys():
            choice_group = message.text
            if choice_group not in data['groups']:
                self.db_prov.add_group_to_coll(data['list_group'][choice_group]['_id'], data['path_list'][data['choice_path']]['_id'])
                await message.answer('✅ Группа добавлена')
                path_list = self.db_prov.get_path_list(data['teachers_list'][data['choice_teach']]['_id'])
                await state.update_data(path_list=path_list)
                groups = self.db_prov.get_group_in_coll(path_list[data['choice_path']]['group_list_id'])
                await state.update_data(groups=groups)
            else:
                await message.answer('⚠ Группа уже добавлена!')
    
    # главное меню/👩🏼‍🏫 Управление преподавателями/[преподаватель]/дисциплина/удаление дисциплины
    async def admin_del_coll(self, message: types.Message, state: FSMContext):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
        data = await state.get_data()
        if message.text == '⬅ Назад':
            choice_path = data['choice_path']
            groups = self.db_prov.get_group_in_coll(data['path_list'][choice_path]['group_list_id'])
            await state.update_data(groups=groups)
            for name in groups.keys():
                keyboard.add(name)
            keyboard.add('🆕 Добавить группу')
            keyboard.add('🗑 Удалить дисциплину')
            keyboard.add('⬅ Назад','🏠 На главную')
            await message.answer(f'*/{data["choice_teach"]}/{data["choice_path"]}', reply_markup=keyboard)
            await self.AdminStates.admin_act_coll.set()
        elif message.text == "🏠 На главную":
            for name in ['👩🏼‍🏫 Управление преподавателями', '🧑🏼‍💻 Управление студентами', '🗂 Управление документами','👋🏼 Выход из панели администратора']:
                keyboard.add(name)
            await message.answer('Главное меню: ', reply_markup=keyboard)
            await self.AdminStates.admin_menu.set()
        elif message.text == data['captcha']:
            coll_id = data['path_list'][data['choice_path']]['_id']
            teach_id = data['teachers_list'][data['choice_teach']]['_id']
            if self.db_prov.del_coll(coll_id, teach_id):
                await message.answer('✅ Успешно удалено!')
                choice_teach = data['choice_teach']
                path_list = self.db_prov.get_path_list(data['teachers_list'][choice_teach]['_id'])
                await state.update_data(path_list=path_list)
                for name in path_list.keys():
                    keyboard.add(name)
                keyboard.add('🆕 Добавить дисциплину')
                keyboard.add('🗑 Удалить преподавателя')
                keyboard.add('⬅ Назад','🏠 На главную')
                await message.answer(
                    'Для редактирования перподавателя пришлите данные сообщением в формате: \n[Фамилия],[Имя],[Отчество],[Telegram-id]',
                    reply_markup=keyboard)
                await self.AdminStates.admin_action_teach.set()
            else:
                await message.answer('🚫 Ошибка при удалении!')
    
    async def admin_doc_menu(self, message: types.Message, state: FSMContext):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
        data = await state.get_data()
        if message.text == '⬅ Назад':
            for name in ['👩🏼‍🏫 Управление преподавателями', '🧑🏼‍💻 Управление студентами', '🗂 Управление документами','👋🏼 Выход из панели администратора']:
                keyboard.add(name)
            await message.answer('Главное меню: ', reply_markup=keyboard)
            await self.AdminStates.admin_menu.set()
        elif message.text == "📑 Управление типами":
            types_doc = self.db_prov.get_types_doc()
            await state.update_data(types_doc=types_doc)
            for name in types_doc.keys():
                keyboard.add(name)
            keyboard.add('⬅ Назад','🏠 На главную')
            await message.answer(
                'Для добавления нового типа документа пришлите данные в формате: \n[Название],[Префикс],[Срок хранения(мес)]',
                reply_markup=keyboard)
            await self.AdminStates.admin_choice_type.set()
        elif message.text == "🧹 Запустить очистку":
            a = await message.answer('Идет очистка...')
            list_clear = self.db_prov.start_clear()
            self.cloud_mail.del_file()
            await self.bot.delete_message(a.chat.id, a.message_id)
            await message.answer(f'🧽 Удалено {len(list_clear)} файлов!')
    
    async def admin_choice_type(self, message: types.Message, state: FSMContext):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
        data = await state.get_data()
        if message.text == "⬅ Назад":
            for name in ['📑 Управление типами', '🧹 Запустить очистку', '⬅ Назад']:
                keyboard.add(name)
            await message.answer('Гл.меню/Управление документами:', reply_markup=keyboard)
            await self.AdminStates.admin_doc_menu.set()
        elif message.text == "🏠 На главную":
            for name in ['👩🏼‍🏫 Управление преподавателями', '🧑🏼‍💻 Управление студентами', '🗂 Управление документами','👋🏼 Выход из панели администратора']:
                keyboard.add(name)
            await message.answer('Главное меню: ', reply_markup=keyboard)
            await self.AdminStates.admin_menu.set()
        elif message.text in data['types_doc'].keys():
            captcha = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(8))
            await state.update_data(captcha=captcha)
            choice_type = message.text
            await state.update_data(choice_type=choice_type)
            keyboard.add('⬅ Назад','🏠 На главную')
            await message.answer(f'❕ Для удаления выбранного типа документа введите {captcha} ', reply_markup=keyboard)
            await message.answer(f'❕ Для изменения срока хранения введите новый срок:')
            await self.AdminStates.admin_update_type.set()
        elif message.text:
            mess_ = message.text
            mess_ = mess_.replace('[','').replace(']','').split(',')
            if len(mess_) == 3:
                if self.db_prov.add_file_type(mess_[0], mess_[1], mess_[2]):
                    await message.answer(f'♻ Успешно добавлено!')
                    types_doc = self.db_prov.get_types_doc()
                    await state.update_data(types_doc=types_doc)
                    for name in types_doc.keys():
                        keyboard.add(name)
                    keyboard.add('⬅ Назад','🏠 На главную')
                    await message.answer(
                        '❕ Для добавления нового типа документа пришлите данные в формате: \n\n[Название],[Срок хранения(мес)]',
                        reply_markup=keyboard)
                    await self.AdminStates.admin_choice_type.set()
                else:
                    await message.answer('🚫 Возникла ошибка!')
            else:
                await message.answer('🚫 Неверное количество параметров!')
    
    async def admin_update_type(self, message: types.Message, state: FSMContext):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
        data = await state.get_data()
        if message.text == '⬅ Назад':
            types_doc = self.db_prov.get_types_doc()
            await state.update_data(types_doc=types_doc)
            for name in types_doc.keys():
                keyboard.add(name)
            keyboard.add('⬅ Назад','🏠 На главную')
            await message.answer(
                '❕ Для добавления нового типа документа пришлите данные в формате: \n[Название],[Срок хранения(мес)]',
                reply_markup=keyboard)
            await self.AdminStates.admin_choice_type.set()
        elif message.text == "🏠 На главную":
            for name in ['👩🏼‍🏫 Управление преподавателями', '🧑🏼‍💻 Управление студентами', '🗂 Управление документами','👋🏼 Выход из панели администратора']:
                keyboard.add(name)
            await message.answer('Главное меню: ', reply_markup=keyboard)
            await self.AdminStates.admin_menu.set()
        elif message.text == data['captcha']:
            if self.db_prov.del_type(data['types_doc'][data['choice_type']]['_id']):
                await message.answer('✅ Успешно удалено!')
            else:
                await message.answer('🚫 Ошибка удаления!')
            types_doc = self.db_prov.get_types_doc()
            await state.update_data(types_doc=types_doc)
            for name in types_doc.keys():
                keyboard.add(name)
            keyboard.add('⬅ Назад','🏠 На главную')
            await message.answer(
                '❕ Для добавления нового типа документа пришлите данные в формате: \n[Название],[Срок хранения(мес)]',
                reply_markup=keyboard)
            await self.AdminStates.admin_doc_menu.set()
        elif message.text:
            try:
                exp = int(message.text)
                if self.db_prov.update_type(data['types_doc'][data['choice_type']]['_id'],exp):
                    await message.answer('✅ Успешно обновлено!')
                    types_doc = self.db_prov.get_types_doc()
                    await state.update_data(types_doc=types_doc)
                    for name in types_doc.keys():
                        keyboard.add(name)
                    keyboard.add('⬅ Назад','🏠 На главную')
                    await message.answer(
                        '❕ Для добавления нового типа документа пришлите данные в формате: \n[Название],[Срок хранения(мес)]',
                        reply_markup=keyboard)
                    await self.AdminStates.admin_doc_menu.set()
                else:
                    await message.answer('🚫 Ошибка обновления!')
            except Exception:
                pass
    
    def register_handlers_admin(self, dp: Dispatcher):
        dp.register_message_handler(self.admin_menu, state=self.AdminStates.admin_menu)
        dp.register_message_handler(self.admin_choice_teach, state=self.AdminStates.admin_choice_teach)
        dp.register_message_handler(self.admin_choice_group, state=self.AdminStates.admin_choice_group)
        dp.register_message_handler(self.admin_add_stud, state=self.AdminStates.admin_add_stud)
        dp.register_message_handler(self.admin_add_teacher, state=self.AdminStates.admin_add_teacher)
        dp.register_message_handler(self.admin_action_teach, state=self.AdminStates.admin_action_teach)
        dp.register_message_handler(self.admin_del_teach, state=self.AdminStates.admin_del_teach)
        dp.register_message_handler(self.admin_add_coll, state=self.AdminStates.admin_add_coll)
        dp.register_message_handler(self.admin_act_coll, state=self.AdminStates.admin_act_coll)
        dp.register_message_handler(self.admin_del_coll, state=self.AdminStates.admin_del_coll)
        dp.register_message_handler(self.admin_update_stud, state=self.AdminStates.admin_update_stud)
        dp.register_message_handler(self.admin_del_stud, state=self.AdminStates.admin_del_stud)
        dp.register_message_handler(self.admin_add_gr_to_coll, state=self.AdminStates.admin_add_gr_to_coll)
        dp.register_message_handler(self.admin_del_group, state=self.AdminStates.admin_del_group)
        dp.register_message_handler(self.admin_del_gr_from_coll,state=self.AdminStates.admin_del_gr_from_coll)
        dp.register_message_handler(self.admin_doc_menu, state=self.AdminStates.admin_doc_menu)
        dp.register_message_handler(self.admin_choice_type, state=self.AdminStates.admin_choice_type)
        dp.register_message_handler(self.admin_update_type, state=self.AdminStates.admin_update_type)
        dp.register_message_handler(self.get_voucher, state=self.AdminStates.get_voucher)