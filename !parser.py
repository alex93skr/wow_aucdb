#!/usr/bin/python
# -*- coding: utf-8 -*-
#############################################################

import datetime
import pickle
from pprint import pprint
from time import sleep

import luadata
import re
import json


#############################################################


def unix2ts(ts):
    return datetime.datetime.fromtimestamp(ts)


def print_auc_str(data):
    """список номеров строк ауков"""
    res = []
    for n, ah in enumerate(data['AuctionDBSaved']['ah']):
        if type(ah) is dict:
            # print(n, type(ah))
            ts = datetime.datetime.fromtimestamp(data['AuctionDBSaved']['ah'][n]['ts'])
            print(f"{n:<3} {ts}:  data['AuctionDBSaved']['ah'][{n}]['data']  {data['AuctionDBSaved']['ah'][n]['ts']}")
            res.append(n)
    return res


#############################################################


def parser_substr(one_position):
    """ парсер каждой позиции  """

    # print(one_position)

    # селлер
    if '!' == one_position[0]:
        seller_search = re.search(r'!\w*\/', one_position)
        if seller_search is None or seller_search[0][1:-1] == '':
            seller = None
        else:
            seller = seller_search[0][1:-1]
    else:
        seller = None

    timeleft = re.search(r'[&\/]\d*,', one_position)
    timeleft = int(timeleft[0][1:-1])

    one_position = one_position[one_position.find(',') + 1:]
    itemCount = int(one_position[:one_position.find(',')])

    one_position = one_position[one_position.find(',') + 1:]
    minBid = int(one_position[:one_position.find(',')])

    one_position = one_position[one_position.find(',') + 1:]
    buyoutPrice = one_position[:one_position.find(',')]
    buyoutPrice = None if buyoutPrice == '' else int(buyoutPrice)

    # curBid_search = re.search(r',\d*(&|!|$)', one_position)
    # проверка на конец записи или чтот в этом роде
    if one_position[-1] == '!' or one_position[-1] == '&':
        curBid = one_position[one_position.find(',') + 1:-1]
    else:
        curBid = one_position[one_position.find(',') + 1:]
    curBid = None if curBid == '' else int(curBid)

    return seller, timeleft, itemCount, minBid, buyoutPrice, curBid


def parser(n_req):
    ''' парсер записей аука '''

    str_data = n_req['data']

    DEBUGPRINT = False

    data_dict = {}

    end_of_working_line = 0

    while end_of_working_line != -1:

        bid_count = 0

        end_of_working_line = str_data.find(' ')
        work_str = str_data[:end_of_working_line] if end_of_working_line != -1 else str_data

        if DEBUGPRINT: print('|', work_str, '|')

        # разбор рабочей строки
        # itemKey!seller1 / timeleft, itemCount, minBid, buyoutPrice, curBid & auction2

        itemkey = re.search(r'i\d+[?!:]', work_str)[0][1:-1]
        itemkey = int(itemkey)

        itemkeysub_search = re.search(r'[\?:>]\d+!', work_str)
        itemkeysub = int(itemkeysub_search[0][1:-1]) if not itemkeysub_search is None else 0

        if DEBUGPRINT: print(f'{itemkey} {itemkeysub} ')

        # !!!   ДЕЛАЕМ ДЖЕЙСОН    !!!
        if itemkey not in data_dict:
            data_dict.update({itemkey: {}})
        data_dict[itemkey].update({itemkeysub: {'bids': {}}})

        # разбор позиций внутри итема на ставки
        work_str = work_str[work_str.find('!'):]
        # print('>', work_str, '<', sep='')

        substring_pattern = r'[&!].+?(&|!|$)'
        substring = re.search(substring_pattern, work_str)

        while not substring is None:
            if DEBUGPRINT: print(substring[0])

            if substring[0][0] == '!':
                seller, timeleft, itemCount, minBid, buyoutPrice, curBid = parser_substr(substring[0])
            else:
                _, timeleft, itemCount, minBid, buyoutPrice, curBid = parser_substr(substring[0])

            if DEBUGPRINT:
                print(
                    # f'{itemkey:<8} {itemkeysub:<8} {seller:<8} {timeleft:<3} {itemCount:<3} {minBid:<8} {buyoutPrice:<8} {curBid:<8}')
                    # f'{itemkey} {itemkeysub} {seller} {timeleft} {itemCount} {minBid} {buyoutPrice} {curBid}')
                    f' {seller} {timeleft} {itemCount} {minBid} {buyoutPrice} {curBid}')

            # ДЕЛАЕМ ДЖЕЙСОН        !!!
            data_dict[itemkey][itemkeysub]['bids'].update(
                {bid_count:
                     {'seller': seller,
                      'timeleft': timeleft,
                      'itemCount': itemCount,
                      'minBid': minBid,
                      'buyoutPrice': buyoutPrice,
                      'curBid': curBid
                      }
                 }
            )
            bid_count += 1

            # переход хода
            work_str = work_str[len(substring[0]) - 1:]
            # print('>', work_str, '<', sep='')
            substring = re.search(substring_pattern, work_str)

        # след итерация
        str_data = str_data[end_of_working_line + 1:]
        # print(data_dict)
        if DEBUGPRINT:
            # sleep(0.1)
            print()

    return data_dict


# def all_data_from_lua_to_json():
#     for i in range(0, 20, 3)


def make_auc_archive():
    pass


#############################################################

def main():
    '''
    АРХИТЕКТУРА:

    загрузка lua
    unserialize lua

    вывод статистика

    базу в itemDB.json

    песледний аук
        проверка совпадение по ts
        запись в data_current.json

    все ауки кроме последнего
        проверка совпадение по ts
        запись в data_archive.json

    '''

    # ЗАГРУЗКА ДЕСЕРИАЛИЗАЦИЯ LUA
    path = 'D:\\Games\\World of Warcraft\\_classic_\\WTF\\Account\\112287723#2\\SavedVariables\\AuctionDB.lua'
    data_from_lua = luadata.unserialize(path, encoding='utf-8')
    # data_from_lua = luadata.unserialize('AuctionDB.lua', encoding='utf-8')

    print('LOAD', path)

    numbers_of_aucs_list = print_auc_str(data_from_lua)

    print()
    print(numbers_of_aucs_list)
    print('CURRENT AH:', max(numbers_of_aucs_list))
    print()

    # ПАРСИНОГ, ФОРМИРОВАНИЕ ДЖЕЙСОНОВ

    # try:
    #     data_archive_file = open("data_archive.json", "r+", encoding='utf-8')
    #     data_archive = json.load(data_archive_file)
    # except FileNotFoundError:
    #     data_archive_file = open("data_archive.json", "w", encoding='utf-8')
    #     data_archive = {}

    try:
        data_archive_file = open("data_archive.pickle", "rb+")
        data_archive = pickle.load(data_archive_file)
    except FileNotFoundError:
        data_archive_file = open("data_archive.pickle", "wb")
        data_archive = {}

    print(type(data_archive))

    data_archive_update = False

    for n in numbers_of_aucs_list:
        ts = data_from_lua['AuctionDBSaved']['ah'][n]['ts']
        # print(type(ts))
        if ts not in data_archive:
            print('Update arc:', ts, unix2ts(ts))

            data_dict = parser(data_from_lua['AuctionDBSaved']['ah'][n])
            arc = {
                ts: {
                    'itemDBcount': data_from_lua['AuctionDBSaved']['ah'][n]['itemDBcount'],
                    # 'ts': data_from_lua['AuctionDBSaved']['ah'][n]['ts'],
                    'itemsCount': data_from_lua['AuctionDBSaved']['ah'][n]['itemsCount'],
                    'count': data_from_lua['AuctionDBSaved']['ah'][n]['count'],
                    # 'data': data_from_lua['AuctionDBSaved']['ah'][n]['data'],
                    'parsData': data_dict
                }
            }
            data_archive.update(arc)
            data_archive_update = True

    if data_archive_update:
        data_archive_file.seek(0)
        pickle.dump(data_archive, data_archive_file, protocol=4)
        # json.dump(data_archive, data_archive_file, indent=0, ensure_ascii=False)
    else:
        print('No new AH data')

    data_archive_file.close()


#############################################################

if __name__ == '__main__':
    main()

#############################################################

'''
ТЕСТЫ

тест количество уникальных итемов с вложениями (пропадает -1)
print('data_dict id count', len(data_dict))

all_count = 0
for i in data_dict:
    # print(len(data_dict[i]))
    all_count += len(data_dict[i])
print('all_id+sub_count', all_count)

print('-------')

########################################
all_id_plus_sub_from_db = re.findall(r'i.*?!', data_from_lua['AuctionDBSaved']['ah'][n_req]['data'])
print(all_id_plus_sub_from_db)
print('!!!!', len(all_id_plus_sub_from_db))

# all_id_plus_sub_from_db_int = []
for id in all_id_plus_sub_from_db:

    n_id = ''
    n_sub = ''

    # print(id)
    if '?' in id:
        n_id = id[1:id.find('?')]
        # print(n_id)
        n_sub = id[id.find('?')+1:-1]
        # print(n_sub)
    elif ':' in id and '>' in id:
        n_id = id[1:id.find(':')]
        # print(n_id)
        n_sub = id[id.find('>')+1:-1]
        # print(n_sub)
    elif ':' in id and '>' not in id:
        n_id = id[1:id.find(':')]
        # print(n_id)
        n_sub = id[id.find(':')+1:-1]
        # print(n_sub)
    else:
        # print(id)
        n_id = id[1:-1]
        n_sub = 0

if not int(n_sub) in data_dict[int(n_id)]:
    print(n_id, n_sub)

all_id_plus_sub_from_db_int.append()

i12007?590!
i5071!
i2072:723>175!
i3310:41!

########################################
тест сравнение по ключам на нулевом уровне
all_id_from_db = re.findall(r'i[\d]*[!?:]', data_from_lua['AuctionDBSaved']['ah'][n_req]['data'])
print(all_id_from_db)
print('all_id_from_db', len(all_id_from_db))

all_id_from_db_int = []
for i in all_id_from_db:
    all_id_from_db_int.append(int(i[1:-1]))

print(all_id_from_db_int)
print('all_id_from_db_int', len(all_id_from_db_int))

print(list(data_dict.keys()))
print(all_id_from_db_int)

print(len(set(list(data_dict.keys()))))
print(len(set(list(all_id_from_db_int))))

########################################
тест на вложение саб id
for i in data_dict:
    if len(data_dict[i]) != 1 and len(data_dict[i]) != 6:
        # print(len(data_dict[i]))
        pprint(data_dict[i])
'''

"""
#############################################################

0 УРОВЕНЬ ДАННЫХ

'AuctionDBSaved' (2226268475632) = {dict} <class 'dict'>: {'autoScan': False, 'autoSave': False, 'addonVersion': 'v0.14.00-classic', 'showBigButton': False, 'addonHash': 'eb75110', 'autoScanDelay': 10, 'allowLDBI': True, 'showNewItems': 10, 'itemDB_2': {'i15010?25': '|cff1eff00|Hitem:15010::::::25:326574464:34:::::::|h[Изначальная блуза со знаком интеллекта]|h|r', 'i10404?597': '|cff1eff00|Hitem:10404::::::597:1783919744:34:::::::|h[Надежный пояс со знаком мартышки]|h|r', 'i15222?19': '|cff1eff00|Hitem:15222::::::19:2015402368:34:::1::::|h[Колючая дубина с печатью выносливости]|h|r', 'i14172?179': '|cff1eff00|Hitem:14172::::::179:1720700288:34:::::::|h[Одеяния пирата со знаком духа]|h|r', 'i9783?154': '|cff1eff00|Hitem:9783::::::154:544530048:34:::::::|h[Разбойничий нагрудник с печатью выносливости]|h|r', 'i3292': '|cff1eff00|Hitem:3292::::::::34:::::::|h[Мундир предков]|h|r', 'i9854?866': '|cff1eff00|Hitem:9854::::::866:1399970944:34:::::::|h[Жакет лучника со знаком орла]|h|r', 'i6681': '|cffffffff|Hitem:6681::::::::34:::1:::...
 'autoScan' (2226272920880) = {bool} False
 'autoSave' (2226272920944) = {bool} False
 'addonVersion' (2226272920112) = {str} 'v0.14.00-classic'
 'showBigButton' (2226272921008) = {bool} False
 'addonHash' (2226272921136) = {str} 'eb75110'
 'autoScanDelay' (2226272921072) = {int} 10
 'allowLDBI' (2226272921264) = {bool} True
 'showNewItems' (2226272921200) = {int} 10
 'itemDB_2' (2226272920176) = {dict} <class 'dict'>: {'i15010?25': '|cff1eff00|Hitem:15010::::::25:326574464:34:::::::|h[Изначальная блуза со знаком интеллекта]|h|r', 'i10404?597': '|cff1eff00|Hitem:10404::::::597:1783919744:34:::::::|h[Надежный пояс со знаком мартышки]|h|r', 'i15222?19': '|cff1eff00|Hitem:15222::::::19:2015402368:34:::1::::|h[Колючая дубина с печатью выносливости]|h|r', 'i14172?179': '|cff1eff00|Hitem:14172::::::179:1720700288:34:::::::|h[Одеяния пирата со знаком духа]|h|r', 'i9783?154': '|cff1eff00|Hitem:9783::::::154:544530048:34:::::::|h[Разбойничий нагрудник с печатью выносливости]|h|r', 'i3292': '|cff1eff00|Hitem:3292::::::::34:::::::|h[Мундир предков]|h|r', 'i9854?866': '|cff1eff00|Hitem:9854::::::866:1399970944:34:::::::|h[Жакет лучника со знаком орла]|h|r', 'i6681': '|cffffffff|Hitem:6681::::::::34:::1::::|h[Терновый шип]|h|r', 'i14158?1960': '|cff1eff00|Hitem:14158::::::1960:109047552:34:::::::|h[Языческий жилет с ледяной аурой]|h|r', 'i9929?2035': '|cff1eff00|Hitem:9929::::::2035:197516160:34::...
 'targetAuctioneer' (2226272902720) = {bool} True
 'disableKeybinds' (2226272920752) = {bool} False
 'ah' (2226346137840) = {list} <class 'list'>: [{'shortChar': 'Световод', 'testScan': False, 'elapsed': '8.08107920002937', 'data': 'i15010?25!/2,1,1742,1834, i10404?597!/3,1,1296,1599, i15222?19!/4,1,1710,1800, i14172?179!/3,1,1255,1255, i9783?154!/3,1,3230,3400,&3,1,2105,3383, i3292!/3,1,400,500,&3,1,404,500, i9854?866!/3,1,7402,8000, i6681!/4,1,9686,10000, i14158?1960!/3,1,11742,12360, i9929?2035!/3,1,10000,10000, i5773!/1,1,66500,70000,&4,1,91711,101901,&3,1,59999,59999, i14172?1958!/3,1,2128,2150, i3192?671!/3,1,742,1000, i6551?1097!/3,1,2850,2999, i9790?24!/3,1,1045,1100, i9809?1999!/3,1,4582,5000, i8152!/2,1,707,745,&3,2,5294,5296,&4,1,698,735,&2,1,679,715,&2,1,679,715,&2,1,679,715,&4,2,1348,1420,&2,1,669,705, i15222?1548!/2,1,1728,1750,&4,1,1828,2000, i6604?845!/3,1,3800,4000, i7443?1611!/3,1,3550,3995, i4360!/4,5,450,460,&4,8,570,712,&4,10,900,900, i6539?2030!/4,1,2943,4900, i9864?940!/3,1,8590,9900, i2292!/3,1,52001,100000, i3195?844!/4,1,2058,2500, i8178?1012!/4,1,459,550,459&2,1,517,545, i15734!/3,1,3455...
 'ldbi' (2226346137784) = {list} <class 'list'>: ['']

#############################################################

БАЗА ИТЕМОВ

'itemDB_2' (2226272920176) = {dict} <class 'dict'>: {'i15010?25': '|cff1eff00|Hitem:15010::::::25:326574464:34:::::::|h[Изначальная блуза со знаком интеллекта]|h|r', 'i10404?597': '|cff1eff00|Hitem:10404::::::597:1783919744:34:::::::|h[Надежный пояс со знаком мартышки]|h|r', 'i15222?19': '|cff1eff00|Hitem:15222::::::19:2015402368:34:::1::::|h[Колючая дубина с печатью выносливости]|h|r', 'i14172?179': '|cff1eff00|Hitem:14172::::::179:1720700288:34:::::::|h[Одеяния пирата со знаком духа]|h|r', 'i9783?154': '|cff1eff00|Hitem:9783::::::154:544530048:34:::::::|h[Разбойничий нагрудник с печатью выносливости]|h|r', 'i3292': '|cff1eff00|Hitem:3292::::::::34:::::::|h[Мундир предков]|h|r', 'i9854?866': '|cff1eff00|Hitem:9854::::::866:1399970944:34:::::::|h[Жакет лучника со знаком орла]|h|r', 'i6681': '|cffffffff|Hitem:6681::::::::34:::1::::|h[Терновый шип]|h|r', 'i14158?1960': '|cff1eff00|Hitem:14158::::::1960:109047552:34:::::::|h[Языческий жилет с ледяной аурой]|h|r', 'i9929?2035': '|cff1eff00|Hitem:9929::::::2035:197516160:34::...
 'i15010?25' (2226272921456) = {str} '|cff1eff00|Hitem:15010::::::25:326574464:34:::::::|h[Изначальная блуза со знаком интеллекта]|h|r'
 'i10404?597' (2226272921520) = {str} '|cff1eff00|Hitem:10404::::::597:1783919744:34:::::::|h[Надежный пояс со знаком мартышки]|h|r'
 'i15222?19' (2226272921584) = {str} '|cff1eff00|Hitem:15222::::::19:2015402368:34:::1::::|h[Колючая дубина с печатью выносливости]|h|r'
 'i14172?179' (2226272921648) = {str} '|cff1eff00|Hitem:14172::::::179:1720700288:34:::::::|h[Одеяния пирата со знаком духа]|h|r'
 'i9783?154' (2226272921712) = {str} '|cff1eff00|Hitem:9783::::::154:544530048:34:::::::|h[Разбойничий нагрудник с печатью выносливости]|h|r'
 'i3292' (2226272888624) = {str} '|cff1eff00|Hitem:3292::::::::34:::::::|h[Мундир предков]|h|r'
 'i9854?866' (2226272921776) = {str} '|cff1eff00|Hitem:9854::::::866:1399970944:34:::::::|h[Жакет лучника со знаком орла]|h|r'

#############################################################

СПИСОК АУКОВ

'ah' (2226346137840) = {list} <class 'list'>: [{'shortChar': 'Световод', 'testScan': False, 'elapsed': '8.08107920002937', 'data': 'i15010?25!/2,1,1742,1834, i10404?597!/3,1,1296,1599, i15222?19!/4,1,1710,1800, i14172?179!/3,1,1255,1255, i9783?154!/3,1,3230,3400,&3,1,2105,3383, i3292!/3,1,400,500,&3,1,404,500, i9854?866!/3,1,7402,8000, i6681!/4,1,9686,10000, i14158?1960!/3,1,11742,12360, i9929?2035!/3,1,10000,10000, i5773!/1,1,66500,70000,&4,1,91711,101901,&3,1,59999,59999, i14172?1958!/3,1,2128,2150, i3192?671!/3,1,742,1000, i6551?1097!/3,1,2850,2999, i9790?24!/3,1,1045,1100, i9809?1999!/3,1,4582,5000, i8152!/2,1,707,745,&3,2,5294,5296,&4,1,698,735,&2,1,679,715,&2,1,679,715,&2,1,679,715,&4,2,1348,1420,&2,1,669,705, i15222?1548!/2,1,1728,1750,&4,1,1828,2000, i6604?845!/3,1,3800,4000, i7443?1611!/3,1,3550,3995, i4360!/4,5,450,460,&4,8,570,712,&4,10,900,900, i6539?2030!/4,1,2943,4900, i9864?940!/3,1,8590,9900, i2292!/3,1,52001,100000, i3195?844!/4,1,2058,2500, i8178?1012!/4,1,459,550,459&2,1,517,545, i15734!/3,1,3455...
 00 = {dict} <class 'dict'>: {'shortChar': 'Световод', 'testScan': False, 'elapsed': '8.08107920002937', 'data': 'i15010?25!/2,1,1742,1834, i10404?597!/3,1,1296,1599, i15222?19!/4,1,1710,1800, i14172?179!/3,1,1255,1255, i9783?154!/3,1,3230,3400,&3,1,2105,3383, i3292!/3,1,400,500,&3,1,404,500, i9854?866!/3,1,7402,8000, i6681!/4,1,9686,10000, i14158?1960!/3,1,11742,12360, i9929?2035!/3,1,10000,10000, i5773!/1,1,66500,70000,&4,1,91711,101901,&3,1,59999,59999, i14172?1958!/3,1,2128,2150, i3192?671!/3,1,742,1000, i6551?1097!/3,1,2850,2999, i9790?24!/3,1,1045,1100, i9809?1999!/3,1,4582,5000, i8152!/2,1,707,745,&3,2,5294,5296,&4,1,698,735,&2,1,679,715,&2,1,679,715,&2,1,679,715,&4,2,1348,1420,&2,1,669,705, i15222?1548!/2,1,1728,1750,&4,1,1828,2000, i6604?845!/3,1,3800,4000, i7443?1611!/3,1,3550,3995, i4360!/4,5,450,460,&4,8,570,712,&4,10,900,900, i6539?2030!/4,1,2943,4900, i9864?940!/3,1,8590,9900, i2292!/3,1,52001,100000, i3195?844!/4,1,2058,2500, i8178?1012!/4,1,459,550,459&2,1,517,545, i15734!/3,1,34550...
 01 = {str} '--'
 02 = {str} '[1]'
 03 = {dict} <class 'dict'>: {'shortChar': 'Световод', 'testScan': False, 'elapsed': '8.42128780007362', 'data': 'i15010?25!/2,1,1742,1834, i10404?597!Врачица/3,1,1296,1599, i15222?19!/4,1,1710,1800, i14172?179!Классикуе/3,1,1255,1255, i9783?154!/3,1,3230,3400,&3,1,2105,3383, i3292!/3,1,400,500,&3,1,404,500, i9854?866!/3,1,7402,8000, i6681!/4,1,9686,10000, i14158?1960!/3,1,11742,12360, i9929?2035!/3,1,10000,10000, i5773!/1,1,66500,70000,&4,1,91711,101901,!Беспилотник/3,1,59999,59999, i14172?1958!/3,1,2128,2150, i3192?671!/3,1,742,1000, i6551?1097!/3,1,2850,2999, i9790?24!/3,1,1045,1100, i9809?1999!/3,1,4582,5000, i8152!/2,1,707,745,&3,2,5294,5296,&4,1,698,735,&2,1,679,715,&2,1,679,715,&2,1,679,715,&4,2,1348,1420,&2,1,669,705, i4298!/4,1,4750,5000,&4,1,4543,4600, i6604?845!Балрогг/3,1,3800,4000, i7443?1611!/3,1,3550,3995, i4360!/4,5,450,460,&4,8,570,712,&4,10,900,900, i6539?2030!/4,1,2943,4900, i9864?940!Олдовый/3,1,8590,9900, i2292!/3,1,52001,100000, i3195?844!/4,1,2058,2500, i8178?1012!/4,1,459,55...
 04 = {str} '--'
 05 = {str} '[2]'
 06 = {dict} <class 'dict'>: {'shortChar': 'Световод', 'testScan': False, 'elapsed': '6.86670769989491', 'data': 'i15010?25!Ктерн/2,1,1742,1834, i10404?597!Врачица/2,1,1296,1599, i15222?19!Мандрик/4,1,1710,1800, i14172?179!Классикуе/3,1,1255,1255, i9783?154!Тэлри/3,1,3230,3400,!Жак/3,1,2105,3383, i3292!Корвакс/3,1,400,500,!Нейроквейк/3,1,404,500, i9854?866!Вазочка/3,1,7402,8000, i6681!Цугундер/4,1,9686,10000, i14158?1960!Хирос/3,1,11742,12360, i9929?2035!Таджикичан/3,1,10000,10000, i5773!Вега/4,1,91711,101901,!Беспилотник/3,1,59999,59999, i14172?1958!Фулкрум/3,1,2128,2150, i3192?671!Бигмаксколой/3,1,742,1000, i6551?1097!Магирус/3,1,2850,2999, i9790?24!Втриномджке/3,1,1045,1100, i9809?1999!Асакурик/2,1,4582,5000, i8152!Профура/2,1,669,705,!Каза/2,1,707,745,&4,2,1348,1420,!Гидроборода/4,1,698,735,!Понибанк/3,2,5294,5296,!Дивинити/2,1,679,715,&2,1,679,715,&2,1,679,715, i15222?1548!Зафрина/4,1,1828,2000,!Раззин/2,1,1728,1750, i6604?845!Балрогг/3,1,3800,4000, i7443?1611!Пипидастр/3,1,3550,3995, i4360!Ан...
 07 = {str} '--'
 08 = {str} '[3]'
 09 = {dict} <class 'dict'>: {'shortChar': 'Световод', 'testScan': False, 'elapsed': '6.58906459999085', 'data': 'i15010?25!Ктерн/2,1,1742,1834, i10404?597!Врачица/2,1,1296,1599, i15222?19!/4,1,1710,1800, i14172?179!/3,1,1255,1255, i9783?154!/3,1,3230,3400,&3,1,2105,3383, i3292!/3,1,400,500,&3,1,404,500, i9854?866!/3,1,7402,8000, i6047!/4,1,5000,10000, i14158?1960!/3,1,11742,12360, i9929?2035!/3,1,10000,10000, i5773!/4,1,91711,101901,&3,1,59999,59999, i14172?1958!/3,1,2128,2150, i3192?671!/3,1,742,1000, i6551?1097!/3,1,2850,2999, i9790?24!/3,1,1045,1100, i9809?1999!/2,1,4582,5000, i8152!Профура/2,1,669,705,!Каза/2,1,707,745,&4,2,1348,1420,!Гидроборода/4,1,698,735,!Деднаместе/4,1,653,688,!Понибанк/3,2,5294,5296,!Дивинити/1,1,679,715,&1,1,679,715,&1,1,679,715, i15222?1548!/2,1,1728,1750,&4,1,1828,2000, i6604?845!/3,1,3800,4000, i7443?1611!/3,1,3550,3995, i4360!/4,5,450,460,&4,8,570,712,&4,10,900,900, i6539?2030!/4,1,2943,4900, i9864?940!/3,1,8590,9900, i2292!/3,1,52001,100000, i3195?844!/4,1,2058,250...
 10 = {str} '--'
 11 = {str} '[4]'

#############################################################

ДАННЫЕ АУКА

03 = {dict} <class 'dict'>: {'shortChar': 'Световод', 'testScan': False, 'elapsed': '8.42128780007362', 'data': 'i15010?25!/2,1,1742,1834, i10404?597!Врачица/3,1,1296,1599, i15222?19!/4,1,1710,1800, i14172?179!Классикуе/3,1,1255,1255, i9783?154!/3,1,3230,3400,&3,1,2105,3383, i3292!/3,1,400,500,&3,1,404,500, i9854?866!/3,1,7402,8000, i6681!/4,1,9686,10000, i14158?1960!/3,1,11742,12360, i9929?2035!/3,1,10000,10000, i5773!/1,1,66500,70000,&4,1,91711,101901,!Беспилотник/3,1,59999,59999, i14172?1958!/3,1,2128,2150, i3192?671!/3,1,742,1000, i6551?1097!/3,1,2850,2999, i9790?24!/3,1,1045,1100, i9809?1999!/3,1,4582,5000, i8152!/2,1,707,745,&3,2,5294,5296,&4,1,698,735,&2,1,679,715,&2,1,679,715,&2,1,679,715,&4,2,1348,1420,&2,1,669,705, i4298!/4,1,4750,5000,&4,1,4543,4600, i6604?845!Балрогг/3,1,3800,4000, i7443?1611!/3,1,3550,3995, i4360!/4,5,450,460,&4,8,570,712,&4,10,900,900, i6539?2030!/4,1,2943,4900, i9864?940!Олдовый/3,1,8590,9900, i2292!/3,1,52001,100000, i3195?844!/4,1,2058,2500, i8178?1012!/4,1,459,55...
 'shortChar' (2226315080752) = {str} 'Световод'
 'testScan' (2226315080944) = {bool} False
 'elapsed' (2226346135768) = {str} '8.42128780007362'
 'data' (2226346135880) = {str} 'i15010?25!/2,1,1742,1834, i10404?597!Врачица/3,1,1296,1599, i15222?19!/4,1,1710,1800, i14172?179!Классикуе/3,1,1255,1255, i9783?154!/3,1,3230,3400,&3,1,2105,3383, i3292!/3,1,400,500,&3,1,404,500, i9854?866!/3,1,7402,8000, i6681!/4,1,9686,10000, i14158?196
 'itemDBcount' (2226315081072) = {int} 4290
 'realm' (2226346135936) = {str} 'Змейталак'
 'ts' (2226346136048) = {int} 1568160593
 'itemsCount' (2226315081136) = {int} 4274
 'region' (2226346135992) = {str} 'classic'
 'dataFormatVersion' (2226346111240) = {int} 6
 'char' (2226346136160) = {str} 'Световод-Змейталак'
 'newItems' (2226315081200) = {int} 8
 'count' (2226346136216) = {int} 29405
 'faction' (2226346136104) = {str} 'Alliance'
 'dataFormatInfo' (2226315080816) = {str} 'v4key!seller1/timeleft,itemCount,minBid,buyoutPrice,curBid&auction2&auction3!seller2/a1&a2 ...\\n(grouped by itemKey, seller) with auction units being timeleft,itemCount,minBid,buyoutPrice,curBid'
 'classic' (2226346136272) = {bool} True
 'firstCount' (2226315081392) = {int} 29405

"""
