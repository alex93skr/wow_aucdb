#!/usr/bin/python
# -*- coding: utf-8 -*-
#############################################################


import json
import pickle

import pprint
import time



# def load_json(url):
#     with open(url, "r", encoding='utf-8') as read_file:
#         return json.load(read_file)
#
#
# wh_npc = load_json('wowhead_pars_npc.json')
#
# arr = []
# for id in wh_npc:
#     if wh_npc[id]['drop'] != None:
#         for n in wh_npc[id]['info']:
#             type = wh_npc[id]['info'].get('Тип')
#             level = wh_npc[id]['info'].get('Уровень')
#             tmp = [type, level]
#             if tmp not in arr:
#                 arr.append(tmp)
#
# for i in sorted(arr, key=lambda i : i[0] if i[0] != None else '-1'):
#     if i[1] < '40':
#         print(i)

# def find_all_drop(item_id):
#     arr = []
#     for npc_id in wh_npc:
#         # есть дроп
#         if wh_npc[npc_id]['drop'] != None:
#             for n in wh_npc[npc_id]['drop']:
#                 # есть итем в дропе
#                 if n['id'] == item_id:
#                     # print(npc_id, n['id'])
#                     percentOverride = n.get('percentOverride')
#                     modes1 = n['modes'].get('1')
#                     # modes2 = n['modes'].get('2')
#
#                     if modes1 != None:
#                         if modes1['count'] == -1:
#                             modes1 = None
#                         else:
#                             modes1 = round(modes1['count'] / modes1['outof'] * 100, 2)
#
#                     # if modes2 != None:
#                     #     if modes2['count'] == -1:
#                     #         modes2 = None
#                     #     else:
#                     #         modes2 = round(modes2['count'] / modes2['outof'] * 100, 2)
#
#                     drop = None
#
#                     # if modes2 != None:
#                     #     drop = modes2
#                     if modes1 != None:
#                         drop = modes1
#                     if percentOverride != None:
#                         drop = percentOverride
#
#                     arr.append([npc_id, drop, wh_npc[npc_id]['name']])
#
#                     # print(npc_id, n['id'], percentOverride, modes1, modes2, '   ', wh_npc[npc_id]['name'])
#                     # print(npc_id, drop)
#
#     # for i in sorted(arr, key=lambda i: i[1], reverse=True):
#     #     print(i)
#     return sorted(arr, key=lambda i: i[1], reverse=True)
#
#
# find_all_drop(22527)

# for id in wh_npc:
#     if wh_npc[id]['drop'] != None:
#         for n in wh_npc[id]['drop']:
#             # modes = wh_npc[id]['drop'].get('modes')
#             # drop_modes = wh_npc[id]['drop']
#             percentOverride = n.get('percentOverride')
#             if n['modes']['mode'] == 2:
#                 # print(n['modes']['mode']['1'])
#                 if n['modes']['1'] != n['modes']['2']:
#                     print(id, n['id'], percentOverride, n['modes'])

# for id in wh_npc:
#     if wh_npc[id]['drop'] != None:
#         for n in wh_npc[id]['drop']:
#             # modes = wh_npc[id]['drop'].get('modes')
#             drop_modes = wh_npc[id]['drop']
#             percentOverride = n.get('percentOverride')
#             print(id, percentOverride, n['modes'])


# for i in arr:
#     print(i, arr[i])
