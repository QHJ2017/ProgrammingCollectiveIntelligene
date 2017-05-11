# -*- coding: utf-8 -*-
from math import sqrt
from PIL import Image, ImageDraw


# 读取文件
def readfile(filename):
    lines = [line for line in file(filename)]
    # 第一行是列标题
    colname = lines[0].strip().split('\t')[1:]
    rowname = []
    data = []
    for line in lines[1:]:
        p = line.strip().split('\t')  # strip() 默认删除句前、句后空白符（包括'\n', '\r',  '\t',  ' ')
        # 每行的第一列是行名
        rowname.append(p[0])
        # 剩余部分就是对应的数据
        data.append([float(x) for x in p[1:]])
    return rowname, colname, data


blogname, words, data = readfile('blogdata.txt')  # 本文档中有99行数据


# print data

# print blogname, '\n'
# print words


# 皮尔逊相似度，可以把返回值理解为“距离”
def pearson(v1, v2):
    # 简单求和
    sum1 = sum(v1)
    sum2 = sum(v2)

    # 求平方和
    sum1Sq = sum(pow(v, 2) for v in v1)
    sum2Sq = sum(pow(v, 2) for v in v2)

    # 求乘积之和
    pSum = sum([v1[i] * v2[i] for i in range(len(v1))])

    # 计算 r (Person score)
    num = pSum - (sum1 * sum2 / len(v1))  # 皮尔逊相关系数公式的分子
    den = sqrt((sum1Sq - pow(sum1, 2) / len(v1)) * (sum2Sq - pow(sum2, 2) / len(v1)))  # 分母
    if den == 0:
        return 0
    return 1 - num / den


class bicluster:  # 一个类,代表“聚类”这一类型
    def __init__(self, vec, left=None, right=None, distance=0.0, id=None):
        # 聚类的left参数和right参数可以再放 bicluster 类
        self.left = left
        self.right = right
        self.vec = vec
        self.id = id
        self.distance = distance


# 分级聚类算法
def hcluster(rows, distance=pearson):
    distances = {}
    currentclustid = -1

    # 最开始的聚类就是数据中的行
    clust = [bicluster(rows[i], id=i) for i in range(len(rows))]

    while len(clust) > 1:
        lowestpair = (0, 1)
        closest = distance(clust[0].vec, clust[1].vec)

        # 遍历每一个配对，寻找最小距离
        for i in range(len(clust)):
            for j in range(i + 1, len(clust)):
                # 用distances来缓存距离的计算值
                if (clust[i].id, clust[j].id) not in distances:
                    distances[(clust[i].id, clust[j].id)] = distance(clust[i].vec, clust[j].vec)

                d = distances[(clust[i].id, clust[j].id)]

                if d < closest:
                    closest = d
                    lowestpair = (i, j)

        # 计算两个聚类的平均值
        # print lowestpair, 'Number: ', i
        mergevec = [(clust[lowestpair[0]].vec[i] + clust[lowestpair[1]].vec[i]) / 2.0 for i in range(len(clust[0].vec))]

        # 建立新的聚类
        newcluster = bicluster(mergevec, left=clust[lowestpair[0]], right=clust[lowestpair[1]], distance=closest,
                               id=currentclustid)

        # 不在原始集合中的聚类，其id为负数
        currentclustid -= 1
        del clust[lowestpair[1]]
        del clust[lowestpair[0]]
        clust.append(newcluster)

        # print 'clust`s type: ', type(clust[1])
    # print len(clust[0].vec)  # 706
    return clust[0]


clust = hcluster(data)


# print clust


# 打印输出
def printclust(clust, labels=None, n=0):
    # 利用缩进来建立层级布局
    for i in range(n):
        print ' ',
    if clust.id < 0:
        # 负数标记代表这是一个分支
        print '-'
    else:
        # 整数标记代表这是一个叶节点
        if labels == None:
            print clust.id
        else:
            print labels[clust.id]

    # 现在开始打印右侧分支和左侧分支
    if clust.left != None: printclust(clust.left, labels=labels, n=n + 1)
    if clust.right != None: printclust(clust.right, labels=labels, n=n + 1)


# printclust(clust)


def getheight(clust):
    if clust.left == None and clust.right == None: return 1
    return getheight(clust.left) + getheight(clust.right)


print 'height:', getheight(clust)
print type(clust)


# 节点的误差深度
def getdepth(clust):
    # 一个叶节点的距离是0.0
    if clust.left == None and clust.right == None: return 0
    return max(getdepth(clust.left), getdepth(clust.right)) + clust.distance


print 'getdepth(clust):', getdepth(clust)


def drawdendrogram(clust, labels, jpeg='cluster.jpg'):
    # 高和宽
    h = getheight(clust) * 20
    w = 1200
    depth = getdepth(clust)

    # 由于宽度是固定的，因此我们需要对距离做相应地调整
    scaling = float(w - 150) / depth

    # 创建一个白色背景的图片
    img = Image.new('RGB', (w, h), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    draw.line((0, h / 2, 10, h / 2), fill=(255, 0, 0))

    # 画第一个节点
    drawnode(draw, clust, 10, (h / 2), scaling, labels)
    img.save(jpeg, 'JPEG')


def drawnode(draw, clust, x, y, scaling, labels):
    if clust.id < 0:
        h1 = getheight(clust.left) * 20
        h2 = getheight(clust.right) * 20
        top = y - (h1 + h2) / 2
        bottom = y + (h1 + h2) / 2
        # Line length
        ll = clust.distance * scaling
        # Vertical line from this cluster to children
        draw.line((x, top + h1 / 2, x, bottom - h2 / 2), fill=(255, 0, 0))

        # Horizontal line to left item
        draw.line((x, top + h1 / 2, x + ll, top + h1 / 2), fill=(255, 0, 0))

        # Horizontal line to right item
        draw.line((x, bottom - h2 / 2, x + ll, bottom - h2 / 2), fill=(255, 0, 0))

        # Call the function to draw the left and right nodes
        drawnode(draw, clust.left, x + ll, top + h1 / 2, scaling, labels)
        drawnode(draw, clust.right, x + ll, bottom - h2 / 2, scaling, labels)
    else:
        # If this is an endpoint, draw the item label
        draw.text((x + 5, y - 7), labels[clust.id], (0, 0, 0))
