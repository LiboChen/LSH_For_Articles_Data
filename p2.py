__author__ = 'libochen'

# set global variables here
p = 4294967311

import binascii
from random import randint
from nltk.corpus import stopwords
stop = stopwords.words('english')

for i in range(len(stop)):
    stop[i] = str(stop[i])

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


def actual(col1, col2, slist, alist):
    count = 0
    total = 0
    for ii in range(len(slist)):
        exist1 = exist(ii, col1, slist, dict, alist)
        exist2 = exist(ii, col2, slist, dict, alist)
        if exist1 and exist2:
            count += 1
        if exist1 or exist2:
            total += 1

    return float(count) / total


dict = {}
artical_list = []
universal_shingle_set = set()
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

# print dict['t120']
# print 'news agency' in dict['t120']


# a, total number of shingles, average number
shingle_sum = 0

for key in dict:
    shingle_sum += len(dict[key])

shingle_average = float(shingle_sum) / len(dict)

print "the total number of shingles is ", shingle_sum
print "the average number of shingle is", shingle_average

# ########################## phase 2 min hash #################################################
# querying characteristic matrix using querying function to avoid using too much memory
print "the total number of unique shingles is", len(universal_shingle_set)

universal_shingle_list = list(universal_shingle_set)
row = len(universal_shingle_list)
col = len(artical_list)

hash_functions = []
n = 10
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

estimated_similarity = 0
most_similar_id = -1
for c in range(1, col):
    if estimate(0, c, s_matrix) > estimated_similarity:
        most_similar_id = c
        estimated_similarity = estimate(0, c, s_matrix)

actual_similarity = actual(0, most_similar_id, universal_shingle_list, artical_list)

print "most similar col number is ", most_similar_id
# for debug
# estimate(0, most_similar_id, s_matrix, True)
most_similar_id = artical_list[most_similar_id]


print "actual similarity is ", actual_similarity
print "estimate similarity is ", estimated_similarity
print "most similar id is ", most_similar_id



# ######################## phase 3 LSH ################################################################





# ######################### for debug phase 2####################################################################
# s_matrix = [[p] * col] * n        silly mistakes
"""
print "hash functions are below "
for i in range(n):
    print hash_functions[i]

s_matrix = [[p] * col for i in range(n)]
for r in range(row):
    hash_values = []
    # calculate each hash values
    for i in range(n):
        c1 = hash_functions[i][0]
        c2 = hash_functions[i][1]
        hash_value = (c1 * r + c2) % p
        hash_values.append(hash_value)

    for c in [0]:
        if exist(r, c, universal_shingle_list, dict, artical_list):
            for row_id in range(n):
                if s_matrix[row_id][c] > hash_values[row_id]:
                    print "hash value is, ", hash_values[row_id]
                    print "cur row is: ", r
                    print " change ", "row_id,", row_id

                    # s_matrix[row_id][c] = min(s_matrix[row_id][c], hash_values[row_id])
                    s_matrix[row_id][c] = hash_values[row_id]
                    print hash_values[0], ' ', hash_values[1], ' ', hash_values[2], ' ', hash_values[3], ' ', \
                        hash_values[4], ' ', hash_values[5], ' ', hash_values[6], ' ', hash_values[7], ' ', \
                        hash_values[8], ' ', hash_values[9]

                    print s_matrix[0][0], ' ', s_matrix[1][0], ' ', s_matrix[2][0], ' ', s_matrix[3][0], \
                        ' ', s_matrix[4][0], ' ', s_matrix[5][0], ' ', s_matrix[6][0], ' ', s_matrix[7][0], \
                        ' ', s_matrix[8][0], ' ', s_matrix[9][0]

"""