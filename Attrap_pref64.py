import os
import datetime

from bs4 import BeautifulSoup
from urllib.parse import unquote

from Attrap import Attrap


class Attrap_pref64(Attrap):

    # Config
    hostname = 'https://www.pyrenees-atlantiques.gouv.fr'
    raa_page = f'{hostname}/Publications/Recueil-des-actes-administratifs'
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/115.0'
    full_name = 'Préfecture des Pyrénées-Atlantiques'
    short_code = 'pref64'
    timezone = 'Europe/Paris'

    def __init__(self, data_dir):
        super().__init__(data_dir, self.user_agent)
        self.set_sleep_time(30)

    def get_raa(self, keywords):
        # On récupère les pages d'années
        year_pages = []
        page_content = self.get_page(self.raa_page, 'get').content
        for year_page in self.get_sub_pages(
            page_content,
            'div.fr-card__body div.fr-card__content h2.fr-card__title a',
            self.hostname,
            False
        ):
            year = Attrap.guess_date(year_page['name'], '.* ([0-9]{4})').year
            if year < 9999 and year >= self.not_before.year:
                year_pages.append(year_page['url'])

        # Pour chaque page d'année, on récupère les pages de mois
        month_pages = []
        for year_page in year_pages:
            page_content = self.get_page(year_page, 'get').content
            for month_page in self.get_sub_pages(
                page_content,
                'div.fr-card__body div.fr-card__content h2.fr-card__title a',
                self.hostname,
                False
            ):
                if Attrap.guess_date(month_page['name'], '(.*)').replace(day=1) >= self.not_before.replace(day=1):
                    month_pages.append(month_page['url'])

        # On récupère les RAA en suivant la navigation de chaque page de mois
        elements = self.get_raa_with_pager(
            month_pages[::-1],
            'a.fr-pagination__link--next.fr-pagination__link--lg-label',
            self.hostname
        )[::-1]

        self.parse_raa(elements, keywords)

    def get_raa_elements(self, page_content):
        elements = []
        # On charge le parser
        soup = BeautifulSoup(page_content, 'html.parser')

        # On récupère chaque balise a
        for a in soup.select('div.fr-card__body div.fr-card__content h2.fr-card__title a.fr-card__link.menu-item-link'):
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
