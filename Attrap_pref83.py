import os
import datetime

from bs4 import BeautifulSoup
from urllib.parse import unquote

from Attrap import Attrap


class Attrap_pref83(Attrap):

    # Config
    hostname = 'https://www.var.gouv.fr'
    raa_page = f'{hostname}/Publications/Recueil-des-actes-administratifs'
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/115.0'
    full_name = 'Préfecture du Var'
    short_code = 'pref83'
    timezone = 'Europe/Paris'

    def __init__(self, data_dir):
        super().__init__(data_dir, self.user_agent)
        self.set_sleep_time(30)

    def get_raa(self, keywords):
        year_pages_to_parse = []

        # On détermine quelles pages d'année parser
        page_content = self.get_page(self.raa_page, 'get').content
        for year_page in self.get_sub_pages(
            page_content,
            'div.fr-card__body div.fr-card__content h2.fr-card__title a',
            self.hostname,
            False
        ):
            year = Attrap.guess_date(year_page['name'].strip(), 'Recueil des actes administratifs ([0-9]{4})').year
            if year < 9999 and year >= self.not_before.year:
                year_pages_to_parse.append(year_page['url'])

        pages_to_parse = []

        # Pour chaque année, on cherche les sous-pages de mois
        for raa_page in year_pages_to_parse:
            pages_to_parse.append(raa_page)
            page_content = self.get_page(raa_page, 'get').content
            for month_page in self.get_sub_pages(
                page_content,
                '.fr-card.fr-card--sm.fr-card--grey.fr-enlarge-link div.fr-card__body div.fr-card__content h2.fr-card__title a',
                self.hostname,
                False
            )[::-1]:
                card_date = Attrap.guess_date(month_page['name'].strip(), '(.*)').replace(day=1)
                if card_date >= self.not_before.replace(day=1):
                    pages_to_parse.append(month_page['url'])

        # On parse les pages contenant des RAA
        elements = self.get_raa_with_pager(
            pages_to_parse[::-1],
            '.fr-pagination__link.fr-pagination__link--next',
            self.hostname
        )
        self.parse_raa(elements, keywords)

    def get_raa_elements(self, page_content):
        elements = []
        # On charge le parser
        soup = BeautifulSoup(page_content, 'html.parser')

        # On récupère chaque section contenant un RAA
        cards = soup.select('div.fr-card__body div.fr-card__content h2.fr-card__title a.fr-card__link.menu-item-link')
        for a in cards:
            if a.get('href') and a['href'].endswith('.pdf'):
                if a['href'].startswith('/'):
                    url = f"{self.hostname}{a['href']}"
                else:
                    url = a['href']

                url = unquote(url)
                name = a.get_text().strip()
                date = datetime.datetime.strptime(a['title'].split(' - ')[-1].strip(), '%d/%m/%Y')

                raa = Attrap.RAA(url, date, name, timezone=self.timezone)
                elements.append(raa)
        return elements
