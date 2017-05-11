# -*- coding: utf-8 -*-

import math as math


def G_1(x):
    if x < 2.5:
        return 1
    else:
        return -1


def G_2(x):
    if x < 8.5:
        return 1
    else:
        return -1


def G_3(x):
    if x < 5.5:
        return -1
    else:
        return 1


for i in range(10):
    print i, ":", 0.4236 * G_1(i) + 0.6496 * G_2(i) + 0.7514 * G_3(i)


# def W(w, a, y, x, G=G_1):
#     return w * math.exp(-1 * a * y * G(x))
#
#
# v1 = W(0.1, 0.4236, 1, 0) * 2  # 0,1
# v2 = W(0.1, 0.4236, 1, 2)  # 2
# v3 = W(0.1, 0.4236, -1, 3) * 3  # 3,4,5
# v4 = W(0.1, 0.4236, 1, 3)  # 6,7,8
# v5 = W(0.1, 0.4236, -1, 9)
# sum = v1 + v2 + v3 + v4 + v5
# print sum
# print W(0.1, 0.4236, 1, 0) / sum
