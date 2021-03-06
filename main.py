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

all_red_users = list(seed_dic['seed_1'].keys()) + list(seed_dic['seed_2'].keys()) + list(seed_dic['seed_3'].keys()) + \
    list(seed_dic['seed_4'].keys())
red_total_count = len(all_red_users)

data = pd.DataFrame(columns=['seed', 'account', 'similar_in_followees', 'similar_in_red', 'red_in_followees',
                             'bussines', 'category', 'nofollowees', 'nofollowers', 'noposts', 'private', 'verified'])

DG = nx.DiGraph()

for seed in ['seed_1', 'seed_2', 'seed_3', 'seed_4']:
    for count in list(seed_dic[seed].keys()):
        similares_followees_count = 0
        similares_red_count = 0
        red_followees_count = 0
        similar_total_count = len(seed_dic[seed][count]['similares'])

        for seguidos in seed_dic[seed][count]['similares']:
            if seguidos in seed_dic[seed][count]['followees']:
                similares_followees_count += 1
            if seguidos in all_red_users:
                similares_red_count += 1  # cuantos de los similares estan en la red
        for red in all_red_users:
            if red in seed_dic[seed][count]['followees']:
                red_followees_count += 1

        data = data.append({'seed': int(seed[-1]),
                            'account': count,
                            'similar_in_followees': (similares_followees_count * 100 / similar_total_count),
                            'similar_in_red': (similares_red_count * 100 / similar_total_count),
                            'red_in_followees': (red_followees_count * 100 / red_total_count),
                            'category': seed_dic[seed][count]['category'],
                            'nofollowees': float(seed_dic[seed][count]['nofollowees']),
                            'nofollowers': float(seed_dic[seed][count]['nofollowers']),
                            'noposts': float(seed_dic[seed][count]['noposts']),
                            'private': seed_dic[seed][count]['private'],
                            'verified': seed_dic[seed][count]['verified']
                            },
                           ignore_index=True)

    for user_red in all_red_users:
        for user_seed_2 in list(seed_dic[seed].keys()):
            if user_red in seed_dic[seed][user_seed_2]['similares']:
                DG.add_edges_from([(user_seed_2, user_red)])

    for i in ['bussines', 'category', 'nofollowees', 'nofollowers', 'noposts', 'private', 'verified']:
        for j in list(seed_dic[seed].keys()):
            DG.nodes[j][i] = seed_dic[seed][j][i]

data['clustering'] = ""
data['centrality'] = ""
data['degree_centrality'] = ""
data['betweenness_centrality'] = ""
data['degree'] = ""

clust = nx.clustering(DG)
centr = nx.degree_centrality(DG)
eigcentral = nx.eigenvector_centrality(DG)
betcentral = nx.betweenness_centrality(DG)
degree = nx.degree(DG)

for keys_clustering in clust.keys():
    data.loc[data['account'] == keys_clustering, 'clustering'] = clust[keys_clustering]
    data.loc[data['account'] == keys_clustering, 'centrality'] = centr[keys_clustering]
    data.loc[data['account'] == keys_clustering, 'degree_centrality'] = eigcentral[keys_clustering]
    data.loc[data['account'] == keys_clustering, 'betweenness_centrality'] = betcentral[keys_clustering]
    data.loc[data['account'] == keys_clustering, 'degree'] = degree[keys_clustering]

data['nofollowers_nofollowees'] = (data['nofollowers']-data['nofollowees'])/(data['nofollowers']+data['nofollowees'])

# Select some columns using a criteria
data[((data['category'].isna()) | (data['category'] == 'Creators & Celebrities'))
     & (data['betweenness_centrality'] != 0)
     & (data['centrality'] > 0.28)].sort_values(by=['betweenness_centrality'], ascending=False)

# New network --------
new_red_users = list(data[((data['category'].isna()) | (data['category'] == 'Creators & Celebrities'))
                          & (data['betweenness_centrality'] != 0)
                          & (data['centrality'] > 0.28)]['account'])
red_total_count = len(new_red_users)


DG = nx.DiGraph()

i = 'nofollowees'
for seed in ['seed_1', 'seed_2', 'seed_3', 'seed_4']:
    for user_red in new_red_users:
        for user_seed_2 in list(seed_dic[seed].keys()):
            if (user_red in seed_dic[seed][user_seed_2]['followees']) & (user_seed_2 in new_red_users):
                DG.add_edges_from([(user_seed_2, user_red)])

for seed in ['seed_1', 'seed_2', 'seed_3', 'seed_4']:
    for i in ['bussines', 'category', 'nofollowees', 'nofollowers', 'noposts', 'private', 'verified']:
        for j in list(seed_dic[seed].keys()):
            if j in new_red_users:
                DG.nodes[j][i] = seed_dic[seed][j][i]

# --- Plot 1
pos = nx.spring_layout(DG)  # https://www.datacamp.com/community/tutorials/social-network-analysis-python
betCent = nx.betweenness_centrality(DG, normalized=True, endpoints=True)
node_color = [20000.0*DG.degree(v) for v in DG]
node_size = [v * 10000 for v in betCent.values()]
plt.figure(figsize=(20, 20))
nx.draw_networkx(DG, pos=pos, with_labels=True,
                 node_color=node_color,
                 node_size=node_size)
plt.savefig('testplot.png')

# ---- Plot 2
# Draw graph with varying node color, node size, and edge width
plt.figure(figsize=(20, 10))

node_color = [DG.degree(v) for v in DG]
node_size = [0.0005*nx.get_node_attributes(DG, 'nofollowers')[v] for v in DG]
# edge_width = [0.0015*DG[u][v]['nofollowees'] for u,v in DG.edges()]

pos = nx.circular_layout(DG)
nx.draw_networkx(DG, pos, node_size=node_size,
                 node_color=node_color, alpha=0.7, with_labels=True, edge_color='.4', cmap=plt.cm.Blues)

plt.axis('off')
plt.tight_layout()
plt.savefig('testplot_2.png')

print(data)
print(len(new_red_users))
'''
plt.figure(figsize=(20, 10))

node_color = [DG.degree(v) for v in DG]
node_size = [0.0005*nx.get_node_attributes(DG, 'nofollowers')[v] for v in DG]
#edge_width = [0.0015*DG[u][v]['nofollowees'] for u,v in DG.edges()]

pos = nx.circular_layout(DG)
nx.draw_networkx(DG, pos, node_size=node_size,
                 node_color=node_color, alpha=0.7, with_labels=False, edge_color='.4', cmap=plt.cm.Blues)

plt.axis('off')
plt.tight_layout()
plt.show(block=False)
plt.show()
'''
