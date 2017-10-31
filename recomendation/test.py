#!/usr/bin/python
import MySQLdb
import sql_service
import collaborative_filtering as filter
from recommendation_data import dataset
from datetime import datetime


db = sql_service.connect()
cur = db.cursor()
cur.execute("SELECT * FROM `BX-Book-Ratings` LIMIT 10000000")

# print all the first cell of all the rows
# rows = cur.fetchall()
# dataset = {}
#
# def merge_two_dicts(x, y):
#     """Given two dicts, merge them into a new dict as a shallow copy."""
#     z = x.copy()
#     z.update(y)
#     return z
#
# for row in rows:
#     key = str(row[0])
#     k = str(row[1])
#     value = float(row[2]) / 2
#     # import pdb;pdb.set_trace()
#     if value == 0:
#         continue
#     else:
#         if key in dataset:
#             dts = dict()
#             dts[k] = value
#             dataset[key] = merge_two_dicts(dataset[key], dts)
#         else:
#             dataset[key] = {k:value}

# print type(dataset)

filter.dataset = dataset
from recommendation_data import dataset as dt
# print dt
# user = "Jack Matthews"
print dataset
for dts in dataset:
    user = dts
    print user
    # print filter.pearson_correlation(user, "Toby"), filter.calculate_sim_pearson_score(user, "Toby")
    print filter.user_recommendations(user), '\n---------------\n', filter.user_recommendations_pearson(user, 4)
    # print filter.k_nearest_users(user, 4), '\n---------------\n', filter.most_similar_users(user, 4)
# pearson_correlation
# calculate_sim_pearson_score
db.close()
