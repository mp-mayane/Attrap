import os
import datetime
import logging

from bs4 import BeautifulSoup
from urllib.parse import unquote

from Attrap import Attrap

logger = logging.getLogger(__name__)


class Attrap_pref80(Attrap):

    # Config
    hostname = 'https://www.somme.gouv.fr'
    raa_page = f'{hostname}/Publications/Recueil-des-actes-administratifs-du-departement-de-la-Somme'
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/115.0'
    full_name = 'Préfecture de la Somme'
    short_code = 'pref80'
    timezone = 'Europe/Paris'

    def __init__(self, data_dir):
        super().__init__(data_dir, self.user_agent)
        self.set_sleep_time(30)

    def get_raa(self, keywords):
        year_pages_to_parse = []

        # On détermine quelles pages d'année parser
        page_content = self.get_page(self.raa_page, 'get').content
        year_pages = self.get_sub_pages(
            page_content,
            'div.fr-card.fr-card--sm.fr-card--grey.fr-enlarge-link div.fr-card__body div.fr-card__content h2.fr-card__title a',
            self.hostname,
            False
        )
        for year_page in year_pages:
            year_date = Attrap.guess_date(year_page['name'].strip(), '.*([0-9]{4})').replace(day=1, month=1)
            if year_date.year >= self.not_before.year:
                year_pages_to_parse.append(year_page['url'])

        # Pour chaque page Année, on récupère la liste des RAA
        elements = []
        for year_page in year_pages_to_parse:
            page_content = self.get_page(year_page, 'get').content
            for element in self.get_raa_elements(page_content):
                elements.append(element)

        self.parse_raa(elements, keywords)

    def get_raa_elements(self, page_content):
        elements = []
        # On charge le parser
        soup = BeautifulSoup(page_content, 'html.parser')

        # Pour chaque balise a, on regarde si c'est un PDF, et si oui on le
        # parse
        for a in soup.select('div.fr-text--lead p a.fr-link'):
            if a.get('href') and a['href'].endswith('.pdf'):
                if a['href'].startswith('/'):
                    url = f"{self.hostname}{a['href']}"
                else:
                    url = a['href']

                url = unquote(url)
                # On enlève les espaces insécables, les double-espaces, et le texte « Télécharger » de certains liens
                name = a.get_text().replace('Télécharger ', '').strip().replace(u"\u00A0", ' ').replace('  ', ' ')
                if name and not name == '':
                    # Certains RAA de la Somme ont une ligne avec les détails du fichier. Si cette ligne
                    # est disponible, on la parse, sinon on devine la date à partir du nom
                    date = None
                    if a.find('span'):
                        date = datetime.datetime.strptime(a.find('span').get_text().split(' - ')[-1].strip(), '%d/%m/%Y')
                    else:
                        regex = '.* n°.*(?:du)? ([0-9]*(?:er)? [a-zéû]* (?:[0-9]{4}|[0-9]{2}))'
                        date = Attrap.guess_date(name, regex)
                        # Parfois, il manque l'année dans le nom du RAA, alors on essaie avec l'année de la page
                        if date.year == 9999:
                            page_year = soup.select('nav.fr-breadcrumb div.fr-collapse ol.fr-breadcrumb__list li a.fr-breadcrumb__link.breadcrumb-item-link')[-1].get_text().replace('Année ', '').strip()
                            date = Attrap.guess_date(f'{name} {page_year}', regex)

                            # Parfois, c'est que le fichier n'est pas un RAA mais un arrêté seul
                            if date.year == 9999:
                                date = Attrap.guess_date(name, '([0-9]*(?:er)? [a-zéû]* [0-9]{4})')

                    if date.year == 9999:
                        logger.warning(f'On ignore {name} (URL : {url})')
                    else:
                        raa = Attrap.RAA(url, date, name, timezone=self.timezone)
                        elements.append(raa)
        return elements[::-1]
    