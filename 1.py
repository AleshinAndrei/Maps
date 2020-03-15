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


response = None
coords = list(map(float, input("Введите координаты в формате 'долгота,широта':  ").split(",")))
spn = float(input("Введите масштаб  ").strip())

# Инициализируем pygame
pygame.init()
screen = pygame.display.set_mode((600, 450))
ex = ''
q = 'sat'
f1 = pygame.font.Font(None, 25)
text1 = f1.render('Спутник', 1, (180, 0, 0))
text2 = f1.render('Карта', 1, (0, 180, 0))
text3 = f1.render('Гибрид', 1, (0, 180, 0))
screen.blit(text1, (0, 5))
screen.blit(text2, (70, 5))
screen.blit(text3, (125, 5))
text4 = f1.render('Найти', 1, (250, 250, 0), (0, 0, 0))
screen.blit(text4, (0, 30))

# Рисуем картинку, загружаемую из только что созданного файла.
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                coords[1] += spn
            elif event.key == pygame.K_DOWN:
                coords[1] -= spn
            elif event.key == pygame.K_RIGHT:
                coords[0] += spn
            elif event.key == pygame.K_LEFT:
                coords[0] -= spn
            elif event.key == pygame.K_PAGEDOWN:
                if spn - 5 >= 0:
                    spn -= 5
            elif event.key == pygame.K_PAGEUP:
                if spn + 5 < 95:
                    spn += 5

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
    if ex != '' and ex.is_clicked:
        find = ex.text
        ex.close()
        ex = ''
        form_map_request(find)

    map_request = f'https://static-maps.yandex.ru/1.x/?ll=' \
                  f'{",".join(map(str, coords))}&' \
                  f'spn={",".join([str(spn)] * 2)}&l={q}'
    response = requests.get(map_request)
    if not response:
        print()
        # print(spn)
        print("Ошибка выполнения запроса:")
        print(map_request)
        print("Http статус:", response.status_code, "(", response.reason, ")")
    else:
        # Запишем полученное изображение в файл.
        map_file = "map.png"
        with open(map_file, "wb") as file:
            file.write(response.content)
        screen.fill((0, 0, 0))
        screen.blit(pygame.image.load(map_file), (0, 0))
        screen.blit(text1, (0, 5))
        screen.blit(text2, (70, 5))
        screen.blit(text3, (125, 5))
        screen.blit(text4, (0, 30))
        pygame.display.flip()

pygame.quit()

# Удаляем за собой файл с изображением.
os.remove(map_file)
