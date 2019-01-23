# coding=utf-8

"""
This part of code is the Q learning brain, which is a brain of the agent.
All decisions are made in here.
View more on my tutorial page: https://morvanzhou.github.io/tutorials/
"""

import numpy as np
import pandas as pd
import tensorflow as tf


np.random.seed(1)
tf.set_random_seed(1)


# deep Q Network off-policy
class DeepQNetwork:
    def __init__(
            self,
            n_actions,
            n_features,
            learning_rate=0.01,
            reward_decay=0.9,   # gamma
            e_greedy=0.9,
            replace_target_iter=300,    # 隔多少步之后 把 target net 的参数变成最新的参数
            memory_size=500,        # 记忆库容量, (多少条 state?)
            batch_size=32,
            e_greed_increment=None,
            output_graph=False
    ):
        self.n_actions = n_actions
        self.n_features = n_features
        self.lr = learning_rate
        self.gamma = reward_decay
        self.epsilon_max = e_greedy
        self.replace_target_iter = replace_target_iter
        self.memory_size = memory_size
        self.batch_size = batch_size
        self.epsilon_increment = e_greed_increment
        self.epsilon = 0 if e_greed_increment is not None else self.epsilon_max

        # total learning step
        self.learn_step_counter = 0  # 要根据 step 不断提高 self.spsilon

        # initialize zero memory [s, a, r, s_]
        # self.memory = pd.DataFrame(np.zeros(self.memory_size, n_features * 2 + 2))
        self.memory = np.zeros((self.memory_size, n_features * 2 + 2))

        # consist of [target_net, evaluate_net]
        self._build_net()

        self.session = tf.Session()


        if output_graph:
            # $ tensorboard -- logdir=logs
            # tf.train.SummaryWriter soon be deprecated, use following
            tf.summary.FileWriter("logs/", self.session.graph)

        self.session.run(tf.global_variables_initializer())
        self.cost_his = []


    def _build_net(self):
        # ---------------------- build evaluate_net --------------
        self.s = tf.placeholder(tf.float32, [None, self.n_features], name='s')  # input
        self.q_target = tf.placeholder(tf.float32, [None, self.n_actions], name='Q_target')  # for calculation q value
        with tf.variable_scope('eval_net'):
            # c_names(collections_names) are the collections to store variables
            c_names, n_l1, w_initializer, b_initializer = \
                ['eval_net_params', tf.GraphKeys.GLOBAL_VARIABLES], 20, \
                tf.random_normal_initializer(0., 0.3), tf.constant_initializer(0.1)  # config of layers


            # first layer, collections is used later when assign to target net
            with tf.variable_scope('l1'):
                w1 = tf.get_variable('w1', [self.n_features, n_l1], initializer=w_initializer, collections=c_names)
                b1 = tf.get_variable('b1', [1, n_l1], initializer=b_initializer, collections=c_names)
                l1 = tf.nn.relu(tf.matmul(self.s, w1) + b1)    # 有多少个行为输出多少个值, 作为 该 state 的Q 值

            # second layer, collections is used later when assign to target net
            with tf.variable_scope('l2'):
                w2 = tf.get_variable('w2', [n_l1, self.n_actions], initializer=w_initializer, collections=c_names)
                b2 = tf.get_variable('b2', [1, self.n_actions], initializer=b_initializer, collections=c_names)
                self.q_eval = tf.matmul(l1, w2) + b2   # Q 估计, 下一步搞 Q 现实 self.q_target


        with tf.name_scope('loss'):
            self.loss = tf.reduce_sum(tf.squared_difference(self.q_target, self.q_eval))
        with tf.variable_scope('train'):
            self._train_op = tf.train.RMSPropOptimizer(self.lr).minimize(self.loss)

        # ---------------------- build target_net ---------------
        self.s_ = tf.placeholder(tf.float32, [None, self.n_features], name='s_')    # input s_ , 是下一个 state 的观测值
        with tf.variable_scope('target_net'):
            # c_name(collections_names) are the collection to store variables
            c_names = ['target_net_params', tf.GraphKeys.GLOBAL_VARIABLES]

            # first layer, collections is used later when assign to target net
            with tf.variable_scope('l1'):
                w1 = tf.get_variable('w1', [self.n_features, n_l1], initializer=w_initializer, collections=c_names)
                b1 = tf.get_variable('b1', [1, n_l1], initializer=b_initializer, collections=c_names)
                l1 = tf.nn.relu(tf.matmul(self.s_, w1) + b1)

            # second layer, collections is used later when assign to target net
            with tf.variable_scope('l2'):
                w2 = tf.get_variable('w2', [n_l1, self.n_actions], initializer=w_initializer, collections=c_names)
                b1 = tf.get_variable('b2', [1, n_l1], initializer=b_initializer, collections=c_names)
                self.q_next = tf.matmul(l1, w2) + b2




    """ 存储记忆(transition) """
    def store_transition(self, s, a, r, s_):    # s_ 下一次的 观测值
        if not hasattr(self, 'memory_counter'):
            self.memory_counter = 0

        transition = np.hstack((s, [a, r], s_))  # 第 0 行 插入 transition

        # replace the old memory with new memory
        # 这里是设定 当 存储库满了之后 再重头存储到 index 中
        index = self.memory_counter % self.memory_size
        self.memory.iloc[index, :] = transition

        self.memory_counter += 1


    """ 选择动作 """
    def choose_action(self, observation):
        # to have batch dimension when feed into tf placeholder
        observation = observation[np.newaxis, :]    # 为了 tf 能够处理, 所以需要 新增一个维度

        if np.random.uniform() < self.epsilon:
            # forward feed the observation and get q value for every actions
            actions_value = self.session.run(self.q_eval, feed_dict={self.s: observation})
            action = np.argmax(actions_value)
        else:
            action = np.random.randint(0, self.n_actions)
        return action

    """ 把最新的参数放到 Q 现实的神经网络中 """
    def _replace_target_params(self):
        t_params = tf.get_collection('target_net_params')   # 能够调用到所有的 已经添加到 target_net_params 的参数
        e_params = tf.get_variable('eval_net_params')

        # 对每一个 e_params 赋值 到 每一个 t_params 当中去
        self.session.run(tf.assign(t, e) for t, e in zip(t_params, e_params))

    def learn(self):
        # check to replace target parameters
        if self.learn_step_counter % self.replace_target_iter == 0:
            self._replace_target_params()
            print('\ntarget_params_replaced\n')

        # sample batch memory from all memory, 调用记忆库中的记忆
        batch_memory = self.memory.sample(self.batch_size) \
            if self.memory_counter > self.memory_size \
            else self.memory.iloc[:self.memory_counter].sample(self.batch_size, replace=True)

        q_next, q_eval = self.session.run(
            [self.q_next, self.q_eval],
            feed_dict={
                self.s_: batch_memory.iloc[:, -self.n_features],
                self.s: batch_memory.iloc[:, self.n_features]
            })

        # change q_target w.r.t q_eval's action
        batch_index = np.arange(self.batch_size, dtype=np.int32)
        eval_act_index = batch_memory[:, self.n_features].astype(int)
        reward = batch_memory[:, self.n_features + 1]
        q_target = q_eval.copy()
        q_target[batch_index, eval_act_index] = reward + self.gamma * np.max(q_next, axis=1)

        """
            Fro example in this batch I have 2 samples and 3 actions
            q_eval = 
            [[1, 2, 3], 
            [4, 5, 6]]
            
            q_target = q_eval = 
            [[1, 2, 3], 
            [4, 5, 6]]
            
            Then change q_target with the real q_target value w.r.t and the q_eval's action.
            Fro example in :
                sample 0, I took action 0, and the max q_target value is -1;
                sample 1, I took action 2, and the max q_target value is -2;
                
            q_target = 
            [[-1, 2, 3], 
            [4, 5, -2]]
            
            So the [q_target - q_eval] becomes:
            [[(-1)-(-1), 0, 0],
            [0 , 0 (-2)-(6)]]
            
            We then back propagate this error w.r.t the corresponded action to 
            leave other action as error=0 cause we didn't choose i.
            
        """

        # train eval network
        _, self.cost = self.session.run([self._train_op, self.loss],
                                        feed_dict={self.s: batch_memory.iloc[:, :self.n_features],
                                                   self.q_target: q_target})

        self.cost_his.append(self.cost)

        # increasing epsilon
        self.epsilon = self.epsilon + self.epsilon_increment if self.epsilon < self.epsilon_max else self.epsilon_max
        self.learn_step_counter += 1


    """ 展示 cost 曲线 """
    def plot_cost(self):
        import matplotlib.pyplot as plt
        plt.plot(np.arange(len(self.cost_his)), self.cost_his)
        plt.show()






















