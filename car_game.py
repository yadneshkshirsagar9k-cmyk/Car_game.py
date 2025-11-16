import pygame
import random
import sys

# Initialize pygame
pygame.init()

# ----------------------------
# Basic settings
# ----------------------------
WIDTH, HEIGHT = 480, 700
FPS = 60
LANE_COUNT = 3
LANE_PADDING = 40

# Colors
ROAD_COLOR = (50, 50, 50)
LANE_LINE_COLOR = (255, 255, 255)
CAR_COLOR = (0, 200, 0)
ENEMY_COLOR = (200, 0, 0)
TEXT_COLOR = (255, 255, 255)
BG_COLOR = (20, 20, 20)

# Screen setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Car Racing Game (No Images)")
clock = pygame.time.Clock()

# Fonts
font = pygame.font.SysFont("Arial", 30)

# ----------------------------
# Player class
# ----------------------------
class Player(pygame.sprite.Sprite):
    def __init__(self, lanes_x, lane_index, y_bottom):
        super().__init__()
        self.lanes_x = lanes_x
        self.lane_index = lane_index
        self.image = pygame.Surface((40, 80))
        self.image.fill(CAR_COLOR)
        self.rect = self.image.get_rect()
        self.rect.centerx = lanes_x[lane_index]
        self.rect.bottom = y_bottom
        self.move_speed = 12
        self.target_x = self.rect.centerx

    def move_left(self):
        if self.lane_index > 0:
            self.lane_index -= 1
            self.target_x = self.lanes_x[self.lane_index]

    def move_right(self):
        if self.lane_index < len(self.lanes_x) - 1:
            self.lane_index += 1
            self.target_x = self.lanes_x[self.lane_index]

    def update(self):
        # smooth movement between lanes
        dx = self.target_x - self.rect.centerx
        if abs(dx) < 2:
            self.rect.centerx = self.target_x
        else:
            self.rect.centerx += dx / abs(dx) * self.move_speed


# ----------------------------
# Enemy class
# ----------------------------
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, speed):
        super().__init__()
        self.image = pygame.Surface((40, 80))
        self.image.fill(ENEMY_COLOR)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.y = y
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()


# ----------------------------
# Game class
# ----------------------------
class Game:
    def __init__(self):
        self.reset()

    def reset(self):
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.score = 0
        self.speed = 6
        self.running = True

        # setup lanes
        lane_width = (WIDTH - 2 * LANE_PADDING) / LANE_COUNT
        self.lanes_x = [int(LANE_PADDING + lane_width / 2 + i * lane_width) for i in range(LANE_COUNT)]

        # player setup
        self.player = Player(self.lanes_x, 1, HEIGHT - 40)
        self.all_sprites.add(self.player)

        # spawn timer
        self.enemy_timer = 0
        self.spawn_delay = 1000  # milliseconds

    def spawn_enemy(self):
        lane = random.choice(self.lanes_x)
        enemy = Enemy(lane, -100, self.speed + random.randint(0, 3))
        self.all_sprites.add(enemy)
        self.enemies.add(enemy)

    def check_collision(self):
        for enemy in self.enemies:
            if self.player.rect.colliderect(enemy.rect):
                return True
        return False

    def draw_road(self, offset):
        screen.fill(BG_COLOR)
        pygame.draw.rect(screen, ROAD_COLOR, (LANE_PADDING, 0, WIDTH - 2 * LANE_PADDING, HEIGHT))
        
        # draw lane lines
        lane_width = (WIDTH - 2 * LANE_PADDING) / LANE_COUNT
        for i in range(1, LANE_COUNT):
            x = int(LANE_PADDING + i * lane_width)
            pygame.draw.line(screen, (80, 80, 80), (x, 0), (x, HEIGHT), 5)

        # dashed center line animation
        dash_height = 30
        gap = 20
        y = -offset % (dash_height + gap)
        center_x = WIDTH // 2
        while y < HEIGHT:
            pygame.draw.line(screen, LANE_LINE_COLOR, (center_x, y), (center_x, y + dash_height), 4)
            y += dash_height + gap

    def update(self, dt):
        self.enemy_timer += dt
        if self.enemy_timer >= self.spawn_delay:
            self.spawn_enemy()
            self.enemy_timer = 0

        self.all_sprites.update()
        self.score += dt // 10

        # gradually increase game speed
        if self.score % 1000 == 0 and self.speed < 18:
            self.speed += 0.5

    def draw_ui(self):
        score_text = font.render(f"Score: {int(self.score)}", True, TEXT_COLOR)
        screen.blit(score_text, (10, 10))

    def game_over_screen(self):
        text = font.render("GAME OVER", True, (255, 0, 0))
        retry = font.render("Press R to Restart", True, TEXT_COLOR)
        screen.blit(text, ((WIDTH - text.get_width()) // 2, HEIGHT // 2 - 50))
        screen.blit(retry, ((WIDTH - retry.get_width()) // 2, HEIGHT // 2 + 10))
        pygame.display.flip()

    def run(self):
        offset = 0
        while True:
            dt = clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.player.move_left()
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.player.move_right()
                    elif event.key == pygame.K_r and not self.running:
                        self.reset()

            if self.running:
                offset += self.speed
                self.update(dt)
                self.draw_road(offset)
                self.all_sprites.draw(screen)
                self.draw_ui()

                if self.check_collision():
                    self.running = False
            else:
                self.game_over_screen()

            pygame.display.flip()


# ----------------------------
# Run the game
# ----------------------------
if __name__ == "__main__":
    Game().run()