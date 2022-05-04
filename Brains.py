import math
import random
import time
import pygame

import tensorflow as tf
from tensorflow import keras
import numpy as np
import keras
from keras.models import Sequential 
from keras.layers import Dense, Dropout, Conv2D, MaxPooling2D, Flatten,Activation, Input
from keras.losses import mse
from keras import layers
import main

class brains:
    
    def __init__(self):
        # Keras internal modifications
        self.loss_function = keras.losses.Huber()
        self.optimizer = tf.keras.optimizers.Adam(learning_rate=0.00025, clipnorm=1.0)

        # CONSTANTS
        self.DISCOUNT = 0.99
        self.EPISODES = 2000
        self.episode_rewards = 0 
        self.EP_REWARD_HISTORY = []

        # How often to update the target network
        self.UPDATE_TARGET_EVERY = 10000
        self.ACTIONS = [0,1,2,3,4]
        self.UPDATE_EVERY_STEP = 5 # because the step sizes are small

        # epsilon
        self.EPSILON = 0.2 # chaneg to 1.0
        self.EPSILON_INTERVAL = 0.9

        # Memory buffer
        self.replay_buffer = []
        self.batch_size = 100
        self.max_size = 100000

        # models
        self.model = self.create_model()
        self.target_model = self.create_model() 

    def create_model(self):
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

    def Q (self, state):
        state_tensor = tf.convert_to_tensor(state)
        state_tensor = tf.expand_dims(state_tensor, 0)
        action_probs = self.model(state_tensor, training = False)
        # insert model here, q_values is a list
        # q_values = self.model.predict(state)
        return tf.argmax(action_probs[0]).numpy()

    def get_action(self, state, EPSILON):
        if random.random() < EPSILON:
            return random.choice(self.ACTIONS)
        else:
            return self.Q(state)

    def train(self, NUM_EPISODES, EP_DURATION, hider_start_state, seeker_start_state, step, reset):
        #  run n episodes
        for ep in range(NUM_EPISODES):
            start = time.time()
            elapsed = 0
            GAME_DURATION = EP_DURATION # in seconds
            running = True
            steps = 0
            episode_reward = 0

            reset # reset the game
            
            # The current state is the initial position for hider here
            current_state = (hider_start_state[0], hider_start_state[1], hider_start_state[2], math.inf)

            # Run each game and check time limit
            while running and elapsed <= GAME_DURATION:

                if elapsed % 10 == 0: print(f"\nTime passed {elapsed}s\n")

                ######## See if player hit Quit button
                for event in pygame.event.get():
                    # if user quits it
                    if event.type == pygame.QUIT:
                        running = False

                ######## get action for each actor
                hider_action = self.get_action(current_state, self.EPSILON)
                seeker_action = 0

                ######## Decay the epsilon to take less random choices
                # self.EPSILON -= self.epsilon_interval / epsilon_greedy_frames
                # self.EPSILON = max(epsilon, epsilon_min)
                
                ######## take step
                next_state, reward, done = step(hider_action, seeker_action)
                if done: running = False
                next_state = np.array(next_state)
                self.episode_rewards += reward 
                steps += 1

                ######## add to buffer for hider
                self.replay_buffer.append(current_state, hider_action, reward, next_state)
                # Update current state
                current_state = next_state
                
                # update every 5th step (because step size too small), and once the batch size > 100
                if steps % self.UPDATE_EVERY_STEP == 0 and len(self.replay_buffer) > self.batch_size:
                    # select random indecies for picking the samples from batch:
                    indices = np.random.choice(range(len(self.replay_buffer)), size=self.batch_size)

                    ######## select sample of random states
                    # S,a,r,S'
                    current_state_sample, hider_action_sample, reward_sample, next_state_sample = [self.replay_buffer[i] for i in indices]

                    # Build the updated Q-values for the sampled future states
                    # Use the target model for stability
                    future_rewards = self.target_model.predict(next_state_sample)
                    updated_q_values = reward_sample + self.DISCOUNT * tf.reduce_max(future_rewards, axis=1)
                    

                    # Create a mask so we only calculate loss on the updated Q-values
                    masks = tf.one_hot(hider_action_sample, len(self.ACTIONS))
                    
                    with tf.GradientTape() as tape:
                        q_values = self.model(current_state_sample)
                        # Calculate loss between new Q-value and old Q-value
                        # Apply the masks to the Q-values to get the Q-value for action taken
                        q_action = tf.reduce_sum(tf.multiply(q_values, masks), axis=1)

                        loss = self.loss_function(updated_q_values, q_action)
                    
                    # Backpropagation
                    grads = tape.gradient(loss, self.model.trainable_variables)
                    self.optimizer.apply_gradients(zip(grads, self.model.trainable_variables))
                
                if steps % self.UPDATE_TARGET_EVERY == 0:
                    # update the the target network with new weights
                    self.target_model.set_weights(self.model.get_weights())
                    # Log details
                    template = "episode rewards: {:.2f} at episode: {} of {}, steps so far: {}"
                    print(template.format(self.episode_rewards, ep, NUM_EPISODES, steps))

                if len(self.replay_buffer) > self.max_size:
                    del self.replay_buffer[:1] 

            # record the episode rewards to monitor improvements
            self.EP_REWARD_HISTORY.append(reward)
            
            
            # Calculate time passed
            elapsed = time.time() - start
            if elapsed >= GAME_DURATION:
                reset()
                running = False


        # Display the summery of the model trained.   
        self.model.summery()

# if __name__ == '__main__':

#     brain = brains()

#     print(brain.model.summary())
#     print(brain.target_model.summary())

#     hider_start_state = (main.HIDER_START_POS[0],main.HIDER_START_POS[1],main.PLAYER_START_ANGLE)
#     seeker_start_state = (main.SEEKER_START_POS[0],main.SEEKER_START_POS[1],main.PLAYER_START_ANGLE)
#     brain.train(10, 10, hider_start_state, seeker_start_state, main.step(0,0), main.reset())