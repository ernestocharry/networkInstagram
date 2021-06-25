# Seed_1: list, with Followees and Similars
# Seed_2: accounts from similar who pass the filter, each has Followees and Similars
# Seed_3:

# This code is create in order to evalute how is the red growthing and if there is a stable red (parameter of filter)
import seaborn as sns
import networkx as nx
import instaloader
import pandas as pd
import numpy as np
import csv
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
from datetime import datetime, timedelta
from numpyencoder import NumpyEncoder
import json
import flag

seed_dic = json.load(open('seed_dic.json'))

total_seeds = ['seed_1', 'seed_2', 'seed_3']

seed_dic_yes_no = {'yes': {}, 'no': {}}

for seed in total_seeds:
    seed_dic_yes_no['yes'][seed] = {}
    seed_dic_yes_no['no'][seed] = {}

    for account in list(seed_dic[seed].keys()):

        if len(seed_dic[seed][account]['similares']) != 0:
            seed_dic_yes_no['yes'][seed][account] = {'similares': list(seed_dic[seed][account]['similares']),
                                                     'followees': list(seed_dic[seed][account]['followees'])}
        else:
            seed_dic_yes_no['no'][seed][account] = {'similares': list(seed_dic[seed][account]['similares']),
                                                    'followees': list(seed_dic[seed][account]['followees'])}

# print(seed_dic_yes_no)
print("How many account from seed_1-similar, are in the red?")
for i in seed_dic_yes_no['yes']['seed_1'].keys():
    count_yes = 0
    count_no = 0
    for j in seed_dic_yes_no['yes']['seed_1'][i]['similares']:
        if j in seed_dic_yes_no['yes']['seed_2'].keys():
            count_yes += 1
        else:
            count_no += 1
    print('Count: ', i, 'count_yes: ', count_yes, 'count_no: ', count_no)

print("Sum all similar from seed_2, how are they in the seed?")
all_similar = []
for i in seed_dic_yes_no['yes']['seed_2'].keys():

    for j in seed_dic_yes_no['yes']['seed_2'][i]['similares']:
        all_similar.append(j)
print(len(all_similar))

count_values = pd.DataFrame.from_dict({'account': [x for x in set(all_similar)],
                                       'count': [all_similar.count(x) for x in set(all_similar)]})


def function_seed(account):
    if account in seed_dic_yes_no['yes']['seed_1'].keys():
        return 1
    elif account in seed_dic_yes_no['yes']['seed_2'].keys():
        return 2
    elif account in seed_dic_yes_no['yes']['seed_3'].keys():
        return 3
    else:
        return np.nan


count_values['in_seed_2'] = count_values['account'].apply(lambda x: function_seed(x))

print(count_values.sort_values(by='count', ascending=False).head(30))
