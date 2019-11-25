import argparse
import os
import requests
import json

from urllib import parse
from bs4 import BeautifulSoup

# 参考: https://qiita.com/yottyann1221/items/a08300b572206075ee9f


class ImageCollector:

    def __init__(self, save_dir=None):
        self.GOOGLE_SEARCH_URL = 'https://www.google.co.jp/search'
        self.session = requests.session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0'})
        self.save_dir = os.path.join(os.path.join(os.getcwd(), 'images'), 'original')
        if save_dir is not None:
            self.save_dir = save_dir

    def collect_images(self, keywords):
        for keyword in keywords:
            image_urls = self._search(keyword=keyword, type='image')
            os.makedirs(self.save_dir, exist_ok=True)

            self._save_image(image_urls, keyword)

    def _search(self, keyword, type='text', maximum=1000):
        '''Google検索'''
        print('Google', type.capitalize(), 'Search :', keyword)
        result, total = [], 0
        query = self._generate_query(keyword, type)
        while True:
            # 検索
            html = self.session.get(next(query)).text
            links = self._get_links(html, type)

            # 検索結果の追加
            if not len(links):
                print('-> No more links')
                break
            elif len(links) > maximum - total:
                result += links[:maximum - total]
                break
            else:
                result += links
                total += len(links)

        print('-> 結果', str(len(result)), 'のlinksを取得しました')
        return result

    def _generate_query(self, keyword, type):
        '''検索クエリジェネレータ'''
        page = 0
        while True:
            if type == 'text':
                params = parse.urlencode({
                    'q': keyword,
                    'num': '100',
                    'filter': '0',
                    'start': str(page * 100)})
            elif type == 'image':
                params = parse.urlencode({
                    'q': keyword,
                    'tbm': 'isch',
                    'filter': '0',
                    'ijn': str(page)})

            yield self.GOOGLE_SEARCH_URL + '?' + params
            page += 1

    def _get_links(self, html, type):
        '''リンク取得'''
        soup = BeautifulSoup(html, 'lxml')
        if type == 'text':
            elements = soup.select('.rc > .r > a')
            links = [e['href'] for e in elements]
        elif type == 'image':
            elements = soup.select('.rg_meta.notranslate')
            jsons = [json.loads(e.get_text()) for e in elements]
            links = [js['ou'] for js in jsons]
        return links

    def _save_image(self, image_urls, keyword):
        print('-> 保存中')
        os.makedirs(os.path.join(self.save_dir, keyword), exist_ok=True)

        for i, target in enumerate(image_urls):
            try:
                re = requests.get(target, allow_redirects=False)
                with open(os.path.join(os.path.join(self.save_dir, keyword), str(i) + '.jpg'),
                          'wb') as f:
                    f.write(re.content)
            except requests.exceptions.ConnectionError:
                continue
            except UnicodeEncodeError:
                continue
            except UnicodeError:
                continue
            except IsADirectoryError:
                continue


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--keywords', nargs='*', help='search keywords', required=True)
    parser.add_argument('--savedir', help='image save directory')
    args = parser.parse_args()

    ic = ImageCollector(save_dir=args.savedir)
    ic.collect_images(keywords=args.keywords)

