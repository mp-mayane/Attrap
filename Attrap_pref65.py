import os
import datetime

from bs4 import BeautifulSoup
from urllib.parse import unquote

from Attrap import Attrap


class Attrap_pref65(Attrap):

    # Config
    hostname = 'https://www.hautes-pyrenees.gouv.fr'
    raa_page = f'{hostname}/Publications/Recueil-d-actes-administratifs'
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/115.0'
    full_name = 'Préfecture des Hautes-Pyrénées'
    short_code = 'pref65'
    timezone = 'Europe/Paris'

    def __init__(self, data_dir):
        super().__init__(data_dir, self.user_agent)
        self.set_sleep_time(30)

    def get_raa(self, keywords):
        # On détermine quelles pages d'année parser
        pages_to_parse = []
        year_pages = self.get_sub_pages_with_pager(
            self.raa_page,
            'div.fr-card.fr-card--horizontal.fr-card--sm.fr-enlarge-link.fr-mb-3w div.fr-card__body div.fr-card__content h2.fr-card__title a.fr-card__link',
            'ul.fr-pagination__list li a.fr-pagination__link.fr-pagination__link--next.fr-pagination__link--lg-label',
            'div.fr-card.fr-card--horizontal.fr-card--sm.fr-enlarge-link.fr-mb-3w div.fr-card__body div.fr-card__content div.fr-card__end p.fr-card__detail',
            self.hostname
        )
        for year_page in year_pages:
            if Attrap.guess_date(year_page['name'].strip(), '.*([0-9]{4})').year >= self.not_before.year:
                pages_to_parse.append(year_page['url'])

        elements = []
        for raa_page in pages_to_parse:
            page_content = self.get_page(raa_page, 'get').content
            for element in self.get_raa_elements(page_content):
                elements.append(element)

        self.parse_raa(elements, keywords)

    def get_raa_elements(self, page_content):
        elements = []
        # On charge le parser
        soup = BeautifulSoup(page_content, 'html.parser')

        # Pour chaque balise a, on regarde si c'est un PDF, et si oui on le parse
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
