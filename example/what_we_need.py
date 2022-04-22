import numpy as np
import matplotlib.pyplot as plt


# save the env
env = gym.make("MountainCar-v0")

# Constants
LEARNING_RATE = 0.1
DISCOUNT = 0.95 # how important we find future actions vs current reward, has to be a value between 0 and 1
EPISODES = 2000
SHOW_EVERY = 1000
EPSILON = 0.5


# we need a for loop to run game multiple times
for episode in range(EPISODES):

    # our reset function needs to communicate that it executed
    # +=1 episode per reset
    episode_reward = 0

    # which episodes to render. don't want to render all because speed
    if episode % SHOW_EVERY == 0:
        render = True
        print(episode)
    else: 
        render = False

    ### inside the for loop we need while loop:
    while not done:
        action = np.argmax(qs_fromNN) # qs_fromNN = are the q values that we get from neural network

        # we take the action inside the step function.
        # save the new states and reward done
        new_state, reward, done = env.step(action)

        episode_reward += reward

        # if we decide to show the game
        if render: 
            env.render()


        # follow the Q value formula
        # Q(State, action) = Qold(S,a) + LearningRate * (reward + DISCOUNT * MAX( Q(state_t+1, a) - Q(s,a)))
        new_Q = current_q + LEARNING_RATE * (reward + DISCOUNT * max_future_q)


        # decay epsilon

        