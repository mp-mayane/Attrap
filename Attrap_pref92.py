import datetime
import re

from bs4 import BeautifulSoup
from urllib.parse import unquote

from Attrap import Attrap


class Attrap_pref92(Attrap):

    # Config
    hostname = 'https://www.hauts-de-seine.gouv.fr'
    raa_page = f'{hostname}/Publications/Annonces-avis/Le-Recueil-des-actes-administratifs'
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/115.0'
    full_name = 'Préfecture des Hauts-de-Seine'
    short_code = 'pref92'
    timezone = 'Europe/Paris'

    def __init__(self, data_dir):
        super().__init__(data_dir, self.user_agent)
        self.set_sleep_time(5)

    def get_raa(self, keywords):
        # On récupère les pages d'années
        year_pages = []
        page_content = self.get_page(self.raa_page, 'get').content
        for card in self.get_sub_pages(
            page_content,
            'div.fr-card__body div.fr-card__content h2.fr-card__title a',
            self.hostname,
            False
        ):
            if Attrap.guess_date(card['name'], '.* ([0-9]{4})').year >= self.not_before.year:
                year_pages.append(card['url'])

        # On récupère tous les RAA en suivant la navigation
        elements = self.get_raa_with_pager(
            year_pages,
            'a.fr-pagination__link.fr-pagination__link--next',
            self.hostname
        )

        self.parse_raa(elements, keywords)

    def get_raa_elements(self, page_content):
        elements = []
        # On charge le parser
        soup = BeautifulSoup(page_content, 'html.parser')

        # Pour chaque balise a, on regarde si c'est un PDF, et si oui on le parse
        for a in soup.select('.fr-card__title a.fr-card__link.menu-item-link'):
            if a.get('href') and a['href'].endswith('.pdf'):
                if a['href'].startswith('/'):
                    url = f"{self.hostname}{a['href']}"
                else:
                    url = a['href']

                url = unquote(url)
                name = re.sub(r'([0-9]{4}-[0-9]{2}-[0-9]{2}) ', ' ', a.get_text()).strip()
                date = datetime.datetime.strptime(a['title'].split(' - ')[-1].strip(), '%d/%m/%Y')

                raa = Attrap.RAA(url, date, name, timezone=self.timezone)
                elements.append(raa)
        return elements
