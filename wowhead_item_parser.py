#!/usr/bin/python
# -*- coding: utf-8 -*-
#############################################################


import json
import threading

import psycopg2
import requests
from fake_headers import Headers


#############################################################


def random_proxy_from_db():
    with conn.cursor() as cursor:
        cursor.execute("select ip from proxy limit 1 offset floor(random() * (select count(*) from proxy));")
        conn.commit()
        proxy = cursor.fetchone()
    return proxy[0]


def fake_head():
    return Headers(headers=True).generate()


class MyThread(threading.Thread):

    def __init__(self, id):
        self.id = id
        threading.Thread.__init__(self)

    def run(self):
        print('ID START:', self.id)

        url = f'https://classic.wowhead.com/item={self.id}&xml'
        proxy1 = {'https': f'https://{random_proxy_from_db()}'}

        while True:
            try:
                # print(self.id, proxy1)
                # r = requests.get(url, headers=fake_head(), timeout=2)
                r = requests.get(url, proxies=proxy1, headers=fake_head(), timeout=2)
                # r = requests.get(url, timeout=2)
                if r.ok:
                    # print(self.id, r.text)
                    lockarr.acquire()
                    pars_data.update({self.id: r.text})
                    lockarr.release()
                    # print('ID END:', self.id)
                    return
            except Exception as err:
                # print('err:', err)
                proxy1 = {'https': f'https://{random_proxy_from_db()}'}


#############################################################

# https://ru.classic.wowhead.com/tooltips

if __name__ == "__main__":

    pars_data = {}
    lockarr = threading.Lock()
    lockprint = threading.Lock()

    host = 'ec2-176-34-183-20.eu-west-1.compute.amazonaws.com'
    database = 'd5d2079cgeblj3'
    user = 'fzzgiynifzdxbs'
    password = 'c8764f4669fc42774110fc08bb1ed91d608bb98c540d79e92affd0912396efd1'
    conn = psycopg2.connect(dbname=database, user=user, password=password, host=host, sslmode='require')
    print('connect to postgres OK')

    MAX_THREAD_COUNT = 100

    id_list = [i for i in range(0, 25000)]

    for id in id_list[::MAX_THREAD_COUNT]:
        threads = []
        for id_n in range(id, id + MAX_THREAD_COUNT):
            t = MyThread(id_n)
            t.start()
            threads.append(t)
        for t in threads:
            t.join()

    # limit = 0
    # while limit <= len(proxy_list_not_checked):
    #     threads = []
    #     for ip in proxy_list_not_checked[limit:limit + MAX_THREAD_COUNT]:
    #         t = MyThread(ip)
    #         t.start()
    #         threads.append(t)
    #     for t in threads:
    #         t.join()
    #     limit += MAX_THREAD_COUNT
    #     print('list shift limit', limit)

    print(len(pars_data))
    print(pars_data)

    with open("wowhead_pars_db.json", "w", encoding='utf-8') as write_file:
        json.dump(pars_data, write_file, sort_keys=True, indent=2, ensure_ascii=False)

    conn.close()

#############################################################
