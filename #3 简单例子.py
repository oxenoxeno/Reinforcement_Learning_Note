# coding=utf-8

import numpy as np
import pandas as pd
import time             # 控制探索者移动的模块

np.random.seed(2)   # reproducible  种子

N_STATES = 8                    # the length of the 1 dimensional world
ACTIONS = ['left', 'right']     # available actions
EPSILON = 0.9                   # 就是公式中的 epsilon-greedy: 90% 的机会选择最优的动作, 10%的机会选择非最优的动作
ALPHA = 0.1                     # learning rate 学习效率, 也就是公式中的 γMax() 中的 γ, 是对于未来奖励的衰减值
GAMMA = 0.9                    # discount factor
MAX_EPISODES = 200               # 最大允许的尝试回合数
FRESH_TIME = 0.00                # 走一步的间隔


""" 建立 Q Table """


def build_q_table(n_state, actions):
    table = pd.DataFrame(
        np.zeros((n_state, len(actions))),      # q_table initial values
        columns=actions,                        # action's name
    )
    # print(table)    # show table
    # print
    return table




# build_q_table(N_STATES, ACTIONS)  # 纵轴是 states, 横轴是 actions

"""
    选择动作 
"""
def choose_action(state, q_table):
    # 根据
    # this is how to choose an action
    state_actions = q_table.iloc[state, :]  # 根据 state 选择 Q table 相应行的 left right 分数到 state_actions
    if (np.random.uniform() > EPSILON) or (state_actions.all() == 0):  # act non-greedy or state-action
        action_name = np.random.choice(ACTIONS)
    else:   # act greedy
        action_name = state_actions.idxmax()    # .argmax() 就是返回调用者里面最大的一个的 index name, 这里是 left 或者 right
    return action_name



""" 创建环境 和环境的 feed back """
def get_env_feedback(S, A):
    # This is how agent will interact with the environment
    if A =='right':  # move right
        if S == N_STATES - 2:  # terminal
            S_ = 'terminal'
            R = 1   # reward, 也就是 算法公式中, 在选择了一个Action 后, 所返回的一个reward 和 一个state
        else:
            S_ = S + 1
            R = 0

    else:   # move left
        R = 0
        if S == 0:
            S_ = S  # reach the wall
        else:
            S_ = S - 1

    return S_, R




""" 
    建立环境
    不必在意代码, 这里的作用是 让 '--------T' 探索者在 一维的环境中移动 
"""


def update_env(S, episode, step_counter):
    # This is how environment be update
    env_list = ['-'] * (N_STATES - 1) + ['T']   # '--------T' out environment
    if S == 'terminal':
        interaction = 'Episode %s: total_steps = %s' % (episode + 1, step_counter)
        print('\r{}'.format(interaction))
        # time.sleep(2)
        print('\r                       ')

    else:
        env_list[S] = 'o'
        interaction = ''.join(env_list)
        print('\r{}'.format(interaction))
        time.sleep(FRESH_TIME)




""" 主循环 """


def reinforcement_learning():
    # main part of RL loop
    q_table = build_q_table(N_STATES, ACTIONS)  # 创建 q table



    for episode in range(MAX_EPISODES):
        step_counter = 0
        S = 0   # 让初始 state 为0, 让探索者放在最左边
        is_terminated = False   # 判断是否终止符号, 如果是终止符就结束这一回合
        update_env(S, episode, step_counter)
        while not is_terminated:

            A = choose_action(S, q_table)
            S_, R = get_env_feedback(S, A) # take action & get next state
            q_predict = q_table.ix[S, A]
            if S_ != 'terminal':
                q_target = R + GAMMA * q_table.iloc[S_, :].max()  # next action
            else:
                q_target = R    # next state is terminal
                is_terminated = True

            # 下一步
            q_table.ix[S, A] += ALPHA * (q_target - q_predict)  # update
            S = S_  # move to next state

            update_env(S, episode, step_counter + 1)
            step_counter += 1

    return q_table  # 为了训练完之后 看一下 q table 里面的样子


if __name__ == '__main__':
    q_table = reinforcement_learning()

    # 看一下训练好之后的 q_table
    print('\r\nQ-table:\n')
    print(q_table)















