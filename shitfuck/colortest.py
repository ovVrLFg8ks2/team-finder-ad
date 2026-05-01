import pygame
import sys
from random import randint

def randcol(x, m):
    r = max(m, abs(x - 382) - 127)
    g = max(m, 255 - abs(x - 255))
    b = max(m, 255 - abs(x - 510))
    return (r, g, b)

def randcol2(x, m):
    r = max(0, abs(x - 382) - 127)
    g = max(0, 255 - abs(x - 255))
    b = max(0, 255 - abs(x - 510))
    
    k = (255-m)/255
    r = 255-(255-r)*k
    g = 255-(255-g)*k
    b = 255-(255-b)*k
    return (r, g, b)

def randcol3(x, m):
    k = (255 - m) / 255
    
    r = max(0, abs(x - 382) - 127) * k + m
    g = max(0, 255 - abs(x - 255)) * k + m
    b = max(0, 255 - abs(x - 510)) * k + m
    return (r, g, b)

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Smooth Color Cycle")
clock = pygame.time.Clock()

x = 0

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    #x = randint(0, 765)
    color = randcol3(x, 120)
    screen.fill(color)
    
    pygame.display.flip()
    
    x = (x + 1) % 765
    
    clock.tick(60) 
