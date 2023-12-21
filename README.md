## GoogleNews Python Wrapper
This Python package provides a simple wrapper for accessing news articles from Google News. It utilizes the feedparser, BeautifulSoup, urllib, dateparser, requests, pandas, time, cloudscraper, and math libraries to facilitate the extraction of news articles based on user-defined queries, date ranges, and other parameters.

## Installation
To use this package, you need to install the required dependencies. You can do this by running:

```bash
pip install feedparser
pip install beautifulsoup4
pip install urllib3
pip install python-dateutil
pip install requests
pip install pandas
pip install cloudscraper
```
## Usage
```Python
from your_module import GoogleNews

# Create an instance of GoogleNews
gn = GoogleNews()

# Perform a search for news articles
result = gn.search(query='your_search_query', when='your_time_range', from_='start_date', to_='end_date', proxies=None, scraping_bee=None)

# Access the results
entries = result['entries']

# Print the titles of the articles
for entry in entries:
    print(entry['title'])

# Append articles to a CSV file
gn.append_csv(query='your_search_query', years_back=5, days_back=0)
```
### Class: GoogleNews
#### Methods
__init__(self, lang='en', country='US')
* Initializes the GoogleNews object with language and country parameters.

search(self, query, helper=True, when=None, from_=None, to_=None, proxies=None, scraping_bee=None)
* Searches for news articles based on the provided parameters.
* Returns a dictionary containing feed information and entries.

search_past(self, query, now, back=5)
* Searches for news articles from the past based on the specified query and time range.
* Returns lists of titles, dates, and content for the found articles.
  
append_csv(self, query, years_back, days_back=0)
* Appends news articles to a CSV file for a specified query and time range.

### Example
```Python
gn = GoogleNews()

now = datetime.today().date()
date_str = '2023-09-12'
date = datetime.strptime(date_str, '%Y-%m-%d').date()
back = 0
back = int((datetime.today().date() - date).days)

r = gn.append_csv('PYPL', years_back=5, days_back=back)
```
