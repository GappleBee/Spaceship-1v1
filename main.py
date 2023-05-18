# Started 1/5/23
import pygame
from pygame.locals import *

pygame.mixer.pre_init(48000, 16, 2)  # The first parameter is frequency, the second is bit depth and the third is channels (1 = mono, 2 = stereo)
pygame.init()


# Constants
WIDTH, HEIGHT = 1920, 1080  # Change this to your monitor's resolution
RESOLUTION = (WIDTH, HEIGHT)
FPS = 67  # Change this to your monitor's refresh rate

# Setting up the window - Includes double buffering to increase performance
FLAGS = FULLSCREEN | DOUBLEBUF  # Renders the game in a special fullscreen window which increases performance
WIN = pygame.display.set_mode(RESOLUTION, FLAGS, 24)
pygame.display.set_caption("Spaceship 1v1")

BG = pygame.transform.scale(pygame.image.load("assets/space.png"), RESOLUTION).convert()

BORDER_WIDTH, BORDER_HEIGHT = 30, HEIGHT

FONT = pygame.font.SysFont("comfortaa", 50)

SHIP_WIDTH, SHIP_HEIGHT = 80, 50
SHIP_RESOLUTION = (SHIP_WIDTH, SHIP_HEIGHT)
SHIP_VEL = 10
SHIP_HEALTH = 50

BULLET_WIDTH, BULLET_HEIGHT = 30, 10
BULLET_VEL = 15
BULLET_COOLDOWN = 250  # In milliseconds


class Ship(pygame.sprite.Sprite):
    def __init__(self, width, height, x, y, health, image_path, angle, name=None):
        super().__init__()
        self.name = name
        self.health = health
        self.health_text = FONT.render(f"Health: {self.health}", 1, "white")
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.bullets = []

        image = pygame.image.load(image_path).convert_alpha()
        scaled_image = pygame.transform.scale(image, (width, height))
        self.image = pygame.transform.rotate(scaled_image, angle)

        self.mask = pygame.mask.from_surface(self.image)

    def draw(self, health_x, health_y):
        # Drawing the ship
        WIN.blit(self.image, (self.x, self.y))

        # Drawing the health text
        self.health_text = FONT.render(f"Health: {self.health}", 1, "white")
        WIN.blit(self.health_text, (health_x, health_y))

    def move_x(self, dx):
        self.x += dx

    def move_y(self, dy):
        self.y += dy

    def add_bullet(self, bullet):
        self.bullets.append(bullet)

    def remove_bullet(self, bullet):
        self.bullets.remove(bullet)

    def hit(self):
        self.health -= 1


class Bullet(pygame.sprite.Sprite):
    fire_sound = pygame.mixer.Sound("assets/Gun+Silencer.mp3")
    hit_sound = pygame.mixer.Sound("assets/Grenade+1.mp3")

    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.mask = pygame.mask.Mask((width, height))
        self.mask.fill()

    def draw(self, colour):
        pygame.draw.rect(WIN, colour, self.rect)


def handle_red_bullets_move(ship, ship2, vel):
    for bullet in ship.bullets:
        bullet.rect.x += vel

        offset = (bullet.rect.x - ship2.x, bullet.rect.y - ship2.y)
        collision = ship2.mask.overlap(bullet.mask, offset)
        if collision:
            bullet.hit_sound.play()
            ship2.hit()
            ship.remove_bullet(bullet)

        elif bullet.rect.x > WIDTH:
            ship.remove_bullet(bullet)


def handle_yellow_bullets_move(ship, ship2, vel):
    for bullet in ship2.bullets:
        bullet.rect.x -= vel

        offset = (bullet.rect.x - ship.x, bullet.rect.y - ship.y)
        collision = ship.mask.overlap(bullet.mask, offset)
        if collision:
            bullet.hit_sound.play()
            ship.hit()
            ship2.remove_bullet(bullet)

        elif bullet.rect.x + bullet.rect.width < 0:
            ship2.remove_bullet(bullet)


def game_over(winner):
    game_over_font = pygame.font.SysFont("comfortaa", 120)
    game_over_text = game_over_font.render(f"Game Over! {winner} Wins!", 1, "white")
    WIN.blit(game_over_text, ((WIDTH - game_over_text.get_width()) / 2, (HEIGHT - game_over_text.get_height()) / 2))
    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()


def handle_game_over(red_ship, yellow_ship):
    if red_ship.health == 0:
        game_over(yellow_ship.name)
    elif yellow_ship.health == 0:
        game_over(red_ship.name)


def draw(border, red_ship, yellow_ship):
    WIN.blit(BG, (0, 0))  # Drawing the background

    pygame.draw.rect(WIN, "black", border)  # Drawing the border

    # Drawing the two spaceships
    red_ship.draw(10, 10)
    yellow_ship.draw(WIDTH - yellow_ship.health_text.get_width() - 10, 10)

    # Drawing the bullets
    for bullet in red_ship.bullets:
        bullet.draw("red")

    for bullet in yellow_ship.bullets:
        bullet.draw("yellow")

    pygame.display.update()

def main():
    clock = pygame.time.Clock()

    border = pygame.Rect((WIDTH - BORDER_WIDTH) / 2, 0, BORDER_WIDTH, BORDER_HEIGHT)


    red_x = (WIDTH / 4) - (SHIP_WIDTH / 2)
    red_y = (HEIGHT - SHIP_HEIGHT) / 2
    red_ship = Ship(SHIP_WIDTH, SHIP_HEIGHT, red_x, red_y, SHIP_HEALTH, "assets/spaceship_red.png", 90, "Red")

    yellow_x = ((WIDTH * 3) / 4) - (SHIP_WIDTH / 2)
    yellow_y = (HEIGHT - SHIP_HEIGHT) / 2
    yellow_ship = Ship(SHIP_WIDTH, SHIP_HEIGHT, yellow_x, yellow_y, SHIP_HEALTH, "assets/spaceship_yellow.png", -90, "Yellow")

    red_bullet_time_elapsed = BULLET_COOLDOWN
    yellow_bullet_time_elapsed = BULLET_COOLDOWN

    
    run = True
    while run:
        ticked_time = clock.tick(FPS)
        red_bullet_time_elapsed += ticked_time
        yellow_bullet_time_elapsed += ticked_time

        # Deals with closing the game
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        keys = pygame.key.get_pressed()

        # Red ship
        # Movement
        if keys[pygame.K_a] and red_ship.x - SHIP_VEL >= 0:
            red_ship.move_x(-SHIP_VEL)
        if keys[pygame.K_d] and red_ship.x + red_ship.width + SHIP_VEL <= (WIDTH - BORDER_WIDTH) / 2:
            red_ship.move_x(SHIP_VEL)
        if keys[pygame.K_w] and red_ship.y - SHIP_VEL >= 0:
            red_ship.move_y(-SHIP_VEL)
        if keys[pygame.K_s] and red_ship.y + red_ship.height + SHIP_VEL <= HEIGHT:
            red_ship.move_y(SHIP_VEL)
        # Shooting
        if keys[pygame.K_SPACE]:
            if red_bullet_time_elapsed >= BULLET_COOLDOWN:
                red_bullet_time_elapsed = 0
                red_bullet = Bullet(red_ship.x + red_ship.width, red_ship.y + (red_ship.height / 2), BULLET_WIDTH, BULLET_HEIGHT)
                red_ship.add_bullet(red_bullet)
                red_bullet.fire_sound.play()

        # Yellow ship
        # Movement
        if keys[pygame.K_LEFT] and yellow_ship.x - SHIP_VEL >= (WIDTH + BORDER_WIDTH) / 2:
            yellow_ship.move_x(-SHIP_VEL)
        if keys[pygame.K_RIGHT] and yellow_ship.x + yellow_ship.width + SHIP_VEL <= WIDTH:
            yellow_ship.move_x(SHIP_VEL)
        if keys[pygame.K_UP] and yellow_ship.y - SHIP_VEL >= 0:
            yellow_ship.move_y(-SHIP_VEL)
        if keys[pygame.K_DOWN] and yellow_ship.y + yellow_ship.height + SHIP_VEL <= HEIGHT:
            yellow_ship.move_y(SHIP_VEL)
        # Shooting
        if keys[pygame.K_SEMICOLON]:
            if yellow_bullet_time_elapsed >= BULLET_COOLDOWN:
                yellow_bullet_time_elapsed = 0
                yellow_bullet = Bullet(yellow_ship.x, yellow_ship.y + (yellow_ship.height / 2), BULLET_WIDTH, BULLET_HEIGHT)
                yellow_ship.add_bullet(yellow_bullet)
                yellow_bullet.fire_sound.play()

        handle_game_over(red_ship, yellow_ship)
        handle_red_bullets_move(red_ship, yellow_ship, BULLET_VEL)
        handle_yellow_bullets_move(red_ship, yellow_ship, BULLET_VEL)

        draw(border, red_ship, yellow_ship)

    pygame.quit()
    quit()

if __name__ == "__main__":
    main()
