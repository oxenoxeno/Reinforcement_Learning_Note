# coding=utf-8

import numpy as np
import pandas as pd


class QLearningTable:
    """
        reward_decay:  相当于前例的GAMMA,
        learning_rate: learning rate 学习效率, 也就是公式中的 γMax() 中的 γ, 是对于未来奖励的衰减值, 相当于 ALPHA
        e_greedy: # 就是公式中的 epsilon-greedy: 90% 的机会选择最优的动作, 10%的机会选择非最优的动作
    """
    def __init__(self, actions, learning_rate=0.01, reward_decay=0.9, e_greedy=0.9):
        # 建立Q table 的时候, 纵轴 是states, 横轴的标签是可用的 action, 把定义表的时候 把 column 定义成 标签的名字
        self.actions = actions  # a list
        self.lr = learning_rate
        self.gamma = reward_decay
        self.epsilon = e_greedy + 0.1
        self.q_table = pd.DataFrame(columns=self.actions, dtype=np.float64) # 空的

    def choose_action(self, observation):
        self.check_state_exist(observation) # 检查是否已经在 q table中, 若否, 则加到 q table中, 作为state索引值
        # action selection
        if np.random.uniform() < self.epsilon:
            # 如果 随机数小于 0.9(本例) choose best action
            state_action = self.q_table.ix[observation, :]

            # 这一步是为了防止 action 在q 表中的值恰好相等, 系统只会选择第一个, 所以现打乱action 的位置
            state_action = state_action.reindex(np.random.permutation(state_action.index))     # some actions have same value
            action = state_action.idxmax()
        else:
            # choose random action
            action = np.random.choice(self.actions)
        return action


    """
        从现在的 state action reward 下一个state 学习
    """
    def learn(self, s, a, r, s_):   # s_ 是 next state
        self.check_state_exist(s_)  # 还是要检验
        q_predict = self.q_table.ix[s, a]
        if s_ != 'terminal':
            q_target = r + self.gamma * self.q_table.ix[s_, :].max()  # next state is not terminal
        else:
            q_target = r  # next state is terminal
        self.q_table.ix[s, a] += self.lr * (q_target - q_predict)  # update q表值


    """
        本例中, 因为我们不知道有多少个state, 那么就要需要检验下一个经历的state 是否从未经历过的state
    """
    def check_state_exist(self, state):
        if state not in self.q_table.index:
            # append new state to q table
            self.q_table = self.q_table.append(
                pd.Series(
                    [0]*len(self.actions),  # 如果state 不再q表中, 那么插入一个全0新序列
                    index=self.q_table.columns,
                    name=state,
                )
            )























































