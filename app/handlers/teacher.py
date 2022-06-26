import os
from datetime import datetime
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from .. import cert_helper as crt_h

class TeacherPanel():
    cert_helper = crt_h.Cert_Helper()
    
    def __init__(self, db, bot, cloud_mail, AdmS, conf):
        self.AdminStates = AdmS
        self.db_prov = db
        self.bot = bot
        self.cloud_mail = cloud_mail
        self.config = conf
    
    class TeachStates(StatesGroup):
        teach_menu = State()
        teach_choice_coll = State()
        teach_choice_group = State()
        teach_choice_stud = State()
        teach_choice_type_f = State()
        teach_choice_file = State()
        teach_uncheck_choice_coll = State()
        teach_uncheck_choice_group = State()
        teach_uncheck_choice_stud = State()
        teach_uncheck_choice_type_f = State()
        teach_uncheck_choice_file = State()
        teach_file_act = State()
        teach_file_comp = State()
        teach_send_f_back = State()
        teach_pers_data = State()
        teach_pers_data_ch_srt = State()
    
    async def teach_menu(self,message: types.Message, state: FSMContext):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
        data = await state.get_data()
        if message.text == '📝 Документы':
            list_coll = self.db_prov.get_coll_teach(data['obj_id'])
            await state.update_data(fl=1)
            await state.update_data(list_coll=list_coll)
            for name in sorted(list_coll.keys(), reverse=True):
                keyboard.add(name)
            keyboard.add('⬅ Назад', '📊 Получить отчет')
            await message.answer('Гл.меню/Документы:', reply_markup=keyboard)
            await self.TeachStates.teach_choice_coll.set()
        elif message.text == "⏳ Непроверенные документы":
            file_list = self.db_prov.get_uncheck_files_teach(data['obj_id'])
            if file_list:
                await state.update_data(fl=2)
                await state.update_data(file_list=file_list)
                for name in sorted(file_list.keys(), reverse=True):
                    keyboard.add(name)
                keyboard.add('⬅ Назад')
                await message.answer('Гл.меню/Документы:', reply_markup=keyboard)
                await self.TeachStates.teach_uncheck_choice_coll.set()
            else:
                for name in ['📝 Документы', '⏳ Непроверенные документы', '🔏 Личные данные']:
                    keyboard.add(name)
                await message.answer('✅ Непровернные документы отсутствуют!', reply_markup=keyboard)
        elif message.text == '🔏 Личные данные':
            teach_info = self.db_prov.get_teach_info(data['obj_id'])
            await state.update_data(teach_info=teach_info)
            for name in ['♻ Сменить подпись','⬅ Назад']:
                keyboard.add(name)
            key = self.db_prov.get_key(data['obj_id'])
            if not key:
                key = '🤷‍♂ Не установлен!'
            await message.answer(
                f'Фамилия: {teach_info["l_name"]} \nИмя: {teach_info["f_name"]} \nОтчество: {teach_info["m_name"]} \nTelegram-id: {teach_info["tg_id"]} \nКлюч подписи: \n\n{key} ',
                reply_markup=keyboard)
            await self.TeachStates.teach_pers_data.set()
        elif message.text == 'admin':
            teach_info = self.db_prov.get_teach_info(data['obj_id'])
            await state.update_data(teach_info=teach_info)
            if teach_info['tg_id'] in self.config.ADMINS:
                for name in ['👩🏼‍🏫 Управление преподавателями', '🧑🏼‍💻 Управление студентами', '🗂 Управление документами','👋🏼 Выход из панели администратора']:
                    keyboard.add(name)
                await message.answer('Главное меню: ', reply_markup=keyboard)
                await self.AdminStates.admin_menu.set()
    
    # Главное меню/Документы
    async def teach_choice_coll(self, message: types.Message,state: FSMContext):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
        data = await state.get_data()
        if message.text == '⬅ Назад':
            for name in ['📝 Документы','⏳ Непроверенные документы', '🔏 Личные данные']:
                keyboard.add(name)
            await message.answer('Главное меню:', reply_markup=keyboard)
            await self.TeachStates.teach_menu.set()
        elif message.text == '📊 Получить отчет':
            a = await message.answer('Отчет формируется...')
            file_name = self.db_prov.get_report(data['obj_id'])
            if file_name:
                await message.answer_document(open(file_name, 'rb'))
                os.remove(file_name)
            else:
                await message.answer('❌ Недостаточно данных для формирования отчета!')
            await self.bot.delete_message(a.chat.id, a.message_id)
        elif message.text in data['list_coll'].keys():
            choice_coll = message.text
            await state.update_data(choice_coll=choice_coll)
            group_list = self.db_prov.get_group_list(data['list_coll'][choice_coll]['_id'])
            await state.update_data(group_list=group_list)
            for name in group_list.keys():
                keyboard.add(name)
            keyboard.add('⬅ Назад','🏠 На главную')
            await message.answer(f'Гл.меню/Документы/{message.text}:', reply_markup=keyboard)
            await self.TeachStates.teach_choice_group.set()
    
    # Главное меню/Документы/[Дисциплина]
    async def teach_choice_group(self,message: types.Message,state: FSMContext):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
        data = await state.get_data()
        if message.text == '⬅ Назад':
            list_coll = self.db_prov.get_coll_teach(data['obj_id'])
            await state.update_data(list_coll=list_coll)
            for name in sorted(list_coll.keys(), reverse=True):
                keyboard.add(name)
            keyboard.add('⬅ Назад')
            await message.answer('Гл.меню/Документы:', reply_markup=keyboard)
            await self.TeachStates.teach_choice_coll.set()
        elif message.text == '🏠 На главную':
            for name in ['📝 Документы','⏳ Непроверенные документы', '🔏 Личные данные']:
                keyboard.add(name)
            await message.answer('Главное меню:', reply_markup=keyboard)
            await self.TeachStates.teach_menu.set()
        elif message.text in data['group_list'].keys():
            choice_group = message.text
            await state.update_data(choice_group=choice_group)
            stud_list = self.db_prov.get_stud_list(data["group_list"][choice_group]['_id'])
            await state.update_data(stud_list=stud_list)
            for name in stud_list.keys():
                keyboard.add(name)
            keyboard.add('⬅ Назад','🏠 На главную')
            await message.answer(f'*/Документы/{data["choice_coll"]}/{choice_group}:', reply_markup=keyboard)
            await self.TeachStates.teach_choice_stud.set()
    
    # Главное меню/Документы/[Дисциплина]/[Группа]/[Студент]
    async def teach_choice_stud(self,message: types.Message,state: FSMContext):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
        data = await state.get_data()
        if message.text == '⬅ Назад':
            choice_coll = data['choice_coll']
            group_list = self.db_prov.get_group_list(data['list_coll'][choice_coll]['_id'])
            await state.update_data(group_list=group_list)
            for name in group_list.keys():
                keyboard.add(name)
            keyboard.add('⬅ Назад','🏠 На главную')
            await message.answer(f'Гл.меню/Документы/{choice_coll}:', reply_markup=keyboard)
            await self.TeachStates.teach_choice_group.set()
        elif message.text == '🏠 На главную':
            for name in ['📝 Документы','⏳ Непроверенные документы', '🔏 Личные данные']:
                keyboard.add(name)
            await message.answer('Главное меню:', reply_markup=keyboard)
            await self.TeachStates.teach_menu.set()
        elif message.text in data['stud_list'].keys():
            choice_stud = message.text
            await state.update_data(choice_stud=choice_stud)
            file_list = self.db_prov.get_files_teach(data['stud_list'][choice_stud]['_id'], data['list_coll'][data['choice_coll']]['_id'])
            await state.update_data(file_list=file_list)
            for name in file_list.keys():
                keyboard.add(name)
            keyboard.add('⬅ Назад','🏠 На главную')
            await message.answer(f'*/{data["choice_group"]}/{choice_stud}:', reply_markup=keyboard)
            await self.TeachStates.teach_choice_type_f.set()
    
    # Главное меню/Документы/[Дисциплина]/[Группа]/[Студент]/(выбор типа файла)
    async def teach_choice_type_f(self,message: types.Message,state: FSMContext):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
        data = await state.get_data()
        if message.text == '⬅ Назад':
            choice_group = data['choice_group']
            await state.update_data(choice_group=choice_group)
            stud_list = self.db_prov.get_stud_list(data["group_list"][choice_group]['_id'])
            await state.update_data(stud_list=stud_list)
            for name in stud_list.keys():
                keyboard.add(name)
            keyboard.add('⬅ Назад','🏠 На главную')
            await message.answer(f'*/Документы/{data["choice_coll"]}/{choice_group}:', reply_markup=keyboard)
            await self.TeachStates.teach_choice_stud.set()
        elif message.text == '🏠 На главную':
            for name in ['📝 Документы','⏳ Непроверенные документы', '🔏 Личные данные']:
                keyboard.add(name)
            await message.answer('Главное меню:', reply_markup=keyboard)
            await self.TeachStates.teach_menu.set()
        elif message.text in data['file_list'].keys():
            choice_type = message.text
            await state.update_data(choice_type=choice_type)
            for name in data['file_list'][choice_type]:
                keyboard.add(name)
            keyboard.add('⬅ Назад','🏠 На главную')
            await message.answer(f'*/{data["choice_stud"]}/{choice_type}:', reply_markup=keyboard)
            await self.TeachStates.teach_choice_file.set()
    
    # Главное меню/Документы/[Дисциплина]/[Группа]/[Студент]/[тип] (выбор файла)
    async def teach_choice_file(self,message: types.Message,state: FSMContext):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
        data = await state.get_data()
        if message.text == '⬅ Назад':
            choice_stud = data["choice_stud"]
            file_list = self.db_prov.get_files_teach(data['stud_list'][choice_stud]['_id'], data['list_coll'][data['choice_coll']]['_id'])
            await state.update_data(file_list=file_list)
            for name in file_list.keys():
                keyboard.add(name)
            keyboard.add('⬅ Назад','🏠 На главную')
            await message.answer(f'*/{data["choice_group"]}/{choice_stud}:', reply_markup=keyboard)
            await self.TeachStates.teach_choice_type_f.set()
        elif message.text == '🏠 На главную':
            for name in ['📝 Документы','⏳ Непроверенные документы', '🔏 Личные данные']:
                keyboard.add(name)
            await message.answer('Главное меню:', reply_markup=keyboard)
            await self.TeachStates.teach_menu.set()
        elif message.text in data['file_list'][data['choice_type']].keys():
            choice_file = message.text
            if data['file_list'][data['choice_type']][choice_file]['status'] != 'accepted':
                await state.update_data(choice_file=choice_file)
                for name in ['📤 Выгрузить работу', '📝 Принять работу', '🛠 Отправить на доработку']:
                    keyboard.add(name)
                keyboard.add("⬅ Назад",'🏠 На главную')
                txt = f'Информация о выбранном файле:\n\n🧑‍💻 Владелец: <b><i>{data["choice_stud"]}</i></b>\n📥 Дата загрузки: <b><i>{data["file_list"][data["choice_type"]][choice_file]["date_upload"]}</i></b>\n📚 Вид работы: <b><i>{data["choice_type"]}</i></b>\n📁 Файл: <b><i>{choice_file}</i></b>'
                if data["file_list"][data["choice_type"]][choice_file]["comment"]!="":
                    txt += f'\n\n📌 Последний комментарий к работе:\n<b><i>{data["file_list"][data["choice_type"]][choice_file]["comment"]}</i></b>'
                await message.answer(txt,reply_markup=keyboard, parse_mode=types.ParseMode.HTML)
                await self.TeachStates.teach_file_act.set()
            else:
                await message.answer('❎ Файл уже принят, действия над ним невозможны!')
    
    # Главное меню/Документы/[Дисциплина]/[Группа]/[Студент]/[тип]/[файл] (действия над файлом)
    async def teach_file_act(self,message: types.Message,state: FSMContext):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
        data = await state.get_data()
        if message.text == '⬅ Назад':
            if data['fl']==1:
                choice_type = data["choice_type"]
                choice_stud = data['choice_stud']
                file_list = self.db_prov.get_files_teach(data['stud_list'][choice_stud]['_id'], data['list_coll'][data['choice_coll']]['_id'])
                await state.update_data(file_list=file_list)
                try:
                    for name in file_list[choice_type]:
                        keyboard.add(name)
                    keyboard.add('⬅ Назад','🏠 На главную')
                    await message.answer(f'*/{data["choice_stud"]}/{choice_type}:', reply_markup=keyboard)
                    await self.TeachStates.teach_choice_file.set()
                except Exception:
                    for name in file_list.keys():
                        keyboard.add(name)
                    keyboard.add('⬅ Назад','🏠 На главную')
                    await message.answer(f'*/{data["choice_group"]}/{choice_stud}:', reply_markup=keyboard)
                    await self.TeachStates.teach_choice_type_f.set()
            if data['fl']==2:
                choice_type = data['choice_type']
                for name in data['file_list'][data['choice_coll']][data['choice_group']][data['choice_stud']][
                    choice_type].keys():
                    keyboard.add(name)
                keyboard.add('⬅ Назад','🏠 На главную')
                await message.answer(f'*/{data["choice_stud"]}/{choice_type}:', reply_markup=keyboard)
                await self.TeachStates.teach_uncheck_choice_file.set()
        elif message.text == '🏠 На главную':
            for name in ['📝 Документы','⏳ Непроверенные документы', '🔏 Личные данные']:
                keyboard.add(name)
            await message.answer('Главное меню:', reply_markup=keyboard)
            await self.TeachStates.teach_menu.set()
        elif message.text == '📤 Выгрузить работу':
                if data['fl'] == 1:
                    path = self.config.HOME_PATH + f'\\unchecked_files\\{data["file_list"][data["choice_type"]][data["choice_file"]]["_id"]}.pdf'
                else:
                    path = self.config.HOME_PATH + f'\\unchecked_files\\{data["file_list"][data["choice_coll"]][data["choice_group"]][data["choice_stud"]][data["choice_type"]][data["choice_file"]]["_id"]}.pdf'
                path_ = self.config.HOME_PATH + f'\\unchecked_files\\{data["choice_file"]}'
                if os.path.isfile(path):
                    os.rename(path, path_)
                    await message.answer_document(open(path_, 'rb'))
                    os.rename(path_, path)
                else:
                    await message.answer('❌ Ошибка загрузки. Попробуйте снова.')
        elif message.text == '🛠 Отправить на доработку':
            keyboard.add('Пропустить')
            keyboard.add('⬅ Назад','🏠 На главную')
            await message.answer('Напишите коментарий:', reply_markup=keyboard)
            await self.TeachStates.teach_send_f_back.set()
        elif message.text == '📝 Принять работу':
            keyboard.add('⬅ Назад','🏠 На главную')
            await message.answer(f'Отправьте проверенный файл:', reply_markup=keyboard)
            await self.TeachStates.teach_file_comp.set()
    
    # Главное меню/Документы/[Дисциплина]/[Группа]/[Студент]/[тип]/[файл] (принять)
    async def teach_file_comp(self,message: types.Message,state: FSMContext):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
        data = await state.get_data()
        if message.text == '⬅ Назад':
            choice_file = data['choice_file']
            for name in ['📤 Выгрузить работу', '📝 Принять работу', '🛠 Отправить на доработку']:
                keyboard.add(name)
            keyboard.add("⬅ Назад",'🏠 На главную')
            if data['fl'] == 1:
                txt = f'Информация о выбранном файле:\n\n🧑‍💻 Владелец: <b><i>{data["choice_stud"]}</i></b>\n📥 Дата загрузки: <b><i>{data["file_list"][data["choice_type"]][choice_file]["date_upload"]}</i></b>\n📚 Вид работы: <b><i>{data["choice_type"]}</i></b>\n📁 Файл: <b><i>{choice_file}</i></b>'
                if data["file_list"][data["choice_type"]][choice_file]["comment"] != "":
                    txt += f'\n\n📌 Последний комментарий к работе:\n<b><i>{data["file_list"][data["choice_type"]][choice_file]["comment"]}</i></b>'
                await message.answer(txt, reply_markup=keyboard, parse_mode=types.ParseMode.HTML)
            else:
                txt = f'Информация о выбранном файле:\n\n🧑‍💻 Владелец: <b><i>{data["choice_stud"]}</i></b>\n📥 Дата загрузки: <b><i>{data["file_list"][data["choice_coll"]][data["choice_group"]][data["choice_stud"]][data["choice_type"]][choice_file]["date_upload"]}</i></b>\n📚 Вид работы: <b><i>{data["choice_type"]}</i></b>\n📁 Файл: <b><i>{choice_file}</i></b>'
                if data['file_list'][data['choice_coll']][data['choice_group']][data['choice_stud']][data['choice_type']][
                    choice_file]["comment"] != "":
                    txt += f"\n\n📌 Последний комментарий к работе:\n<b><i>{data['file_list'][data['choice_coll']][data['choice_group']][data['choice_stud']][data['choice_type']][choice_file]['comment']}</i></b>"
                await message.answer(txt, reply_markup=keyboard, parse_mode=types.ParseMode.HTML)
            await self.TeachStates.teach_file_act.set()
        elif message.text == '🏠 На главную':
            for name in ['📝 Документы','⏳ Непроверенные документы', '🔏 Личные данные']:
                keyboard.add(name)
            await message.answer('Главное меню:', reply_markup=keyboard)
            await self.TeachStates.teach_menu.set()
        elif message.document:
            a = await message.answer('Идет проверка...')
            doc_ = await message.document.get_file()
            date_t = datetime.today()
            date_ = date_t.strftime("%d%m%Y")
            if data['fl'] == 1:
                file_info = data['file_list'][data['choice_type']][data['choice_file']]
            else:
                file_info = data['file_list'][data['choice_coll']][data['choice_group']][data['choice_stud']][data['choice_type']][data['choice_file']]
            key_teacher = self.db_prov.get_key(data['obj_id'])
            if key_teacher:
                key_student = self.db_prov.get_key(file_info['st_id'])
                file_path = self.config.HOME_PATH + f'\\unchecked_files\\{file_info["_id"]}.pdf'
                file_path_new = self.config.HOME_PATH + f'\\unchecked_files\\{file_info["_id"]}new.pdf'
                await doc_.download(destination_file=file_path_new)
                if await self.cert_helper.check_valid_cert(file_path_new):
                    list_keys = self.cert_helper.get_pub_key_pdf(file_path_new)
                    if (key_teacher in list_keys) and (key_student in list_keys):
                        os.replace(file_path_new,file_path)
                        file_name = file_info['file_name']
                        new_name = file_name[:file_name.rfind('_')+1]+date_+'.pdf'
                        tc = self.db_prov.db.teachers.find_one({'_id':data['obj_id']})
                        new_path = tc['home_path']+self.db_prov.get_file_path(file_info['_id'])
                        if not os.path.isdir(self.config.HOME_PATH + new_path):
                            os.makedirs(self.config.HOME_PATH + new_path)
                        ink = 1
                        while os.path.isfile(self.config.HOME_PATH + new_path + f'\\{new_name}'):
                            new_name = new_name[:-4]+f'({ink}).pdf'
                            ink+=1
                        os.replace(file_path, self.config.HOME_PATH + new_path + f'\\{new_name}')
                        _id = self.db_prov.db.files.find_one_and_update({'_id':file_info["_id"]},{'$set':{"file_name":new_name, "date_upload":date_t, "status":"accepted", "path":new_path}})
                        if data['fl'] == 1:
                            self.db_prov.db.teachers.update_one({'_id': data['obj_id']}, {
                                '$pull': {'uncheck_file': data["file_list"][data["choice_type"]][data["choice_file"]]["_id"]}})
                        else:
                            self.db_prov.db.teachers.update_one({'_id': data['obj_id']}, {
                                '$pull': {'uncheck_file': data['file_list'][data['choice_coll']][data['choice_group']][data['choice_stud']][data["choice_type"]][data["choice_file"]]["_id"]}})
                        self.db_prov.db.unsent_files.insert_one({'_id':_id['_id'], 'operation': 'ADD'})
                        self.cloud_mail.start_upload()
                        await message.answer("✅ Файл был успешно помещен в архив.")
                    else:
                        if os.path.isfile(file_path_new):
                            os.remove(file_path_new)
                        await message.answer('🚫 Неверная подпись!')
                else:
                    if os.path.isfile(file_path_new):
                        os.remove(file_path_new)
                    await message.answer('🚫 Подпись не действительна!')
            else:
                await message.answer('‼ Для начала добавьте ключ!')
            await self.bot.delete_message(a.chat.id, a.message_id)
            if data['fl'] == 1:
                file_list = self.db_prov.get_files_teach(data['stud_list'][data['choice_stud']]['_id'],data['list_coll'][data['choice_coll']]['_id'])
            else:
                file_list = self.db_prov.get_uncheck_files_teach(data['obj_id'])
            await state.update_data(file_list=file_list)
            choice_type = data['choice_type']
            if data['fl'] == 1:
                if file_list.keys():
                    for name in file_list[choice_type]:
                        keyboard.add(name)
                keyboard.add('⬅ Назад','🏠 На главную')
                await message.answer(f'*/{data["choice_stud"]}/{choice_type}:', reply_markup=keyboard)
                await self.TeachStates.teach_choice_file.set()
            else:
                try:
                    for name in file_list[data['choice_coll']][data['choice_group']][data['choice_stud']][
                        choice_type].keys():
                        keyboard.add(name)
                    keyboard.add('⬅ Назад')
                    await message.answer(f'*/{data["choice_stud"]}/{choice_type}:', reply_markup=keyboard)
                    await self.TeachStates.teach_uncheck_choice_file.set()
                except Exception:
                    for name in sorted(file_list.keys(), reverse=True):
                        keyboard.add(name)
                    keyboard.add('⬅ Назад')
                    await message.answer('Гл.меню/Документы:', reply_markup=keyboard)
                    await self.TeachStates.teach_uncheck_choice_coll.set()
    
    # Главное меню/Документы/[Дисциплина]/[Группа]/[Студент]/[тип]/[файл] (🛠 Отправить на доработку)
    async def teach_send_f_back(self,message: types.Message, state: FSMContext):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
        data = await state.get_data()
        if message.text == '⬅ Назад':
            choice_file = data['choice_file']
            for name in ['📤 Выгрузить работу', '📝 Принять работу', '🛠 Отправить на доработку']:
                keyboard.add(name)
            keyboard.add("⬅ Назад",'🏠 На главную')
            if data['fl']==1:
                txt = f'Информация о выбранном файле:\n\n🧑‍💻 Владелец: <b><i>{data["choice_stud"]}</i></b>\n📥 Дата загрузки: <b><i>{data["file_list"][data["choice_type"]][choice_file]["date_upload"]}</i></b>\n📚 Вид работы: <b><i>{data["choice_type"]}</i></b>\n📁 Файл: <b><i>{choice_file}</i></b>'
                if data["file_list"][data["choice_type"]][choice_file]["comment"] != "":
                    txt += f'\n\n📌 Последний комментарий к работе:\n<b><i>{data["file_list"][data["choice_type"]][choice_file]["comment"]}</i></b>'
                await message.answer(txt, reply_markup=keyboard, parse_mode=types.ParseMode.HTML)
            else:
                txt = f'Информация о выбранном файле:\n\n🧑‍💻 Владелец: <b><i>{data["choice_stud"]}</i></b>\n📥 Дата загрузки: <b><i>{data["file_list"][data["choice_coll"]][data["choice_group"]][data["choice_stud"]][data["choice_type"]][choice_file]["date_upload"]}</i></b>\n📚 Вид работы: <b><i>{data["choice_type"]}</i></b>\n📁 Файл: <b><i>{choice_file}</i></b>'
                if data['file_list'][data['choice_coll']][data['choice_group']][data['choice_stud']][data['choice_type']][
                    choice_file]["comment"] != "":
                    txt += f"\n\n📌 Последний комментарий к работе:\n<b><i>{data['file_list'][data['choice_coll']][data['choice_group']][data['choice_stud']][data['choice_type']][choice_file]['comment']}</i></b>"
                await message.answer(txt, reply_markup=keyboard, parse_mode=types.ParseMode.HTML)
            await self.TeachStates.teach_file_act.set()
        elif message.text == '🏠 На главную':
            for name in ['📝 Документы','⏳ Непроверенные документы', '🔏 Личные данные']:
                keyboard.add(name)
            await message.answer('Главное меню:', reply_markup=keyboard)
            await self.TeachStates.teach_menu.set()
        elif message.text:
            if message.text == 'Пропустить':
                comment = '(Нет)'
            else:
                comment = message.text
            if data['fl']==1:
                tg_id_stud = self.db_prov.db.students.find_one({'_id':data['file_list'][data["choice_type"]][data['choice_file']]['st_id']})
                self.db_prov.db.files.update_one({'_id': data["file_list"][data["choice_type"]][data["choice_file"]]["_id"]},{"$set":{'status' : "modification","comment":comment}})
                self.db_prov.db.teachers.update_one({'_id': data['obj_id']}, {'$pull': {'uncheck_file': data["file_list"][data["choice_type"]][data["choice_file"]]["_id"]}})
            elif data['fl']==2:
                tg_id_stud = self.db_prov.db.students.find_one(
                    {'_id': data['file_list'][data['choice_coll']][data['choice_group']][data['choice_stud']][data["choice_type"]][data['choice_file']]['st_id']})
                self.db_prov.db.files.update_one({'_id': data['file_list'][data['choice_coll']][data['choice_group']][data['choice_stud']][data["choice_type"]][data["choice_file"]]["_id"]},
                                            {"$set": {'status': "modification", "comment": comment}})
                self.db_prov.db.teachers.update_one({'_id': data['obj_id']}, {
                    '$pull': {'uncheck_file': data['file_list'][data['choice_coll']][data['choice_group']][data['choice_stud']][data["choice_type"]][data["choice_file"]]["_id"]}})
    
            tg_id_stud = tg_id_stud['tg_id']
            await self.bot.send_message(tg_id_stud, f'⚠️⚠️⚠️Уведомление ⚠️⚠️⚠️\n\nФайл {data["choice_file"]} не принят!\n\n📌 Коментарий преподавателя:\n{comment}')
            if data['fl']==1:
                file_list = self.db_prov.get_files_teach(data['stud_list'][data['choice_stud']]['_id'], data['list_coll'][data['choice_coll']]['_id'])
                await state.update_data(file_list=file_list)
                choice_type = data['choice_type']
                for name in file_list[choice_type]:
                    keyboard.add(name)
                keyboard.add('⬅ Назад','🏠 На главную')
                await message.answer(f'*/{data["choice_stud"]}/{choice_type}:', reply_markup=keyboard)
                await self.TeachStates.teach_choice_file.set()
            elif data['fl']==2:
                file_list = self.db_prov.get_uncheck_files_teach(data['obj_id'])
                await state.update_data(file_list=file_list)
                choice_type = data['choice_type']
                await state.update_data(choice_type=choice_type)
                try:
                    for name in file_list[data['choice_coll']][data['choice_group']][data['choice_stud']][
                        choice_type].keys():
                        keyboard.add(name)
                    keyboard.add('⬅ Назад','🏠 На главную')
                    await message.answer(f'*/{data["choice_stud"]}/{choice_type}:', reply_markup=keyboard)
                    await self.TeachStates.teach_uncheck_choice_file.set()
                except Exception:
                    for name in sorted(file_list.keys(), reverse=True):
                        keyboard.add(name)
                    keyboard.add('⬅ Назад','🏠 На главную')
                    await message.answer('Гл.меню/Документы:', reply_markup=keyboard)
                    await self.TeachStates.teach_uncheck_choice_coll.set()
    
    # Главное меню/Непроверенные документы
    async def teach_uncheck_choice_coll(self,message: types.Message,state: FSMContext):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
        data = await state.get_data()
        if message.text == '⬅ Назад':
            for name in ['📝 Документы','⏳ Непроверенные документы', '🔏 Личные данные']:
                keyboard.add(name)
            await message.answer('Главное меню:', reply_markup=keyboard)
            await self.TeachStates.teach_menu.set()
        elif message.text in data['file_list'].keys():
            choice_coll = message.text
            await state.update_data(choice_coll=choice_coll)
            for name in data['file_list'][choice_coll].keys():
                keyboard.add(name)
            keyboard.add('⬅ Назад','🏠 На главную')
            await message.answer(f'Гл.меню/Документы/{message.text}:', reply_markup=keyboard)
            await self.TeachStates.teach_uncheck_choice_group.set()
    
    # Главное меню/Непроверенные документы/[Дисциплина]
    async def teach_uncheck_choice_group(self,message: types.Message,state: FSMContext):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
        data = await state.get_data()
        if message.text == '⬅ Назад':
            file_list = self.db_prov.get_uncheck_files_teach(data['obj_id'])
            await state.update_data(file_list=file_list)
            for name in sorted(file_list.keys(), reverse=True):
                keyboard.add(name)
            keyboard.add('⬅ Назад')
            await message.answer('Гл.меню/Документы:', reply_markup=keyboard)
            await self.TeachStates.teach_uncheck_choice_coll.set()
        elif message.text == '🏠 На главную':
            for name in ['📝 Документы','⏳ Непроверенные документы', '🔏 Личные данные']:
                keyboard.add(name)
            await message.answer('Главное меню:', reply_markup=keyboard)
            await self.TeachStates.teach_menu.set()
        elif message.text in  data['file_list'][data['choice_coll']].keys():
            choice_group = message.text
            await state.update_data(choice_group=choice_group)
            for name in data['file_list'][data['choice_coll']][choice_group].keys():
                keyboard.add(name)
            keyboard.add('⬅ Назад','🏠 На главную')
            await message.answer(f'*/Документы/{data["choice_coll"]}/{choice_group}:', reply_markup=keyboard)
            await self.TeachStates.teach_uncheck_choice_stud.set()
    
    # Главное меню/Непроверенные документы/[Дисциплина]/[Группа]/[Студент]
    async def teach_uncheck_choice_stud(self,message: types.Message,state: FSMContext):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
        data = await state.get_data()
        if message.text == '⬅ Назад':
            choice_coll = data['choice_coll']
            for name in data['file_list'][choice_coll].keys():
                keyboard.add(name)
            keyboard.add('⬅ Назад','🏠 На главную')
            await message.answer(f'Гл.меню/Документы/{choice_coll}:', reply_markup=keyboard)
            await self.TeachStates.teach_uncheck_choice_group.set()
        elif message.text == '🏠 На главную':
            for name in ['📝 Документы','⏳ Непроверенные документы', '🔏 Личные данные']:
                keyboard.add(name)
            await message.answer('Главное меню:', reply_markup=keyboard)
            await self.TeachStates.teach_menu.set()
        elif message.text in data['file_list'][data['choice_coll']][data['choice_group']].keys():
            choice_stud = message.text
            await state.update_data(choice_stud=choice_stud)
            for name in data['file_list'][data['choice_coll']][data['choice_group']][choice_stud].keys():
                keyboard.add(name)
            keyboard.add('⬅ Назад','🏠 На главную')
            await message.answer(f'*/{data["choice_group"]}/{choice_stud}:', reply_markup=keyboard)
            await self.TeachStates.teach_uncheck_choice_type_f.set()
    
    # Главное меню/Непроверенные документы/[Дисциплина]/[Группа]/[Студент]/(выбор типа файла)
    async def teach_uncheck_choice_type_f(self,message: types.Message,state: FSMContext):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
        data = await state.get_data()
        if message.text == '⬅ Назад':
            choice_group = data['choice_group']
            for name in data['file_list'][data['choice_coll']][choice_group].keys():
                keyboard.add(name)
            keyboard.add('⬅ Назад','🏠 На главную')
            await message.answer(f'*/Документы/{data["choice_coll"]}/{choice_group}:', reply_markup=keyboard)
            await self.TeachStates.teach_uncheck_choice_stud.set()
        elif message.text == '🏠 На главную':
            for name in ['📝 Документы','⏳ Непроверенные документы', '🔏 Личные данные']:
                keyboard.add(name)
            await message.answer('Главное меню:', reply_markup=keyboard)
            await self.TeachStates.teach_menu.set()
        elif message.text in data['file_list'][data['choice_coll']][data['choice_group']][data['choice_stud']].keys():
            choice_type = message.text
            await state.update_data(choice_type=choice_type)
            for name in data['file_list'][data['choice_coll']][data['choice_group']][data['choice_stud']][choice_type].keys():
                keyboard.add(name)
            keyboard.add('⬅ Назад','🏠 На главную')
            await message.answer(f'*/{data["choice_stud"]}/{choice_type}:', reply_markup=keyboard)
            await self.TeachStates.teach_uncheck_choice_file.set()
    
    # Главное меню/Непроверенные документы/[Дисциплина]/[Группа]/[Студент]/[тип] (выбор файла)
    async def teach_uncheck_choice_file(self,message: types.Message,state: FSMContext):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
        data = await state.get_data()
        if message.text == '⬅ Назад':
            choice_stud = data["choice_stud"]
            for name in data['file_list'][data['choice_coll']][data['choice_group']][choice_stud].keys():
                keyboard.add(name)
            keyboard.add('⬅ Назад','🏠 На главную')
            await message.answer(f'*/{data["choice_group"]}/{choice_stud}:', reply_markup=keyboard)
            await self.TeachStates.teach_uncheck_choice_type_f.set()
        elif message.text == '🏠 На главную':
            for name in ['📝 Документы','⏳ Непроверенные документы', '🔏 Личные данные']:
                keyboard.add(name)
            await message.answer('Главное меню:', reply_markup=keyboard)
            await self.TeachStates.teach_menu.set()
        elif message.text in data['file_list'][data['choice_coll']][data['choice_group']][data['choice_stud']][data['choice_type']].keys():
            choice_file = message.text
            if data['file_list'][data['choice_coll']][data['choice_group']][data['choice_stud']][data['choice_type']][choice_file]['status'] != 'accepted':
                await state.update_data(choice_file=choice_file)
                for name in ['📤 Выгрузить работу', '📝 Принять работу', '🛠 Отправить на доработку']:
                    keyboard.add(name)
                keyboard.add("⬅ Назад",'🏠 На главную')
                txt = f'Информация о выбранном файле:\n\n🧑‍💻 Владелец: <b><i>{data["choice_stud"]}</i></b>\n📥 Дата загрузки: <b><i>{data["file_list"][data["choice_coll"]][data["choice_group"]][data["choice_stud"]][data["choice_type"]][choice_file]["date_upload"]}</i></b>\n📚 Вид работы: <b><i>{data["choice_type"]}</i></b>\n📁 Файл: <b><i>{choice_file}</i></b>'
                if data['file_list'][data['choice_coll']][data['choice_group']][data['choice_stud']][data['choice_type']][choice_file]["comment"]!="":
                    txt += f"\n\n📌 Последний комментарий к работе:\n<b><i>{data['file_list'][data['choice_coll']][data['choice_group']][data['choice_stud']][data['choice_type']][choice_file]['comment']}</i></b>"
                await message.answer(txt,reply_markup=keyboard, parse_mode=types.ParseMode.HTML)
                await self.TeachStates.teach_file_act.set()
            else:
                await message.answer('❎ Файл уже принят, действия над ним невозможны!')
    
    # Главное меню/🔏 Личные данные
    async def teach_pers_data(self,message: types.Message, state: FSMContext):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
        if message.text == '⬅ Назад':
            for name in ['📝 Документы','⏳ Непроверенные документы', '🔏 Личные данные']:
                keyboard.add(name)
            await message.answer('Главное меню:', reply_markup=keyboard)
            await self.TeachStates.teach_menu.set()
        if message.text == '♻ Сменить подпись':
            keyboard.add('⬅ Назад','🏠 На главную')
            await message.answer('❕❕❕ Загрузите сертификат в формате .fdf или пришлите публичный ключ сертификата.', reply_markup=keyboard)
            await self.TeachStates.teach_pers_data_ch_srt.set()
    
    # Главное меню/🔏 Личные данные/Смена подписи
    async def teach_pers_data_ch_srt(self,message: types.Message, state: FSMContext):
        data = await state.get_data()
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
        if message.text == '⬅ Назад':
            teach_info = self.db_prov.get_teach_info(data['obj_id'])
            await state.update_data(teach_info=teach_info)
            for name in ['♻ Сменить подпись', '⬅ Назад']:
                keyboard.add(name)
            key = self.db_prov.get_key(data['obj_id'])
            if not key:
                key = '🤷‍♂ Не установлен!'
            await message.answer(
                f'Фамилия: {teach_info["l_name"]} \nИмя: {teach_info["f_name"]} \nОтчество: {teach_info["m_name"]} \nTelegram-id: {teach_info["tg_id"]} \nКлюч подписи: \n\n{key} ',
                reply_markup=keyboard)
            await self.TeachStates.teach_pers_data.set()
        elif message.text == '🏠 На главную':
            for name in ['📝 Документы','⏳ Непроверенные документы', '🔏 Личные данные']:
                keyboard.add(name)
            await message.answer('Главное меню:', reply_markup=keyboard)
            await self.TeachStates.teach_menu.set()
        elif message.document:
            doc_ = await message.document.get_file()
            await doc_.download()
            pdf_cert = self.cert_helper.get_pub_key_fdf(doc_['file_path'])
            if pdf_cert:
                pdf_cert = pdf_cert.replace(' ', '')
                key = self.db_prov.get_key(data['obj_id'])
                if (pdf_cert != key) or (not key):
                    self.db_prov.change_teach_key(data['obj_id'], pdf_cert)
                    await message.answer('✅ Ключ изменен!')
                else:
                    await message.answer('❕❔ Ключ совпадает с настоящим!')
            else:
                await message.answer('❌ Неверный сертификат!')
            if os.path.isfile(doc_['file_path']):
                os.remove(doc_['file_path'])
        elif message.text:
            sert = message.text
            sert = sert.replace(' ', '')
            pos = sert.find('06092A864886F70D010101')
            if pos != -1:
                user_key = self.db_prov.get_key(data['obj_id'])
                if (sert != user_key) or (not user_key):
                    if self.db_prov.add_pub_key(sert, data['obj_id'], 'teacher'):
                        await message.answer('✅ Ключ изменен!')
                    else:
                        await message.answer('❌ Ошибка при добавлении/изменении ключа!')
                else:
                    await message.answer('❕❔ Ключ совпадает с настоящим!')
            else:
                await message.answer('❌ Неподходящий формат ключа!')
    
    
    
    def register_handlers_teacher(self, dp: Dispatcher):
        dp.register_message_handler(self.teach_menu, state=self.TeachStates.teach_menu)
        dp.register_message_handler(self.teach_choice_coll, state=self.TeachStates.teach_choice_coll)
        dp.register_message_handler(self.teach_choice_group, state=self.TeachStates.teach_choice_group)
        dp.register_message_handler(self.teach_choice_stud, state=self.TeachStates.teach_choice_stud)
        dp.register_message_handler(self.teach_choice_type_f, state=self.TeachStates.teach_choice_type_f)
        dp.register_message_handler(self.teach_choice_file,state=self.TeachStates.teach_choice_file)
        dp.register_message_handler(self.teach_uncheck_choice_coll, state=self.TeachStates.teach_uncheck_choice_coll)
        dp.register_message_handler(self.teach_uncheck_choice_group, state=self.TeachStates.teach_uncheck_choice_group)
        dp.register_message_handler(self.teach_uncheck_choice_stud, state=self.TeachStates.teach_uncheck_choice_stud)
        dp.register_message_handler(self.teach_uncheck_choice_type_f, state=self.TeachStates.teach_uncheck_choice_type_f)
        dp.register_message_handler(self.teach_uncheck_choice_file, state=self.TeachStates.teach_uncheck_choice_file)
        dp.register_message_handler(self.teach_file_act, state=self.TeachStates.teach_file_act)
        dp.register_message_handler(self.teach_file_comp, content_types=[types.ContentType.ANY], state=self.TeachStates.teach_file_comp)
        dp.register_message_handler(self.teach_send_f_back, state=self.TeachStates.teach_send_f_back)
        dp.register_message_handler(self.teach_pers_data, state=self.TeachStates.teach_pers_data)
        dp.register_message_handler(self.teach_pers_data_ch_srt,content_types=[types.ContentType.ANY], state=self.TeachStates.teach_pers_data_ch_srt)
