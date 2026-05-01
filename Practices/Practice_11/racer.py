import pygame
import random
import sys

pygame.init()

# Window settings
WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Practice 11 - Racer")
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (50, 50, 50)
RED = (220, 40, 40)
BLUE = (50, 100, 230)
YELLOW = (240, 210, 40)
ORANGE = (255, 150, 30)
GREEN = (40, 180, 80)

font = pygame.font.SysFont("Verdana", 24)

# Game settings
PLAYER_SPEED = 5
BASE_ENEMY_SPEED = 4
SPEED_UP_EVERY = 5      # enemy becomes faster after every 5 collected coins


class Player:
    """Player car controlled by keyboard."""
    def __init__(self):
        self.rect = pygame.Rect(WIDTH // 2 - 25, HEIGHT - 100, 50, 80)

    def move(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += PLAYER_SPEED

    def draw(self):
        pygame.draw.rect(screen, BLUE, self.rect, border_radius=8)


class Enemy:
    """Enemy car moving down the road."""
    def __init__(self):
        self.rect = pygame.Rect(random.randint(0, WIDTH - 50), -100, 50, 80)
        self.speed = BASE_ENEMY_SPEED

    def reset(self):
        self.rect.x = random.randint(0, WIDTH - 50)
        self.rect.y = -100

    def move(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.reset()

    def draw(self):
        pygame.draw.rect(screen, RED, self.rect, border_radius=8)


class Coin:
    """Coin with random weight. Bigger weight gives more score."""
    def __init__(self):
        self.spawn()

    def spawn(self):
        self.weight = random.choice([1, 2, 3])
        self.radius = 10 + self.weight * 3
        self.x = random.randint(self.radius, WIDTH - self.radius)
        self.y = random.randint(-300, -50)
        self.speed = 3

        # Different weights have different colors.
        self.color = {1: YELLOW, 2: ORANGE, 3: GREEN}[self.weight]
        self.rect = pygame.Rect(self.x - self.radius, self.y - self.radius,
                                self.radius * 2, self.radius * 2)

    def move(self):
        self.y += self.speed
        self.rect.center = (self.x, self.y)

        # If coin leaves the screen, create a new coin.
        if self.y > HEIGHT + self.radius:
            self.spawn()

    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)
        value_text = font.render(str(self.weight), True, BLACK)
        screen.blit(value_text, value_text.get_rect(center=(self.x, self.y)))


def draw_road():
    """Draw simple road background."""
    screen.fill(GRAY)
    pygame.draw.line(screen, WHITE, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT), 5)
    pygame.draw.line(screen, WHITE, (20, 0), (20, HEIGHT), 5)
    pygame.draw.line(screen, WHITE, (WIDTH - 20, 0), (WIDTH - 20, HEIGHT), 5)


def game_over(score):
    """Show game over screen and close after short delay."""
    screen.fill(BLACK)
    text1 = font.render("GAME OVER", True, RED)
    text2 = font.render(f"Score: {score}", True, WHITE)
    screen.blit(text1, text1.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30)))
    screen.blit(text2, text2.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 10)))
    pygame.display.flip()
    pygame.time.delay(2000)
    pygame.quit()
    sys.exit()


def main():
    player = Player()
    enemy = Enemy()
    coin = Coin()

    score = 0
    collected_coins = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        player.move()
        enemy.move()
        coin.move()

        # Player collects coin.
        if player.rect.colliderect(coin.rect):
            score += coin.weight
            collected_coins += 1
            coin.spawn()

            # Enemy speed increases after every N collected coins.
            enemy.speed = BASE_ENEMY_SPEED + collected_coins // SPEED_UP_EVERY

        # Collision with enemy means game over.
        if player.rect.colliderect(enemy.rect):
            game_over(score)

        draw_road()
        coin.draw()
        player.draw()
        enemy.draw()

        score_text = font.render(f"Score: {score}", True, WHITE)
        coins_text = font.render(f"Coins: {collected_coins}", True, WHITE)
        speed_text = font.render(f"Enemy speed: {enemy.speed}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(coins_text, (10, 40))
        screen.blit(speed_text, (10, 70))

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
