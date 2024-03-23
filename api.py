import openai
import json
from newsapi import NewsApiClient
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

openai.api_key = "MY_OPEN_AI"
def get_news():
    api = NewsApiClient(api_key='MY_NEWS_API')
    today_date = datetime.now()
    today_date = today_date - timedelta(days=1)
    today_date = today_date.strftime('%Y-%m-%d')
    nn = api.get_everything(from_param= today_date, to=today_date, sources='cnn', sort_by='popularity',
                            language='en')
    art = nn['articles']
    art = art[:10]
    urls = []
    img = []
    for i in art:
        urls.append(i['url'])
        img.append(i['urlToImage'])
    return urls, img

def scrape_news(urls, img):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9,ta;q=0.8,id;q=0.7",
        "Accept-Charset": "utf-8, iso-8859-1;q=0.7, *;q=0.7",
        "DNT": "1",
        "Connection": "close",
        "Upgrade-Insecure-Requests": "1",
        "X-Amzn-Trace-Id": "Root=1-65541dca-227e84c03c67107e5e788781"
    }
    img_new = []
    urls_new = []
    content = []
    for i in urls:
        try:
            response = requests.get(i)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                article_content = soup.find_all("div", class_='article__content')

                if (len(article_content) == 0):
                    continue

                article_content[0].find_all('p')
                news = ""
                for j in article_content:
                    news += j.text.strip()

                urls_new.append(i)
                content.append(news)
                img_new.append(img[urls.index(i)])

            else:
                print(f"Failed to fetch data. Status code: {response.status_code}, URL: {url}")

        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
    return [urls_new, content, img_new]

def get_completion(messages, model="gpt-3.5-turbo"):
    response = openai.chat.completions.create(
    model="gpt-3.5-turbo",
    response_format={ "type": "json_object" },
    messages = messages,
    temperature=0
  )
    return response.choices[0].message.content

def get_LLM(urls_new,content,img_new):
    final_news = []

    text = f"""
    You are a professional news reporter bot. You will be given array of news url and its content
    Your task is to generate a short summary of 150 words of the given news article from CNN website.

    For each news summarize it and also provide suitable heading.. Consider only the news content.
    If it has any advertisement any other irrelevant info please disregard it.

    Return result in only as json object with headline, summary and url, not as a string with json inside of it.

    """

    for i in range(len(content)):
        prompt = f"""

          url= ```{urls_new[i]}```
          news= ```{content[i]}```
    
          """

        messages = [
            {"role": "system", "content": text},
            {"role": "user", "content": prompt}
        ]
        response = get_completion(messages)
        json_object = json.loads(response)
        json_object['img'] = img_new[i]
        final_news.append(json_object)

    return final_news
