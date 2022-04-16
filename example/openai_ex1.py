# Solve the open AI car and the hill
import gym 
import numpy as np
import matplotlib.pyplot as plt


env = gym.make("MountainCar-v0")


LEARNING_RATE = 0.1
DISCOUNT = 0.95 # how important we find future actions vs current reward, has to be a value between 0 and 1
EPISODES = 2000
SHOW_EVERY = 1000

# print(env.observation_space.high) # highest q value {pos, vel}
# print(env.observation_space.low) #lowest q value
# print(env.action_space.n) # num of actions possible

DISCRETE_OS_SIZE = [40] * len(env.observation_space.high) # q table size that is managable 
discrete_os_win_size = (env.observation_space.high - env.observation_space.low) / DISCRETE_OS_SIZE # "bucket size" to round up 


epsilon = 0.5
START_EPSILON_DECAYING = 1
END_EPSILON_DECAYING = EPISODES // 2
epsilon_decay_value = epsilon/(END_EPSILON_DECAYING - START_EPSILON_DECAYING)

q_table = np.random.uniform(low = -2, high = 0, size = (DISCRETE_OS_SIZE + [env.action_space.n]))

ep_reward = []
aggr_ep_rewards = {'ep':[], 'avg':[], 'min':[], 'max':[]}




def get_discrete_state(state):
    discrete_state= (state - env.observation_space.low)/ discrete_os_win_size
    return tuple(discrete_state.astype(np.int)) # np.int is a discrete state


for episode in range(EPISODES):
    episode_reward = 0

    if episode % SHOW_EVERY == 0:
        render = True
        print(episode)
    else: 
        render = False

    discrete_state = get_discrete_state(env.reset()) # env.reset return four initial values



    done = False

    while not done:
        action = np.argmax(q_table[discrete_state])  # moves right (predefined openai)
        # new_state = pos, velocity 
        new_state, reward, done, _ = env.step(action) #todo : create our own step function in main, have it return this

        episode_reward += reward

        new_discrete_state = get_discrete_state(new_state)
    
        if render: 
            env.render()
        if not done:
            max_future_q = np.max(q_table[new_discrete_state])
            current_q = q_table[discrete_state + (action, )] #get q value for specific action, rather than all q values for all actions

            new_q = (1 - LEARNING_RATE) * current_q + LEARNING_RATE * (reward + DISCOUNT * max_future_q) # formula for calculating all q values
            q_table[discrete_state + (action, )] = new_q # update that specific q value in table (backpropagation)
        elif new_state[0] >= env.goal_position:
            q_table[discrete_state + (action, )] = 0 
        
        discrete_state = new_discrete_state
    

    if END_EPSILON_DECAYING >= episode >= START_EPSILON_DECAYING:
        epsilon -= epsilon_decay_value

    ep_reward.append(episode_reward)

    if episode % SHOW_EVERY == 0:
        # pick out the last 500 everytime, not hardcoded
        avg_reward = sum(ep_reward[-SHOW_EVERY:])/len(ep_reward[-SHOW_EVERY:])
        aggr_ep_rewards['ep'].append(episode)
        aggr_ep_rewards['avg'].append(avg_reward)
        aggr_ep_rewards['min'].append(min(ep_reward[-SHOW_EVERY:]))
        aggr_ep_rewards['max'].append(max(ep_reward[-SHOW_EVERY:]))

    print(f'episode: {episode}, avg: {avg_reward}, min: {min(ep_reward[-SHOW_EVERY:])}, max: {max(ep_reward[-SHOW_EVERY:])}')
    
    # save Q-tables every 10:
    # if episode % 10 == 0:
    #     # make dir name qtable/EpisodeNumber , q_table is what is saved
    #     np.save(f'../qtable/{episode}-qtable.npy', q_table)

env.close()

plt.plot(aggr_ep_rewards['ep'], aggr_ep_rewards['avg'], label= 'avg')
plt.plot(aggr_ep_rewards['ep'], aggr_ep_rewards['min'], label= 'min')
plt.plot(aggr_ep_rewards['ep'], aggr_ep_rewards['max'], label= 'max')
plt.legend(loc=4)
plt.show()