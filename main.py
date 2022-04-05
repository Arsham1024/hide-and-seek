import pygame
import random
import math

# needs to be on every game
pygame.init()
running = True
pygame.display.set_caption("HIDE AND SEEK")


# Global CONSTANTS
# everything depends on the window width
WINDOW_WIDTH = 800
WINDOW_HEIGHT = WINDOW_WIDTH # make sure the window is a square!
MAP_SIZE = int(WINDOW_WIDTH / 80) # number of rows and cols
TILE_SIZE = int(WINDOW_WIDTH/MAP_SIZE)
MAP = (
    '##########'
    '#    #   #'
    '#        #'
    '#  ###   #'
    '#    ##  #'
    '#        #'
    '#  ####  #'
    '#  #     #'
    '####     #'
    '##########'
)

# global vars
player_x = int(WINDOW_WIDTH/2)
player_y = int(WINDOW_WIDTH/2)

# Colors palate
BLACK = (0, 0, 0)
WHITE = (200, 200, 200)
STEEL_TEAL = (91, 130, 142)
PEWTER_BLUE = (135, 159, 169)
SILVER_SAND = (171, 184, 191)
ANTIQUE_BRASS = (183, 151, 134)

# Game set up
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
clock = pygame.time.Clock()

# Helper functions -----------------------------------------------------------------------------

def draw_map():
    for row in range(MAP_SIZE):
        for col in range(MAP_SIZE):
            # calculate square index
            square = row * MAP_SIZE + col
            # draw rectangle for each tile
            pygame.draw.rect(
                screen,
                STEEL_TEAL if MAP[square] == '#' else SILVER_SAND,
                (col*TILE_SIZE, row*TILE_SIZE, TILE_SIZE-1, TILE_SIZE-1) # -1 for the borders
            )
def draw_player():
    pygame.draw.circle(
        screen,
        PEWTER_BLUE,
        (player_x, player_y),
        10
    )



# Main loop of the game -----------------------------------------------------------------------------
while running:
    screen.fill(BLACK)
    
    # All events
    for event in pygame.event.get():
        # if user quits it
        if event.type == pygame.QUIT:
            running = False
    
    # construct the map before everything
    draw_map()
    
    # draw player on map
    draw_player()

    # Update display at the end
    pygame.display.flip()
    clock.tick(30)
