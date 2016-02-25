__author__ = 'libochen'

# set global variables here
p = 4294967311

import binascii
from random import randint
from nltk.corpus import stopwords
import numpy as np
stop = stopwords.words('english')

for index in range(len(stop)):
    stop[index] = str(stop[index])

# print stop


# define several functions
def estimate(col1, col2, matrix, debug=False):
    res = 0
    length = len(matrix)
    for ii in range(length):
        if matrix[ii][col1] == matrix[ii][col2]:
            res += 1

    if debug:
        print "compare ", col1, " and ", col2, " in signature matrix"
        for ii in range(length):
            print matrix[ii][col1], " VS ", matrix[ii][col2]

    return float(res) / len(matrix)


def exist(rr, cc, slist, mydict, alist):
    query_shingle = slist[rr]
    containing_set = mydict[alist[cc]]
    return query_shingle in containing_set


def actual(col1, col2, alist, mydict):
    set1 = mydict[alist[col1]]
    set2 = mydict[alist[col2]]
    union_set = set1 | set2
    intersection_set = set1 & set2
    return float(len(intersection_set)) / len(union_set)


dict = {}
artical_list = []
universal_shingle_set = set()
# ######################### Phase 1 process shingles #######################################
# parse all the data in txt and store them in dict
with open('articles-1000.txt') as f:
    for line in f:
        word_list = []

        # split result stores all the split strings without those stop words
        split_res = []
        for word in line.split():
            if word not in stop:
                split_res.append(word)
        word_num = len(split_res)
        book_id = split_res[0]
        artical_list.append(book_id)
        shingle_set = set()
        for i in range(1, word_num-1):
            shingle = split_res[i] + " " + split_res[i+1]
            shingle_id = binascii.crc32(shingle) & 0xffffffff
            shingle_set.add(shingle_id)
            universal_shingle_set.add(shingle_id)
        dict[book_id] = shingle_set

# a, total number of shingles, average number
shingle_sum = 0

for key in dict:
    shingle_sum += len(dict[key])

shingle_average = float(shingle_sum) / len(dict)
print "the total number of shingles is ", shingle_sum
print "the average number of shingle is", shingle_average
print "the total number of unique shingles is", len(universal_shingle_set)

# ########################## phase 2 min hash #################################################
# querying characteristic matrix using querying function to avoid using too much memory
universal_shingle_list = list(universal_shingle_set)
row = len(universal_shingle_list)
col = len(artical_list)


'''
def min_hash(n):
    hash_functions = []
    for i in range(n):
        c1 = randint(1, p-1)
        c2 = randint(1, p-1)
        hash_functions.append([c1, c2])

    # print len(artical_list)
    # print hash_functions

    # build signature matrix with n * col
    s_matrix = [[p] * col for i in range(n)]

    for r in range(row):
        hash_values = []
        # calculate each hash values
        for i in range(n):
            c1 = hash_functions[i][0]
            c2 = hash_functions[i][1]
            hash_value = (c1 * r + c2) % p
            hash_values.append(hash_value)

        for c in range(col):
            if exist(r, c, universal_shingle_list, dict, artical_list):
                for row_id in range(n):
                    s_matrix[row_id][c] = min(s_matrix[row_id][c], hash_values[row_id])
    return s_matrix
'''


def min_hash(n):
    hash_functions = []
    for i in range(n):
        c1 = randint(1, p-1)
        c2 = randint(1, p-1)
        hash_functions.append([c1, c2])

    # build signature matrix with n * col
    s_matrix = [[p] * col for i in range(n)]

    for c in range(col):
        # print artical_list[c]
        # shingle_array = list(dict[artical_list[c]])
        shingle_array = np.array(list(dict[artical_list[c]]))
        for i in range(n):
            c1 = hash_functions[i][0]
            c2 = hash_functions[i][1]
            hash_values = (c1 * shingle_array + c2) % p
            s_matrix[i][c] = min(hash_values)

    return s_matrix


def find_similar(s_matrix):
    estimated_similarity = 0
    most_similar_id = -1
    for c in range(1, col):
        if estimate(0, c, s_matrix) > estimated_similarity:
            most_similar_id = c
            estimated_similarity = estimate(0, c, s_matrix)

    actual_similarity = actual(0, most_similar_id, artical_list, dict)

    print "most similar col number is ", most_similar_id
    # for debug
    # estimate(0, most_similar_id, s_matrix, True)
    most_similar_id = artical_list[most_similar_id]

    print "actual similarity is ", actual_similarity
    print "estimate similarity is ", estimated_similarity
    print "most similar id is ", most_similar_id


def phase2():
    s_matrix = min_hash(10)
    find_similar(s_matrix)

phase2()


# ######################## phase 3 LSH ################################################################
actual_sim = []


def calc_as():
    for c in range(col):
        sim = actual(0, c, artical_list, dict)
        actual_sim.append(sim)

calc_as()


def is_match(col1, col2, b_index, r, s_matrix):
    # how to hash to bucket
    # my naive direct comparison
    for i in range(b_index * r, b_index * r + r):
        if s_matrix[i][col1] != s_matrix[i][col2]:
            return False
    return True


def calculate_fp(b, r, t):
    s_matrix = min_hash(b * r)
    candidate_set = set()
    for b_index in range(b):
        for c in range(1, col):
            if is_match(0, c, b_index, r, s_matrix):
                candidate_set.add(c)

    count = 0
    for c in candidate_set:
        # if actual(0, c, artical_list, dict) < t:
        #     count += 1

        if actual_sim[c] < t:
            count += 1

    return float(count) / len(candidate_set)


def plot_figure(t):
    iteration = 10
    fp_list = []
    for b in [1, 3, 5, 7, 9]:
        r = 2
        fp = 0
        for i in range(iteration):
            fp += calculate_fp(b, r, t)
        fp = float(fp) / iteration
        fp_list.append(fp)

    print "fp values are ", fp_list

    fp_list = []
    for r in [1, 3, 5, 7, 9]:
        b = 10
        fp = 0
        for i in range(iteration):
            fp += calculate_fp(b, r, t)
        fp = float(fp) / iteration
        fp_list.append(fp)

    print "fp values are ", fp_list

plot_figure(0.8)


# ######################### for debug phase 2####################################################################
# s_matrix = [[p] * col] * n        silly mistakes
