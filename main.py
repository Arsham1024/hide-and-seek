from sys import flags
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

FOV = math.pi /3 #60 deg
HALF_FOV = FOV/2
CASTED_RAYS = 120
STEP_ANGLE = FOV/CASTED_RAYS
MAX_DEPTH = WINDOW_WIDTH

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
    '###### ###'
)

# global vars
seeker_x = int(WINDOW_WIDTH/2)
seeker_y = int(WINDOW_WIDTH/2)
seeker_angle = math.pi

hider_x = 120
hider_y = 120

flag_x = 680
flag_y = 120

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

def draw_player(player_x, player_y, color):
    pygame.draw.circle(
        screen,
        color,
        (player_x, player_y),
        10
    )

def draw_FOV():
    # draw direction
    pygame.draw.line(
        screen, 
        ANTIQUE_BRASS,
        (seeker_x, seeker_y), 
        (seeker_x - math.sin(seeker_angle) * 50,
         seeker_y + math.cos(seeker_angle) * 50,
        ),
        3
    )
    #draw FOV left boundary
    pygame.draw.line(
        screen, 
        ANTIQUE_BRASS,
        (seeker_x, seeker_y), 
        (seeker_x - math.sin(seeker_angle - HALF_FOV) * 50,
         seeker_y + math.cos(seeker_angle - HALF_FOV) * 50,
        ),
        3
    )
    #draw FOV right boundary
    pygame.draw.line(
        screen, 
        ANTIQUE_BRASS,
        (seeker_x, seeker_y), 
        (seeker_x - math.sin(seeker_angle + HALF_FOV) * 50,
         seeker_y + math.cos(seeker_angle + HALF_FOV) * 50,
        ),
        3
    )

# ray casting algorithm
def cast_rays():
    start_angle = seeker_angle - HALF_FOV

    # for all casted rays 
    for ray in range (CASTED_RAYS):
        for depth in range(MAX_DEPTH):
            target_x = seeker_x - math.sin(start_angle) * depth
            target_y = seeker_y + math.cos(start_angle) * depth

            #draw casted ray 
            pygame.draw.line(screen, WHITE, (seeker_x, seeker_y), (target_x, target_y))
        # increment casted ray angle
        start_angle += STEP_ANGLE



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

    # get player input
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]: seeker_angle -= 0.1
    if keys[pygame.K_RIGHT]: seeker_angle += 0.1
    
    # draw player on map
    draw_player(seeker_x, seeker_y, PEWTER_BLUE)
    draw_player(flag_x, flag_y, ANTIQUE_BRASS)
    draw_player(hider_x, hider_y, BLACK)
    draw_FOV()
    cast_rays()
    

    # Update display at the end
    pygame.display.flip()
    clock.tick(30)
