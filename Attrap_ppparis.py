import datetime

from bs4 import BeautifulSoup
from urllib.parse import unquote

from Attrap import Attrap


class Attrap_ppparis(Attrap):

    # Config
    hostname = 'https://www.prefecturedepolice.interieur.gouv.fr'
    raa_page = f'{hostname}/actualites-et-presse/arretes/accueil-arretes'
    __WAIT_ELEMENT = 'block-decree-list-block'
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    full_name = 'Préfecture de police de Paris'
    short_code = 'ppparis'
    timezone = 'Europe/Paris'

    def __init__(self, data_dir):
        super().__init__(data_dir, self.user_agent)

    def get_raa(self, keywords):
        page_content = self.get_session(self.raa_page, self.__WAIT_ELEMENT, 6)
        raa_elements = self.get_raa_elements(page_content)
        self.parse_raa(raa_elements, keywords)

    def get_raa_elements(self, page_content):
        elements = []
        # On charge le parser
        soup = BeautifulSoup(page_content, 'html.parser')

        # Pour chaque balise a, on regarde si c'est un PDF, et si oui on le
        # parse
        for a in soup.find_all('a', href=True):
            if a['href'].endswith('.pdf'):
                if a['href'].startswith('/'):
                    url = 'https://www.prefecturedepolice.interieur.gouv.fr' + a['href']
                else:
                    url = a['href']

                url = unquote(url)
                name = a.find('span').get_text()
                date = datetime.datetime.strptime(a.find('div', class_="field--type-datetime").get_text().strip(), '%d/%m/%Y')

                raa = Attrap.RAA(url, date, name, timezone=self.timezone)
                elements.append(raa)
        return elements
