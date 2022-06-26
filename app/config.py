
import configparser
from dataclasses import dataclass

@dataclass
class Config:
    HOME_PATH: str
    PATH_CLOUD: str
    ADMINS: list
    EMAIL_CLOUD: str
    PASS: str
    HOST: str
    PORT: int
    DB_NAME: str
    TOKEN: str


def load_config(path: str):
    config = configparser.ConfigParser()
    config.read(path,encoding='utf-8')
    conf = config['DEFAULT']
    return Config(
        HOME_PATH = conf['HOME_PATH'],
        PATH_CLOUD= conf['PATH_CLOUD'],
        ADMINS = list(conf['ADMINS'].split(',')),
        EMAIL_CLOUD= conf['EMAIL_CLOUD'],
        PASS = conf['PASS'],
        HOST = conf['HOST'],
        PORT= int(conf['PORT']),
        DB_NAME = conf['DB_NAME'],
        TOKEN = conf['TOKEN']
    )


