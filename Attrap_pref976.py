import os
import datetime

from bs4 import BeautifulSoup
from urllib.parse import unquote

from Attrap import Attrap


class Attrap_pref976(Attrap):

    # Config
    hostname = 'https://www.mayotte.gouv.fr'
    raa_page = f'{hostname}/Publications/Recueil-des-actes-administratifs-R.A.A'
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/115.0'
    full_name = 'Préfecture de Mayotte'
    short_code = 'pref976'
    timezone = 'Indian/Mayotte'

    def __init__(self, data_dir):
        super().__init__(data_dir, self.user_agent)
        self.set_sleep_time(5)

    def get_raa(self, keywords):
        year_pages_to_parse = []

        # On récupère les pages d'années
        page_content = self.get_page(self.raa_page, 'get').content
        for card in self.get_sub_pages(
            page_content,
            'div.fr-card__body div.fr-card__content h2.fr-card__title a',
            self.hostname,
            False
        ):
            if Attrap.guess_date(card['name'], '([0-9]{4})').year >= self.not_before.year:
                year_pages_to_parse.append(card['url'])

        pages_to_parse = [self.raa_page]

        # Pour chaque année, on cherche les sous-pages de mois
        for raa_page in year_pages_to_parse:
            page_content = self.get_page(raa_page, 'get').content
            month_pages = self.get_sub_pages(
                page_content,
                '.fr-card.fr-card--sm.fr-card--grey.fr-enlarge-link div.fr-card__body div.fr-card__content h2.fr-card__title a',
                self.hostname,
                False
            )[::-1]

            # On regarde aussi si sur la page de l'année il n'y aurait pas un
            # RAA mal catégorisé
            for page_to_parse in self.find_raa_card(page_content):
                pages_to_parse.append(page_to_parse)

            # Pour chaque mois, on cherche les pages des RAA
            for month_page in month_pages:
                year = Attrap.guess_date(month_page['name'], '(.*)').year
                for page_to_parse in self.find_raa_card(
                    month_page['url'],
                    year
                ):
                    pages_to_parse.append(page_to_parse)

        # On parse les pages contenant des RAA
        elements = []
        for page in pages_to_parse:
            page_content = self.get_page(page, 'get').content
            for element in self.get_raa_elements(page_content):
                elements.append(element)

        self.parse_raa(elements, keywords)

    def find_raa_card(self, page, year=None):
        pages = []
        card_pages = self.get_sub_pages_with_pager(
            page,
            'div.fr-card__body div.fr-card__content h2.fr-card__title a.fr-card__link',
            'ul.fr-pagination__list li a.fr-pagination__link.fr-pagination__link--next',
            None,
            self.hostname
        )[::-1]
        for card_page in card_pages:
            # On filtre les pages de RAA ne correspondant pas à la période
            # analysée
            guessed_date = Attrap.guess_date(card_page['name'], 'n°[ 0-9]* du ([0-9]*(?:er)? [a-zéû]* [0-9]*)')
            if year:
                guessed_date = guessed_date.replace(year=year)
            if guessed_date >= self.not_before:
                pages.append(card_page['url'])
        return pages

    def get_raa_elements(self, page_content):
        elements = []
        # On charge le parser
        soup = BeautifulSoup(page_content, 'html.parser')

        # On récupère chaque balise a
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
