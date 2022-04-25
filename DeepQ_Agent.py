# Class for creating the deep neural network
import tensorflow as tf
import numpy as np
from keras.models import Sequential 
from keras.layers import Dense, Dropout, Conv2D, MaxPooling2D, Activation, Flatten, Input
from keras.callbacks import TensorBoard
from keras.optimizers import Adam
from collections import deque

import time

REPLAY_MEMORY_SIZE = 50_000
MODEL_NAME = "256x2" 

# Own Tensorboard class
class ModifiedTensorBoard(TensorBoard):

    # Overriding init to set initial step and writer (we want one log file for all .fit() calls)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.step = 1
        self.writer = tf.summary.FileWriter(self.log_dir)

    # Overriding this method to stop creating default log writer
    def set_model(self, model):
        pass

    # Overrided, saves logs with our step number
    # (otherwise every .fit() will start writing from 0th step)
    def on_epoch_end(self, epoch, logs=None):
        self.update_stats(**logs)

    # Overrided
    # We train for one batch only, no need to save anything at epoch end
    def on_batch_end(self, batch, logs=None):
        pass

    # Overrided, so won't close writer
    def on_train_end(self, _):
        pass

    # Custom method for saving own metrics
    # Creates writer, writes custom metrics and closes writer
    def update_stats(self, **stats):
        self._write_logs(stats, self.step)


class DQNAgent:

    def __init__(self):
        #main model  gets trained every step 
        self.model = self.create_model()

        #target model  this is what we .predict against every step
        self.target_model = self.create_model()
        self.target_model.set_weights(self.model.get_weights())

        self.replay_memory = deque(maxlen = REPLAY_MEMORY_SIZE)

        self.tensorboard = ModifiedTensorBoard(Log_dir= f"logs/{MODEL_NAME}-{int(time.time())}")

        self.target_update_counter = 0

    
# not a cnn : 
# need more info for input
# [ X, Y , theta , dist to the wall in front ]

    def create_model(self):
        model = tf.Sequential()

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

        return model

    def update_replay_memory(self,transition):
        self.replay_memory.append(transition)

    # revisit and update 255 (rgb) -----------------------------------------------------------
    # state : [ X, Y , theta , dist to the wall in front ]
    def get_qs(self, state):
        return self.model(np.array(state).reshape(-1,*state.shape)) # return a 4d vector for each action
    
    def get_action(self, state):
        # get Q on state
        # use tf.argmax for the largest Q value -> make sure it is mapped right
        pass