from flask import Flask, render_template
from api import get_news, scrape_news, get_LLM
import openai
import json
from newsapi import NewsApiClient
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/')
def index():
    urls = get_news()
    figure = scrape_news(urls[0], urls[1])
    json_obj = get_LLM(figure[0], figure[1], figure[2])
    return render_template('index.html', data=json_obj)
    #return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port = 8080)
