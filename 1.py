import os
import sys
import pygame
import requests

response = None
coords = input("Введите координаты в формате 'долгота,широта':  ")
spn = int(input("Введите масштаб  ").strip())


# Инициализируем pygame
pygame.init()
screen = pygame.display.set_mode((600, 450))
# Рисуем картинку, загружаемую из только что созданного файла.
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key in {pygame.K_PAGEDOWN, pygame.K_PAGEUP} or response is None:
            if response:
                if event.key == pygame.K_PAGEDOWN:
                    if spn - 5 >= 0:
                        spn -= 5
                elif event.key == pygame.K_PAGEUP:
                    if spn + 5 < 95:
                        spn += 5

            map_request = f'https://static-maps.yandex.ru/1.x/?ll={coords}&spn={",".join([str(spn)] * 2)}&l=sat'
            response = requests.get(map_request)
            if not response:
                print()
                print(spn)
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
                pygame.display.flip()

pygame.quit()
# Удаляем за собой файл с изображением.
os.remove(map_file)
