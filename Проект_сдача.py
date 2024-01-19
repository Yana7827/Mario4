import pygame
import os
import sys
pygame.init()


fps = 60

WHITE = (255, 255, 255)
window_width = 500
window_height = 450
window_color = WHITE

def start_screen():

    fon1 = pygame.transform.scale(load_image('fon.jpg'), (500, 450))
    window.blit(fon1, (0, 0))

    x = True

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                x = False
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(fps)

def second_screen():
    global level
    all_levels = [['map.txt', 'map3.txt', 'map5.txt', 'map7.txt', 'map9.txt'], ['map2.txt', 'map4.txt', 'map6.txt', 'map8.txt', 'map10.txt']]
    fon1 = pygame.transform.scale(load_image('sky.png'), (500, 450))
    window.blit(fon1, (0, 0))

    x = '1'

    for i in range(5):
        for j in range(2):
            pygame.draw.rect(window, (0, 0, 0), (
            100 * i, 100 * j + 125, 100, 100), width=1)

            f1 = pygame.font.Font(None, 48)
            text1 = f1.render(x, True,
                              (180, 0, 0))
            window.blit(text1, (100 * i + 40, 100 * j + 160))
            x = str(int(x) + 1)

    run = True

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                y = (event.pos[0]) // 100
                x = (event.pos[1] - 125) // 100
                if y >= 5 or x < 0:
                    pass
                elif x >= 2 or y < 0:
                    print("None")
                else:
                    level = load_level(all_levels[x][y])
                    print((x, y))
                    run = False
        pygame.display.flip()
        clock.tick(fps)


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey != None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image

window = pygame.display.set_mode((window_width, window_height))
fon = pygame.transform.scale(load_image('sky.png'), (500, 450))
window.blit(fon, (0, 0))
pygame.display.set_caption("Bub - the game")

clock = pygame.time.Clock()
stone_fly = False


def load_level(filename):
    filename = "levels/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))



class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, velocity, *grps):
        super().__init__(*grps)
        self.image = load_image('mar.png')
        self.rect = self.image.get_rect()
        self.rect.topleft = (x - velocity, y - velocity)
        self.velocity = velocity
        self.on_ground = True
        self.xvel = 0
        self.yvel = 0

    def collide(self, xvel, yvel, obstacle_sprite):
        for p in pygame.sprite.spritecollide(self, obstacle_sprite, False):
            if obstacle_sprite == foe_sprites:
                pygame.sprite.spritecollide(self, obstacle_sprite, True)

            if xvel > 0:
                self.rect.right = p.rect.left
                if obstacle_sprite == foe_sprites:
                    life_line.update()

            if xvel < 0:
                self.rect.left = p.rect.right
                if obstacle_sprite == foe_sprites:
                    life_line.update()

            if yvel > 0:
                self.rect.bottom = p.rect.top
                self.on_ground = True
                self.yvel = 0
            if yvel < 0:
                self.rect.top = p.rect.bottom
                self.yvel = 0


    def update(self, obstacle_sprites):
        key = pygame.key.get_pressed()

        self.xvel = 0
        if key[pygame.K_LEFT]:
            self.xvel =- self.velocity
        if key[pygame.K_RIGHT]:
            self.xvel = self.velocity
        if self.on_ground:
            if key[pygame.K_UP]:
                self.on_ground = False
                self.yvel = -15
        else:
            self.yvel += 1

        self.rect.left += self.xvel
        self.collide(self.xvel, 0, obstacle_sprites)
        self.collide(self.xvel, 0, foe_sprites)


        self.rect.top += self.yvel
        self.on_ground = False
        self.collide(0, self.yvel, obstacle_sprites)
        self.collide(0, self.yvel, foe_sprites)

        self.rect.clamp_ip(pygame.display.get_surface().get_rect())
        if self.rect.bottom == pygame.display.get_surface().get_rect().bottom:
            self.on_ground = True

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, *grps):
        super().__init__(*grps)
        self.image = load_image('grass.png')
        self.rect = self.image.get_rect(center=(x, y))

    def update(self, a):
        pygame.sprite.spritecollide(self, stone_sprites, True)
        pygame.sprite.spritecollide(self, foe_sprites, True)

class Foe(pygame.sprite.Sprite):
    def __init__(self, x, y, *grps):
        super().__init__(*grps)
        self.image = pygame.transform.scale(load_image('foe1.png'), (50, 50))
        # self.x = x
        # self.y = y
        self.rect = self.image.get_rect(center=(x, y))
        self.width = 100

    def change_turn(self):
        if self.sight == 'back':
            self.sight = 'forward'
        elif self.sight == 'forward':
            self.sight = 'back'

    def update(self, x):
        if pygame.sprite.spritecollideany(self, player_sprite) == None and pygame.sprite.spritecollideany(hero, foe_sprites) == None:
            if self.width == 100:
                self.sight = 'back'
            elif self.width == 0:
                self.sight = 'forward'
            if self.sight == 'back':
                self.width -= 1
                self.rect.x -= 1

            elif self.sight == 'forward':
                self.width += 1
                self.rect.x += 1

        else:
            pygame.sprite.spritecollide(hero, foe_sprites, True)
            pygame.sprite.spritecollide(self, player_sprite, True)
            life_line.update()


class Stones(pygame.sprite.Sprite):
    def __init__(self, *grps):
        super().__init__(*grps)
        self.image = pygame.transform.scale(load_image('stone.png'), (20, 20))
        self.rect = self.image.get_rect(center=(hero.rect.center))
        # self.rect = self.image.get_rect(center=(0, 0))

    def update(self, stone_sprites):
        pygame.sprite.spritecollide(self, foe_sprites, True)
        self.rect.x += 7

class Life:
    def __init__(self, screen):
        self.lifex = 110
        self.screen = screen
        pygame.draw.line(self.screen, (0, 250, 0), (10, 20), (self.lifex, 20), width=10)

    def draw(self):
        pygame.draw.line(self.screen, (250, 0, 0), (10, 20), (110, 20), width=10)
        pygame.draw.line(self.screen, (0, 250, 0), (10, 20), (self.lifex, 20), width=10)

    def update(self):
        self.lifex -= 34


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - window_width // 2)


class Game(pygame.sprite.Sprite):
    image = load_image("gameover.png")

    def __init__(self, group):
        super().__init__(group)
        self.image = pygame.transform.scale(Game.image, (503, 450))
        self.rect = self.image.get_rect()
        self.rect.x = -500
        self.rect.y = 0
        self.v = 400
        self.forward = True

    def update(self, c):
        if self.rect.x >= -3:
            self.forward = False
        if self.forward:
            self.rect.x += self.v / c


all_sprites = pygame.sprite.Group()
player_sprite = pygame.sprite.Group()
obstacle_sprites = pygame.sprite.Group()
foe_sprites = pygame.sprite.Group()
stone_sprites = pygame.sprite.Group()
game_sprites = pygame.sprite.Group()


run = True
camera = Camera()
life_line = Life(window)
start_screen()
second_screen()

for y in range(len(level)):
    for x in range(len(level[y])):
        if level[y][x] == '#':
            Obstacle(x * 50, y * 50, all_sprites, obstacle_sprites)
        elif level[y][x] == '@':
            hero = Player(x * 50, y * 50, 5, all_sprites, player_sprite)
        elif level[y][x] == '$':
            Foe(x * 50, y * 50, all_sprites, foe_sprites)

fps = 60
clock = pygame.time.Clock()
f1 = pygame.font.Font(None, 36)

while run:

    clock.tick(fps)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        key = pygame.key.get_pressed()
        if key[pygame.K_x]:
            stone = Stones(all_sprites, stone_sprites)

    pygame.sprite.spritecollide(hero, foe_sprites, True)
    if life_line.lifex <= 10:
        game = Game(game_sprites)
        life_line.lifex = 110

    camera.update(hero)
    # обновляем положение всех спрайтов
    for sprite in all_sprites:
        camera.apply(sprite)

    # for sprite in game_sprites:
    #     camera.apply(sprite)

    # game_sprites.update(FPS)
    # clock.tick(FPS)

    window.blit(fon, (0, 0))
    all_sprites.update(obstacle_sprites)
    game_sprites.update(fps)

    life_line.draw()
    all_sprites.draw(window)
    game_sprites.draw(window)

    pygame.display.update()

pygame.quit()