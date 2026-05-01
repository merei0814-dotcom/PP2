import pygame
import random
import sys

pygame.init()

# Window settings
WIDTH, HEIGHT = 600, 400
CELL = 20
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Practice 11 - Snake")
clock = pygame.time.Clock()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (40, 180, 80)
RED = (230, 40, 40)
YELLOW = (240, 210, 40)
ORANGE = (255, 150, 30)
PURPLE = (160, 80, 220)

font = pygame.font.SysFont("Verdana", 22)

# Food lives only this many milliseconds.
FOOD_LIFETIME = 5000


def random_cell():
    """Return random position on the grid."""
    x = random.randrange(0, WIDTH, CELL)
    y = random.randrange(0, HEIGHT, CELL)
    return x, y


class Food:
    """Food has weight and disappears after timer."""
    def __init__(self, snake):
        self.spawn(snake)

    def spawn(self, snake):
        # Choose position that is not inside the snake.
        while True:
            self.position = random_cell()
            if self.position not in snake:
                break

        self.weight = random.choice([1, 2, 3])
        self.color = {1: YELLOW, 2: ORANGE, 3: PURPLE}[self.weight]
        self.spawn_time = pygame.time.get_ticks()

    def expired(self):
        """Return True if food lived too long."""
        return pygame.time.get_ticks() - self.spawn_time > FOOD_LIFETIME

    def draw(self):
        rect = pygame.Rect(self.position[0], self.position[1], CELL, CELL)
        pygame.draw.rect(screen, self.color, rect, border_radius=6)

        # Draw food weight number.
        text = font.render(str(self.weight), True, BLACK)
        screen.blit(text, text.get_rect(center=rect.center))


def game_over(score):
    """Show game over screen."""
    screen.fill(BLACK)
    text1 = font.render("GAME OVER", True, RED)
    text2 = font.render(f"Score: {score}", True, WHITE)
    screen.blit(text1, text1.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20)))
    screen.blit(text2, text2.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20)))
    pygame.display.flip()
    pygame.time.delay(2000)
    pygame.quit()
    sys.exit()


def main():
    # Snake is a list of body parts. First item is head.
    snake = [(WIDTH // 2, HEIGHT // 2)]
    direction = (CELL, 0)
    next_direction = direction
    grow = 0
    score = 0

    food = Food(snake)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                # Do not allow instant reverse direction.
                if event.key == pygame.K_UP and direction != (0, CELL):
                    next_direction = (0, -CELL)
                elif event.key == pygame.K_DOWN and direction != (0, -CELL):
                    next_direction = (0, CELL)
                elif event.key == pygame.K_LEFT and direction != (CELL, 0):
                    next_direction = (-CELL, 0)
                elif event.key == pygame.K_RIGHT and direction != (-CELL, 0):
                    next_direction = (CELL, 0)

        direction = next_direction

        # Calculate new head position.
        head_x, head_y = snake[0]
        new_head = (head_x + direction[0], head_y + direction[1])

        # Check wall collision.
        if not (0 <= new_head[0] < WIDTH and 0 <= new_head[1] < HEIGHT):
            game_over(score)

        # Check self collision.
        if new_head in snake:
            game_over(score)

        snake.insert(0, new_head)

        # Check food collision.
        if new_head == food.position:
            score += food.weight
            grow += food.weight     # snake grows by food weight
            food.spawn(snake)

        # Food disappears after timer and respawns.
        if food.expired():
            food.spawn(snake)

        # Remove tail if snake should not grow.
        if grow > 0:
            grow -= 1
        else:
            snake.pop()

        # Draw everything.
        screen.fill(BLACK)

        for part in snake:
            pygame.draw.rect(screen, GREEN, pygame.Rect(part[0], part[1], CELL, CELL), border_radius=4)

        food.draw()

        # Show score and food timer.
        time_left = max(0, FOOD_LIFETIME - (pygame.time.get_ticks() - food.spawn_time)) // 1000
        score_text = font.render(f"Score: {score}", True, WHITE)
        timer_text = font.render(f"Food disappears in: {time_left}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(timer_text, (10, 40))

        pygame.display.flip()
        clock.tick(10)


if __name__ == "__main__":
    main()
