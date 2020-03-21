import os
import sys
import pygame
import requests
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QWidget


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
        # Координаты центра топонима:
        toponym_coodrinates = toponym["Point"]["pos"]

        # Печатаем извлечённые из ответа поля:
        coord = list(map(float, toponym_coodrinates.split(' ')))
        global coords, marker_coords, toponym_address
        # помнишь, что нам говорили про глобальныепеременные? Не надо так со мной обращаться,
        # ты этот код не одна пишешь
        # Полный адрес топонима:
        toponym_address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]
        coords = coord[:]
        marker_coords = coord[:]
        
    else:
        print("Ошибка выполнения запроса:")
        print(geocoder_request)
        print("Http статус:", response.status_code, "(", response.reason, ")")


class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('search.ui', self)
        self.text = ''
        self.is_clicked = False
        self.btn_search.clicked.connect(self.search)

    def search(self):
        self.text = self.line.text()
        self.is_clicked = True


map_file = "map.png"
coords = list(map(float, input("Введите координаты в формате 'долгота,широта':  ").split(",")))[:]
z = int(input("Введите масштаб от 0 до 17, где 0 - это весь земной шар:  "))

pygame.init()
screen = pygame.display.set_mode((450, 450))

ex = None
marker = False
display_address = False
toponym_address = ""
marker_coords = coords[:]
map_type = 'sat'
selected_map = 0
font = pygame.font.Font(None, 25)
text1 = font.render('Спутник', 1, (180, 0, 0))
text2 = font.render('Карта', 1, (0, 180, 0))
text3 = font.render('Гибрид', 1, (0, 180, 0))
text4 = font.render('Найти', 1, (250, 250, 0), (0, 0, 0))
text5 = font.render('Сброс поискового результата', 1, (200, 200, 0), (0, 0, 0))
text6 = font.render(toponym_address, 1, (250, 250, 0), (0, 0, 0))

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
            if event.key in {pygame.K_PAGEDOWN, pygame.K_KP3}:
                # у меня на компе на этих кнопках написано PgUp и PgDn, но pygame их неправильно определяет
                if z > 0:
                    z -= 1
            elif event.key in {pygame.K_PAGEUP, pygame.K_KP9}:
                if z < 17:
                    z += 1
            change = True

        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            if 0 <= pos[0] <= 65 and 0 <= pos[1] <= 23:
                map_type = 'sat'
                selected_map = 0
            elif 70 <= pos[0] <= 120 and pos[1] <= 23:
                map_type = 'map'
                selected_map = 1
            elif 123 <= pos[0] <= 190 and pos[1] <= 23:
                map_type = 'sat,skl'
                selected_map = 2
            elif pos[0] <= 50 and 30 <= pos[1] <= 50:
                app = QApplication(sys.argv)
                ex = MyWidget()
                ex.show()
            elif 60 <= pos[0] <= 305 and 30 <= pos[1] <= 50:
                marker = False
                display_address = False
            text1 = font.render('Спутник', 1,
                                (180, 0, 0) if selected_map == 0 else (0, 180, 0))
            text2 = font.render('Карта', 1,
                                (180, 0, 0) if selected_map == 1 else (0, 180, 0))
            text3 = font.render('Гибрид', 1,
                                (180, 0, 0) if selected_map == 2 else (0, 180, 0))
            change = True

    if ex is not None and ex.is_clicked:
        find = ex.text
        ex.close()
        ex = None
        form_map_request(find)
        change = True
        marker = True
        display_address = True
        text6 = font.render(toponym_address, 1, (250, 250, 0), (0, 0, 0))

    if change:
        map_api_server = 'https://static-maps.yandex.ru/1.x/'
        if marker:
            pt = ','.join(map(str, marker_coords)) + ',pm2dbl'
            params = {
                "l": map_type,
                "z": z,
                "ll": ','.join(map(str, coords)),
                "pt": pt,
                "size": "450,450",
            }
        else:
            params = {
                "l": map_type,
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
            screen.blit(text5, (60, 30))
            if display_address:
                screen.blit(text6, (0, 85))
            pygame.display.flip()

    change = False

pygame.quit()
os.remove(map_file)
