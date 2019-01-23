# coding=utf-8

import random



Q = [[random.uniform(0, 1),
     random.uniform(0, 1),
     random.uniform(0, 1),
     random.uniform(0, 1),
     random.uniform(0, 1),
     random.uniform(0, 1),
     random.uniform(0, 1),
     random.uniform(0, 1),
     random.uniform(0, 1),
     random.uniform(0, 1)],

     [random.uniform(0, 1),
     random.uniform(0, 1),
     random.uniform(0, 1),
     random.uniform(0, 1),
     random.uniform(0, 1),
     random.uniform(0, 1),
     random.uniform(0, 1),
     random.uniform(0, 1),
     random.uniform(0, 1),
     random.uniform(0, 1)],
     ]

# print(Q)
world = '-------T'
end = False
learningRate = 0.1
discount = 0.9
position = 0
R = -1
action = -1
steps = 0
direction = -1
left = 0
right = 1
now = ''

for _ in range(100):
    while True:
        now = ''
        steps += 1
        action = - 1 if Q[0][position] > Q[1][position] else 1
        if action == -1:
            direction = left
            if random.uniform(0, 1) < 0.05:
                direction = right
                action = 1
        else:
            direction = right
            if random.uniform(0, 1) < 0.05:
                direction = left
                action = -1

        if direction == right:
            R = 1
        else:
            R = 0

        position = position + action

        if position < 0:
            position = 0

        # print(position)

        if position == 10:
            position = 0
            print('Round ', _ + 1, 'end!', 'Steps used: ', steps)
            Q[direction][position] += (R * learningRate * Q[direction][position])
            print(Q[0])
            print(Q[1])
            now += position * 'o'
            now += (9 - position) * '-'
            now += 'T'
            print(now)
            steps = 0
            break

        Q[direction][position] += (R * learningRate * Q[direction][position])
        # print(Q[0])
        # print(Q[1])

        # world.replace('-', 'o', position)
        now += position * 'o'
        now += (9 - position) * '-'
        now += 'T'
        print(now)
        print
        # print(world)


















































































