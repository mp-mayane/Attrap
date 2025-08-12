import os
import datetime

from bs4 import BeautifulSoup
from urllib.parse import unquote

from Attrap import Attrap


class Attrap_prefpaca(Attrap):

    # Config
    hostname = 'https://www.prefectures-regions.gouv.fr'
    raa_page = f'{hostname}/provence-alpes-cote-dazur/Documents-publications'
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0'
    full_name = 'Préfecture de la région Provence-Alpes-Côte-d\'Azur'
    short_code = 'prefpaca'
    timezone = 'Europe/Paris'

    def __init__(self, data_dir):
        super().__init__(data_dir, self.user_agent)
        self.enable_tor(10)
        self.set_sleep_time(10)

    def get_raa(self, keywords):
        # On récupère une session avec Selenium
        page_content = self.get_session(self.raa_page, 'main', 6)

        # On récupère les pages d'années
        year_pages = []
        for year_page in self.get_sub_pages_with_pager(
            page_content,
            'article.news-list-item header h2.news-list-title a',
            'article.article div.content-pagination ul.pagination li.next a',
            None,
            self.hostname,
            selenium=True
        ):
            year = Attrap.guess_date(year_page['name'].strip(), 'RAA ([0-9]{4})').year
            if year < 9999 and year >= self.not_before.year:
                year_pages.append(year_page['url'])

        elements = []
        for year_page in year_pages:
            page_content = self.get_session(year_page, 'main', 6)
            for element in self.get_raa_elements(page_content):
                elements.append(element)

        self.parse_raa(elements, keywords)

    def get_raa_elements(self, page_content):
        elements = []
        # On charge le parser
        soup = BeautifulSoup(page_content, 'html.parser')

        # Pour chaque balise a, on regarde si c'est un PDF, et si oui on le parse
        for a in soup.select('main div.container.main-container div.col-main article.article div.texte div a.link-download'):
            if a.get('href') and a['href'].endswith('.pdf'):
                if a['href'].startswith('/'):
                    url = f"{self.hostname}{a['href']}"
                else:
                    url = a['href']
                url = unquote(url)
                name = a.find('span').get_text().strip()
                # On devine la date du RAA à partir du nom de fichier
                guessed = Attrap.guess_date(name, '((?:[0-9]{2}|[0-9]{1})(?:er){0,1}[ _](?:[a-zéû]{3,9})[ _](?:[0-9]{4}|[0-9]{2}))')
                if (guessed == datetime.datetime(9999, 1, 1, 0, 0)):
                    date = None
                else:
                    date = guessed

                raa = Attrap.RAA(url, date, name, timezone=self.timezone)
                elements.append(raa)
        return elements
