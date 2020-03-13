import os
import sys
import pygame
import requests

map_file = "map.png"
coords = list(map(float, input("Введите координаты в формате 'долгота,широта':  ").split(",")))
z = int(input("Введите масштаб от 0 до 17, где 0 - это весь земной шар:  "))

pygame.init()
screen = pygame.display.set_mode((450, 450))

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

    if change:
        map_api_server = 'https://static-maps.yandex.ru/1.x/'
        params = {
            "l": "sat",
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

        with open(map_file, "wb") as file:
            file.write(response.content)

        screen.blit(pygame.image.load(map_file), (0, 0))
        pygame.display.flip()

    change = False

pygame.quit()
os.remove(map_file)
