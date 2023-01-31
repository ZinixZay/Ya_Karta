import os
import sys

from io import BytesIO
from enum import Enum
from PyQt5.QtWidgets import (QApplication, QMainWindow)
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
        self.map_params = {
            "ll": "40.984110,56.985042",
            "l": "map",
            "spn": "0.002,0.002"
        }
        url = QUrl(self.parse_dict_to_url(ApiCategory.STATIC_MAP))
        req = QNetworkRequest(url)
        self.nam = QNetworkAccessManager()
        self.nam.finished.connect(self.handleResponse)
        self.nam.get(req)

    def parse_dict_to_url(self, category: ApiCategory) -> str:
        if category == ApiCategory.STATIC_MAP:
            url = self.map_api_server + '?'
            for param, value in self.map_params.items():
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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
