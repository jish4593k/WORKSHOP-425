import requests
from bs4 import BeautifulSoup
import csv
import re
import torch
import torch.nn as nn
import seaborn as sns
import matplotlib.pyplot as plt

class AmazonScraper:
    def __init__(self, search_query, base_url='https://www.amazon.com/):
        self.search_query = search_query
        self.base_url = base_url
        self.page_links = 1

    def get_page_links(self, soup):
        for page in soup.find_all('span', class_='pagnLink'):
            self.page_links += 1

    def scrape_page(self, link, csv_writer):
        source = requests.get(link).text
        soup = BeautifulSoup(source, 'lxml')

        if self.page_links == 1:
            csv_writer.writerow(['Title', 'Price', 'Description'])

        for group in soup.find_all('a', class_='s-access-detail-page'):
            title = group.find('h2', class_='a-size-medium')
            if title and self.search_query.lower() in title.text.lower():
                det_link = group['href']
                self.scrape_details(det_link, csv_writer)

    def scrape_details(self, det_link, csv_writer):
        next_source = requests.get(det_link).text
        soup = BeautifulSoup(next_source, 'lxml')
        total_price = self.extract_price(soup)
        description = self.extract_description(soup)

        try:
            csv_writer.writerow([title.text, total_price, description])
        except UnicodeEncodeError:
            print(title.text, total_price, description)

    def extract_price(self, soup):
        for spans in soup.find_all('table', id='price'):
            new_price = spans.find('div', id='newPrice')
            used_price = spans.find('div', id='usedPrice')

            if new_price and new_price.text != '':
                return self.clean_price(new_price.text)
            elif used_price and used_price.text != '':
                return self.clean_price(used_price.text)

        return ''

    def clean_price(self, price):
        return price.replace('\n', '.').replace('/t', '').replace('$', '').replace('...', '')

    def extract_description(self, soup):
        description = []
        data = soup.find('div', id='feature-bullets')

        if data:
            for list_item in data.find_all('span', class_='a-list-item'):
                des = list_item.text[9:].replace('\n', '').replace('\t', '')
                description.append(des)

        return description

    def run(self):
        csv_file = open('amazon.csv', 'w', newline='', encoding='utf-8')
        csv_writer = csv.writer(csv_file)
        current_page = 1

        while current_page <= self.page_links:
            link = f'{self.base_url}?fst=as%3Aoff&page={current_page}&keywords={self.search_query.replace(" ", "+")}&ie=UTF8'
            self.scrape_page(link, csv_writer)
            current_page += 1

        csv_file.close()

def visualize_data(csv_path):
    data = torch.randn(100, 2)  # Replace with your actual data

    
    sns.scatterplot(x=data[:, 0].numpy(), y=data[:, 1].numpy())
    plt.title('Data Visualization')
    plt.xlabel('Feature 1')
    plt.ylabel('Feature 2')
    plt.show()

if __name__ == '__main__':
    scraper = AmazonScraper('Dragon Ball Fighter')
    scraper.run()

    
    visualize_data('amazon.csv')
