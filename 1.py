import os
import sys
import pygame
import requests

map_file = "map.png"
coords = list(map(float, input("Введите координаты в формате 'долгота,широта':  ").split(",")))
z = int(input("Введите масштаб от 0 до 17, где 0 - это весь земной шар:  "))

pygame.init()
screen = pygame.display.set_mode((450, 450))

q = 'sat'
f1 = pygame.font.Font(None, 25)
text1 = f1.render('Спутник', 1, (180, 0, 0))
text2 = f1.render('Карта', 1, (0, 180, 0))
text3 = f1.render('Гибрид', 1, (0, 180, 0))

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
            # может лучше делать через спрайты? Нет так нет, как хочешь
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
            pygame.display.flip()

    change = False

pygame.quit()
os.remove(map_file)
