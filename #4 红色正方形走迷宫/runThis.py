# coding=utf-8

"""
Reinforcement learning maze example.
Red rectangle:          explorer.
Black rectangles:       hells       [reward = -1].
Yellow bin circle:      paradise    [reward = +1].
All other states:       ground      [reward = 0].
This script is the main part which controls the update method of this example.
The RL is in RL_brain.py.
View more on my tutorial page: https://morvanzhou.github.io/tutorials/
"""

from maze_env import Maze
from RL_brain import QLearningTable

def update():
    for episode in range(100):  # 100回合
        # initial observation
        observation = env.reset()   # 环境观测值, 红正方形所在位置的坐标 初始 [1, 1]

        print('episode: ', episode)
        while True:
            # fresh env
            env.render()    # 每回合没有结束的时候要刷新一下

            # RL choose action based on observation
            action = RL.choose_action(str(observation))  # 基于观测值str(observation) 挑选动作, 在table中可以当做是索引

            # RL take action and get next observation and reward
            observation_, reward, done = env.step(action)  # 施加动作, 并获得施加动作后的 reward 和 observation (奖励和观测值), done 就是标示是否结束(跳坑或者拿到到达黄色圆圈)

            # RL learn from this transition
            RL.learn(str(observation), action, reward, str(observation_))   # 从 (第一个观测值, 基于第一个观测值施加的动作, 施加动作后的reward, 试驾动作后的新观测值) 进行学习

            # swap observation
            observation = observation_  # 进入下一个循环前, 把新观测值 赋值给 就的观测值变量

            # break while loop when end of this episode
            if done:
                print('Done! ', 'episode: ', episode, 'state: ', observation)
                print(RL.q_table)
                break

    # end of game
    print('game over')
    env.destroy()

if __name__ == '__main__':
    env = Maze()
    RL = QLearningTable(actions=list(range(env.n_actions)))

    env.after(100, update)
    env.mainloop()























































































































