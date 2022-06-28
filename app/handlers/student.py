import os
import random
import re
import string
from datetime import datetime
from transliterate import translit
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from .. import cert_helper as crt_h


class StudentPanel():
    cert_helper = crt_h.Cert_Helper()

    def __init__(self, db, bot , AdmS,conf):
        self.AdminStates = AdmS
        self.db_prov = db
        self.bot = bot
        self.config = conf


    class StudStates(StatesGroup):
        stud_menu = State()
        stud_doc = State()
        stud_choice_type = State()
        stud_ch_upl_type_file = State()
        stud_upload_file = State()
        stud_pers_data = State()
        stud_pers_data_ch_srt =State()
        stud_file_list = State()
        stud_file_update = State()
    
    
    # CТУДЕНТ
    # Главное меню
    async def stud_menu(self, message: types.Message, state: FSMContext):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
        data = await state.get_data()
        if message.text == '📝 Документы':
            stud_info = self.db_prov.get_stud_info(data['obj_id'])
            await state.update_data(stud_info=stud_info)
            coll_list = self.db_prov.get_coll_stud(data['obj_id'])
            await state.update_data(coll_list=coll_list)
            for name in coll_list.keys():
                keyboard.add(name)
            keyboard.add('⬅ Назад')
            await message.answer('Гл.меню/Документы:',reply_markup=keyboard)
            await self.StudStates.stud_doc.set()
        elif message.text == '🔏 Личные данные':
            stud_info = self.db_prov.get_stud_info(data['obj_id'])
            await state.update_data(stud_info=stud_info)
            for name in ['♻ Сменить подпись','⬅ Назад']:
                keyboard.add(name)
            key = self.db_prov.get_key(data['obj_id'])
            if not key:
                key = '🤷‍♂ Не установлен!'
            await message.answer(
                f'Фамилия: {stud_info["l_name"]} \nИмя: {stud_info["f_name"]} \nОтчество: {stud_info["m_name"]} \nTelegram-id: {stud_info["tg_id"]} \nКлюч подписи: \n\n{key} ',
                reply_markup=keyboard)
            await self.StudStates.stud_pers_data.set()
        elif message.text == 'admin':
            stud_info = self.db_prov.get_stud_info(data['obj_id'])
            await state.update_data(stud_info=stud_info)
            if stud_info['tg_id'] in self.config.ADMINS:
                for name in ['👩🏼‍🏫 Управление преподавателями', '🧑🏼‍💻 Управление студентами', '🗂 Управление документами','👋🏼 Выход из панели администратора']:
                    keyboard.add(name)
                await message.answer('Главное меню: ', reply_markup=keyboard)
                await self.AdminStates.admin_menu.set()
    
    # Главное меню/Документы
    async def stud_doc(self, message: types.Message, state: FSMContext):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
        data = await state.get_data()
        if message.text == '⬅ Назад':
            for name in ['📝 Документы', '🔏 Личные данные']:
                keyboard.add(name)
            await message.answer('Главное меню:', reply_markup=keyboard)
            await self.StudStates.stud_menu.set()
        if message.text in data['coll_list'].keys():
            choice_coll = message.text
            await state.update_data(choice_coll=choice_coll)
            files = self.db_prov.get_files(data['obj_id'],data['coll_list'][choice_coll]['_id'])
            await state.update_data(files=files)
            for name in files:
                keyboard.add(name)
            keyboard.add('Загрузить файл')
            keyboard.add('⬅ Назад','🏠 На главную')
            await message.answer(f'Гл.меню/документы/{choice_coll}:', reply_markup=keyboard)
            await self.StudStates.stud_choice_type.set()
    
    async def stud_choice_type(self, message: types.Message, state: FSMContext):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
        data = await state.get_data()
        if message.text=='⬅ Назад':
            coll_list = self.db_prov.get_coll_stud(data['obj_id'])
            await state.update_data(coll_list=coll_list)
            for name in coll_list.keys():
                keyboard.add(name)
            keyboard.add('⬅ Назад')
            await message.answer('Гл.меню/Документы:', reply_markup=keyboard)
            await self.StudStates.stud_doc.set()
        elif message.text == '🏠 На главную':
            for name in ['📝 Документы', '🔏 Личные данные']:
                keyboard.add(name)
            await message.answer('Главное меню:', reply_markup=keyboard)
            await self.StudStates.stud_menu.set()
        elif message.text == 'Загрузить файл':
            types_f = self.db_prov.get_types()
            await state.update_data(types_f=types_f)
            for name in types_f:
                keyboard.add(name)
            keyboard.add('⬅ Назад','🏠 На главную')
            await message.answer('Выберите тип работы: ', reply_markup=keyboard)
            await self.StudStates.stud_ch_upl_type_file.set()
        elif message.text in data['files'].keys():
            choice_type = message.text
            await state.update_data(choice_type=choice_type)
            for name in data['files'][choice_type].keys():
                keyboard.add(name)
            keyboard.add('⬅ Назад','🏠 На главную')
            await message.answer(f'*/{data["choice_coll"]}/{choice_type}:', reply_markup=keyboard)
            await self.StudStates.stud_file_list.set()
    
    async def stud_file_list(self, message: types.Message, state: FSMContext):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
        data = await state.get_data()
        if message.text=='⬅ Назад':
            choice_coll = data['choice_coll']
            await state.update_data(choice_coll=choice_coll)
            files = self.db_prov.get_files(data['obj_id'],data['coll_list'][data['choice_coll']]['_id'])
            await state.update_data(files=files)
            for name in files:
                keyboard.add(name)
            keyboard.add('Загрузить файл')
            keyboard.add('⬅ Назад','🏠 На главную')
            await message.answer(f'Гл.меню/документы/{choice_coll}:', reply_markup=keyboard)
            await self.StudStates.stud_choice_type.set()
        elif message.text == '🏠 На главную':
            for name in ['📝 Документы', '🔏 Личные данные']:
                keyboard.add(name)
            await message.answer('Главное меню:', reply_markup=keyboard)
            await self.StudStates.stud_menu.set()
        elif message.text in data['files'][data['choice_type']].keys():
            choice_file = message.text
            await state.update_data(choice_file=choice_file)
            if data['files'][data['choice_type']][choice_file]['status']=='accepted':
                await message.answer('⚠️Документ уже принят. Действия над ним невозможны!')
            else:
                captcha = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(8))
                await state.update_data(captcha=captcha)
                keyboard.add('⬅ Назад','🏠 На главную')
                await message.answer(f'❕ Для удаления файла введите: {captcha}')
                await message.answer(f'❕ Чтобы заменить файл пришлите новый сообщением.', reply_markup=keyboard)
                if data['files'][data['choice_type']][choice_file]=='modification':
                    await message.answer(f"Коментарий от преподавателя:\n\n"+data['files'][data['choice_type']][choice_file]['comment'])
                await self.StudStates.stud_file_update.set()
    
    async def stud_file_update(self, message: types.Message, state: FSMContext):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
        data = await state.get_data()
        if message.text == '⬅ Назад':
            files = self.db_prov.get_files(data['obj_id'],data['coll_list'][data['choice_coll']]['_id'])
            await state.update_data(files=files)
            choice_type = data['choice_type']
            for name in files[choice_type].keys():
                keyboard.add(name)
            keyboard.add('⬅ Назад','🏠 На главную')
            await message.answer(f'*/{data["choice_coll"]}/{choice_type}:', reply_markup=keyboard)
            await self.StudStates.stud_file_list.set()
        elif message.text == '🏠 На главную':
            for name in ['📝 Документы', '🔏 Личные данные']:
                keyboard.add(name)
            await message.answer('Главное меню:', reply_markup=keyboard)
            await self.StudStates.stud_menu.set()
        elif message.document:
            doc_ = await message.document.get_file()
            date_t = datetime.today()
            date_ = date_t.strftime("%d%m%Y")
            try:
                f_id = data['files'][data['choice_type']][data['choice_file']]['_id']
                file_path = self.config.HOME_PATH + f'\\unchecked_files\\{f_id}.pdf'
                file_path_new = self.config.HOME_PATH + f'\\unchecked_files\\{f_id}new.pdf'
                await doc_.download(destination_file=file_path_new)
                if await self.cert_helper.check_valid_cert(file_path_new):
                    key = self.db_prov.get_key(data['obj_id'])
                    if key in self.cert_helper.get_pub_key_pdf(file_path_new):
                        if self.db_prov.update_file(f_id, date_, date_t):
                            os.replace(file_path_new,file_path)
                            await message.answer('✅ Файл успешно изменен!')
                        else:
                            if os.path.isfile(file_path_new):
                                os.remove(file_path_new)
                            await message.answer('🚫 Ошибка изменения файла. Попробуйте снова.')
                            choice_coll = data['choice_coll']
                            await state.update_data(choice_coll=choice_coll)
                            files = self.db_prov.get_files(data['obj_id'],data['coll_list'][data['choice_coll']]['_id'])
                            await state.update_data(files=files)
                            for name in files:
                                keyboard.add(name)
                            keyboard.add('Загрузить файл')
                            keyboard.add('⬅ Назад','🏠 На главную')
                            await message.answer(f'Гл.меню/документы/{choice_coll}:', reply_markup=keyboard)
                            await self.StudStates.stud_choice_type.set()
                            files = self.db_prov.get_files(data['obj_id'],data['coll_list'][data['choice_coll']]['_id'])
                            await state.update_data(files=files)
                    else:
                        await message.answer('🚫 Неверная подпись!')
                        if os.path.isfile(file_path_new):
                            os.remove(file_path_new)
                else:
                    if os.path.isfile(file_path_new):
                        os.remove(file_path_new)
                    await message.answer('🚫 Подпись не действительна!')
            except Exception:
                await message.answer('🚫 Ошибка изменения файла. Попробуйте снова.')
                choice_coll = data['choice_coll']
                await state.update_data(choice_coll=choice_coll)
                files = self.db_prov.get_files(data['obj_id'],data['coll_list'][data['choice_coll']]['_id'])
                await state.update_data(files=files)
                for name in files:
                    keyboard.add(name)
                keyboard.add('Загрузить файл')
                keyboard.add('⬅ Назад','🏠 На главную')
                await message.answer(f'Гл.меню/документы/{choice_coll}:', reply_markup=keyboard)
                await self.StudStates.stud_choice_type.set()
        elif message.text == data['captcha']:
            if self.db_prov.del_file_by_id(data['files'][data['choice_type']][data['choice_file']]['_id']):
                await message.answer('✅ Успешно удалено!')
            else:
                await message.answer('🚫 Ошибка при попытке удалени!')
            files = self.db_prov.get_files(data['obj_id'],data['coll_list'][data['choice_coll']]['_id'])
            await state.update_data(files=files)
            choice_type = data['choice_type']
            try:
                for name in files[choice_type].keys():
                    keyboard.add(name)
                keyboard.add('⬅ Назад','🏠 На главную')
                await message.answer(f'*/{data["choice_coll"]}/{choice_type}:', reply_markup=keyboard)
                await self.StudStates.stud_file_list.set()
            except Exception:
                choice_coll = data['choice_coll']
                await state.update_data(choice_coll=choice_coll)
                files = self.db_prov.get_files(data['obj_id'],data['coll_list'][data['choice_coll']]['_id'])
                await state.update_data(files=files)
                for name in files:
                    keyboard.add(name)
                keyboard.add('Загрузить файл')
                keyboard.add('⬅ Назад','🏠 На главную')
                await message.answer(f'Гл.меню/документы/{choice_coll}:', reply_markup=keyboard)
                await self.StudStates.stud_choice_type.set()
    
    async def stud_ch_upl_type_file(self, message: types.Message, state: FSMContext):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
        data = await state.get_data()
        if message.text == '⬅ Назад':
            choice_coll = data['choice_coll']
            await state.update_data(choice_coll=choice_coll)
            files = self.db_prov.get_files(data['obj_id'],data['coll_list'][data['choice_coll']]['_id'])
            await state.update_data(files=files)
            for name in files:
                keyboard.add(name)
            keyboard.add('Загрузить файл')
            keyboard.add('⬅ Назад','🏠 На главную')
            await message.answer(f'Гл.меню/документы/{choice_coll}:', reply_markup=keyboard)
            await self.StudStates.stud_choice_type.set()
        elif message.text == '🏠 На главную':
            for name in ['📝 Документы', '🔏 Личные данные']:
                keyboard.add(name)
            await message.answer('Главное меню:', reply_markup=keyboard)
            await self.StudStates.stud_menu.set()
        elif message.text in data['types_f'].keys():
            choice_type = message.text
            await state.update_data(choice_type=choice_type)
            keyboard.add('⬅ Назад','🏠 На главную')
            date_ = datetime.today()
            date_ = date_.strftime("%d%m%Y")
            fio = data['stud_info']['l_name']+data['stud_info']['f_name'][:1]+data['stud_info']['m_name'][:1]
            fio = translit(fio, 'ru', reversed=True)
            file_name = f"{data['types_f'][choice_type]['prefix']}NN_{data['coll_list'][data['choice_coll']]['nickname']}_{fio}_{date_}.pdf"
            await message.answer(f'Загрузите файл c именем: \n\n<i><b>{file_name}\n\n</b></i>где NN - порядковый номер работы', reply_markup=keyboard, parse_mode=types.ParseMode.HTML)
            await self.StudStates.stud_upload_file.set()
    
    # Главное меню/Документы/[Файл]
    async def stud_upload_file(self, message: types.Message, state: FSMContext):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
        data = await state.get_data()
        if message.text=='⬅ Назад':
            types_f = self.db_prov.get_types()
            await state.update_data(types_f=types_f)
            for name in types_f:
                keyboard.add(name)
            keyboard.add('⬅ Назад','🏠 На главную')
            await message.answer('Выберите тип работы: ', reply_markup=keyboard)
            await self.StudStates.stud_ch_upl_type_file.set()
        elif message.text == '🏠 На главную':
            for name in ['📝 Документы', '🔏 Личные данные']:
                keyboard.add(name)
            await message.answer('Главное меню:', reply_markup=keyboard)
            await self.StudStates.stud_menu.set()
        elif message.document:
            doc_ = await message.document.get_file()
            a = await message.answer('Идет проверка...')
            date_t = datetime.today()
            date_ = date_t.strftime("%d%m%Y")
            fio = data['stud_info']['l_name'] + data['stud_info']['f_name'][:1] + data['stud_info']['m_name'][:1]
            fio = translit(fio, 'ru', reversed=True)
            regexp = fr"\b{data['types_f'][data['choice_type']]['prefix']}\d*_{data['coll_list'][data['choice_coll']]['nickname']}_{fio}_{date_}.pdf\b"
            if re.fullmatch(regexp, message.document.file_name):
                if data['choice_type'] in data['files'].keys():
                    list_files = data['files'][data['choice_type']]
                else:
                    list_files = {}
                if self.db_prov.check_free_file_name(message.document.file_name, list_files):
                    id_ = self.db_prov.add_file(data['coll_list'][data['choice_coll']]['_id'],
                                     data['obj_id'],
                                     data['coll_list'][data['choice_coll']]['owner_id']['_id'],
                                     date_t,
                                     data['types_f'][data['choice_type']]['_id'],
                                     message.document.file_name)
                    if id_:
                        file_path = self.config.HOME_PATH + f'\\unchecked_files\\{id_}.pdf'
                        await doc_.download(destination_file=file_path)
                        key = self.db_prov.get_key(data['obj_id'])
                        if key:
                            if await self.cert_helper.check_valid_cert(file_path):
                                if key in self.cert_helper.get_pub_key_pdf(file_path):
                                    await message.answer('✅ Файл успешно загружен!')
                                    files = self.db_prov.get_files(data['obj_id'],data['coll_list'][data['choice_coll']]['_id'])
                                    await state.update_data(files=files)
                                else:
                                    self.db_prov.del_file_by_id(id_)
                                    await message.answer('🚫 Неверная подпись!')
                            else:
                                self.db_prov.del_file_by_id(id_)
                                await message.answer('🚫 Подпись не действительна!')
                        else:
                            await message.answer('‼ Для начала добавьте ключ!')
                            self.db_prov.del_file_by_id(id_)
                    else:
                        await message.answer('🚫 Ошибка загрузки файла!')
                else:
                    await message.answer('‼ Имя файла занято!')
            else:
                await message.answer('🚫 Неверное имя файла!')
            await self.bot.delete_message(a.chat.id, a.message_id)
    
    # Главное меню/🔏 Личные данные
    async def stud_pers_data(self, message: types.Message, state: FSMContext):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
        data = await state.get_data()
        if message.text == '⬅ Назад':
            for name in ['📝 Документы', '🔏 Личные данные']:
                keyboard.add(name)
            await message.answer('Главное меню:', reply_markup=keyboard)
            await self.StudStates.stud_menu.set()
        elif message.text == '♻ Сменить подпись':
            keyboard.add('⬅ Назад','🏠 На главную')
            await message.answer('❕❕❕ Загрузите сертификат в формате .fdf или пришлите публичный ключ сертификата.', reply_markup=keyboard)
            await self.StudStates.stud_pers_data_ch_srt.set()
    
    # Главное меню/🔏 Личные данные/Смена подписи
    async def stud_pers_data_ch_srt(self, message: types.Message, state: FSMContext):
        data = await state.get_data()
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
        if message.text == '⬅ Назад':
            stud_info = self.db_prov.get_stud_info(data['obj_id'])
            await state.update_data(stud_info=stud_info)
            for name in ['♻ Сменить подпись', '⬅ Назад']:
                keyboard.add(name)
            key = self.db_prov.get_key(data['obj_id'])
            if not key:
                key = '🤷‍♂ Не установлен!'
            await message.answer(
                f'Фамилия: {stud_info["l_name"]} \nИмя: {stud_info["f_name"]} \nОтчество: {stud_info["m_name"]} \nTelegram-id: {stud_info["tg_id"]} \nКлюч подписи: \n\n{key} ',
                reply_markup=keyboard)
            await self.StudStates.stud_pers_data.set()
        elif message.text == '🏠 На главную':
            for name in ['📝 Документы', '🔏 Личные данные']:
                keyboard.add(name)
            await message.answer('Главное меню:', reply_markup=keyboard)
            await self.StudStates.stud_menu.set()
        elif message.document:
            doc_ = await message.document.get_file()
            await doc_.download()
            pdf_cert = self.cert_helper.get_pub_key_fdf(doc_['file_path'])
            if pdf_cert:
                pdf_cert = pdf_cert.replace(' ', '')
                key = self.db_prov.get_key(data['obj_id'])
                if (pdf_cert != key) or (not key):
                    self.db_prov.change_stud_key(data['obj_id'], pdf_cert)
                    await message.answer('✅ Ключ изменен!')
                else:
                    await message.answer('❕❔ Ключ совпадает с настоящим!')
            else:
                await message.answer('❌ Неверный сертификат!')
            if os.path.isfile(doc_['file_path']):
                os.remove(doc_['file_path'])
        elif message.text:
            sert = message.text
            sert = sert.replace(' ','')
            pos = sert.find('06092A864886F70D010101')
            if pos != -1:
                user_key = self.db_prov.get_key(data['obj_id'])
                if (sert != user_key) or (not user_key):
                    if self.db_prov.add_pub_key(sert, data['obj_id'], 'student'):
                        await message.answer('✅ Ключ изменен!')
                    else:
                        await message.answer('❌ Ошибка при добавлении/изменении ключа!')
                else:
                    await message.answer('❕❔ Ключ совпадает с настоящим!')
            else:
                await message.answer('❌ Неподходящий формат ключа!')


    def register_handlers_student(self, dp: Dispatcher):
        dp.register_message_handler(self.stud_menu, state=self.StudStates.stud_menu)
        dp.register_message_handler(self.stud_doc, state=self.StudStates.stud_doc)
        dp.register_message_handler(self.stud_choice_type, state=self.StudStates.stud_choice_type)
        dp.register_message_handler(self.stud_upload_file,content_types=[types.ContentType.ANY], state=self.StudStates.stud_upload_file)
        dp.register_message_handler(self.stud_ch_upl_type_file, state=self.StudStates.stud_ch_upl_type_file)
        dp.register_message_handler(self.stud_pers_data, state=self.StudStates.stud_pers_data)
        dp.register_message_handler(self.stud_pers_data_ch_srt,content_types=[types.ContentType.ANY], state=self.StudStates.stud_pers_data_ch_srt)
        dp.register_message_handler(self.stud_file_list, state=self.StudStates.stud_file_list)
        dp.register_message_handler(self.stud_file_update,content_types=[types.ContentType.ANY], state=self.StudStates.stud_file_update)