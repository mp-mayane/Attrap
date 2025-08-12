import os
import datetime

from bs4 import BeautifulSoup
from urllib.parse import unquote

from Attrap import Attrap


class Attrap_pref69(Attrap):

    # Config
    hostname = 'https://www.rhone.gouv.fr'
    raa_page = f'{hostname}/Publications/Recueil-des-actes-administratifs-du-Rhone-RAA'
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/115.0'
    full_name = 'Préfecture du Rhône'
    short_code = 'pref69'
    timezone = 'Europe/Paris'

    def __init__(self, data_dir):
        super().__init__(data_dir, self.user_agent)
        self.set_sleep_time(30)

    def get_raa(self, keywords):
        # On détermine quelles pages d'année parser
        year_pages = []
        page_content = self.get_page(self.raa_page, 'get').content
        for year_page in self.get_sub_pages(
            page_content,
            'div.fr-card__body div.fr-card__content h2.fr-card__title a',
            self.hostname,
            False
        ):
            year = Attrap.guess_date(year_page['name'].strip(), '.* ([0-9]{4})').year
            if year < 9999 and year >= self.not_before.year:
                year_pages.append(year_page['url'])

        sub_pages_to_parse = []
        for raa_page in year_pages:
            sub_pages = self.get_sub_pages_with_pager(
                raa_page,
                'div.fr-card__body div.fr-card__content h2.fr-card__title a.fr-card__link',
                'ul.fr-pagination__list li a.fr-pagination__link--next',
                None,
                self.hostname)[::-1]
            for sub_page in sub_pages:
                sub_pages_to_parse.append(sub_page['url'])

        elements = []
        for sub_page_to_parse in sub_pages_to_parse:
            page_content = self.get_page(sub_page_to_parse, 'get').content
            for element in self.get_raa_elements(page_content)[::-1]:
                elements.append(element)

        self.parse_raa(elements, keywords)

    def get_raa_elements(self, page_content):
        elements = []
        # On charge le parser
        soup = BeautifulSoup(page_content, 'html.parser')

        # On récupère chaque balise a
        for a in soup.select('a.fr-link.fr-link--download'):
            if a.get('href') and a['href'].endswith('.pdf'):
                if a['href'].startswith('/'):
                    url = f"{self.hostname}{a['href']}"
                else:
                    url = a['href']

                url = unquote(url)
                name = a.find('span').previous_sibling.replace('Télécharger ', '').strip()
                date = datetime.datetime.strptime(a.find('span').get_text().split(' - ')[-1].strip(), '%d/%m/%Y')

                raa = Attrap.RAA(url, date, name, timezone=self.timezone)
                elements.append(raa)
        return elements
