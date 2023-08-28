
import os
import re
import requests
from bs4 import BeautifulSoup
from feedgenerator import Rss201rev2Feed
from dateutil.parser import parse
from xml.dom.minidom import parseString
from datetime import datetime

# ファイル名
exportfile = "feed.xml"

def create_rss_feed():
    url = "https://newspicks.com/series/list/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
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

    # 最初の記事の情報を取得
    first_article_div = soup.find('div', class_="news-card vertical big clear")
    print(first_article_div)

    if first_article_div is None:
        print("first_article_div が None やで！クラス名やタグが正しいか確認してみてな！")
        # デバッグ情報として、対象のHTMLの一部を出力
        print(soup.prettify()[:500]) # 最初の500文字を出力
    else:
        a_tag = first_article_div.find('a', href=True)
        title_tag = first_article_div.find(class_="title _ellipsis")
        subtitle_tag = first_article_div.find('span', class_="publisher _ellipsis")
        time_tag = re.search(r'data-key="(\d{12,})', first_article_div['data-key']).group(1)
        
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

    # 2個目以降の記事の情報を取得してRSSフィードに追加
    for a_tag in soup.find_all('a', class_="css-dv7pnt", href=True):
        if a_tag is None:
            continue
        title_tag = a_tag.find(class_="typography css-1ta5siq")
        subtitle_tag = a_tag.find(class_="typography css-rvnxno")
        time_tag = a_tag.find('time', datetime=True)
        href = a_tag['href']

        if title_tag and subtitle_tag and time_tag:
            title = title_tag.text
            subtitle = subtitle_tag.text
            date = parse(time_tag['datetime'])

            full_title = title + " - " + subtitle

            feed.add_item(
                title=full_title,
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
