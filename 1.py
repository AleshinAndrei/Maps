import os
import sys
import pygame
import requests

response = None
coords = list(map(float, input("Введите координаты в формате 'долгота,широта':  ").split(",")))
spn = float(input("Введите масштаб  ").strip())

# Инициализируем pygame
pygame.init()
screen = pygame.display.set_mode((600, 450))

q = 'sat'
f1 = pygame.font.Font(None, 25)
text1 = f1.render('Спутник', 1, (180, 0, 0))
text2 = f1.render('Карта', 1, (0, 180, 0))
text3 = f1.render('Гибрид', 1, (0, 180, 0))
screen.blit(text1, (0, 5))
screen.blit(text2, (0, 25))
screen.blit(text3, (0, 45))

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

    map_request = f'https://static-maps.yandex.ru/1.x/?ll=' \
                  f'{",".join(map(str, coords))}&' \
                  f'spn={",".join([str(spn)] * 2)}&l={q}'
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
        screen.blit(text1, (0, 5))
        screen.blit(text2, (70, 5))
        screen.blit(text3, (125, 5))
        pygame.display.flip()

pygame.quit()

# Удаляем за собой файл с изображением.
os.remove(map_file)
