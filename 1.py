import os
import sys
import pygame
import requests
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget


def form_map_request(find):
    geocoder_request = f"http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&" \
                       f"geocode={find}&format=json"
    # Выполняем запрос.
    response = requests.get(geocoder_request)
    if response:
        # Преобразуем ответ в json-объект
        json_response = response.json()

        # Получаем первый топоним из ответа геокодера.
        # Согласно описанию ответа, он находится по следующему пути:
        toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        # Полный адрес топонима:
        toponym_address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]
        # Координаты центра топонима:
        toponym_coodrinates = toponym["Point"]["pos"]

        # Печатаем извлечённые из ответа поля:
        coord = toponym_coodrinates.split(' ')
        coord = list(map(float, coord))
        global coords
        coords = coord
    else:
        print("Ошибка выполнения запроса:")
        print(geocoder_request)
        print("Http статус:", response.status_code, "(", response.reason, ")")


class MyWidget(QMainWindow, QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('search.ui', self)
        self.text = ''
        self.is_clicked = False
        self.btn_search.clicked.connect(self.search)

    def search(self):
        self.is_clicked = True
        self.text = self.line.text()


map_file = "map.png"
coords = list(map(float, input("Введите координаты в формате 'долгота,широта':  ").split(",")))
z = int(input("Введите масштаб от 0 до 17, где 0 - это весь земной шар:  "))

pygame.init()
screen = pygame.display.set_mode((450, 450))

ex = ''
q = 'sat'
f1 = pygame.font.Font(None, 25)
text1 = f1.render('Спутник', 1, (180, 0, 0))
text2 = f1.render('Карта', 1, (0, 180, 0))
text3 = f1.render('Гибрид', 1, (0, 180, 0))
text4 = f1.render('Найти', 1, (250, 250, 0), (0, 0, 0))

running = True
change = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                coords[1] = (coords[1] + 180.0 / (2 ** z) + 90) % 180 - 90
            elif event.key == pygame.K_DOWN:
                coords[1] = (coords[1] - 180.0 / (2 ** z) + 90) % 180 - 90
            elif event.key == pygame.K_RIGHT:
                coords[0] = (coords[0] + 360.0 / (2 ** z) + 180) % 360 - 180
            elif event.key == pygame.K_LEFT:
                coords[0] = (coords[0] - 360.0 / (2 ** z) + 180) % 360 - 180
            if event.key == pygame.K_PAGEDOWN:
                # у меня на компе на этих кнопках написано PgUp и PgDn, но pygame их неправильно определяет
                if z > 0:
                    z -= 1
            elif event.key == pygame.K_PAGEUP:
                if z < 17:
                    z += 1
            change = True

        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            if pos[0] <= 65 and pos[1] <= 23:
                q = 'sat'
                text1 = f1.render('Спутник', 1, (180, 0, 0))
                text2 = f1.render('Карта', 1, (0, 180, 0))
                text3 = f1.render('Гибрид', 1, (0, 180, 0))
            elif 70 <= pos[0] <= 120 and pos[1] <= 23:
                q = 'map'
                text1 = f1.render('Спутник', 1, (0, 180, 0))
                text2 = f1.render('Карта', 1, (180, 0, 0))
                text3 = f1.render('Гибрид', 1, (0, 180, 0))
            elif 123 <= pos[0] <= 190 and pos[1] <= 23:
                q = 'sat,skl'
                text1 = f1.render('Спутник', 1, (0, 180, 0))
                text2 = f1.render('Карта', 1, (0, 180, 0))
                text3 = f1.render('Гибрид', 1, (180, 0, 0))
            elif pos[0] <= 50 and 30 <= pos[1] <= 50:
                app = QApplication(sys.argv)
                ex = MyWidget()
                ex.show()
            change = True

    if ex != '' and ex.is_clicked:
        find = ex.text
        ex.close()
        ex = ''
        form_map_request(find)
        change = True

    if change:
        map_api_server = 'https://static-maps.yandex.ru/1.x/'
        params = {
            "l": q,
            "z": z,
            "ll": ','.join(map(str, coords)),
            "size": "450,450",
        }
        response = requests.get(map_api_server, params=params)
        if not response:
            print("Ошибка выполнения запроса:")
            print(params)
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)

        else:
            with open(map_file, "wb") as file:
                file.write(response.content)

            screen.blit(pygame.image.load(map_file), (0, 0))
            screen.blit(text1, (0, 5))
            screen.blit(text2, (70, 5))
            screen.blit(text3, (125, 5))
            screen.blit(text4, (0, 30))
            pygame.display.flip()

    change = False

pygame.quit()
os.remove(map_file)
