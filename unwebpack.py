import os
import json
import random
import string
import requests
import argparse
from bs4 import BeautifulSoup


requests.packages.urllib3.disable_warnings()
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"}

class Unwebpack(object):
    def __init__(self, args):
        self.url = args.url.strip('/') if args.url else None
        self.file = args.file if args.file else None
        self.js_list = []
        self.mapsource = {}
        if self.url:
            self.outpath = self.url.replace('http://', '').replace('https://', '') + '-' + ''.join(random.sample(string.ascii_letters, 5)).lower()
        elif self.file:
            self.outpath = self.file + '-' + ''.join(random.sample(string.ascii_letters, 5)).lower()
    
    def attack(self):
        if self.url:
            self.get_js_list()
            self.get_js_mapsource()
        elif self.file:
            with open(self.file, 'r') as f:
                self.mapsource[self.file] = json.loads(f.read())
        os.mkdir(self.outpath)
        os.chdir(self.outpath)
        print(f'[+] results write in {self.outpath}')
        self.parse_mapsource()

    def get_js_list(self):
        resp = requests.get(self.url, headers=headers, verify=False, allow_redirects=False)
        assert resp.status_code == 200
        soup = BeautifulSoup(resp.text, "html.parser")
        self.js_list = [i.get('src') for i in soup.find_all('script') if i.get('src')]

    def get_js_mapsource(self):
        for js_path in self.js_list:
            try:
                tmpname = js_path + '.map'
                resp = requests.get(self.url + '/' + tmpname, headers=headers, verify=False, allow_redirects=False)
                if resp and resp.status_code == 200 and '"sources"' in resp.text and '"sourcesContent"' in resp.text:
                    self.mapsource[tmpname] = resp.json()
            except:
                print(f"[-] {self.url + '/' + tmpname} not exist!")

    def parse_mapsource(self):
        for value in self.mapsource.values():
            self.parse(value['sources'], value['sourcesContent'])

    def parse(self, sources, sourcesContent):
        for source, sourceContent in zip(sources, sourcesContent):
            path, f_name = os.path.split(source.replace('webpack:///', ''))
            f_name = f_name.replace('?', '')
            if not path.startswith('./'):
                path = './' + path
            if not os.path.exists(path):
                os.makedirs(path)
            with open(path + '/' + f_name, 'a') as f:
                f.write(sourceContent)
            print(f"[+] {path + '/' + f_name} write success!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url", type=str, help="Target URL. e.g: -u http://192.168.1.1")
    parser.add_argument("-f", "--file", type=str, help="Target FILE. e.g: -f app.83edd403.js.map")
    args = parser.parse_args()
    unwebpack = Unwebpack(args)
    unwebpack.attack()
