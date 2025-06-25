import os
import pygame
from time import time
from random import randint

class Settings:
    WINDOW_WIDTH = 350
    WINDOW_HEIGHT = 600
    FPS = 60
    DELTATIME = 1.0 / FPS
    TITLE = "Bird"
    FILE_PATH = os.path.dirname(os.path.abspath(__file__))
    IMAGE_PATH = os.path.join(FILE_PATH, "Bilder", "images")
    BACKGROUND_PATH = os.path.join(FILE_PATH, "Bilder", "images")

    @staticmethod
    def filepath(name: str):
        return os.path.join(Settings.FILE_PATH, name)

    @staticmethod
    def imagepath(name: str):
        return os.path.join(Settings.IMAGE_PATH, name)

    @staticmethod
    def backgroundpath(name: str):
        return os.path.join(Settings.BACKGROUND_PATH, name)

class Bird:
    def __init__(self):
        self.skins = []
        for i in range(4):
            image_path = Settings.imagepath(f"{i}.png")
            original_image = pygame.image.load(image_path).convert_alpha()
            new_width = original_image.get_width() // 9
            new_height = original_image.get_height() // 9
            scaled_image = pygame.transform.scale(original_image, (new_width, new_height))
            self.skins.append(scaled_image)

        self.skin_index = 0
        self.image = self.skins[self.skin_index]
        self.rect = self.image.get_rect()
        self.rect.center = (Settings.WINDOW_WIDTH // 2, Settings.WINDOW_HEIGHT // 2)
        self.velocity = 0

    def apply_gravity(self):
        gravity = 0.3
        self.velocity += gravity
        self.rect.y += self.velocity

        if self.rect.bottom > Settings.WINDOW_HEIGHT:
            self.rect.bottom = Settings.WINDOW_HEIGHT
            self.velocity = 0

        if self.rect.top < 0:
            self.rect.top = 0
            self.velocity = 0

    def jump(self):
        if self.rect.top > 0:
            self.velocity = -6

    def switch_skin(self, direction: int):
        self.skin_index = (self.skin_index + direction) % len(self.skins)
        self.image = self.skins[self.skin_index]
        self.rect = self.image.get_rect(center=self.rect.center)

class Pipe:
    def __init__(self, x: int, y: int, is_top: bool):
        pipe_image_path = Settings.imagepath("pipe.png")
        original_image = pygame.image.load(pipe_image_path).convert_alpha()
        self.image = pygame.transform.scale(original_image, (50, 320))
        if is_top:
            self.image = pygame.transform.flip(self.image, False, True)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def move(self):
        self.rect.x -= 3

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((Settings.WINDOW_WIDTH, Settings.WINDOW_HEIGHT))
        pygame.display.set_caption(Settings.TITLE)
        self.clock = pygame.time.Clock()
        self.running = False
        self.starting = True

        background_path = Settings.backgroundpath("bg.png")
        self.background = pygame.image.load(background_path).convert()

        backgroundnight_path = Settings.backgroundpath("bg_night.png")
        self.backgroundnight = pygame.image.load(backgroundnight_path).convert()
        self.use_night_background = False

        arrow_path = Settings.imagepath("Arrow.png")
        self.arrow_ui = pygame.image.load(arrow_path).convert_alpha()
        self.arrow_ui = pygame.transform.scale(self.arrow_ui, (250, 200))  

        self.bird = Bird()
        self.pipes = []
        self.pipe_timer = 0
        self.score = 0

        self.font = pygame.font.Font("fonts/PressStart2P-Regular.ttf", 14)

    def reset_game(self):
        self.bird = Bird()
        self.pipes = []
        self.pipe_timer = 0
        self.score = 0
        self.starting = True

    def run(self):
        time_previous = time()
        self.running = True
        while self.running:
            if self.starting:
                self.show_start_screen()
            else:
                self.watch_for_events()
                self.update()
                self.draw()
                self.clock.tick(Settings.FPS)
                time_current = time()
                Settings.DELTATIME = time_current - time_previous
                time_previous = time_current
        pygame.quit()

    def show_start_screen(self):
        self.draw_start_screen_with_score()
        while self.starting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.starting = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                        self.starting = False
                    elif event.key == pygame.K_SPACE:
                        self.starting = False
                    elif event.key == pygame.K_LEFT:
                        self.bird.switch_skin(-1)
                        self.draw_start_screen_with_score()
                    elif event.key == pygame.K_RIGHT:
                        self.bird.switch_skin(1)
                        self.draw_start_screen_with_score()
                    elif event.key == pygame.K_h:  
                        self.use_night_background = not self.use_night_background
                        self.draw_start_screen_with_score()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.starting = False

    def draw_start_screen_with_score(self):
        if self.use_night_background:
            self.screen.blit(self.backgroundnight, (0, 0))
        else:
            self.screen.blit(self.background, (0, 0))


        self.screen.blit(self.bird.image, self.bird.rect)


        score_img_path = Settings.imagepath("score1.png")
        score_img = pygame.image.load(score_img_path).convert_alpha()
        score_img = pygame.transform.scale(score_img, (150, 50))
        self.screen.blit(score_img, (5, 5))

        score_text = self.font.render(f"Score: {int(self.score)}", True, (255, 255, 255))
        self.screen.blit(score_text, (15, 20))


        arrow_rect = self.arrow_ui.get_rect()
        arrow_rect.center = (Settings.WINDOW_WIDTH // 2, Settings.WINDOW_HEIGHT // 2 - 25)
        self.screen.blit(self.arrow_ui, arrow_rect)

        pygame.display.flip()

    def watch_for_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    self.bird.jump()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.bird.jump()

    def update(self):
        self.bird.apply_gravity()

        for pipe in self.pipes[:]:
            pipe.move()
            if pipe.rect.right < 0:
                self.pipes.remove(pipe)

        for pipe in self.pipes:
            if self.bird.rect.colliderect(pipe.rect):
                self.reset_game()
                return

        if self.bird.rect.top <= 0 or self.bird.rect.bottom >= Settings.WINDOW_HEIGHT:
            self.reset_game()
            return

        self.pipe_timer += 1
        if self.pipe_timer > 90:
            self.pipe_timer = 0
            gap_size = 150
            pipe_x = Settings.WINDOW_WIDTH
            pipe_y = randint(300, Settings.WINDOW_HEIGHT - gap_size - 100)
            top_pipe = Pipe(pipe_x, pipe_y - 350 - gap_size, is_top=True)
            bottom_pipe = Pipe(pipe_x, pipe_y, is_top=False)
            self.pipes.append(top_pipe)
            self.pipes.append(bottom_pipe)

        for pipe in self.pipes:
            if pipe.rect.right < self.bird.rect.left and not hasattr(pipe, "scored"):
                self.score += 0.5
                pipe.scored = True

    def draw(self):
        if self.use_night_background:
            self.screen.blit(self.backgroundnight, (0, 0))
        else:
            self.screen.blit(self.background, (0, 0))

        
        for pipe in self.pipes:
            self.screen.blit(pipe.image, pipe.rect)
        self.screen.blit(self.bird.image, self.bird.rect)

        score_img_path = Settings.imagepath("score1.png")
        score_img = pygame.image.load(score_img_path).convert_alpha()
        score_img = pygame.transform.scale(score_img, (150, 50))
        self.screen.blit(score_img, (5, 5))

        score_text = self.font.render(f"Score: {int(self.score)}", True, (255, 255, 255))
        self.screen.blit(score_text, (15, 20))  
        pygame.display.flip()

def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main()
