import feedparser
from bs4 import BeautifulSoup
import urllib
from dateparser import parse as parse_date
from datetime import datetime, timedelta
import requests
import pandas as pd
import time
import cloudscraper
import math


class GoogleNews:
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}
    def __init__(self, lang = 'en', country = 'US'):
        self.lang = lang.lower()
        self.country = country.upper()
        self.BASE_URL = 'https://news.google.com/rss'

    def __top_news_parser(self, text):
        """Return subarticles from the main and topic feeds"""
        try:
            bs4_html = BeautifulSoup(text, "html.parser")
            # find all li tags
            lis = bs4_html.find_all('li')
            sub_articles = []
            for li in lis:
                try:
                    sub_articles.append({"url": li.a['href'],
                                         "title": li.a.text,
                                         "publisher": li.font.text})
                except:
                    pass
            return sub_articles
        except:
            return text

    def __ceid(self):
        """Compile correct country-lang parameters for Google News RSS URL"""
        return '?ceid={}:{}&hl={}&gl={}'.format(self.country,self.lang,self.lang,self.country)

    def __add_sub_articles(self, entries):
        for i, val in enumerate(entries):
            if 'summary' in entries[i].keys():
                entries[i]['sub_articles'] = self.__top_news_parser(entries[i]['summary'])
            else:
                entries[i]['sub_articles'] = None
        return entries

    def __scaping_bee_request(self, api_key, url):
        response = requests.get(
            url="https://app.scrapingbee.com/api/v1/",
            params={
                "api_key": api_key,
                "url": url,
                "render_js": "false"
            }
        )
        if response.status_code == 200:
            return response
        if response.status_code != 200:
            raise Exception("ScrapingBee status_code: "  + str(response.status_code) + " " + response.text)

    def __parse_feed(self, feed_url, proxies=None, scraping_bee = None):

        if scraping_bee and proxies:
            raise Exception("Pick either ScrapingBee or proxies. Not both!")

        if proxies:
            r = requests.get(feed_url, proxies = proxies)
        else:
            r = requests.get(feed_url)

        if scraping_bee:
            r = self.__scaping_bee_request(url = feed_url, api_key = scraping_bee)
        else:
            r = requests.get(feed_url)


        if 'https://news.google.com/rss/unsupported' in r.url:
            raise Exception('This feed is not available')

        d = feedparser.parse(r.text)

        if not scraping_bee and not proxies and len(d['entries']) == 0:
            d = feedparser.parse(feed_url)

        return dict((k, d[k]) for k in ('feed', 'entries'))

    def __search_helper(self, query):
        return urllib.parse.quote_plus(query)

    def __from_to_helper(self, validate=None):
        try:
            validate = parse_date(validate).strftime('%Y-%m-%d')
            return str(validate)
        except:
            raise Exception('Could not parse your date')

    def search(self, query: str, helper = True, when = None, from_ = None, to_ = None, proxies=None, scraping_bee=None):
        """
        Return a list of all articles given a full-text search parameter,
        a country and a language

        :param bool helper: When True helps with URL quoting
        :param str when: Sets a time range for the artiles that can be found
        """

        if when:
            query += ' when:' + when

        if from_ and not when:
            from_ = self.__from_to_helper(validate=from_)
            query += ' after:' + from_

        if to_ and not when:
            to_ = self.__from_to_helper(validate=to_)
            query += ' before:' + to_

        if helper == True:
            query = self.__search_helper(query)

        search_ceid = self.__ceid()
        search_ceid = search_ceid.replace('?', '&')

        d = self.__parse_feed(self.BASE_URL + '/search?q={}'.format(query) + search_ceid, proxies = proxies, scraping_bee=scraping_bee)

        d['entries'] = self.__add_sub_articles(d['entries'])
        return d
    def search_past(self, query: str, now, back = 5):
        title = []
        dates = []
        content = []
        for d in range(back):
            j = 0
            search = gn.search(query, from_ = str((now - timedelta(days=d)).date()), to_ = str((now - timedelta(days=d-3)).date()))
            curr_date = str((now - timedelta(days=d)).date())
            print(curr_date)
            scraper = cloudscraper.create_scraper()
            csv = query + "_news.csv"
            df = pd.read_csv(csv)
            matrix = df[df.columns[1]]
            list2 = matrix.tolist()
            for i in range(len(search['entries'])):
                if (not(search['entries'][i]['source']['title'] == 'Yahoo Finance')): #change to be what website we get, check if valid site
                    continue
                # if (not((" " + curr_date[len(curr_date)-2: len(curr_date)]) in search['entries'][i]['published'])):
                #     continue
                #getting any dates that might have been missed without getting doubles
                print(search['entries'][i]['published'])
                st = search['entries'][i]['summary']
                webUrl = st[st.find("\"")+1:st.find("\"",st.find("\"")+1)]
                r =  scraper.get(webUrl).text #this will give us the rss
                idx = r.index("data-n-au=")
                actual_link = r[idx:r.index("\"", idx+20)+1]
                actual_link = actual_link[actual_link.find("\"")+1:actual_link.find("\"",actual_link.find("\"")+1)] #redirected link
                soup = BeautifulSoup(scraper.get(actual_link, headers=self.headers).text, "html.parser")
                if (search['entries'][i]['title'] in title or search['entries'][i]['title'] in list2):
                    continue
                title.append(search['entries'][i]['title']) #title of article
                complete = ""
                complete = " ".join([t.get_text() for t in soup.findAll('p')]) #getting the content of the page
                dates.append(search['entries'][i]['published']) #date published
                content.append(complete)
        return title, dates, content

    def append_csv(self, query, years_back, days_back = 0):
        ###########################################
        # Query: str what you are searching
        # years_back: int how many years back of news you want to search
        # day_back: int in case search fails, we can go back how many days and continue from there
        ##########################################
        now = datetime.utcnow() - timedelta(days=days_back)
        idx = math.floor((365*years_back-days_back)/5)
        csv = query + "_news.csv"
        for i in range(idx):
            title = []
            dates = []
            content = []
            t, d, c = self.search_past(query, now)
            title +=  t
            dates += d
            content += c
            now = now - timedelta(days=5)
            d = {'dates': dates, 'title': title, 'content' : content}
            df = pd.DataFrame(data=d)
            df.to_csv(csv, mode='a', index=False, header=False)
        print("done")

#2023-05-06
gn = GoogleNews()


now = datetime.today().date()
date_str = '2023-09-12'
date = datetime.strptime(date_str, '%Y-%m-%d').date()
back = 0
back = int((datetime.today().date()-date).days)
r = gn.append_csv('PYPL', years_back = 5, days_back = back)