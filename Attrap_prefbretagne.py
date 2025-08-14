import datetime
import time

from bs4 import BeautifulSoup
from urllib.parse import unquote

from Attrap import Attrap


class Attrap_prefbretagne(Attrap):

    # Config
    hostname = 'https://www.prefectures-regions.gouv.fr'
    raa_page = f'{hostname}/bretagne/Documents-publications/Recueils-des-actes-administratifs/Recueil-des-actes-administratifs'
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0'
    full_name = 'Préfecture de la région Bretagne'
    short_code = 'prefbretagne'
    timezone = 'Europe/Paris'

    def __init__(self, data_dir):
        super().__init__(data_dir, self.user_agent)
        self.enable_tor(10)
        self.set_sleep_time(10)

    def get_raa(self, keywords):
        # page_content = self.get_page(self.raa_page, 'get').content
        page_content = self.get_session(self.raa_page, 'main', 6)
        elements = self.get_raa_elements(page_content)

        time.sleep(10)

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
