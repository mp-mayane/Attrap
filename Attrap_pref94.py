import os
import datetime

from bs4 import BeautifulSoup
from urllib.parse import unquote

import logging
from Attrap import Attrap


class Attrap_pref94(Attrap):

    # Config
    hostname = 'https://www.val-de-marne.gouv.fr'
    raa_page = f'{hostname}/Publications/Publications-legales/RAA-Recueil-des-actes-administratifs'
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/115.0'
    full_name = 'Préfecture du Val-de-Marne'
    short_code = 'pref94'
    timezone = 'Europe/Paris'

    def __init__(self, data_dir):
        super().__init__(data_dir, self.user_agent)
        self.set_sleep_time(30)

    def get_raa(self, keywords):
        elements = []
        page_content = self.get_page(self.raa_page, 'get').content
        for sub_page in self.get_sub_pages(
            page_content,
            'div.fr-card__body div.fr-card__content h2.fr-card__title a',
            self.hostname,
            False
        ):
            if Attrap.guess_date(sub_page['name'], '([0-9]{4})$').year >= self.not_before.year:
                sub_page_content = self.get_page(sub_page['url'], 'get').content
                for element in self.get_raa_elements(sub_page_content):
                    elements.append(element)

        self.parse_raa(elements, keywords)

    def get_raa_elements(self, page_content):
        elements = []
        # On charge le parser
        soup = BeautifulSoup(page_content, 'html.parser')

        # Pour chaque balise a, on regarde si c'est un PDF, et si oui on le
        # parse
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
