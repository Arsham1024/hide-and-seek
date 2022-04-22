from os import system
from sys import flags
from tkinter.tix import MAIN
from turtle import update, window_width
from pip import main
import pygame
import random
import math

# needs to be on every game
pygame.init()
running = True
pygame.display.set_caption("HIDE AND SEEK")

# Global REWARDS -----------------------------------------------------------------------------
NEAR_WALL = -1
# hider's rewards
GOT_THE_FLAG = 50
HIDER_WINS = 100
HIDER_LOSES = -200
# seeker's rewards
SEEKER_WINS = 150
SEEKER_LOSES = -200

NOT_MOVING = -2
MOVING = -1

# Global CONSTANTS -----------------------------------------------------------------------------
# everything depends on the window width
WINDOW_WIDTH = 800
WINDOW_HEIGHT = WINDOW_WIDTH # make sure the window is a square!
MAP_SIZE = int(WINDOW_WIDTH / 80) # number of rows and cols
TILE_SIZE = int(WINDOW_WIDTH/MAP_SIZE)
NUM_TILES = MAP_SIZE ** 2

PLAYER_DIAMETER = 10
PLAYER_START_ANGLE = math.pi
SEEKER_START_POS = (200,120)
HIDER_START_POS = (680, 680)

FOV = math.pi /3 #60 deg
HALF_FOV = FOV/2
CASTED_RAYS = 120
STEP_ANGLE = FOV/CASTED_RAYS
MAX_DEPTH = 240 # depth of FOV

PLAYER_SPEED = 5
FLAG_CAPTURED = False

ACTION_TIME = 0.5

# End game conditions, IF EITHER IS TRUE GAME IS OVER
HIDER_WINS = False
SEEKER_WINS = False

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
seeker_x, seeker_y = SEEKER_START_POS[0], SEEKER_START_POS[1]
hider_x, hider_y = HIDER_START_POS[0], HIDER_START_POS[1]

hider_angle, seeker_angle = PLAYER_START_ANGLE, PLAYER_START_ANGLE

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
    '###!######')

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

def reset():
    global SEEKER_START_POS, HIDER_START_POS,HIDER_WINS, SEEKER_WINS, seeker_x, seeker_y, hider_x, hider_y, MAP, seeker_angle, hider_angle
    seeker_x, seeker_y = SEEKER_START_POS[0], SEEKER_START_POS[1]
    hider_x, hider_y = HIDER_START_POS[0], HIDER_START_POS[1] 
    seeker_angle, hider_angle = PLAYER_START_ANGLE, PLAYER_START_ANGLE

    SEEKER_WINS = False
    HIDER_WINS = False

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
    '##########')

# ray casting algorithm - for seeker
def cast_rays_seeker():
    global SEEKER_WINS, seeker_points
    start_angle = seeker_angle - HALF_FOV

    # for all casted rays 
    for ray in range (CASTED_RAYS):
        for depth in range(MAX_DEPTH):
            # coordinates of the end of the ray, grows per frame rate
            target_x = seeker_x - math.sin(start_angle) * depth
            target_y = seeker_y + math.cos(start_angle) * depth

            # capture the hider if in range
            if target_y - 1 <= hider_y <= target_y + 1 and target_x - 1 <= hider_x <= target_x + 1:
                seeker_points += 2
                SEEKER_WINS = True
                # these loops are too fast for the reset() call. so we need to return and end it.
                return SEEKER_WINS
             
            # if the index bigger than 100 because of the exit
            if not is_valid(target_x, target_y):
                break
            
            #draw casted ray 
            pygame.draw.line(screen, ANTIQUE_BRASS, (seeker_x, seeker_y), (target_x, target_y))

        # increment casted ray angle
        start_angle += STEP_ANGLE

# ray casting algorithm - for hider
def cast_rays_hider():
    global hider_points, NUM_TILES
    start_angle = hider_angle - HALF_FOV
    dist_towall = math.inf

    for depth in range(MAX_DEPTH):
        # the tip of the ray as it is expanding
        target_x = hider_x - math.sin(start_angle) * depth
        target_y = hider_y + math.cos(start_angle) * depth

        # find index of the tile
        col = int(target_x / TILE_SIZE)
        row = int(target_y / TILE_SIZE)
        index_square = row * (MAP_SIZE) + col
        
        if index_square >= NUM_TILES:
            break

        # if the ray hits a wall then calculate the disance to the wall and return it.
        elif MAP[index_square] == "#":
            dist_towall = int(math.dist([hider_x, hider_y], [target_x, target_y]))
            # if we are too close to the wall then neg rewards
            if dist_towall <= 50:
                hider_points += NEAR_WALL

    # for all casted rays 
    for ray in range (CASTED_RAYS):
        for depth in range(MAX_DEPTH):
            # coordinates of the end of the ray, grows per frame rate
            target_x = hider_x - math.sin(start_angle) * depth
            target_y = hider_y + math.cos(start_angle) * depth
                
            # if the index bigger than 100 because of the exit
            if not is_valid(target_x, target_y):
                break
        
            #draw casted ray 
            pygame.draw.line(screen, ANTIQUE_BRASS, (hider_x, hider_y), (target_x, target_y))

        # increment casted ray angle
        start_angle += STEP_ANGLE

    return dist_towall

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
    

def get_key(action):
    if action == 0:
        return
    elif action == 1:
        return
    elif action == 2:
        return
    elif action == 3:
        return
    else:
        return 
        

# Main loop of the game -------------------------------------------------------------------------------
# this function is called as oppose to loop. we need to get deep neural network's decision for each move
# action (int) : between 0-4.
# 0 = left
# 1 = up
# 2 = right
# 3 = down
# 4 = don't move

def step(action):
    global SEEKER_START_POS, HIDER_START_POS, HIDER_WINS, SEEKER_WINS, seeker_x, seeker_y, hider_x, hider_y, MAP, seeker_angle, hider_angle, hider_points
    screen.fill(BLACK)

    draw_map()

    # get player input
    keys = pygame.key.get_pressed()

    # ------------- seeker control -------------
    if keys[pygame.K_LEFT] : seeker_angle -= 0.1 # left
    if keys[pygame.K_RIGHT] : seeker_angle += 0.1 # right

    # up
    if keys[pygame.K_UP]:
        seeker_x += -math.sin(seeker_angle) * PLAYER_SPEED
        seeker_y += math.cos(seeker_angle) * PLAYER_SPEED
        if not is_valid(seeker_x, seeker_y):
            # check x and y and see if it is wall
            # if yes go back to privious x and y
            # if not move
            seeker_x -= -math.sin(seeker_angle) * PLAYER_SPEED
            seeker_y -= math.cos(seeker_angle) * PLAYER_SPEED

    # down
    if keys[pygame.K_DOWN]:
        seeker_x -= -math.sin(seeker_angle) * PLAYER_SPEED
        seeker_y -= math.cos(seeker_angle) * PLAYER_SPEED

        if not is_valid(seeker_x, seeker_y):
            seeker_x += -math.sin(seeker_angle) * PLAYER_SPEED
            seeker_y += math.cos(seeker_angle) * PLAYER_SPEED
    
    # don't move
    else: pass

    # ------------- hider control -------------
    if action == 0: hider_angle -= 0.1 # turn left
    if action == 2: hider_angle += 0.1 # turn right

    # go up
    if action == 1:
        hider_x += -math.sin(hider_angle) * PLAYER_SPEED
        hider_y += math.cos(hider_angle) * PLAYER_SPEED
        if not is_valid(hider_x, hider_y):
            # check x and y and see if it is wall
            # if yes go back to privious x and y
            # if not move
            hider_x -= -math.sin(hider_angle) * PLAYER_SPEED
            hider_y -= math.cos(hider_angle) * PLAYER_SPEED

    # go down
    if action == 3:
        hider_x -= -math.sin(hider_angle) * PLAYER_SPEED
        hider_y -= math.cos(hider_angle) * PLAYER_SPEED

        if not is_valid(hider_x, hider_y):
            hider_x += -math.sin(hider_angle) * PLAYER_SPEED
            hider_y += math.cos(hider_angle) * PLAYER_SPEED

    # don't move
    else: pass

    # draw player on map
    draw_player(seeker_x, seeker_y, PEWTER_BLUE)
    
    draw_player(hider_x, hider_y, BLACK)

    draw_FOV(seeker_x, seeker_y, seeker_angle)
    draw_FOV(hider_x, hider_y, hider_angle)
    
    # player vision being drawn
    SEEKER_WINS = cast_rays_seeker()
    dist_towall = cast_rays_hider()


    # if the hider is within 10 px of the flag capture it and open exit
    if flag_y - 10 <= hider_y <= flag_y + 10 and flag_x - 10 <= hider_x <= flag_x + 10:
        FLAG_CAPTURED = True
        MAP = update_map()
        hider_points += 1
    else:    
        draw_flag()
    
    # hider makes it to exit without being captured
    if 750 <= hider_y <= 800 and 240 <= hider_x <= 320:
        HIDER_WINS = True
        hider_points += 1

    # check if anyone won the game
    if HIDER_WINS or SEEKER_WINS:    
        done = True
        reset()
    else: 
        done = False
    
    
    # display the points
    # print( "Seeker's points: ", seeker_points )
    # print( "Hider's points: ", hider_points )

    # Update display at the end
    pygame.display.flip()
    clock.tick(60) #run faster

    return (hider_x, hider_y, hider_angle, dist_towall), done



################## Main Method #######################
if __name__ == "__main__":
    while running:
        action = random.randint(0,5)

        state, done = step(action)

        

            # All events
        for event in pygame.event.get():
            # if user quits it
            if event.type == pygame.QUIT:
                running = False

        