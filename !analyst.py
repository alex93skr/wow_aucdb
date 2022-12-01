#!/usr/bin/python
# -*- coding: utf-8 -*-
#############################################################


import re
import json
import numpy
import datetime
import pickle
import statistics

from pprint import pprint
from time import sleep
from tabulate import tabulate


#############################################################


def load_json(url):
    with open(url, "r", encoding='utf-8') as read_file:
        return json.load(read_file)


def load_pickle(url):
    with open(url, "rb") as read_file:
        return pickle.load(read_file)


def gold(n):
    if n == 'None' or n == None:
        return n
    n = str(n)
    if len(n) > 4:
        return f'{n[:-4]}.{n[-4:-2]}.{n[-2:]}'
    elif len(n) > 2:
        return f'{n[:-2]}.{n[-2:]}'
    else:
        return n


def unix2ts(ts):
    return datetime.datetime.fromtimestamp(ts)


def find_item_desc(id, sub):
    """описание итема"""
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


def wowhead_url(id):
    return f'<a href="https://ru.classic.wowhead.com/item={id}" target="_blank"> </a>'
    # return f'https://ru.classic.wowhead.com/item={int(id)}'


def wowhead_nps(id):
    return f'<a href="https://ru.classic.wowhead.com/npc={id}" target="_blank"> </a>'
    # return f'https://ru.classic.wowhead.com/npc={int(id)}'


def find_all_drop(item_id):
    # список шанса дропа по всем НПЦ
    # [id_npc, drop, npc_name]

    arr = []
    for npc_id in wh_npc:
        # есть дроп
        if wh_npc[npc_id]['drop'] != None:
            for n in wh_npc[npc_id]['drop']:
                # есть итем в дропе
                if n['id'] == item_id:
                    # print(npc_id, n['id'])

                    drop = n.get('percentOverride')

                    if drop == None:
                        modes1 = n['modes'].get('1')
                        drop = round(modes1['count'] / modes1['outof'] * 100, 2)

                    arr.append([npc_id, drop, wh_npc[npc_id]['name']])

    return sorted(arr, key=lambda i: i[1], reverse=True)


#############################################################

class Graphic:

    def __init__(self):
        # self.graphic_count_of_all_ah()
        self.graphic_item_arcts()
        # self.graphic_central_tendency()

    def graphic_count_of_all_ah(self):
        # графика
        import matplotlib.pyplot as plt

        # кол-во ставок по всем архивам
        print('draw graphic archive', len(data_archive))
        print()

        # for archive in data_archive:
        #     count_allbids = data_archive[archive]['count_of_all_sub']
        #
        #     print(archive, unix2ts(archive), archive)
        #     print(archive, len(data_archive[archive]['parsData']))
        #     print(count_allbids)

        # x = [data_archive[archive]['ts'] for archive in data_archive]

        ts = [unix2ts(ts) for ts in data_archive]

        count_of_all_sub = [data_archive[archive]['count_of_all_sub'] for archive in data_archive]
        count_of_all_bids = [data_archive[archive]['count_of_all_bids'] for archive in data_archive]

        plt.plot(ts, count_of_all_sub, 'g.-')
        # plt.plot(ts, count_of_all_bids, 'r.-')

        # подписи
        plt.xlabel('ts')
        plt.ylabel('count')
        plt.grid(True)

        # рисовка
        plt.show()

    def graphic_central_tendency(self):
        # графика
        import matplotlib.pyplot as plt

        # кол-во ставок по всем архивам
        print('draw graphic archive', len(data_archive))
        print()

        item = '15407'
        avg_buyoutPrice_arr = []
        median_buyoutPrice_arr = []
        mode_buyoutPrice_arr = []
        item_ts = []
        for arc_ts in data_archive:
            try:
                avg_buyoutPrice = data_archive[arc_ts]['parsData'][item]['0']['avg_buyoutPrice']
                avg_buyoutPrice_arr.append(avg_buyoutPrice)

                median_buyoutPrice = data_archive[arc_ts]['parsData'][item]['0']['median_buyoutPrice']
                median_buyoutPrice_arr.append(median_buyoutPrice)

                mode_buyoutPrice = data_archive[arc_ts]['parsData'][item]['0']['mode_buyoutPrice']
                mode_buyoutPrice_arr.append(mode_buyoutPrice)

                item_ts.append(unix2ts(arc_ts))
            except:
                pass

        # print(count_item_in_arc)
        # print(price_item_in_arc)
        # print(item_ts)

        # fig, axs = plt.subplots(2, 1, sharex=True, sharey=True)
        plt.subplot(311)
        plt.plot(item_ts, avg_buyoutPrice_arr, 'r.-', label='avg')
        # plt.ylabel('count bids')
        plt.grid(True)
        plt.legend(loc='upper right')

        title = find_item_desc(item, '0')
        plt.title(title)

        plt.subplot(312)
        plt.plot(item_ts, median_buyoutPrice_arr, 'g.-', label='median')
        # plt.ylabel('avg price')
        plt.grid(True)
        plt.legend(loc='upper right')

        plt.subplot(313)
        plt.plot(item_ts, mode_buyoutPrice_arr, 'b.-', label='mode')
        # plt.ylabel('avg price')
        plt.xlabel('ts')
        plt.grid(True)
        plt.legend(loc='upper right')
        # рисовка

        plt.show()

    def graphic_item_arcts(self):
        # графика
        import matplotlib.pyplot as plt

        # кол-во ставок по всем архивам
        print('draw graphic archive', len(data_archive))
        print()

        # for archive in data_archive:
        #     count_allbids = data_archive[archive]['count_of_all_sub']
        #
        #     print(archive, unix2ts(archive), archive)
        #     print(archive, len(data_archive[archive]['parsData']))
        #     print(count_allbids)

        # x = [data_archive[archive]['ts'] for archive in data_archive]

        count_item_in_arc = []
        price_item_in_arc = []
        item_ts = []
        for arc_ts in data_archive:
            try:
                count = data_archive[arc_ts]['parsData'][item_for_graph]['0']['count_of_internal_bids']
                count_item_in_arc.append(count)

                price = data_archive[arc_ts]['parsData'][item_for_graph]['0']['avg_buyoutPrice']
                price_item_in_arc.append(price)

                print(gold(price), unix2ts(arc_ts))

                item_ts.append(unix2ts(arc_ts))

            except:
                pass

        # print(count_item_in_arc)
        # print(price_item_in_arc)
        # print(item_ts)

        # fig, axs = plt.subplots(2, 1, sharex=True, sharey=True)
        plt.subplot(211)
        plt.plot(item_ts, count_item_in_arc, 'r.-', label='count bids')
        plt.ylabel('count bids')
        plt.grid(True)
        plt.legend(loc='upper right')

        title = find_item_desc(item_for_graph, '0')
        plt.title(title)

        plt.subplot(212)
        plt.plot(item_ts, price_item_in_arc, 'g.-', label='avg price')
        plt.ylabel('avg price')
        plt.xlabel('ts')
        plt.grid(True)
        plt.legend(loc='upper right')

        # рисовка

        plt.show()


#############################################################


class Analyst:
    def __init__(self):

        # ЗАГРУЗКА АРХИВОВ ПО ВРЕМЕНИ
        self.analyst_load_archive()

        # + count_of_bids
        # + count_of_internal_bids количество вложенных ставок
        self.analyst_count_of_bids()

        # count_of_all_sub
        # count_of_all_bids
        self.analyst_count_of_all_bids()

        # for ts in data_archive:
        #     print(ts, data_archive[ts]['count_of_all_sub'])
        #     print(ts, data_archive[ts]['count_of_all_bids'])

        # + avg_buyoutPrice
        self.analyst_avg_buyoutPrice()

        #  smart_avg_buyoutPrice

        print()

        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!

        if GRAPH:
            Graphic()

        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!

        # РАЗДЕЛЕНИЕ НА
        # АРХИВЫ    data_archive
        # КУРРЕНТ   data_current

        last_data_archive_key = list(data_archive.keys())[-1]
        print('last_data_archive_key', last_data_archive_key)

        for subkey in data_archive[last_data_archive_key]:
            data_current.update({subkey: data_archive[last_data_archive_key][subkey]})

        print('data_current:', unix2ts(last_data_archive_key), data_current.keys())
        del data_archive[last_data_archive_key]
        print('data_archive:', len(data_archive))

        print()

        #  + avg_from_all_archive_avg_buyoutPrice
        self.analyst_avg_from_all_archive_avg_buyoutPrice()

        print()

        # pprint(data_current)

        # print(len(data_current))
        #
        # for i in data_current:
        #     print(type(i))

    def analyst_load_archive(self):
        # архив ауков с разрывом по времени
        previous_ts = 0

        print('load all archives', len(data_archive_unanalyzed))

        # print(type(data_archive_unanalyzed))
        # print()

        data_archive_keys = list(data_archive_unanalyzed.keys())

        for ts in data_archive_keys[:-1]:

            ts = int(ts)
            # timeleft
            # 4 13260   более 8 часов
            # 3 12466   от 2 до 8 часов
            # 2 2496    от 30 мин до 2 часов
            # 1 873     менее 30 мин

            # 86400     сутки
            # 28800 сек - 8 часов
            # 14400   4

            # print(n, previous_ts, ts, unix2ts(ts))

            if (previous_ts == 0) or (previous_ts + 28800 < ts):
                print('add', ts, unix2ts(ts))
                previous_ts = ts
                data_archive.update({ts: data_archive_unanalyzed[ts]})
            else:
                print('skip', ts, unix2ts(ts))

        ts_last = int(data_archive_keys[-1])
        data_archive.update({ts_last: data_archive_unanalyzed[ts_last]})
        print('add last', ts_last, unix2ts(ts_last))

        print('archives after time sorting', len(data_archive))
        print()

    def analyst_count_of_bids(self):
        # подсчет всех вложенных ставок

        for ts in data_archive:
            for id in data_archive[ts]['parsData']:
                for sub in data_archive[ts]['parsData'][id]:

                    SUB_STR = data_archive[ts]['parsData'][id][sub]

                    n_count = 0

                    for n in SUB_STR['bids']:

                        # внутри стаков
                        if SUB_STR['bids'][n]['itemCount'] == 1:
                            n_count += 1
                        else:
                            n_count += SUB_STR['bids'][n]['itemCount']
                    # print(n_count)

                    SUB_STR.update({'count_of_bids': len(SUB_STR['bids'])})
                    SUB_STR.update({'count_of_internal_bids': n_count})

        print('ADD count_of_bids')
        print('ADD analyst_count_of_internal_bids')

    def analyst_count_of_all_bids(self):
        # подсчет всех ставок во все архивах

        for ts in data_archive:
            count_of_all_sub = 0
            count_of_all_bids = 0
            for id in data_archive[ts]['parsData']:
                for sub in data_archive[ts]['parsData'][id]:
                    count_of_all_sub += data_archive[ts]['parsData'][id][sub]['count_of_bids']
                    count_of_all_bids += data_archive[ts]['parsData'][id][sub]['count_of_internal_bids']

            data_archive[ts].update({'count_of_all_sub': count_of_all_sub})
            data_archive[ts].update({'count_of_all_bids': count_of_all_bids})

            # print(count_of_all_bids)

        print('ADD count_of_all_sub')
        print('ADD count_of_all_bids')

    def analyst_avg_buyoutPrice(self):
        # подсчет всех вложенных ставок

        for ts in data_archive:
            for id in data_archive[ts]['parsData']:
                for sub in data_archive[ts]['parsData'][id]:

                    SUB_STR = data_archive[ts]['parsData'][id][sub]

                    avg_n_count = 0
                    avg_n_sum = 0
                    avg_buyoutPrice = 0
                    avg_all_value_list = []

                    for n in SUB_STR['bids']:
                        if not SUB_STR['bids'][n]['buyoutPrice'] is None:

                            itemCount = SUB_STR['bids'][n]['itemCount']
                            buyoutPrice = SUB_STR['bids'][n]['buyoutPrice']

                            # внутри стаков
                            if itemCount == 1:
                                avg_n_count += 1
                                avg_n_sum += buyoutPrice
                                avg_all_value_list.append(buyoutPrice)
                            else:
                                avg_n_count += itemCount
                                avg_n_sum += buyoutPrice
                                avg_all_value_list += [buyoutPrice for _ in range(itemCount)]

                    if avg_n_count != 0:
                        avg_buyoutPrice = round(avg_n_sum / avg_n_count)

                    if avg_all_value_list == []:
                        median_buyoutPrice = 0
                        mode_buyoutPrice = 0
                    else:
                        median_buyoutPrice = round(statistics.median(avg_all_value_list), 1)

                        try:
                            mode_buyoutPrice = round(statistics.mode(avg_all_value_list), 1)
                        except:
                            pass

                    SUB_STR.update({'avg_buyoutPrice': avg_buyoutPrice})
                    SUB_STR.update({'median_buyoutPrice': median_buyoutPrice})
                    SUB_STR.update({'mode_buyoutPrice': mode_buyoutPrice})

        print('ADD analyst_avg_buyoutPrice')

    def analyst_avg_from_all_archive_avg_buyoutPrice(self):
        # средняя цена выкупа по всем архивам

        for id in data_current['parsData']:
            for sub in data_current['parsData'][id]:

                archive_avg_buyoutPrice = 0
                tmp_arr = []

                for ts in data_archive:
                    try:
                        avg_buyoutPrice = data_archive[ts]['parsData'][id][sub]['avg_buyoutPrice']
                        if avg_buyoutPrice != 0:
                            # print(archive, tmp)
                            tmp_arr.append(avg_buyoutPrice)
                    except:
                        pass

                if tmp_arr != []:
                    archive_avg_buyoutPrice = round(sum(tmp_arr) / len(tmp_arr))

                data_current['parsData'][id][sub].update(
                    {'avg_from_all_archive_avg_buyoutPrice': archive_avg_buyoutPrice})

                # print(archive_avg_buyoutPrice)

        print('ADD analyst_avg_from_all_archive_avg_buyoutPrice')


#############################################################


header = '''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
 <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <title>aucdb_report</title>
    <link rel="stylesheet" type="text/css" href="style.css">
    <script>var whTooltips = {colorLinks: true, iconizeLinks: true, renameLinks: true};</script>
    <script src="https://wow.zamimg.com/widgets/power.js"></script>
 </head>

<script>
function copyText() {
  let text = document.activeElement.parentElement.previousSibling.innerText;
  let tmp = document.createElement("INPUT"), // Создаём новый текстовой input
    focus = document.activeElement; // Получаем ссылку на элемент в фокусе (чтобы не терять фокус)
  tmp.value = text; // Временному input вставляем текст для копирования
  document.body.appendChild(tmp); // Вставляем input в DOM
  tmp.select(); // Выделяем весь текст в input
  document.execCommand("copy"); // Магия! Копирует в буфер выделенный текст (см. команду выше)
  document.body.removeChild(tmp); // Удаляем временный input
  focus.focus(); // Возвращаем фокус туда, где был
}
</script>

<center>
'''


class Printer:
    def __init__(self):
        # print_buyout_dynamics()

        file_html = open('aucdb_report.html', 'w', encoding='utf-8')

        file_html.write(header)

        # NPC
        # file_html.write('<br>САМЫЕ ГОЛДОВЫЕ НЕПИСИ')
        # out = self.print_npc_gold()
        # file_html.write(out.replace('<thead>', '<thead class="rtfm">').replace('<tbody>', '<tbody class="rtfm">'))

        # file_html.write('<br>ВСЕ НЕПИСИ')
        # out = self.print_npc_all()
        # file_html.write(out.replace('<thead>', '<thead class="rtfm">').replace('<tbody>', '<tbody class="rtfm">'))

        # AUC
        file_html.write('<br>МИН СТАВКА к ПОСЛЕДНЕМУ выкупу')
        out = self.print_min_bid_2_all_archive_avg_buyout(avg='c', time_left=[1,2,3], sort_by_col=7, cut_lines=100)
        file_html.write(out.replace('<thead>', '<thead class="rtfm">').replace('<tbody>', '<tbody class="rtfm">'))

        file_html.write('<br>МИН СТАВКА к АРХИВАМ ')
        out = self.print_min_bid_2_all_archive_avg_buyout(avg='a', time_left=[1,2,3], sort_by_col=7, cut_lines=100)
        file_html.write(out.replace('<thead>', '<thead class="rtfm">').replace('<tbody>', '<tbody class="rtfm">'))

        file_html.write('<br>ВЫКУПИТЬ и продать ВЕНДОРУ')
        out = self.print_buyoutPrice_for_vendorprice()
        file_html.write(out.replace('<thead>', '<thead class="rtfm">').replace('<tbody>', '<tbody class="rtfm">'))

        file_html.write('<br>ТОП РЕАГЕНТЫ НА АХ')
        out = self.print_topreagent_count_on_ah()
        file_html.write(out.replace('<thead>', '<thead class="rtfm">').replace('<tbody>', '<tbody class="rtfm">'))

        # file_html.write('<br>РЕАГЕНТЫ ОТ ВЕНДОРОВ')
        # out = self.print_topreagent_vendor_sall_count_on_ah()
        # file_html.write(out.replace('<thead>', '<thead class="rtfm">').replace('<tbody>', '<tbody class="rtfm">'))

        # file_html.write('<br>Все сортированные ставки по выкупу')
        # out = self.print_all_sort_by_arc_buyout()
        # file_html.write(out.replace('<thead>', '<thead class="rtfm">').replace('<tbody>', '<tbody class="rtfm">'))

        # NPC + AUC
        # file_html.write('<br>Средний архивный выкуп и шанс дропа')
        # out = self.print_all_sort_by_arc_buyout_and_drop()
        # file_html.write(out.replace('<thead>', '<thead class="rtfm">').replace('<tbody>', '<tbody class="rtfm">'))

        # file_html.write('<br>Весь падающий лут по ценности / шансу дропа')
        # out = self.print_all_sort_all_drop_and_dropchance()
        # file_html.write(out.replace('<thead>', '<thead class="rtfm">').replace('<tbody>', '<tbody class="rtfm">'))

        file_html.close()

        import os
        myCmd = 'explorer D:\\code\\wow_aucdb\\aucdb_report.html'
        os.system(myCmd)

        # В КОНСОЛЬ

        # print('\n', '#' * 80, '\nCURRENT мин ставка к среднему выкупу по АРХИВАМ \n', sep='')
        # print_min_bid_2_all_archive_avg_buyout(avg='c', time_left=1, sort_by_col=7, cut_lines=100)
        #
        # print('\n', '#' * 80, '\nARCHIVES мин ставка к среднему выкупу КУРРЕНТ \n', sep='')
        # print_min_bid_2_all_archive_avg_buyout(avg='a', time_left=1, sort_by_col=7, cut_lines=100)
        #
        # print('\n', '#' * 80, '\nВЫКУП к ВЕНДОРУ \n', sep='')
        # print_buyoutPrice_for_vendorprice()
        #
        # print('\n', '#' * 80, '\nРЕАГЕНТЫ ОТ ВЕНДОРОВ \n', sep='')
        # print_topreagent_vendor_sall_count_on_ah()
        #
        # print('\n', '#' * 80, '\nТОП РЕАГЕНТЫ НА АХ \n', sep='')
        # print_topreagent_count_on_ah()

    def print_all_sort_all_drop_and_dropchance(self):
        # Весь падающий лут по ценности / шансу дропа
        arr = []

        # pprint(wh_npc['9437'])

        for npc_id in wh_npc:
            # есть дроп
            if wh_npc[npc_id]['drop'] != None:
                # итемов в дропе
                for n in wh_npc[npc_id]['drop']:
                    # качество
                    n_id_item = str(n['id'])
                    if wh_item[n_id_item]['quality']['@id'] in ['3', '4', '5', '6'] and \
                            wh_item[n_id_item]['class']['@id'] != '12':
                        # print(npc_id, n_id_item)

                        name = wh_npc[npc_id].get('name', '')
                        type = wh_npc[npc_id]['info'].get('Тип', '')
                        level = wh_npc[npc_id]['info'].get('Уровень', '')
                        zone = wh_npc[npc_id]['zone']
                        # gold = wh_npc[id]['info'].get('Деньги', '')

                        # print(npc_id, n_id_item, pprint() 9437 11197)

                        drop = n.get('percentOverride')

                        if drop == None:
                            modes1 = n['modes'].get('1')
                            if modes1['outof'] != 0:
                                drop = round(modes1['count'] / modes1['outof'] * 100, 2)
                            else:
                                drop = 0

                        try:
                            avg_arc = data_current['parsData'][int(n_id_item)][0]['avg_buyoutPrice']
                        except:
                            avg_arc = 0

                        arr.append([
                            wowhead_url(n_id_item),
                            drop,
                            avg_arc,
                            wowhead_nps(npc_id),
                            # npc_id,
                            # name,
                            type,
                            level,
                            # gold,
                            zone[:25],
                        ])

        return tabulate(
            sorted(arr, key=lambda i: i[1], reverse=True)[:1000],
            # sorted(arr, key=lambda bids: bids[3], reverse=True)[:200],
            # arr,
            # header,
            # colalign=('left', 'left', 'center', 'right', 'right', 'right', 'right'),
            tablefmt="html"
            # tablefmt="simple"
        )

    def print_all_sort_by_arc_buyout(self):
        arr = []
        for id in data_current['parsData']:
            for sub in data_current['parsData'][id]:
                arr.append([
                    id,
                    sub,

                    data_current['parsData'][id][sub]['count_of_internal_bids'],
                    data_current['parsData'][id][sub]['avg_from_all_archive_avg_buyoutPrice'],
                    data_current['parsData'][id][sub]['avg_buyoutPrice'],

                    # find_item_desc(id, sub),  # 6
                    wowhead_url(id)  # 7
                ])
        # for i in sorted(arr, key=lambda bids: bids[3], reverse=True):
        #     print(
        #         f'{i[0]:<6} '
        #         f'{i[1]:<4} '
        #         f'{gold(i[2]):>14} '
        #         f'{gold(i[3]):>14}  '
        #         f'{i[4]} '
        #         f'{i[5]}'
        #     )

        arr.sort(key=lambda bids: bids[3], reverse=True)

        arr = arr[:300]
        for line in arr:
            line[3] = gold(line[3])
            line[4] = gold(line[4])

        header = ['id', 'sub', 'count', 'arc', 'avg', '']

        return tabulate(
            arr,
            # sorted(arr, key=lambda bids: bids[3], reverse=True)[:200],
            # arr,
            header,
            # colalign=('left', 'left', 'center', 'right', 'right', 'right', 'right'),
            tablefmt="html"
            # tablefmt="simple"
        )

    def print_all_sort_by_arc_buyout_and_drop(self):
        arr = []
        for id in data_current['parsData']:
            for sub in data_current['parsData'][id]:
                arr.append([
                    id,
                    sub,

                    data_current['parsData'][id][sub]['count_of_internal_bids'],
                    data_current['parsData'][id][sub]['avg_from_all_archive_avg_buyoutPrice'],
                    data_current['parsData'][id][sub]['avg_buyoutPrice'],

                    # find_item_desc(id, sub),  # 6
                    wowhead_url(id),  # 7
                ])
        # for i in sorted(arr, key=lambda bids: bids[3], reverse=True):
        #     print(
        #         f'{i[0]:<6} '
        #         f'{i[1]:<4} '
        #         f'{gold(i[2]):>14} '
        #         f'{gold(i[3]):>14}  '
        #         f'{i[4]} '
        #         f'{i[5]}'
        #     )

        arr.sort(key=lambda bids: bids[3], reverse=True)

        arr_drop = []

        for line in arr[:500]:
            line[3] = gold(line[3])
            line[4] = gold(line[4])
            drop = find_all_drop(int(line[0]))[:1]

            # print(drop)
            if drop != []:
                dropfrom = drop[0][0]
                drop = drop[0][1]
                # if wh_npc[dropfrom]['info'].get('Тип') == None:
                line.append(drop)
                arr_drop.append(line)

        # print(arr_drop)

        header = ['id', 'sub', 'count', 'arc', 'avg', '', '']

        return tabulate(
            # arr,
            sorted(arr_drop, key=lambda bids: bids[6], reverse=True),
            # arr,
            header,
            # colalign=('left', 'left', 'center', 'right', 'right', 'right', 'right'),
            tablefmt="html"
            # tablefmt="simple"
        )

    def print_min_bid_2_all_archive_avg_buyout(self, avg='c', time_left=[1], sort_by_col=7, cut_lines=500):
        # мин ставка к среднему выкупу по архивам
        arr = []
        for id in data_current['parsData']:
            for sub in data_current['parsData'][id]:

                archive_avg_buyout = data_current['parsData'][id][sub]['avg_from_all_archive_avg_buyoutPrice']

                for n in data_current['parsData'][id][sub]['bids']:

                    minBid = data_current['parsData'][id][sub]['bids'][n]['minBid']
                    curBid = data_current['parsData'][id][sub]['bids'][n]['curBid']
                    timeleft = data_current['parsData'][id][sub]['bids'][n]['timeleft']
                    avg_buyoutPrice = data_current['parsData'][id][sub]['avg_buyoutPrice']
                    difference_bid_vs_avg = 0

                    if not minBid is None and archive_avg_buyout != 0:

                        # отношение к архиву или к куренту
                        if avg == 'c':
                            avg_go = avg_buyoutPrice
                        elif avg == 'a':
                            avg_go = archive_avg_buyout

                        if curBid is None:
                            difference_bid_vs_avg = avg_go / minBid
                            # print('if', avg, minBid, difference_bid_vs_avg)
                        else:
                            difference_bid_vs_avg = avg_go / curBid
                            # print('else', avg, curBid, difference_bid_vs_avg)

                        if minBid is None:
                            minBid = 'None'
                        if curBid is None:
                            curBid = 'None'

                        # условия добавления в печать
                        if timeleft in time_left and avg_go > 9999:
                            arr.append([
                                id,
                                sub,

                                timeleft,
                                gold(minBid),
                                gold(curBid),
                                gold(avg_buyoutPrice),
                                gold(archive_avg_buyout),
                                round(difference_bid_vs_avg, 1),  # 7
                                # [avg_go, minBid, curBid, difference_bid_vs_avg],  # 7

                                wowhead_url(id),
                                '<button onclick="copyText()">copy</button>',

                            ])
        # ВЫВОД
        # https://bitbucket.org/astanin/python-tabulate/src/master/

        # print(tabulate(
        #     sorted(arr, key=lambda col: col[sort_by_col], reverse=True)[:cut_lines],
        #     # arr,
        #     header,
        #     colalign=('left', 'left', 'center', 'right', 'right', 'right', 'right', 'right'),
        #     # tablefmt="html"
        #     tablefmt="simple"
        # ))

        header = ['id', 'sub', 'tleft', 'minBid', 'curBid', 'avg_bout', 'arc_avg', 'bid|avg', 'wh_item', '']

        return tabulate(
            sorted(arr, key=lambda col: col[sort_by_col], reverse=True)[:cut_lines],
            # arr,
            header,
            colalign=('left', 'left', 'center', 'right', 'right', 'right', 'right'),
            tablefmt="html"
            # tablefmt="simple"
        )

    def print_buyoutPrice_for_vendorprice(self):
        # выкуп дешевле чем продать вендору

        arr = []
        for id in data_current['parsData']:
            for sub in data_current['parsData'][id]:
                for n in data_current['parsData'][id][sub]['bids']:

                    try:
                        buyoutPrice = data_current['parsData'][id][sub]['bids'][n]['buyoutPrice']
                        vendorprice = wh_item[id]['jsonEquip']['sellprice']
                        if (buyoutPrice < vendorprice):
                            arr.append(
                                [id,
                                 sub,
                                 buyoutPrice,
                                 vendorprice,
                                 buyoutPrice - vendorprice,
                                 find_item_desc(id, sub)[:40],
                                 wowhead_url(id),
                                 '<button onclick="copyText()">copy</button>',
                                 ])
                    except:
                        pass

        header = ['id', 'sub', 'bOut', 'vendor', 'b/v', '', '', '']

        return tabulate(arr, header,
                        # colalign=('left', 'left', 'center', 'right', 'right', 'right', 'right', 'right'),
                        tablefmt="html"
                        # tablefmt="simple"
                        )

    def print_topreagent_vendor_sall_count_on_ah(self):
        # САМЫЕ ПОПУЛЯРНЫЕ РЕАГЕНТЫ КОТОРЫХ НЕТ НА АУКЕ

        count_reagent = []

        for id in wh_item:
            try:

                reagent = wh_item[id]["createdBy"]['spell']['reagent']
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

        arr = []

        for i in list_result:

            buyprice = wh_item[i[0]]['jsonEquip'].get('buyprice', '')
            if buyprice != '':
                try:
                    count_bids = len(data_current['parsData'][i[0]]['0']['bids'])
                except:
                    count_bids = 0

                arr.append([
                    i[0],
                    i[1],
                    buyprice,
                    count_bids,
                    # find_item_desc(i[0], "0"),
                    wowhead_url(i[0]),
                    '<button onclick="copyText()">copy</button>',

                ])

        header = ['', '', 'buyprice', 'count_bids', '', '']

        return tabulate(arr[:250], header,
                        colalign=('right', 'right', 'right', 'left'),
                        tablefmt="html"
                        # tablefmt="simple"
                        )

    def print_topreagent_count_on_ah(self):
        # ТОПОВЫЕ РЕГИ КОЛВО НА АХ

        good_list = {
            15407: '! 55g+',
            12360: '! 44g+',
            7910: '!!! 1g',
            12803: '!!! 80s',
            3486: '-',
            17010: '! 30g',
            11371: '1',
            17011: '! 30g',
            7076: '!!!',
            12364: '!!!',
            12800: '!!!',
            10505: '-',
            12799: '!',
            19726: '!Кров лоза',
            14256: '!1.24g',
            12361: '!1.24g',
            6265: '-',
            12804: '!',
            4231: '-',
            12809: '!!50g?',
            17012: '!Сердц кожа',
            10558: '?',
            11382: '!159g?',
            13926: '!',
            4387: '-',
            12811: '!20g',
        }

        arr = []
        count_reagent = []

        for id in wh_item:
            try:
                reagent = wh_item[id]["createdBy"]['spell']['reagent']
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
            vendorprice = wh_item[i[0]]['jsonEquip'].get('buyprice', '')

            try:
                # count_bids = len(data_current['parsData'][i[0]]['0']['bids'])
                count_bids = data_current['parsData'][int(i[0])][0]['count_of_internal_bids']
                # pprint(data_current['parsData'][i[0]]['0'])

            except:
                count_bids = 0

            try:
                avg_buyoutPrice = data_current['parsData'][int(i[0])][0]['avg_buyoutPrice']
            except:
                avg_buyoutPrice = None

            try:
                archive_avg_buyout = data_current['parsData'][int(i[0])][0]['avg_from_all_archive_avg_buyoutPrice']
            except:
                archive_avg_buyout = None

            # print(i, count_bids, avg_buyoutPrice, archive_avg_buyout)

            # avg_buyoutPrice = data_current['parsData'][i[0]]['0']['avg_buyoutPrice']
            # archive_avg_buyout = data_current['parsData'][i[0]]['0']['avg_from_all_archive_avg_buyoutPrice']

            my_comm = good_list[int(i[0])] if int(i[0]) in good_list else ''

            arr.append([
                i[0],
                i[1],

                vendorprice,
                count_bids,
                my_comm,

                gold(avg_buyoutPrice),
                gold(archive_avg_buyout),

                # find_item_desc(i[0], "0")[:30],
                wowhead_url(i[0]),
                '<button onclick="copyText()">copy</button>',

            ])

        header = ['id', 'popular\nreag', 'vendor\nprice', 'count\non AH', '', 'avg\nbuyout', 'archive\navg\nbuyout', '',
                  '']

        return tabulate(arr[:250], header,
                        colalign=('left', 'left', 'right', 'right', 'right', 'right', 'right'),
                        tablefmt="html"
                        # tablefmt="simple"
                        )

    def print_npc_gold(self):
        arr = []

        for id in wh_npc:
            gold = wh_npc[id]['info'].get('Деньги')
            type = wh_npc[id]['info'].get('Тип', '')
            if not gold is None and type == '':
                arr.append([
                    int(id),
                    int(gold),
                    wh_npc[id].get('name', ''),
                    type,
                    wh_npc[id]['info'].get('Уровень', ''),
                    wowhead_nps(id),
                ])

        header = ['id', 'gold', 'name', 'Тип', 'Уровень', '']

        return tabulate(sorted(arr, key=lambda bids: bids[1], reverse=True)[:500], header,
                        # colalign=('left', 'left', 'right', 'right', 'right', 'right', 'right'),
                        tablefmt="html"
                        )

    def print_npc_all(self):
        arr = []

        for id in wh_npc:
            name = wh_npc[id].get('name', '')
            type = wh_npc[id]['info'].get('Тип', '')
            level = wh_npc[id]['info'].get('Уровень', '')
            zone = wh_npc[id]['zone']
            gold = wh_npc[id]['info'].get('Деньги', '')

            arr.append([
                id,
                name,
                type,
                level,
                gold,
                zone[:25],
                wowhead_nps(id),
            ])

        # header = ['id', 'name', 'name', 'Тип', 'Уровень', '']

        return tabulate(sorted(arr, key=lambda i: (i[2], i[3]), reverse=True),
                        # colalign=('left', 'left', 'right', 'right', 'right', 'right', 'right'),
                        tablefmt="html"
                        )


#############################################################

def main():
    pass


#############################################################


if __name__ == '__main__':
    # загрузка джейсонов
    # data_archive_unanalyzed = load_json('data_archive.json')
    # wh_item = load_json('wowhead_pars_json.json')
    # wh_npc = load_json('wowhead_pars_npc.json')

    itemDB = load_json('itemDB.json')
    data_archive_unanalyzed = load_pickle('data_archive.pickle')
    wh_item = load_pickle('wowhead_pars_item.pickle')
    wh_npc = load_pickle('wowhead_pars_npc.pickle')

    # рабочие словари
    data_archive = {}
    data_current = {}

    # графики
    item_for_graph = '11207'
    # GRAPH = True
    GRAPH = False

    # запуск
    Analyst()
    Printer()

    print()
#############################################################
