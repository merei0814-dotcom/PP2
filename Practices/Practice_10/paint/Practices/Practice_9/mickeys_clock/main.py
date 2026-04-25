import pygame
from clock import update_angles, draw_clock
pygame.init()
screen=pygame.display.set_mode((600, 600))
clock=pygame.time.Clock()
running=True
while running:
    for i in pygame.event.get():
        if i.type==pygame.QUIT:
            running=False
    screen.fill((255, 255, 255))
    sec, minute=update_angles()
    draw_clock(screen, sec, minute)
    pygame.display.flip()
    clock.tick(1)
pygame.quit()