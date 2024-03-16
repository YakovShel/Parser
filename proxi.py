import os
import pickle
import random
from requests_html import HTMLSession
from datetime import datetime


def get_proxies():
    now_time = datetime.now()

    if 'proxies.pickle' in os.listdir('.'):
        with open('proxies.pickle', 'rb') as f:
            proxies_dump = pickle.load(f)
            dump_time = proxies_dump[1][1]['last_check']
            proxy_list = proxies_dump[1]
            date_time_obj = datetime.strptime(dump_time, '%Y-%m-%d %H:%M:%S')
    else:
        dump_time = None

    if not dump_time or (now_time - date_time_obj).days > 1:
        json_url = 'https://api.best-proxies.ru/proxylist.txt'
        query_params = {
            "key": "23f2dc25ef81e42bc829ae3b49370644",
            "limit": 100,
            "type": "https"
        }

        with HTMLSession() as session:
            response = session.get(json_url, params=query_params)

        proxy_list = response.json()

        with open('proxies.pickle', 'wb') as f:
            pickle.dump((dump_time, proxy_list), f)

    proxies = [{
        'http': f"https://{proxy['ip']}:{proxy['port']}"
    } for proxy in proxy_list]

    return proxies


if __name__ == "__main__":
    print(get_proxies())
