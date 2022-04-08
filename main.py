from asyncio.base_futures import _FINISHED
from os import system
from sys import flags
from turtle import update, window_width
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
CASTED_RAYS = 120
STEP_ANGLE = FOV/CASTED_RAYS
MAX_DEPTH = 240 # depth of FOV

PLAYER_SPEED = 5
FLAG_CAPTURED = False
FINISHED = False
HIDER_CAPTURED = False

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
    '##########'
)

# global vars -----------------------------------------------------------------------------
seeker_x = 200
seeker_y = 120
seeker_angle = math.pi

hider_x = 120
hider_y = 200
hider_angle = math.pi

flag_x = 680
flag_y = 120

# Scores 
seeker_points = 0
hider_points = 0

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
def determine_square_color(square):
    if square == '#':
        return STEEL_TEAL
    elif square == ' ':
        return SILVER_SAND
    else:
        return BLACK

def draw_map():
    for row in range(MAP_SIZE):
        for col in range(MAP_SIZE):
            # calculate square index
            square = row * MAP_SIZE + col
            # draw rectangle for each tile
            pygame.draw.rect(
                screen,
                determine_square_color(MAP[square]),
                (col*TILE_SIZE, row*TILE_SIZE, TILE_SIZE-1, TILE_SIZE-1) # -1 for the borders
            )

def update_map():
    return (
    '##########'
    '#    #   #'
    '# #    # #'
    '# # ## # #'
    '###    # #'
    '#   #    #'
    '#  ##### #'
    '# ##   # #'
    '#    #   #'
    '###!######'
)

def draw_player(player_x, player_y, color):
    pygame.draw.circle(
        screen,
        color,
        (player_x, player_y),
        PLAYER_DIAMETER
    )

def draw_flag():
    if not FLAG_CAPTURED:
        pygame.draw.circle(
            screen,
            ANTIQUE_BRASS,
            (flag_x, flag_y),
            10
        )

def draw_FOV(player_x, player_y, angle):
    # draw direction
    pygame.draw.line(
        screen, 
        ANTIQUE_BRASS,
        (player_x, player_y), 
        (player_x - math.sin(angle) * 50,
         player_y + math.cos(angle) * 50,
        ),
        3
    )
    #draw FOV left boundary
    pygame.draw.line(
        screen, 
        ANTIQUE_BRASS,
        (player_x, player_y), 
        (player_x - math.sin(angle - HALF_FOV) * 50,
         player_y + math.cos(angle - HALF_FOV) * 50,
        ),
        3
    )
    #draw FOV right boundary
    pygame.draw.line(
        screen, 
        ANTIQUE_BRASS,
        (player_x, player_y), 
        (player_x - math.sin(angle + HALF_FOV) * 50,
         player_y + math.cos(angle + HALF_FOV) * 50,
        ),
        3
    )

# ray casting algorithm
def cast_rays():
    global HIDER_CAPTURED, seeker_points
    start_angle = seeker_angle - HALF_FOV

    # for all casted rays 
    for ray in range (CASTED_RAYS):
        for depth in range(MAX_DEPTH):
            # coordinates of the end of the ray, grows per frame rate
            target_x = seeker_x - math.sin(start_angle) * depth
            target_y = seeker_y + math.cos(start_angle) * depth

            # capture the hider if in range
            if target_y - 1 <= hider_y <= target_y + 1 and target_x - 1 <= hider_x <= target_x + 1 and not HIDER_CAPTURED:
                seeker_points += 2
                HIDER_CAPTURED = True

                
            
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

def flag_found():
    if flag_y - 10 <= hider_y <= flag_y + 10 and flag_x - 10 <= hider_x <= flag_x + 10:
        global FLAG_CAPTURED, hider_points
        FLAG_CAPTURED = True
        hider_points += 1 # reward the hider
    
def at_finishline():
    pass

# Main loop of the game -----------------------------------------------------------------------------
while running:
    
    screen.fill(BLACK)
    
    # All events
    for event in pygame.event.get():
        # if user quits it
        if event.type == pygame.QUIT:
            running = False
    
    draw_map()

    # get player input
    keys = pygame.key.get_pressed()

    # seeker control
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
    

    # hider control 
    if keys[pygame.K_a]: hider_angle -= 0.1
    if keys[pygame.K_d]: hider_angle += 0.1

    if keys[pygame.K_w]:
        hider_x += -math.sin(hider_angle) * PLAYER_SPEED
        hider_y += math.cos(hider_angle) * PLAYER_SPEED
        if not is_valid(hider_x, hider_y):
            # check x and y and see if it is wall
            # if yes go back to privious x and y
            # if not move
            hider_x -= -math.sin(hider_angle) * PLAYER_SPEED
            hider_y -= math.cos(hider_angle) * PLAYER_SPEED

    if keys[pygame.K_s]:
        hider_x -= -math.sin(hider_angle) * PLAYER_SPEED
        hider_y -= math.cos(hider_angle) * PLAYER_SPEED

        if not is_valid(hider_x, hider_y):
            hider_x += -math.sin(hider_angle) * PLAYER_SPEED
            hider_y += math.cos(hider_angle) * PLAYER_SPEED


    # draw player on map
    draw_player(seeker_x, seeker_y, PEWTER_BLUE)
    
    draw_player(hider_x, hider_y, BLACK)

    draw_FOV(seeker_x, seeker_y, seeker_angle)
    draw_FOV(hider_x, hider_y, hider_angle)
    cast_rays()

    # if the hider is within 10 px of the flag capture it and open exit
    if flag_y - 10 <= hider_y <= flag_y + 10 and flag_x - 10 <= hider_x <= flag_x + 10 and not FLAG_CAPTURED:
        FLAG_CAPTURED = True
        MAP = update_map()
        hider_points += 1
    else:    
        draw_flag()
    
    
    if 750 <= hider_y <= 800 and 240 <= hider_x <= 320 and not FINISHED:
        FINISHED = True
        hider_points += 1
        # reset the game

    
    print( "Seeker's points: ", seeker_points )
    print( "Hider's points: ", hider_points )
    

    # Update display at the end
    pygame.display.flip()
    clock.tick(30)
