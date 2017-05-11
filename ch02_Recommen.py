# -*- coding: utf-8 -*-
from numpy import *
from math import *

critics = {'Lisa Rose': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.5,
                         'Just My Luck': 3.0, 'Superman Returns': 3.5, 'You, Me and Dupree': 2.5,
                         'The Night Listener': 3.0},
           'Gene Seymour': {'Lady in the Water': 3.0, 'Snakes on a Plane': 3.5,
                            'Just My Luck': 1.5, 'Superman Returns': 5.0, 'The Night Listener': 3.0,
                            'You, Me and Dupree': 3.5},
           'Michael Phillips': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.0,
                                'Superman Returns': 3.5, 'The Night Listener': 4.0},
           'Claudia Puig': {'Snakes on a Plane': 3.5, 'Just My Luck': 3.0,
                            'The Night Listener': 4.5, 'Superman Returns': 4.0,
                            'You, Me and Dupree': 2.5},
           'Mick LaSalle': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
                            'Just My Luck': 2.0, 'Superman Returns': 3.0, 'The Night Listener': 3.0,
                            'You, Me and Dupree': 2.0},
           'Jack Matthews': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
                             'The Night Listener': 3.0, 'Superman Returns': 5.0, 'You, Me and Dupree': 3.5},
           'Toby': {'Snakes on a Plane': 4.5, 'You, Me and Dupree': 1.0, 'Superman Returns': 4.0}}


def sim_distance(prefs, person1, person2):  # 使用欧氏距离计算偏好
    si = {}
    for item in prefs[person1]:
        if item in prefs[person2]:
            si[item] = 1
    if len(si) == 0:
        return 0
    sum_of_squares = sum([pow(prefs[person1][item] - prefs[person2][item], 2)
                          for item in prefs[person1] if item in prefs[person2]])
    return 1 / (1 + sqrt(sum_of_squares))


# print sim_distance(critics, 'Gene Seymour', 'Mick LaSalle')


def sim_pearson(prefs, p1, p2):  # 皮尔逊相关度算法
    si = {}
    for item in prefs[p1]:  # 找到共同存在的项
        if item in prefs[p2]: si[item] = 1  # 注意这条语句，如果传进来的是 'Gene Seymour'和'Mick LaSalle'，则si =
        # {'Lady in the Water': 1, 'Snakes on a Plane': 1, 'Just My Luck': 1, 'Superman Returns': 1, 'The Night Listener': 1, 'You, Me and Dupree': 1}
    n = len(si)
    if n == 0: return 1
    sum1 = sum([prefs[p1][it] for it in si])  # 注意for语句的使用，和[]的使用
    sum2 = sum([prefs[p2][it] for it in si])
    sum1Sq = sum([pow(prefs[p1][it], 2) for it in si])  # 求平方和
    sum2Sq = sum([pow(prefs[p2][it], 2) for it in si])
    pSum = sum([prefs[p1][it] * prefs[p2][it] for it in si])  # it 即在p1、p2中又在si中
    # 计算皮尔逊评价值
    num = pSum - (sum1 * sum2 / n)
    den = sqrt((sum1Sq - pow(sum1, 2) / n) * (sum2Sq - pow(sum2, 2) / n))
    if den == 0: return 0
    r = num / den
    return r


# print sim_pearson(critics, 'Lisa Rose', 'Gene Seymour')


# Returns the best matches for person from the prefs dictionary.
# Number of results and similarity function are optional params.
def topMatches(prefs, person, n=5, similarity=sim_pearson):
    scores = [(similarity(prefs, person, other), other)
              for other in prefs if other != person]  # 这句好屌，自己不和自己比
    scores.sort()
    scores.reverse()
    return scores[0:n]


def getRecommendations(prefs, person, similarity=sim_pearson):
    totals = {}
    simSums = {}
    for other in prefs:

        # 不要和自己作比较
        if other == person: continue
        sim = similarity(prefs, person, other)

        # 忽略评价值为0或小于0的情况
        if sim <= 0: continue
        for item in prefs[other]:
            # 只对自己未曾看过的影片进行评价
            if item not in prefs[person] or prefs[person][item] == 0:
                totals.setdefault(item, 0)
                totals[item] += prefs[other][item] * sim
                # 相似度之和
                simSums.setdefault(item, 0)
                simSums[item] += sim
        # 建立一个归一化的列表
        rankings = [(total / simSums[item], item) for item, total in totals.items()]
        # 返回经排序的列表
        rankings.sort()
        rankings.reverse()
        return rankings


# 名字和电影倒置
def transformPrefs(prefs):
    result = {}
    for person in prefs:
        for item in prefs[person]:
            result.setdefault(item, {})

            # Flip item and person
            result[item][person] = prefs[person][item]
    return result


def calculateSimilarItems(prefs, n=10):
    # 建立字典，存放物品最为相近的所有其他物品
    result = {}
    # 以物品为中心对偏好矩阵实施倒置处理
    itemPrefs = transformPrefs(prefs)
    c = 0
    for item in itemPrefs:
        # 针对大数据更新状态变量
        c += 1
        if c % 100 == 0: print "%d / %d" % (c, len(itemPrefs))
        # 寻找最为相近的物品
        scores = topMatches(itemPrefs, item, n=n, similarity=sim_distance)
        result[item] = scores
    return result


# 基于物品的协作型过滤
def getRecommendedItems(prefs, itemMatch, user):
    userRatings = prefs[user]
    scores = {}
    totalSim = {}
    # 循环遍历当前用户评分的物品
    for (item, rating) in userRatings.items():
        # 如果该用户已经对当前物品做过评价，则将其忽略
        for (similarity, item2) in itemMatch[item]:
            if item2 in userRatings: continue
            # 评价值与相似度的加权之和
            scores.setdefault(item2, 0)
            scores[item2] += similarity * rating
            # 全部相似度之和
            totalSim.setdefault(item2, 0)
            totalSim[item2] += similarity
    rankings = [(score / totalSim[item], item) for item, score in scores.items()]
    rankings.sort()
    rankings.reverse()
    return rankings


# 数据下载地址：http://www.grouplens.org/node/73
def loadMovieLens(path='data'):
    movies = {}
    for line in open(path + '/u.item'):
        # 数据像这样：1|Toy Story (1995)|01-Jan-1995||http://us.imdb.com/M/title-exact?Toy%20Story%20(1995)|0|0|0|1|1|1|0|0|0|0|0|0|0|0|0|0|0|0|0
        (id, title) = line.split('|')[0:2]
        movies[id] = title

    prefs = {}
    for line in open(path + '/u.data'):
        # 数据像这样：196	242	3	881250949
        (user, movieid, rating, ts) = line.split('\t')
        prefs.setdefault(user, {})
        prefs[user][movies[movieid]] = float(rating)
    return prefs


prefs = loadMovieLens()
print prefs['87']
print '基于用户推荐：'
print getRecommendations(prefs, '87')
print '基于物品推荐：'
itemsim = calculateSimilarItems(prefs, n=50)
print getRecommendedItems(prefs, itemsim, '87')[0:30]

'''
itemsim = calculateSimilarItems(critics)
print getRecommendedItems(critics, itemsim, 'Toby')


print transformPrefs(critics)
print
print topMatches(critics, 'Toby', n=100, similarity=sim_distance)
print
print getRecommendations(critics, 'Toby', similarity=sim_distance)
print '/////////////////////////////////////////'
'''
