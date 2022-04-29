from statistics import mode
import main

import random
import pygame
import time

import tensorflow as tf
import numpy as np
from keras.models import Sequential 
from keras.layers import Dense, Dropout, Conv2D, MaxPooling2D, Activation, Flatten, Input
from collections import deque
# from keras.optimizers import Adam

from rl.agents import DQNAgent
from rl.policy import BoltzmannQPolicy
from rl.memory import SequentialMemory

# CONSTANTS --------------------------
NUM_EPISODES = 20

# AI Constants -----
LEARNING_RATE = 0.1
DISCOUNT = 0.95 # how important we find future actions vs current reward, has to be a value between 0 and 1
EPISODES = 2000
SHOW_EVERY = 1000
EPSILON = 0.5


# Run one episode While loop -------
def run_episode():
    # Main game switch ---
    RUNNING = True

    # Game Timer ------
    start = time.time()
    elapsed = 0
    GAME_DURATION = 20 # in seconds

    while RUNNING and elapsed <= GAME_DURATION:
        print(elapsed)
        hider_action = random.randint(0,5)
        seeker_action = 0

        state, reward, done = main.step(hider_action, seeker_action)

        # check the state of the hider
        # print(state, reward, done)

        # All events
        for event in pygame.event.get():
            # if user quits it
            if event.type == pygame.QUIT:
                RUNNING = False
                exit()
        
        # Calculate time passed
        elapsed = time.time() - start



# need more info for input
# [ X, Y , theta , dist to the wall in front ]
def create_model():
    model = Sequential()

    # input layer
    model.add(Input(shape=(4,))) # input = [ X, Y , theta , dist to the wall in front ]

    # hidden 1
    model.add(Dense(128,)) # tweak number
    model.add(Activation('relu'))
    # hidden 2
    model.add(Dense(128,))
    model.add(Activation('relu'))

    #output layer
    model.add(Dense(4,)) # Q values expected for each action

    # Compile the model and calculate its accuracy:
    model.compile(loss='mean_squared_error', optimizer='Adam', metrics=['accuracy'])

    return model

# def build_agent(model, actions):
#     policy = BoltzmannQPolicy()
#     memory = SequentialMemory(limit=50000, window_length=1)
#     dqn = DQNAgent(model=model, memory=memory, policy=policy, 
#                   nb_actions=actions, nb_steps_warmup=10, target_model_update=1e-2)
#     return dqn


# Main Method ------------------------------------------------------------
if __name__ == '__main__':

    # # Run n episodes
    for i in range(NUM_EPISODES):
        run_episode()

        # How are we gonna make these?
        x = [] # states? steps
        y = [] # rewards? for taking those steps?

        model = create_model()
        actions=[0,1,2,3,4]
    

        # dqn = build_agent(model, actions)

        # dqn = build_agent(model, actions)
        # # dqn.compile(Adam(lr=1e-3), metrics=['mae'])
        # # dqn.fit(env, nb_steps50000, visualize=False, verbose=1)


        # # Print a summary of the Keras model:
        model.summary()