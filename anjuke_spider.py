import requests
from fake_useragent import UserAgent
import logging
from pyquery import PyQuery as pq
import csv
import time
from random import randint

CITY = 'xm'  # 厦门
UA = UserAgent()
INDEX_URL = 'https://{city}.zu.anjuke.com/fangyuan/p{page}/'
TOTAL_PAGE = 10
FILENAME = f'{CITY}_house.csv'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


def make_headers():
    return {
        "authority": "xm.zu.anjuke.com",
        "method": "GET",
        "path": "/?from=navigation",
        "scheme": "https",
        "accept-language": "zh-CN,zh;q=0.9",
        "cache-control": "no-cache",
        "cookie": "ctid=46; cmctid=606; aQQ_ajkguid=1F093C96-3B9C-9D3C-A2ED-692DB7D7500D; id58=e87rkGBFsBQizOhbB7gWAg==; id58=e87rkGBFsBQizOhbB7hJAg==; wmda_uuid=c53370dd1cd81557eb04544a5d168993; wmda_new_uuid=1; wmda_visited_projects=%3B6289197098934; sessid=BF480ADD-5B41-1B54-319D-58CB76BC162E; twe=2; obtain_by=2; _ga=GA1.2.753763977.1615259741; _gid=GA1.2.586494276.1615259741; _gat=1; 58tj_uuid=c622135a-e1cd-4f12-82c4-eea78c07213c; new_session=1; init_refer=https%253A%252F%252Fwww.baidu.com%252Fother.php%253Fsc.Ks0000jfdjm2ER4kjAPUGofjwslvINAygsyXR0JRO3PSZCu9sOjiljRjoGT_mL3jUwyXxvNqnA7fbWfuTHurg_r_X5WzN0PaT5wefI8F-OMROjEZBcPCZeUjS3g5_LLXUOCz4HUsyXx8ldekE_GNfg9OBljB94lqET5eqKn51SKhJGucXarYdxtLbO3tFeFqHNGyh0-UkMRWsDWZEiFSoBEdmY_R.DY_NR2Ar5Od663rj6thm_8jViBjEWXkSUSwMEukmnSrZr1wC4eL_8C5RojPak3S5Zm0.TLFWgv-b5HDkrfK1ThPGujYknHb0THY0IAYq_Q2SYeOP0ZN1ugFxIZ-suHYs0A7bgLw4TARqnsKLULFb5UazEVrO1fKzmLmqnfKdThkxpyfqnHRzPjc4n104n0KVINqGujYkPjczPHDkP6KVgv-b5HDsrjm4PW640AdYTAkxpyfqnHczP1n0TZuxpyfqn0KGuAnqiD4K0APzm1YvPj6dPf%2526ck%253D1219.3.66.325.168.273.199.86%2526dt%253D1615259738%2526wd%253D%2525E5%2525AE%252589%2525E5%2525B1%252585%2525E5%2525AE%2525A2%2526tpl%253Dtpl_12273_24677_20875%2526l%253D1524293090%2526us%253DlinkName%25253D%252525E6%252525A0%25252587%252525E9%252525A2%25252598-%252525E4%252525B8%252525BB%252525E6%252525A0%25252587%252525E9%252525A2%25252598%252526linkText%25253D%252525E5%252525AE%25252589%252525E5%252525B1%25252585%252525E5%252525AE%252525A2-%252525E5%25252585%252525A8%252525E6%25252588%252525BF%252525E6%252525BA%25252590%252525E7%252525BD%25252591%252525EF%252525BC%2525258C%252525E6%25252596%252525B0%252525E6%25252588%252525BF%25252520%252525E4%252525BA%2525258C%252525E6%25252589%2525258B%252525E6%25252588%252525BF%25252520%252525E6%2525258C%25252591%252525E5%252525A5%252525BD%252525E6%25252588%252525BF%252525E4%252525B8%2525258A%252525E5%252525AE%25252589%252525E5%252525B1%25252585%252525E5%252525AE%252525A2%252525EF%252525BC%25252581%252526linkType%25253D; new_uv=1; als=0; lps=https%3A%2F%2Fxm.zu.anjuke.com%2F%3Ffrom%3Dnavigation%7Chttps%3A%2F%2Fxm.anjuke.com%2F; wmda_session_id_6289197098934=1615259745542-2610bb33-4a18-b656; xxzl_cid=0b654befc6214b94a2779a4ab88befcf; xzuid=2d855dfe-7233-4aeb-a7f7-d7b253b0a7c9",
        "pragma": "no-cache",
        "referer": "https://xm.anjuke.com/",
        "sec-ch-ua-mobile": "?0",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-site",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": UA.random
    }


def scrape_page(url):
    logging.info('scraping %s', url)
    try:
        response = requests.get(url, headers=make_headers())
        if response.status_code == 200:
            return response.text
        logging.error('get invalid status code %s while scraping %s', response.status_code, url)
    except Exception:
        logging.error('error occurred while scraping %s', url, exc_info=True)


def scrape_index(page):
    url = INDEX_URL.format(city=CITY, page=page)
    return scrape_page(url)


def parse_index(html):
    doc = pq(html)
    houses = doc('div.zu-itemmod')
    for house in houses.items():
        name = house('h3 b').text()
        href = house('h3 a').attr('href')
        detail = house('p.details-item.tag').text()
        detail = detail.split(' ')[0].split('|') if detail else None
        if detail is None or len(detail) != 3:
            house_type = area = floor = None
        else:
            house_type, area, floor = detail
        address = house('address.details-item a').text()
        price = house('.zu-side b').text()
        yield name, house_type, area, floor, address, price, href


def save_data(data):
    with open(FILENAME, 'a') as f:
        writer = csv.writer(f)
        writer.writerows(data)


def main():
    for page in range(1, TOTAL_PAGE + 1):
        index_html = scrape_index(page)
        if not index_html:
            continue
        data = list(parse_index(index_html))
        if not data:
            logging.error('data error while scraping page %s', page)
        save_data(data)
        logging.info('saving page %s data', page)
        time.sleep(randint(3, 5))


if __name__ == '__main__':
    main()
