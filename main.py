from sys import flags
from turtle import window_width
import pygame
import random
import math

# needs to be on every game
pygame.init()
running = True
pygame.display.set_caption("HIDE AND SEEK")


# Global CONSTANTS -----------------------------------------------------------------------------
# everything depends on the window width
WINDOW_WIDTH = 800
WINDOW_HEIGHT = WINDOW_WIDTH # make sure the window is a square!
MAP_SIZE = int(WINDOW_WIDTH / 80) # number of rows and cols
TILE_SIZE = int(WINDOW_WIDTH/MAP_SIZE)
NUM_TILES = MAP_SIZE ** 2

PLAYER_DIAMETER = 10

FOV = math.pi /3 #60 deg
HALF_FOV = FOV/2
CASTED_RAYS = 100
STEP_ANGLE = FOV/CASTED_RAYS
MAX_DEPTH = WINDOW_WIDTH # depth of FOV

PLAYER_SPEED = 5

MAP = (
    '##########'
    '#    #   #'
    '# #    # #'
    '# # ## # #'
    '###    # #'
    '#   #    #'
    '#  ##### #'
    '# ##   # #'
    '#    #   #'
    '### ######'
)

# global vars -----------------------------------------------------------------------------
seeker_x = 200
seeker_y = 120
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
        PLAYER_DIAMETER
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
            # coordinates of the end of the ray, grows per frame rate
            target_x = seeker_x - math.sin(start_angle) * depth
            target_y = seeker_y + math.cos(start_angle) * depth
            
            # if the index bigger than 100 because of the exit
            if not is_valid(target_x, target_y):
                break
            
            #draw casted ray 
            pygame.draw.line(screen, ANTIQUE_BRASS, (seeker_x, seeker_y), (target_x, target_y))

        # increment casted ray angle
        start_angle += STEP_ANGLE

def is_valid(x,y):
    # position + and - 10px
        # find which col & row is the target in based on coordinates
    col = int(x / TILE_SIZE)
    row = int(y / TILE_SIZE)

    # find index of the tile
    index_square = row * (MAP_SIZE) + col

        # if the index bigger than 100 because of the exit
    if index_square >= NUM_TILES or MAP[index_square] == "#":
        return False
    return True

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

    if keys[pygame.K_UP]:
        seeker_x += -math.sin(seeker_angle) * PLAYER_SPEED
        seeker_y += math.cos(seeker_angle) * PLAYER_SPEED
        if not is_valid(seeker_x, seeker_y):
            # check x and y and see if it is wall
            # if yes go back to privious x and y
            # if not move
            seeker_x -= -math.sin(seeker_angle) * PLAYER_SPEED
            seeker_y -= math.cos(seeker_angle) * PLAYER_SPEED


    if keys[pygame.K_DOWN]:
        seeker_x -= -math.sin(seeker_angle) * PLAYER_SPEED
        seeker_y -= math.cos(seeker_angle) * PLAYER_SPEED

        if not is_valid(seeker_x, seeker_y):
            seeker_x += -math.sin(seeker_angle) * PLAYER_SPEED
            seeker_y += math.cos(seeker_angle) * PLAYER_SPEED
    
    # draw player on map
    draw_player(seeker_x, seeker_y, PEWTER_BLUE)
    draw_player(flag_x, flag_y, ANTIQUE_BRASS) # actually draw the flag
    draw_player(hider_x, hider_y, BLACK)

    draw_FOV()
    cast_rays()

    # Update display at the end
    pygame.display.flip()
    clock.tick(30)
