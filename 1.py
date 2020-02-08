import os
import sys
import pygame
import requests

response = None
coords = ''.join(input("Введите координаты в формате 'долгота,широта':  ").split()).split(',')
spn = ''.join(input("Введите масштаб через ',' без пробелов:  ").split()).split(',')
map_request = f'https://static-maps.yandex.ru/1.x/?ll={",".join(coords)}&spn={",".join(spn)}&l=sat'
response = requests.get(map_request)

if not response:
    print("Ошибка выполнения запроса:")
    print(map_request)
    print("Http статус:", response.status_code, "(", response.reason, ")")
    sys.exit(1)

# Запишем полученное изображение в файл.
map_file = "map.png"
with open(map_file, "wb") as file:
    file.write(response.content)

# Инициализируем pygame
pygame.init()
screen = pygame.display.set_mode((600, 450))
# Рисуем картинку, загружаемую из только что созданного файла.
screen.blit(pygame.image.load(map_file), (0, 0))
# Переключаем экран и ждем закрытия окна.
pygame.display.flip()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            response = None
            if event.key == 273:  # up
                coords[1] = str(float(coords[1]) + float(spn[1]))
            elif event.key == 274:  # down
                coords[1] = str(float(coords[1]) - float(spn[1]))
            elif event.key == 275:  # right
                coords[0] = str(float(coords[0]) + float(spn[0]))
            elif event.key == 276:  # left
                coords[0] = str(float(coords[0]) - float(spn[0]))
            map_request = f'https://static-maps.yandex.ru/1.x/?ll={",".join(coords)}&spn={",".join(spn)}&l=sat'
            response = requests.get(map_request)

            if response:
                map_file = "map.png"
                with open(map_file, "wb") as file:
                    file.write(response.content)
                screen.blit(pygame.image.load(map_file), (0, 0))
                pygame.display.flip()
pygame.quit()

# Удаляем за собой файл с изображением.
os.remove(map_file)
