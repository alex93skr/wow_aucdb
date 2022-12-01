#!/usr/bin/python
# -*- coding: utf-8 -*-
#############################################################
import random
import re
from json import loads
from multiprocessing import Process
from pprint import pprint

from bs4 import BeautifulSoup

import json
import random
import threading
from pprint import pprint

import psycopg2
import requests
from fake_headers import Headers


#############################################################

def decoder(st):
    dict_utf = {
        '\\u0410': 'А', '\\u0430': 'а',
        '\\u0411': 'Б', '\\u0431': 'б',
        '\\u0412': 'В', '\\u0432': 'в',
        '\\u0413': 'Г', '\\u0433': 'г',
        '\\u0414': 'Д', '\\u0434': 'д',
        '\\u0415': 'Е', '\\u0435': 'е',
        '\\u0401': 'Ё', '\\u0451': 'ё',
        '\\u0416': 'Ж', '\\u0436': 'ж',
        '\\u0417': 'З', '\\u0437': 'з',
        '\\u0418': 'И', '\\u0438': 'и',
        '\\u0419': 'Й', '\\u0439': 'й',
        '\\u041a': 'К', '\\u043a': 'к',
        '\\u041b': 'Л', '\\u043b': 'л',
        '\\u041c': 'М', '\\u043c': 'м',
        '\\u041d': 'Н', '\\u043d': 'н',
        '\\u041e': 'О', '\\u043e': 'о',
        '\\u041f': 'П', '\\u043f': 'п',
        '\\u0420': 'Р', '\\u0440': 'р',
        '\\u0421': 'С', '\\u0441': 'с',
        '\\u0422': 'Т', '\\u0442': 'т',
        '\\u0423': 'У', '\\u0443': 'у',
        '\\u0424': 'Ф', '\\u0444': 'ф',
        '\\u0425': 'Х', '\\u0445': 'х',
        '\\u0426': 'Ц', '\\u0446': 'ц',
        '\\u0427': 'Ч', '\\u0447': 'ч',
        '\\u0428': 'Ш', '\\u0448': 'ш',
        '\\u0429': 'Щ', '\\u0449': 'щ',
        '\\u042a': 'Ъ', '\\u044a': 'ъ',
        '\\u042b': 'Ы', '\\u044b': 'ы',
        '\\u042c': 'Ь', '\\u044c': 'ь',
        '\\u042d': 'Э', '\\u044d': 'э',
        '\\u042e': 'Ю', '\\u044e': 'ю',
        '\\u042f': 'Я', '\\u044f': 'я',
    }

    for u in dict_utf:
        if u in st:
            st = st.replace(u, dict_utf[u])
    return st


def random_proxy_from_db():
    with conn.cursor() as cursor:
        cursor.execute("select ip from proxy limit 1 offset floor(random() * (select count(*) from proxy));")
        conn.commit()
        proxy = cursor.fetchone()
    return proxy[0]




def fake_head():
    return Headers(headers=True).generate()


#############################################################


class MyThread(threading.Thread):

    def __init__(self, id):
        self.id = id
        threading.Thread.__init__(self)

    def run(self):

        url = f'https://ru.classic.wowhead.com/npc={self.id}'
        proxy1 = {'https': f'https://{random.choice(proxy_data)}'}

        while True:
            try:
                # r = requests.get(url, headers=fake_head(), timeout=1)
                r = requests.get(url, proxies=proxy1, headers=fake_head(), timeout=1)
                # print(r.ok)
                if r.ok:
                    self.html = r.text
                    self.parser()
                    # print(proxy1)
                    return
            except Exception as err:
                proxy1 = {'https': f'https://{random.choice(proxy_data)}'}

    def parser(self):
        id_dict = {}

        # lockprint.acquire()
        # print(self.id)
        # lockprint.release()

        # print(url)

        # r = requests.get(url)
        # r.encoding = 'utf-8'
        # html = r.text

        # print(html)

        soup = BeautifulSoup(self.html, 'html.parser')

        if soup.title.text == 'NPC - World of Warcraft':
            lockprint.acquire()
            print(self.id, 'skip')
            lockprint.release()
            return

        # name
        name = soup.title.text
        name = name[:name.find(' - NPC')]
        # print(name)
        id_dict.update({'name': name})

        # type
        # type = browser.find_element_by_class_name("breadcrumb").text[14:]
        # type = browser.find_element_by_class_name("breadcrumb").text[14:]
        # print(type)
        # id_dict.update({'type': type})

        # zone
        zone = soup.find("span", {"id": "locations"})
        if not zone is None:
            zone = zone.text
        else:
            start = self.html.find('<a href="/zone=')
            if start != -1:
                end = self.html[start:start + 100].find('</a>')
                zone = self.html[start:start + end]
                zone = zone[zone.find('>') + 1:]
                # zone = re.search(r'^.*\(', zone)
                # spawnpoint = re.search(r'\(\d*\)', zone)
            else:
                zone = ''
        # zone = zone.replace('\n', '').replace(' ', '').replace(u'\xa0', ' ')
        zone = zone.replace('\n', '').replace(u'\xa0', ' ').replace(' ', '')
        # print(zone)
        id_dict.update({'zone': zone})

        # try:
        #     zone = soup.find("span", {"id": "locations"})
        #     # zone = browser.find_element_by_id("locations").text
        # except:
        #     start = html.find('<a href="/zone=')
        #     if start != -1:
        #         end = html[start:start + 100].find('</a>')
        #         zone = html[start:start + end]
        #         zone = zone[zone.find('>') + 1:]
        #         # zone = re.search(r'^.*\(', zone)
        #         # spawnpoint = re.search(r'\(\d*\)', zone)
        #     else:
        #         zone = None
        # print(zone)
        # id_dict.update({'zone': zone})

        # info
        info = {}
        info_sub = ['Фракция', 'Деньги', 'Мана', 'Уровень', 'Тип', 'Реакция', 'Здоровье']
        start = self.html.find('[ul][li]')
        end = self.html[start:].find('[\/li][\/ul]')
        info_str = self.html[start + 4:start + end + 6]
        info_str = decoder(info_str)

        # infobox_list = browser.find_element_by_id("infobox-contents-0")
        li_list = re.findall(r'\[li].*?\[\\\/li]', info_str)
        for li in li_list:
            # print(li)

            li = li[4:-6]
            # print(li)
            # text = li.text
            if 'Добавлено' in li:
                info.update({'Добавлено': li[23:]})
                continue

            if 'Можно приручить' in li:
                info.update({'Можно приручить': li[16:]})
                continue

            if 'Можно починить' in li:
                info.update({'Можно починить': True})
                continue

            fnd = False
            for sub in info_sub:
                if sub in li:
                    if sub == 'Деньги':
                        money = re.search(r'money=.*?]', li)[0]
                        info.update({sub: money[6:-1].replace(' ', '')})
                    else:
                        info.update({sub: li[len(sub) + 2:]})
                    fnd = True
                    break
            if not fnd:
                print('!!!', li)
                error.append([self.id, li])

        # print(info)
        id_dict.update({'info': info})

        # Listview = re.findall(r'Listview\({template:.*, name', html)
        # for i in Listview:
        #     tmp = i[10:-6]
        #     print(tmp)
        #     if tmp not in templates:
        #         templates.append(tmp)

        # drop
        drop = re.search(r"template: 'item', id: 'drops'.*]}\);", self.html)
        if not drop is None:
            drop = drop[0]
            drop = drop[drop.find('data:') + 5:-3]
            drop = loads(drop)
        # print(drop)
        id_dict.update({'drop': drop})

        # print()

        # print(html)
        # return id_dict

        lockarr.acquire()
        pars_data.update({self.id: id_dict})
        lockarr.release()

        lockprint.acquire()
        print(self.id, 'done')
        lockprint.release()


#############################################################


if __name__ == "__main__":

    pars_data = {}
    proxy_data = []
    lockarr = threading.Lock()
    lockprint = threading.Lock()

    templates = []
    error = []

    host = 'ec2-176-34-183-20.eu-west-1.compute.amazonaws.com'
    database = 'd5d2079cgeblj3'
    user = 'fzzgiynifzdxbs'
    password = 'c8764f4669fc42774110fc08bb1ed91d608bb98c540d79e92affd0912396efd1'
    conn = psycopg2.connect(dbname=database, user=user, password=password, host=host, sslmode='require')
    print('connect to postgres OK')


    with conn.cursor() as cursor:
        cursor.execute("select * from proxy;")
        conn.commit()
        for ip in cursor.fetchall():
            # print(ip[0])
            proxy_data.append(ip[0])

    print(proxy_data)

    MAX_THREAD_COUNT = 30



    id_list = [i for i in range(0, 18000)]
    # id_list = [random.randint(100, 15000) for i in range(50)]
    # id_list = [10182]

    for id in id_list[::MAX_THREAD_COUNT]:
        threads = []
        for id_n in range(id, id + MAX_THREAD_COUNT):
            t = MyThread(id_n)
            t.start()
            threads.append(t)
            # print(threads)
        for t in threads:
            t.join()


    print('pars_data', len(pars_data))

    # pprint(pars_data)

    with open("wowhead_pars_npc.json", "w", encoding='utf-8') as write_file:
        json.dump(pars_data, write_file, sort_keys=False, indent=0, ensure_ascii=False)
        # json.dump(pars_data, write_file, sort_keys=True, indent=2, ensure_ascii=False)

    print('error')
    print(error)

    conn.close()


#############################################################
