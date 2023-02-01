import os
import sys

from io import BytesIO
from enum import Enum
from PyQt5.QtWidgets import (QApplication, QMainWindow)
from PyQt5 import QtGui, QtCore
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtNetwork import *
from PyQt5.QtCore import QUrl
from PyQt5 import uic
from dotenv import load_dotenv
from io import BytesIO
from PIL import Image
from PIL.ImageQt import ImageQt

load_dotenv()


class ApiCategory(Enum):
    STATIC_MAP = 0
    GEOCODER = 1
    ORGANIZATION = 2


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('screens/main.ui', self)
        self.initUI()

    def initUI(self):
        # "self.api_key": os.getenv('API_KEY') - получить апи
        self.setFixedSize(1080, 720)

        self.map_api_server = "https://static-maps.yandex.ru/1.x/"
        self.latt, self.long = 40.984110, 56.985042
        self.spn = (0.002, 0.002)
        self.l = 'map'

        self.draw_map()

    def draw_map(self):
        url = QUrl(self.parse_dict_to_url(ApiCategory.STATIC_MAP))
        req = QNetworkRequest(url)
        self.nam = QNetworkAccessManager()
        self.nam.finished.connect(self.handleResponse)
        self.nam.get(req)

    def parse_dict_to_url(self, category: ApiCategory) -> str:
        if category == ApiCategory.STATIC_MAP:
            url = self.map_api_server + '?'
            map_params = {'ll': f'{self.latt},{self.long}',
                          'spn': ",".join(map(str, self.spn)),
                          'l': self.l}
            for param, value in map_params.items():
                url += f'{param}={value}'
                url += '&'
            url = url[:-1]
        return url

    def handleResponse(self, reply):
        er = reply.error()
        if er == QNetworkReply.NoError:
            bytes_string = reply.readAll()
            img = QImage()
            img.loadFromData(bytes_string)
            pixmap = QPixmap.fromImage(img)
            pixmap = pixmap.scaled(self.map_label.size())
            self.map_label.setPixmap(pixmap)
        else:
            print('Error occured: ', er)
            print(reply.errorString())

    def eventFilter(self, a0: 'QObject', a1: 'QEvent') -> bool:
        if a1.type() == QtCore.QEvent.Type.KeyPress:  # проверка на то, что a1 - именно нажатие на клавиши
            key_event = QtGui.QKeyEvent(a1)  # чтобы проверить нажатую кнопку, обращаться именно к этой переменной
            if key_event.key() in [QtCore.Qt.Key.Key_Up, QtCore.Qt.Key.Key_Down,
                                   QtCore.Qt.Key.Key_Left, QtCore.Qt.Key.Key_Right]:  # проверка на то, что были
                                                                                      # нажаты кнопки перемещений

                # проверки на конкретные клавииш
                if key_event.key() == QtCore.Qt.Key.Key_Up:
                    self.long += 0.3 * self.spn[1]
                if key_event.key() == QtCore.Qt.Key.Key_Down:
                    self.long -= 0.3 * self.spn[1]
                if key_event.key() == QtCore.Qt.Key.Key_Left:
                    self.latt -= 0.3 * self.spn[0]
                if key_event.key() == QtCore.Qt.Key.Key_Right:
                    self.latt += 0.3 * self.spn[0]

                self.draw_map()
                return True  # обязательно возвращать True после того, как нужный евент произошел
        return False


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    app.installEventFilter(main_window)
    sys.exit(app.exec_())
