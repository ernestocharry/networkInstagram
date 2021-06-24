#!/usr/bin/python
# -*- coding: latin-1 -*-
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



for seed in ['seed_1', 'seed_2', 'seed_3', 'seed_4', 'seed_5']:
    for count in list(seed_dic[seed].keys()):
        similares_followees_count = 0
        similares_red_count = 0
        red_followees_count = 0
        similar_total_count = len(seed_dic[seed][count]['similares'])

        if similar_total_count != 0:
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

seed_2_to_3 = data[data['seed'] == 2]['account'].tolist()

all_similares = []
for account in seed_2_to_3:
    all_similares = np.concatenate((all_similares, seed_dic['seed_2'][account]['similares']), axis=None)

all_similares = np.unique(all_similares)

# Evaluar si son mexicanos
possible_words = ['mx', 'mex', 'méx', flag.flag("MX")]

# seed_dic['seed_5'] = {} # Only where is empy

print(len(all_similares))

# Create an instance of Instaloader class
bot = instaloader.Instaloader()
# Interactive login on terminal
bot.interactive_login("feecharrypa")  # Asks for password in the terminal

i = 41  ## para seed_5
i = 92  # para seed_3: similares de seed_1

for red_user in all_similares[i:]:
    # Are this All Similares in all_Red_users:
    # seed_dic = json.load(open('/content/drive/MyDrive/Colab Notebooks/seed_dic.json'))
    all_red_users = list(seed_dic['seed_1'].keys()) + list(seed_dic['seed_2'].keys()) + list(
        seed_dic['seed_3'].keys()) + list(seed_dic['seed_4'].keys()) + list(seed_dic['seed_5'].keys())
    print(' ')
    print(i, ' starting with: ', red_user, ' ***********************************')
    if red_user not in all_red_users:  # This user is not in the red
        # all_similares.remove(red_user)
        profile = instaloader.Profile.from_username(bot.context, red_user)

        username = red_user
        bio = profile.biography.lower()
        full_name = profile.full_name.lower()
        external = profile.external_url

        username = " " if username is None else username
        bio = " " if bio is None else bio
        full_name = " " if full_name is None else full_name
        external = " " if external is None else external
        suma_todos = full_name + bio + username + external

        print('profile.bussines: ', profile.business_category_name)
        if any((word in suma_todos) for word in possible_words) & \
                (str(profile.business_category_name) == 'None' or str(profile.business_category_name) == 'Creators & Celebrities'):

            followees = [followee.username for followee in profile.get_followees()]
            similares = [similar.username for similar in profile.get_similar_accounts()]

            dictionary = {'full_name': full_name,
                          'user_id': profile.userid,
                          'noposts': profile.mediacount,
                          'nofollowers': profile.followers,
                          'nofollowees': profile.followees,
                          'private': profile.is_private,
                          'verified': profile.is_verified,
                          'bussines': profile.is_business_account,
                          'category': profile.business_category_name,
                          'bio': bio,
                          'external': external,
                          'followees': followees,
                          'similares': similares}

            seed_dic['seed_3'][red_user] = dictionary
            with open('seed_dic.json', 'w') as file:
                json.dump(seed_dic, file, indent=4, sort_keys=True,
                          separators=(', ', ': '), ensure_ascii=False,
                          cls=NumpyEncoder)
            print('i) ', i, ' account: ', red_user, 'is                                    mx      *****')
        else:

            dictionary = {'full_name': full_name,
                          'user_id': profile.userid,
                          'noposts': profile.mediacount,
                          'nofollowers': profile.followers,
                          'nofollowees': profile.followees,
                          'private': profile.is_private,
                          'verified': profile.is_verified,
                          'bussines': profile.is_business_account,
                          'category': profile.business_category_name,
                          'bio': bio,
                          'external': external,
                          'followees': [],
                          'similares': []}

            seed_dic['seed_3'][red_user] = dictionary
            with open('seed_dic.json', 'w') as file:
                json.dump(seed_dic, file, indent=4, sort_keys=True,
                          separators=(', ', ': '), ensure_ascii=False,
                          cls=NumpyEncoder)
            print('i) ', i, ' account: ', red_user, ' is not mx')
    else:
        print(red_user, 'ya se encuentra en la red')
    i += 1

