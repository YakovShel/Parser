import json
import os
import aiohttp
import asyncio
import aiofiles
import random
import pyautogui
from time import sleep

from aiohttp import TCPConnector, ClientSession
from fake_useragent import UserAgent
from selenium import webdriver
from bs4 import BeautifulSoup


async def get_data(url, session):
    ua = UserAgent()
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Host": "www.nike.com",
        "User-Agent": f"{ua.random}",
        "Accept-Language": "ru",
        "Referer": "https://www.nike.com/",
        "Connection": "keep-alive"
    }

    async with session.get(url, headers=headers) as r:
        page_name = url.split("/")[-1]
        print(page_name)
        if not os.path.exists(f"data/{page_name}"):
            os.mkdir(f"data/{page_name}")

        with open(f"data/{page_name}/{page_name}.html", "w") as file:
            file.write(await r.text())

        with open(f"data/{page_name}/{page_name}.html") as file:
            src = file.read()

        soup = BeautifulSoup(src, "lxml")
        articles = soup.find_all("a", class_="product-card__link-overlay")

        products_urls = []
        products_names = []
        products_data_json = []
        for article in articles:
            product_url = article.get("href")
            pos = product_url.rfind("/")
            product_url = product_url[:pos]
            products_urls.append(product_url)

        for product_url in products_urls:
            product_name = product_url.split("/")[-1]

            if len(product_name) >= 5:
                products_names.append(product_name)

                async with session.get(product_url, headers=headers) as req:
                    if not os.path.exists(f"data/{page_name}/{product_name}"):
                        os.mkdir(f"data/{page_name}/{product_name}")

                    with open(f"data/{page_name}/{product_name}/{product_name}.html", "w") as file:
                        file.write(await req.text())

                    with open(f"data/{page_name}/{product_name}/{product_name}.html") as file:
                        src = file.read()

                    soup = BeautifulSoup(src, "lxml")

                    # product_description = soup.find("div", class_="description-preview body-2 css-1pbvugb").text
                    product_text = soup.find("script", id="__NEXT_DATA__").text

                    product_images_urls = []
                    product_text_images = product_text
                    product_image_url = ""
                    index_of_image = product_text_images.find('"url"') + 7
                    while product_text_images[index_of_image] != '"':
                        product_image_url += product_text_images[index_of_image]
                        index_of_image += 1
                    product_images_urls.append(product_image_url)
                    product_text_images = product_text_images[index_of_image::]

                    for i in range(7):
                        product_image_url = ""
                        index_of_image = product_text_images.find("squarishURL") + 14
                        while product_text_images[index_of_image] != '"':
                            product_image_url += product_text_images[index_of_image]
                            index_of_image += 1
                        product_images_urls.append(product_image_url)
                        product_text_images = product_text_images[index_of_image::]

                    product_text_images = product_text
                    product_price = ""
                    index_of_price = product_text_images.find("currentPrice") + 14
                    while product_text_images[index_of_price] != ',':
                        product_price += product_text_images[index_of_price]
                        index_of_price += 1

                    product_text_sizes = product_text
                    index_of_size = product_text_sizes.find("skus") + 7
                    index_of = product_text_sizes[index_of_size::].find("]") + index_of_size
                    product_text_sizes = product_text_sizes[index_of_size:index_of]
                    product_sizes = []
                    while product_text_sizes.find("nikeSize") != -1:
                        product_size = ""
                        index_of_size = product_text_sizes.find("nikeSize") + 11
                        while product_text_sizes[index_of_size] != '"':
                            product_size += product_text_sizes[index_of_size]
                            index_of_size += 1
                        product_sizes.append(product_size)
                        product_text_sizes = product_text_sizes[index_of_size + 1::]

                    products_data_json.append(
                        {
                            "Name": product_name,
                            "URL": product_url,
                            "Price": product_price,
                            "Sizes": product_sizes,
                            "Images": product_images_urls
                            # "Description": product_description
                        }
                    )
                await asyncio.sleep(0.5)

                # pyautogui.scroll(random.randint(-100, 100))
                #
                # pyautogui.moveTo(random.randint(100, 1000), random.randint(100, 800))

        print(f"gather all {page_name}")

        await write_json(f"data/{page_name}/{page_name}.json", products_data_json)
        print(f"write json {page_name}")


async def write_json(filename, data):
    async with aiofiles.open(filename, 'w', encoding='utf-8') as f:
        await f.write(json.dumps(data, ensure_ascii=False, indent=4))


async def main():
    if not os.path.exists("data"):
        os.mkdir("data")

    proxy_list = []
    with open('proxy_list.txt', 'r') as file:
        proxy_list = [line.strip() for line in file.readlines() if line.strip()]

    print(proxy_list)
    connector = TCPConnector(limit_per_host=len(proxy_list))
    async with ClientSession(connector=connector) as session:
        urls = ["https://www.nike.com/w/mens-lifestyle-shoes-13jrmznik1zy7ok",
                "https://www.nike.com/w/mens-jordan-shoes-37eefznik1zy7ok",
                "https://www.nike.com/w/mens-air-max-shoes-a6d8hznik1zy7ok",
                "https://www.nike.com/w/mens-air-force-1-shoes-5sj3yznik1zy7ok",
                "https://www.nike.com/w/mens-shoes-90aohz9gw3aznik1zy7ok",
                "https://www.nike.com/w/mens-training-gym-shoes-58jtoznik1zy7ok",
                "https://www.nike.com/w/mens-basketball-shoes-3glsmznik1zy7ok",
                "https://www.nike.com/w/mens-running-shoes-37v7jznik1zy7ok",
                "https://www.nike.com/w/mens-skateboarding-shoes-8mfrfznik1zy7ok",
                "https://www.nike.com/w/mens-sandals-slides-fl76znik1",
                "https://www.nike.com/w/mens-jordan-clothing-37eefz6ymx6znik1",
                "https://www.nike.com/w/mens-matching-sets-2lukpznik1",
                "https://www.nike.com/w/mens-big-tall-clothing-6ymx6zau499znik1",
                "https://www.nike.com/w/mens-hoodies-pullovers-6riveznik1",
                "https://www.nike.com/w/mens-pants-tights-2kq19znik1",
                "https://www.nike.com/w/mens-jackets-vests-50r7yznik1",
                "https://www.nike.com/w/mens-tops-t-shirts-9om13znik1",
                "https://www.nike.com/w/mens-shorts-38fphznik1",
                "https://www.nike.com/w/mens-underwear-9yhm6znik1",
                "https://www.nike.com/w/mens-socks-7ny3qznik1",
                "https://www.nike.com/w/womens-lifestyle-shoes-13jrmz5e1x6zy7ok",
                "https://www.nike.com/w/womens-jordan-shoes-37eefz5e1x6zy7ok",
                "https://www.nike.com/w/womens-air-max-shoes-5e1x6za6d8hzy7ok",
                "https://www.nike.com/w/womens-air-force-1-shoes-5e1x6z5sj3yzy7ok",
                "https://www.nike.com/w/womens-shoes-5e1x6z90aohz9gw3azy7ok",
                "https://www.nike.com/w/womens-training-gym-shoes-58jtoz5e1x6zy7ok",
                "https://www.nike.com/w/womens-basketball-shoes-3glsmz5e1x6zy7ok",
                "https://www.nike.com/w/womens-running-shoes-37v7jz5e1x6zy7ok",
                "https://www.nike.com/w/sandals-slides-3rauvz5e1x6zfl76",
                "https://www.nike.com/w/womens-jordan-clothing-37eefz5e1x6z6ymx6",
                "https://www.nike.com/w/womens-matching-sets-clothing-2lukpz5e1x6z6ymx6",
                "https://www.nike.com/w/womens-plus-size-clothing-5e1x6z6ymx6z8mjm2",
                "https://www.nike.com/w/womens-hoodies-pullovers-5e1x6z6rive",
                "https://www.nike.com/w/womens-pants-tights-2kq19z5e1x6",
                "https://www.nike.com/w/womens-tights-leggings-29sh2z5e1x6",
                "https://www.nike.com/w/womens-sports-bras-40qgmz5e1x6",
                "https://www.nike.com/w/womens-jackets-vests-50r7yz5e1x6",
                "https://www.nike.com/w/womens-tops-t-shirts-5e1x6z9om13",
                "https://www.nike.com/w/womens-shorts-38fphz5e1x6",
                "https://www.nike.com/w/womens-socks-5e1x6z7ny3q",
                "https://www.nike.com/w/kids-lifestyle-shoes-13jrmzv4dhzy7ok",
                "https://www.nike.com/w/kids-jordan-shoes-37eefzv4dhzy7ok",
                "https://www.nike.com/w/kids-air-max-shoes-a6d8hzv4dhzy7ok",
                "https://www.nike.com/w/kids-air-force-1-lifestyle-shoes-13jrmz5sj3yzv4dhzy7ok",
                "https://www.nike.com/w/1onraz3aqegz90aohz9gw3a",
                "https://www.nike.com/w/kids-basketball-shoes-3glsmzv4dhzy7ok",
                "https://www.nike.com/w/kids-running-shoes-37v7jzv4dhzy7ok",
                "https://www.nike.com/w/kids-sandals-slides-fl76zv4dh",
                "https://www.nike.com/w/kids-jordan-clothing-37eefz6ymx6zv4dh",
                "https://www.nike.com/w/kids-matching-sets-2lukpzv4dh",
                "https://www.nike.com/w/kids-tops-t-shirts-9om13zv4dh",
                "https://www.nike.com/w/kids-shorts-38fphzv4dh",
                "https://www.nike.com/w/kids-hoodies-pullovers-6rivezv4dh",
                "https://www.nike.com/w/kids-jackets-vests-50r7yzv4dh",
                "https://www.nike.com/w/kids-clothing-pants-tights-2kq19z6ymx6zv4dh",
                "https://www.nike.com/w/kids-sports-bras-40qgmzv4dh",
                "https://www.nike.com/w/kids-socks-7ny3qzv4dh"]

        tasks = [get_data(url, session) for url in urls]
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())