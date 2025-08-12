import os
import re
import datetime

from bs4 import BeautifulSoup
from urllib.parse import unquote

from Attrap import Attrap


class Attrap_pref93(Attrap):

    # Config
    hostname = 'https://www.seine-saint-denis.gouv.fr'
    raa_page = f'{hostname}/Publications/Bulletin-d-informations-administratives-Recueil-des-actes-administratifs/'
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/115.0'
    full_name = 'Préfecture de Seine-Saint-Denis'
    short_code = 'pref93'
    timezone = 'Europe/Paris'

    def __init__(self, data_dir):
        super().__init__(data_dir, self.user_agent)
        self.set_sleep_time(30)

    def get_raa(self, keywords):
        pages_to_parse = []

        # On récupère les pages d'années
        page_content = self.get_page(self.raa_page, 'get').content
        year_pages = self.get_sub_pages(
            page_content,
            'div.fr-card__body div.fr-card__content h2.fr-card__title a',
            self.hostname,
            False,
        )[::-1]

        # On filtre par date pour limiter les requêtes
        year_pages_to_parse = []
        for year_page in year_pages:
            year = 9999
            try:
                year = int(re.search('.*([0-9]{4})', year_page['name'].strip(), re.IGNORECASE).group(1))
                if year is None:
                    year = 9999
            except Exception as exc:
                logger.warning(f"Impossible de deviner l\'année de la page {year_page['name']}")
                year = 9999
            if year >= self.not_before.year:
                year_pages_to_parse.append(year_page['url'])

        # Pour chaque année, on cherche les sous-pages de mois
        for year_page in year_pages_to_parse:
            page_content = self.get_page(year_page, 'get').content
            month_pages = self.get_sub_pages(
                page_content,
                '.fr-card.fr-card--sm.fr-card--grey.fr-enlarge-link div.fr-card__body div.fr-card__content h2.fr-card__title a',
                self.hostname,
                False
            )[::-1]

            # On filtre en fonction de la date demandée
            for month_page in month_pages:
                guessed_date = Attrap.guess_date(month_page['name'].strip(), '([a-zéû]*).*')
                if guessed_date >= self.not_before.replace(day=1):
                    pages_to_parse.append(month_page['url'])

        # On parse les pages contenant des RAA
        elements = []
        for page in pages_to_parse:
            page_content = self.get_page(page, 'get').content
            for element in self.get_raa_elements(page_content):
                elements.append(element)

        self.parse_raa(elements[::-1], keywords)

    def get_raa_elements(self, page_content):
        elements = []
        soup = BeautifulSoup(page_content, 'html.parser')

        for card in soup.select('div.fr-card__body div.fr-card__content'):
            a = card.select_one('h2.fr-card__title a.fr-card__link')
            if a.get('href') and a['href'].endswith('.pdf'):
                if a['href'].startswith('/'):
                    url = f"{self.hostname}{a['href']}"
                else:
                    url = a['href']

                url = unquote(url)
                name = a.text.strip()
                date = datetime.datetime.strptime(card.select_one('div.fr-card__end p.fr-card__detail').get_text().removeprefix('Publié le ').strip(), '%d/%m/%Y')

                raa = Attrap.RAA(url, date, name, timezone=self.timezone)
                elements.append(raa)
        return elements
