
import os
import re
import requests
import random
from bs4 import BeautifulSoup
from feedgenerator import Rss201rev2Feed
from dateutil.parser import parse
from xml.dom.minidom import parseString
from datetime import datetime

# ファイル名
exportfile = "feed.xml"

def get_random_user_agent():
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.902.84 Safari/537.36 Edg/92.0.902.84'
    ]
    return random.choice(user_agents)
    
def create_rss_feed():
    url = "https://newspicks.com/series/list/"
    headers = {
        'User-Agent': get_random_user_agent(),
        'Accept-Language': 'ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br'
    }
        
    #response = requests.get(url)
    response = requests.get(url, headers=headers)
    content = response.text

    # ここでステータスコードを確認
    if response.status_code != 200:
        print(f"HTTP Status Code: {response.status_code}")
        return
        
    # HTMLの解析
    soup = BeautifulSoup(content, 'html.parser')
    #print('# HTMLの解析')
    #print(soup)

    # RSSフィードの生成
    feed = Rss201rev2Feed(
        title="NewsPicks_Original",
        link=url,
        description="最新のNewsPicksのオリジナル記事をお届けします",
    )

    # 複数の記事の情報を取得
    article_divs = soup.find_all('div', class_=re.compile("news-card vertical"))

    if not article_divs:
        print("記事が見つからんかったわ！クラス名やタグが正しいか確認してみてな！")
        return

    for article_div in article_divs:
        a_tag = article_div.find('a', href=True)
        title_tag = article_div.find(class_="title _ellipsis")
        subtitle_tag = article_div.find('span', class_="publisher _ellipsis")
        time_tag = article_div.get('data-key')

        if a_tag and title_tag and subtitle_tag and time_tag:
            title = title_tag.text
            subtitle = subtitle_tag.text
            href = a_tag['href']
            date_str = time_tag[:14]  # 最初の14文字だけ取る
            date = datetime.strptime(date_str, '%Y%m%d%H%M%S')

            feed.add_item(
                title=title + " - " + subtitle,
                link=href,
                pubdate=date,
                description="",
            )

    # RSSフィードのXMLを出力
    xml_str = feed.writeString('utf-8')
    dom = parseString(xml_str)
    pretty_xml_str = dom.toprettyxml(indent="    ", encoding='utf-8')

    with open(exportfile, 'wb') as f:
        f.write(pretty_xml_str)

create_rss_feed()
