import pygame
from player import play, stop, next_track, previous_track, current_track

pygame.init()

WIDTH, HEIGHT = 600, 250
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Music Player")

font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 26)

running = True

while running:
    screen.fill((30, 30, 30))

    title = font.render(f"Current: {current_track()}", True, (255, 255, 255))
    controls = small_font.render(
        "P = Play | S = Stop | N = Next | B = Back | Q = Quit",
        True,
        (200, 200, 200),
    )

    screen.blit(title, (30, 80))
    screen.blit(controls, (30, 140))

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                play()

            elif event.key == pygame.K_s:
                stop()

            elif event.key == pygame.K_n:
                next_track()

            elif event.key == pygame.K_b:
                previous_track()

            elif event.key == pygame.K_q:
                running = False

pygame.quit()