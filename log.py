from enum import Enum
from datetime import datetime


class Tag(Enum):
    INFO = 'INFO'
    ERROR = 'ERROR'
    DEBUG = 'DEBUG'


class Log:
    def __init__(self, filename='log.txt'):
        self.filename = filename

    def log(self, tag, message):
        with open(self.filename, 'a') as file:
            file.write(f'{datetime.now()} [{tag.value}] {message}\n')
