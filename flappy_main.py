import pygame
import neat
import time
import os
import random

pygame.font.init()

WINDOW_WIDTH = 550
WINDOW_HEIGHT = 800

PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))
GROUND_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BIRD_IMGS = [
    pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))),
    pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))),
    pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))
]

STAT_FONT = pygame.font.SysFont("comicsans", 40)


class Bird:
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25
    ROTATION_VEL = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.velocity = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):
        self.velocity = -10.5
        self.tick_count = 0
        self.height = self.y

    def move(self):
        self.tick_count += 1
        d = self.velocity * self.tick_count + 1.5 * self.tick_count ** 2

        if d > 16:
            d = 16

        if d < 0:
            d -= 2

        self.y = self.y + d

        if d < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt -= self.ROTATION_VEL

    def draw(self, window):
        self.img_count += 1

        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME * 2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME * 3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME * 4:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME * 4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0

        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME * 2

        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft=(self.x, self.y)).center)
        window.blit(rotated_image, new_rect.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)


class Pipe:
    GAP = 200
    VELOCITY = 5

    def __init__(self, x):
        self.x = x
        self.height = 0
        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
        self.PIPE_BOTTOM = PIPE_IMG

        self.passed = False
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        self.x -= self.VELOCITY

    def draw(self, window):
        window.blit(self.PIPE_TOP, (self.x, self.top))
        window.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_pipe_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_pipe_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - bird.x, int(self.top - round(bird.y)))
        bottom_offset = (self.x - bird.x, int(self.bottom - round(bird.y)))

        bottom_point = bird_mask.overlap(bottom_pipe_mask, bottom_offset)
        top_point = bird_mask.overlap(top_pipe_mask, top_offset)

        if bottom_point or top_point:
            return True
        return False


class Base:
    VELOCITY = 5
    WIDTH = GROUND_IMG.get_width()
    IMG = GROUND_IMG

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.VELOCITY
        self.x2 -= self.VELOCITY

        if self.x1 < - self.WIDTH:
            self.x1 = self.x2 + self.WIDTH
        if self.x2 < - self.WIDTH:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, window):
        window.blit(self.IMG, (self.x1, self.y))
        window.blit(self.IMG, (self.x2, self.y))


def draw_window(window, bird, pipes, base, score):
    window.blit(BG_IMG, (0, 0))

    for pipe in pipes:
        pipe.draw(window)

    text = STAT_FONT.render("Score:" + str(score), True, (255, 255, 255))
    window.blit(text, (WINDOW_WIDTH - 10 - text.get_width(), 10))

    base.draw(window)
    bird.draw(window)
    pygame.display.update()


def draw_game_over(window, score):
    surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    surface.fill((240, 240, 240, 128))
    window.blit(surface, (0, 0))

    draw_score(window, score)

    font = pygame.font.Font(None, 64)
    text = font.render("Game Over", True, (255, 0, 0))
    text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 100))
    window.blit(text, text_rect)
    pygame.display.update()


def draw_score(window, score):
    font = pygame.font.Font(None, 48)
    text = font.render("Your score: %d" % score, True, (0, 0, 0))
    text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50))
    window.blit(text, text_rect)
    pygame.display.update()


class Button:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text

    def draw(self, window):
        pygame.draw.rect(window, (255, 255, 255), self.rect)
        font = pygame.font.Font(None, 32)
        text = font.render(self.text, True, (0, 0, 0))
        text_rect = text.get_rect(center=self.rect.center)
        window.blit(text, text_rect)
        pygame.display.update()

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


def main():
    bird = Bird(230, 350)
    base = Base(730)
    pipes = [Pipe(600)]
    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    run = True
    new_game_clicked = False
    score = 0
    game_over = False

    new_game_button = Button(WINDOW_WIDTH // 2 + 10, WINDOW_HEIGHT * 0.70, 200, 50, "New Game")
    exit_game_button = Button(WINDOW_WIDTH // 2 - 210, WINDOW_HEIGHT * 0.70, 200, 50, "Exit Game")

    clock = pygame.time.Clock()

    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bird.jump()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if new_game_button.is_clicked(event.pos):
                    new_game_clicked = True
                if exit_game_button.is_clicked(event.pos):
                    run = False

        if new_game_clicked:
            game_over = False
            bird = Bird(230, 350)
            pipes = [Pipe(600)]
            score = 0
            new_game_clicked = False

        bird.move()
        base.move()
        remove_list = []
        add_pipe = False
        for pipe in pipes:
            if pipe.collide(bird):
                game_over = True

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                remove_list.append(pipe)

            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True

            pipe.move()

        if add_pipe:
            score += 1
            pipes.append(Pipe(600))

        for pipe in remove_list:
            pipes.remove(pipe)

        if bird.y + bird.img.get_height() > 730:
            game_over = True

        draw_window(window, bird, pipes, base, score)

        if game_over:
            display_menu = True

            draw_game_over(window, score)
            new_game_button.draw(window)
            exit_game_button.draw(window)

            while display_menu:
                for event in pygame.event.get():
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if new_game_button.is_clicked(event.pos):
                            bird = Bird(230, 350)
                            pipes = [Pipe(600)]
                            score = 0
                            game_over = False
                            run = True
                            display_menu = False

                        if exit_game_button.is_clicked(event.pos):
                            pygame.quit()
                            quit()

    pygame.quit()
    quit()


main()
