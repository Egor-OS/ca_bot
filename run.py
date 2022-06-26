import asyncio
import os
import getpass
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
from aiogram import Dispatcher, Bot
from aiogram.contrib.fsm_storage.mongo import MongoStorage
from app import db_provider,cloud_provider
from app import config as cf
from app.handlers import admin, registration, student,teacher,start


async def main():
    config = cf.load_config('conf.ini')
    bot = ''
    cloud_mail = ''

    try:
        bot = Bot(token=config.TOKEN)
        print("[УСПЕХ] Создан экзепляр класса бота")
    except:
        print("[ОШИБКА] Невалидный токен")
        os.abort()

    db_prov = db_provider.DB_provider(config.HOST, config.PORT, config.DB_NAME, config)

    ms = MongoStorage(db_name=config.DB_NAME, port=config.PORT, host=config.HOST)
    dp = Dispatcher(bot, storage=ms)

    try:
        if config.EMAIL_CLOUD == '':
            config.EMAIL_CLOUD = input('Введите e-mail: ')
            if config.EMAIL_CLOUD != '':
                config.PASS = getpass.getpass('Пароль: ')
        cloud_mail = cloud_provider.CloudMail(db_prov, config.EMAIL_CLOUD, config.PASS, config)
        print("[УСПЕХ] Соединение с облаком установлено")
    except Exception as e:
        print("[ОШИБКА] Не удалось подключиться к облаку")
        os.abort()

    StartB = start.Start_Bot(db_prov,bot, config)
    Reg = registration.Registration(db_prov,bot)
    Adm = admin.AdminPanel(db_prov, bot, cloud_mail)
    Std = student.StudentPanel(db_prov, bot, Adm.AdminStates, config)
    Tc = teacher.TeacherPanel(db_prov, bot,cloud_mail,  Adm.AdminStates, config)

    StartB.StudStates = Std.StudStates
    StartB.RegStates = Reg.RegStates
    StartB.AdminStates = Adm.AdminStates
    StartB.TeachStates = Tc.TeachStates
    Adm.TeachStates = Tc.TeachStates
    Adm.StudStates = Std.StudStates

    StartB.register_handlers_start(dp)
    Reg.register_handlers_reg(dp)
    Adm.register_handlers_admin(dp)
    Std.register_handlers_student(dp)
    Tc.register_handlers_teacher(dp)

    await StartB.set_commands()
    print('Бот запущен...')
    await dp.start_polling()


if __name__ == '__main__':
    asyncio.run(main())