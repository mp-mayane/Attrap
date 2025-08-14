import os
import sys
import datetime
import logging

from bs4 import BeautifulSoup
from urllib.parse import unquote

from Attrap import Attrap

logger = logging.getLogger(__name__)


class Attrap_pref66(Attrap):

    # Config
    hostname = 'https://www.pyrenees-orientales.gouv.fr'
    raa_page = f'{hostname}/Publications/Le-recueil-des-actes-administratifs'
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/115.0'
    full_name = 'Préfecture des Pyrénées-Orientales'
    short_code = 'pref66'
    timezone = 'Europe/Paris'

    def __init__(self, data_dir):
        super().__init__(data_dir, self.user_agent)
        self.set_sleep_time(30)

    def get_raa(self, keywords):
        # On détermine quelles pages d'année parser
        year_pages = []
        page_content = self.get_page(self.raa_page, 'get').content
        for year_page in self.get_sub_pages(
            page_content,
            '.fr-table table tr td h3 a.fr-link',
            self.hostname,
            False
        ):
            year = Attrap.guess_date(year_page['name'].strip(), '.* ([0-9]{4})').year
            if year < 9999 and year >= self.not_before.year:
                year_pages.append([year_page['url'], year])

        elements = []

        # La préfecture des Pyrénées-Orientales est une originale : avant 2024,
        # chaque page annuelle contient l'ensemble des RAA, mais pas tout le
        # temps avec leur date, qu'il faut deviner à partir du nom du RAA.
        # Mais en 2024, ça change ! La page de 2024 contient un tableau
        # récapitulatif avec toutes les dates de publication des RAA, mais
        # aussi un pager. Sauf qu'il s'avère que le tableau récapitulatif
        # n'est pas exhaustif. On doit donc parser toutes les sous-pages de
        # 2024 puisqu'on ne peut se fier au tableau récapitulatif.
        # Grrr.
        for year_page in year_pages:
            url = year_page[0]
            year = year_page[1]

            if year >= 2024:
                for element in self.get_raa_elements_since_2024(url):
                    elements.append(element)
            else:
                for element in self.get_raa_elements_before_2024(url):
                    elements.append(element)

        self.parse_raa(elements, keywords)

    # On parse un lien d'avant 2024
    def get_raa_elements_before_2024(self, page):
        elements = []
        page_content = self.get_page(page, 'get').content
        soup = BeautifulSoup(page_content, 'html.parser')
        for a in soup.select('div.fr-table.fr-table--bordered.list a.fr-link.fr-link--download'):
            if a.get('href') and a['href'].endswith('.pdf'):
                date = None
                try:
                    # Lorsque la date n'est pas affichée à l'écran, elle est en
                    # fait cachée dans la propriété "title" du lien
                    details = ''
                    if a.find('span'):
                        details = a.find('span').get_text().split(' - ')[-1].strip()
                    else:
                        details = a['title'].split(' - ')[-1].strip()
                    date = datetime.datetime.strptime(details, '%d/%m/%Y')
                except Exception as exc:
                    logger.error(f'Impossible de trouver de date pour le texte : {text_raw}: {exc}')
                    sys.exit(1)

                if date >= self.not_before:
                    url = ''
                    if a['href'].startswith('/'):
                        url = f"{self.hostname}{a['href']}"
                    else:
                        url = a['href']

                    url = unquote(url)
                    name = ''
                    if a.find('span') and a.find('span').previous_sibling:
                        name = a.find('span').previous_sibling.replace('Télécharger ', '').strip()
                    else:
                        name = a.get_text().replace('Télécharger ', '').strip()

                    elements.append(Attrap.RAA(url, date, name))
        return elements

    # On parse les RAA depuis 2024
    def get_raa_elements_since_2024(self, root_page):
        pages = self.get_sub_pages_with_pager(
            root_page,
            'div.fr-card__body div.fr-card__content h2.fr-card__title a.fr-card__link',
            'ul.fr-pagination__list li a.fr-pagination__link.fr-pagination__link--next',
            'div.fr-card__body div.fr-card__content div.fr-card__end p.fr-card__detail',
            self.hostname
        )[::-1]

        pages_to_parse = []
        elements = []

        for page in pages:
            if not page['url'].endswith('.pdf'):
                logger.warning(f"Attention, le lien vers {page['url']} n'est pas bon !")
            else:
                if page['url'].startswith('/'):
                    url = f"{self.hostname}{page['url']}"
                else:
                    url = page['url']

                url = unquote(url)
                name = page['name'].replace('Télécharger ', '').strip()
                date = datetime.datetime.strptime(page['details'].replace('Publié le ', '').strip(), '%d/%m/%Y')

                elements.append(Attrap.RAA(url, date, name, timezone=self.timezone))
        return elements
