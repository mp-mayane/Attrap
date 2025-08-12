import os
import datetime

from bs4 import BeautifulSoup
from urllib.parse import unquote

from Attrap import Attrap


class Attrap_pref91(Attrap):

    # Config
    hostname = 'https://www.essonne.gouv.fr'
    raa_page = f'{hostname}/Publications/Recueils-des-actes-administratifs-RAA'
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/115.0'
    full_name = 'Préfecture de l\'Essonne'
    short_code = 'pref91'
    timezone = 'Europe/Paris'

    def __init__(self, data_dir):
        super().__init__(data_dir, self.user_agent)
        self.set_sleep_time(30)

    def get_raa(self, keywords):
        pages_to_parse = []

        # On détermine quelles pages d'année parser
        year_pages_to_parse = []
        page_content = self.get_page(self.raa_page, 'get').content
        year_pages = self.get_sub_pages(
            page_content,
            '.fr-card.fr-card--sm.fr-card--grey.fr-enlarge-link div.fr-card__body div.fr-card__content h2.fr-card__title a',
            self.hostname,
            False
        )
        for year_page in year_pages:
            year = int(year_page['name'].strip())
            if year >= self.not_before.year:
                year_pages_to_parse.append(year_page)

        # Pour chaque année, on cherche les sous-pages de mois
        month_pages_to_parse = []
        for year_page in year_pages_to_parse:
            year = year_page['name'].strip()
            page_content = self.get_page(year_page['url'], 'get').content
            month_pages = self.get_sub_pages(
                page_content,
                '.fr-card.fr-card--sm.fr-card--grey.fr-enlarge-link div.fr-card__body div.fr-card__content h2.fr-card__title a',
                self.hostname,
                False
            )[::-1]

            for month_page in month_pages[::-1]:
                month = month_page['name'].strip()
                guessed_date = Attrap.guess_date(f'{month} {year}', '(.*)')
                if guessed_date >= self.not_before.replace(day=1):
                    pages_to_parse.append(month_page['url'])

        # On parse les pages sélectionnées
        elements = []
        for page_to_parse in pages_to_parse:
            page_content = self.get_page(page_to_parse, 'get').content
            for element in self.get_raa_elements(page_content):
                elements.append(element)

        self.parse_raa(elements[::-1], keywords)

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
                if a.get('title'):
                    name = a.get_text().strip()
                    date = datetime.datetime.strptime(a['title'].split(' - ')[-1].strip(), '%d/%m/%Y')
                else:
                    name = a.find('span').previous_sibling.replace('Télécharger ', '').strip()
                    date = datetime.datetime.strptime(a.find('span').get_text().split(' - ')[-1].strip(), '%d/%m/%Y')

                raa = Attrap.RAA(url, date, name, timezone=self.timezone)
                elements.append(raa)
        return elements
