# -*- coding: utf-8 -*-
import re

import skr_library.json2postgre
import xmltodict
import json

from pprint import pprint


def wowhead_url(id):
    return f'https://ru.classic.wowhead.com/item={int(id)}'


def find_item_desc(id, sub):
    """описание отема"""
    # print(id, sub)
    try:
        pattern = f'i{id}' if sub == '0' else f'i{id}?{sub}'
        res = re.search(r'\[.*]', itemDB[pattern])[0][1:-1]
    # except KeyError:
    #     pattern = f'i{id}' if sub == '0' else f'i{id}:{sub}'
    #     res = re.search(r'\[.*]', itemDB[pattern])[0][1:-1]
    except:
        res = '<err load desc>'
    return res


def make_beautiful():
    data_beautiful_json = {}

    with open('wowhead_pars_xml.json', "r", encoding='utf-8') as read_file:
        data_xml = json.load(read_file)

    for id in data_xml:
        if '<error>' in data_xml[id]:
            continue

        tmp = json.dumps(xmltodict.parse(data_xml[id]))
        tmp = json.loads(tmp)['wh_item']['item']

        del tmp['htmlTooltip']
        tmp['json'] = json.loads('{' + tmp['json'] + '}')
        tmp['jsonEquip'] = json.loads('{' + tmp['jsonEquip'] + '}')

        # print(id, tmp)
        data_beautiful_json.update({id: tmp})

    print('--------')

    with open("wowhead_pars_json.json", "w", encoding='utf-8') as write_file:
        json.dump(data_beautiful_json, write_file, indent=2, ensure_ascii=False)


def analyzzz():
    with open('wowhead_pars_json.json', "r", encoding='utf-8') as read_file:
        data = json.load(read_file)

    def topreagent():
        # САМЫЕ ПОПУЛЯРНЫЕ РЕАГЕНТЫ

        count_reagent = []

        for id in data:
            try:

                reagent = data[id]["createdBy"]['spell']['reagent']
                # print(type(data[id]["createdBy"]['spell']['reagent']))
                # pprint(data[id]["createdBy"]['spell']['reagent'])

                if type(reagent) == dict:
                    count_reagent.append(reagent['@id'])
                elif type(reagent) == list:
                    for n in reagent:
                        count_reagent.append(n['@id'])

            except:
                pass

        result = {i: count_reagent.count(i) for i in count_reagent}
        list_result = list(result.items())
        list_result.sort(key=lambda i: i[1], reverse=True)
        for i in list_result:
            # print(i[0], ':', i[1], find_item_desc(i[0], '0'))

            # buyprice = data.get(i[0]['jsonEquip']['buyprice'])
            buyprice = data[i[0]]['jsonEquip'].get('buyprice', '')

            if buyprice != '':
                print(f'{i[0]:<6} {i[1]:<6} {buyprice:<6} {find_item_desc(i[0], "0"):<20} {wowhead_url(i[0])}')

    ##################################################

    def allclass():
        # все классы штемов
        all_class = {}
        for id in data:
            # print(data[id]['class']['@id'])
            all_class.update({data[id]['class']['@id']: data[id]['class']['#text']})
        for i in sorted(all_class.keys()):
            print(i, all_class[i])

    # ALL_CLASS
    # 0 Consumables
    # 1 Containers
    # 2 Weapons
    # 4 Armor
    # 6 Projectiles
    # 7 Trade Goods
    # 9 Recipes
    # 10 Currency
    # 11 Quivers
    # 12 Quest
    # 13 Keys
    # 15 Miscellaneous

    ##################################################

    def allsubclass():
        # сабклассы

        all_subclass = {}
        for id in data:

            class1 = data[id]['class']['@id']

            try:
                subclass1 = data[id]['subclass']['@id']
                subclass1_val = data[id]['subclass']['#text']
                # print(id, data[id]['subclass']['@id'], data[id]['subclass']['#text'])
            except:
                pass
            # all_subclass.update({ data[id]['class']['@id'] : data[id]['class']['#text']})

            if not class1 in all_subclass:
                all_subclass.update({class1: []})
                all_subclass[class1].append(subclass1)
            else:
                all_subclass[class1].append(subclass1)

        for i in sorted(all_subclass.keys()):
            print(i, set(all_subclass[i]))

    # 12 Elixirs
    # 12 Mounts

    # 0 {'3', '-3', '0', '7', '1', '5', '2', '6', '4'}
    # 1 {'3', '1', '2', '0'}
    # 2 {'3', '14', '17', '15', '20', '0', '16', '7', '19', '13', '8', '18', '10', '1', '5', '2', '6', '4'}
    # 4 {'3', '-2', '-5', '-3', '0', '7', '-6', '8', '-8', '-4', '1', '9', '-7', '2', '6', '4'}
    # 6 {'3', '2'}
    # 7 {'3', '12', '11', '0', '7', '8', '10', '1', '9', '5', '2', '6'}
    # 9 {'3', '0', '7', '8', '1', '9', '5', '2', '6', '4'}
    # 10 {'0'}
    # 11 {'3', '2'}
    # 12 {'0'}
    # 13 {'1', '0'}
    # 15 {'3', '-2', '0', '1', '5', '2', '4'}

    ##################################################

    def allsubclass_desc():
        for id in data:
            class1 = data[id]['class']['@id']
            class1_text = data[id]['class']['#text']
            subclass1 = data[id]['subclass']['@id']
            subclass1_text = data[id]['subclass'].get('#text', None)
            link = data[id]['link']

            # print(
            #     id,
            #     class1,
            #     class1_text,
            #     subclass1,
            #     subclass1_text,
            #     find_item_desc(id, '0'),
            #     link,
            # )

            if class1 == '15' and subclass1 == '0':
                print(
                    id,
                    class1,
                    class1_text,
                    subclass1,
                    subclass1_text,
                    find_item_desc(id, '0'),
                    link,
                )

    # ALL_CLASS
    # 0 Consumables
    # 1 Containers
    # 2 Weapons
    # 4 Armor
    # 6 Projectiles
    # 7 Trade Goods
    # 9 Recipes
    # 10 Currency
    # 11 Quivers
    # 12 Quest
    # 13 Keys
    # 15 Miscellaneous

    # 0 {'3':'', '-3':'', '0':'', '7':'', '1':'', '5':'', '2':'', '6':'', '4'}
    # 1 {'3':'', '1':'', '2':'', '0'}
    # 2 {'3':'', '14':'', '17':'', '15':'', '20':'', '0':'', '16':'', '7':'', '19':'', '13':'', '8':'', '18':'', '10':'', '1':'', '5':'', '2':'', '6':'', '4'}
    # 4 {'3':'', '-2':'', '-5':'', '-3':'', '0':'', '7':'', '-6':'', '8':'', '-8':'', '-4':'', '1':'', '9':'', '-7':'', '2':'', '6':'', '4'}
    # 6 {'3':'', '2'}
    # 7 {'3':'', '12':'', '11':'', '0':'', '7':'', '8':'', '10':'', '1':'', '9':'', '5':'', '2':'', '6'}
    # 9 {'3':'', '0':'', '7':'', '8':'', '1':'', '9':'', '5':'', '2':'', '6':'', '4'}
    # 10 {'0'}
    # 11 {'3':'', '2'}
    # 12 {'0'}
    # 13 {'1':'', '0'}
    # 15 {'3':'', '-2':'', '0':'', '1':'', '5':'', '2':'', '4'}

    ##################################################

    def allquality():
        # качество
        all_quality = {}
        for id in data:
            # print(data[id]['class']['@id'])
            all_quality.update({data[id]['quality']['@id']: data[id]['quality']['#text']})
        for i in sorted(all_quality.keys()):
            print(i, all_quality[i])

    # 0 Poor
    # 1 Common
    # 2 Uncommon
    # 3 Rare
    # 4 Epic
    # 5 Legendary
    # 6 Artifact

    ##################################################

    # topreagent()
    # allclass()
    # allsubclass()
    allsubclass_desc()
    # allquality()


if __name__ == "__main__":
    with open('itemDB.json', "r", encoding='utf-8') as read_file:
        itemDB = json.load(read_file)

    # make_beautiful()

    analyzzz()
