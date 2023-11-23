import pygame

pygame.init()
SCREEN_WIDTH = 800
SREEN_HEIGHT = 600

screen = pygame.display.set_mode((SCREEN_WIDTH, SREEN_HEIGHT))
run = True

while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

pygame.quit()
