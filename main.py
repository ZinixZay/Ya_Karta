import sys

from enum import Enum
import math

from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtWidgets import (QApplication, QMainWindow)
from PyQt5 import QtGui, QtCore
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtNetwork import *
from core import geocoder_service
from screens.main_screen import Ui_MainWindow
from core import organization_service


class ApiCategory(Enum):
    STATIC_MAP = 0
    GEOCODER = 1
    ORGANIZATION = 2


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.initUI()

    def initUI(self):
        self.setFixedSize(1080, 720)
        self.setWindowFlags(Qt.FramelessWindowHint)  # Создает окно без полей.
        self.setWindowTitle('YaKarta')
        self.setWindowIcon(QtGui.QIcon('screens/metka.png'))

        with open('core/style.css', 'r') as css_style:
            self.style = css_style.read()
        self.setStyleSheet(self.style)

        self.map_api_server = "https://static-maps.yandex.ru/1.x/"
        self.latt, self.long = 40.984110, 56.985042
        self.spn = [0.002, 0.002]
        self.l = 'map'
        self.points = list()
        self.search_address = 'Типографская 25/55'

        self.map_view_switch.clear()
        self.map_view_switch.addItems(["Схема", "Спутник", "Гибрид"])
        self.map_view_switch.currentTextChanged.connect(self.view_change)
        self.search_button.clicked.connect(self.search_place)
        self.reset_button.clicked.connect(self.reset_result)
        self.collapse_btn.clicked.connect(lambda: self.showMinimized())
        self.close_btn.clicked.connect(lambda: self.close())

        self.mail_index_enabled = False
        self.mail_button.setText("Приписка почтового индекса: ВКЛ")
        self.mail_button.clicked.connect(self.mail_index_enable_disable)

        self.old_pos = None
        self.is_organization_search = False
        self.draw_map(self.search_address)

    # вызывается при нажатии кнопки мыши
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.pos()

    # вызывается при отпускании кнопки мыши
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = None

    # вызывается всякий раз, когда мышь перемещается
    def mouseMoveEvent(self, event):
        if not self.old_pos:
            return
        delta = event.pos() - self.old_pos
        self.move(self.pos() + delta)

    def draw_map(self, request=None, move=True):
        if request is not None:
            if self.mail_index_enabled:
                url = QUrl(self.parse_dict_to_url(ApiCategory.STATIC_MAP, request, True, True, move=move))
            else:
                url = QUrl(self.parse_dict_to_url(ApiCategory.STATIC_MAP, request, True, move=move))
        else:
            url = QUrl(self.parse_dict_to_url(ApiCategory.STATIC_MAP, request))
        req = QNetworkRequest(url)
        self.nam = QNetworkAccessManager()
        self.nam.finished.connect(self.handle_response)
        self.nam.get(req)

    def reset_result(self):
        self.points.clear()
        self.draw_map()
        self.address.setText('Полный адрес объекта')

    def parse_dict_to_url(self, category: ApiCategory, request, search=False, mail_ind=False, move=True) -> str:
        if category == ApiCategory.STATIC_MAP:
            if search:
                coords = [float(i) for i in geocoder_service.get_coords(request).split()]
                if not self.is_organization_search:
                    address = geocoder_service.get_full_address(request, mail_ind)
                else:
                    address = organization_service.get_full_name(request, mail_ind)
                self.address.setText(address)
                self.points.clear()
                self.points.append(coords)
                if move:
                    self.latt, self.long = coords
            url = self.map_api_server + '?'
            map_params = {'ll': f'{self.latt},{self.long}',
                          'spn': ",".join(map(str, self.spn)),
                          'l': self.l}
            for param, value in map_params.items():
                url += f'{param}={value}&'
            if self.points:
                url += 'pt='
                for point in self.points:
                    url += f'{point[0]},{point[1]},pm2rdm~'
            url = url[:-1]
        return url

    def handle_response(self, reply):
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

    def eventFilter(self, a0, a1) -> bool:
        if a1.type() == QtCore.QEvent.Type.KeyPress:  # проверка на то, что a1 - именно нажатие на клавиши
            key_event = QtGui.QKeyEvent(a1)  # чтобы проверить нажатую кнопку, обращаться именно к этой переменной
            if key_event.key() in [QtCore.Qt.Key.Key_Up, QtCore.Qt.Key.Key_Down,
                                   QtCore.Qt.Key.Key_Left, QtCore.Qt.Key.Key_Right,
                                   QtCore.Qt.Key.Key_PageUp, QtCore.Qt.Key.Key_PageDown]:  # проверка на то, что были
                # нажаты кнопки перемещений

                # проверки на конкретные клавииш
                if key_event.key() == QtCore.Qt.Key.Key_PageUp:
                    if self.spn[0] < 25:
                        self.spn[0] += self.spn[0]
                        self.spn[1] += self.spn[0]
                if key_event.key() == QtCore.Qt.Key.Key_PageDown:
                    if self.spn[0] > 0.001:
                        self.spn[0] = self.spn[0] / 2
                        self.spn[1] = self.spn[0] / 2
                if key_event.key() == QtCore.Qt.Key.Key_Up:
                    self.long += self.spn[1]
                if key_event.key() == QtCore.Qt.Key.Key_Down:
                    self.long -= self.spn[1]
                if key_event.key() == QtCore.Qt.Key.Key_Left:
                    self.latt -= self.spn[0] * 2
                if key_event.key() == QtCore.Qt.Key.Key_Right:
                    self.latt += self.spn[0] * 2
                self.draw_map()
                return True

        elif a1.type() == QtCore.QEvent.Type.MouseButtonPress and a0 == self.map_label:
            if a1.button() == QtCore.Qt.MouseButton.LeftButton:
                self.is_organization_search = False
                click_long, click_latt = self.get_click_coords((a1.pos().x(), a1.pos().y()))

                self.search_address = geocoder_service.get_address((click_long, click_latt))

                self.draw_map(self.search_address, move=False)

                return True  # обязательно возвращать True после того, как нужный евент произошел
            if a1.button() == QtCore.Qt.MouseButton.RightButton:
                self.is_organization_search = True
                click_long, click_latt = self.get_click_coords((a1.pos().x(), a1.pos().y()))
                organisation_name = organization_service.get_organization((click_long, click_latt),
                                                                          self.get_coords_from_metres((50, 50)))
                if organisation_name:
                    self.draw_map(organisation_name, move=False)
                else:
                    self.reset_result()
                return True
        return False

    def view_change(self):
        l_param_values = {"Схема": "map",
                          "Спутник": "sat",
                          "Гибрид": "sat,skl"}
        self.l = l_param_values[self.sender().currentText()]
        self.draw_map()

    def search_place(self):
        self.is_organization_search = False
        if self.search_bar.text():
            self.draw_map(self.search_bar.text())

    def mail_index_enable_disable(self):
        if self.mail_button.text() == "Приписка почтового индекса: ВКЛ":
            self.mail_button.setText("Приписка почтового индекса: ВЫКЛ")
            self.mail_index_enabled = True
        elif self.mail_button.text() == "Приписка почтового индекса: ВЫКЛ":
            self.mail_button.setText("Приписка почтового индекса: ВКЛ")
            self.mail_index_enabled = False
        if self.search_bar.text():
            self.search_place()
        else:
            self.draw_map(self.search_address)

    def get_coords_from_metres(self, metres: tuple[int, int]) -> tuple[float, float]:
        earth_r = 6378137
        metre_per_long_degree = 111300
        metre_per_latt_degree = math.radians(1) * earth_r * math.cos(math.radians(self.long))
        return metres[0] / metre_per_long_degree, metres[1] / metre_per_latt_degree

    def get_click_coords(self, mouse_pos: tuple[int, int]) -> tuple[float, float]:
        width = self.map_label.width()
        height = self.map_label.height()

        longitude_per_pixel = self.spn[0] / (width / 2)
        latitude_per_pixel = self.spn[1] / (height / 2)

        d_x_pixels = mouse_pos[0] - width / 2
        d_y_pixels = - (mouse_pos[1] - height / 2)

        click_latt = self.latt + d_x_pixels * latitude_per_pixel
        click_long = self.long + d_y_pixels * longitude_per_pixel
        return click_long, click_latt


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    app.installEventFilter(main_window)
    sys.exit(app.exec_())
