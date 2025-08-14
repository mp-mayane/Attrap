import os
import datetime

from bs4 import BeautifulSoup
from urllib.parse import unquote

from Attrap import Attrap


class Attrap_pref81(Attrap):

    # Config
    hostname = 'https://www.tarn.gouv.fr'
    raa_page = f'{hostname}/Publications/RAA-Recueil-des-Actes-Administratifs/RAA'
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/115.0'
    full_name = 'Préfecture du Tarn'
    short_code = 'pref81'
    timezone = 'Europe/Paris'

    def __init__(self, data_dir):
        super().__init__(data_dir, self.user_agent)
        self.set_sleep_time(5)

    def get_raa(self, keywords):
        year_pages_to_parse = []

        # On détermine quelles pages d'année parser
        page_content = self.get_page(self.raa_page, 'get').content
        year_pages = self.get_sub_pages(
            page_content,
            '.fr-card.fr-card--sm.fr-card--grey.fr-enlarge-link div.fr-card__body div.fr-card__content h2.fr-card__title a',
            self.hostname,
            False
        )
        for year_page in year_pages:
            if int(year_page['name'].replace('Année ', '').strip()) >= self.not_before.year:
                year_pages_to_parse.append(year_page['url'])

        month_pages_to_parse = []
        # Pour chaque année, on cherche les sous-pages de mois
        for year_page in year_pages_to_parse:
            page_content = self.get_page(year_page, 'get').content
            month_pages = self.get_sub_pages(
                page_content,
                '.fr-card.fr-card--sm.fr-card--grey.fr-enlarge-link div.fr-card__body div.fr-card__content h2.fr-card__title a',
                self.hostname,
                False
            )[::-1]
            for month_page in month_pages:
                # On filtre les mois ne correspondant pas à la période analysée
                guessed_date = Attrap.guess_date(month_page['name'], '(.*)')
                if guessed_date.replace(day=1) >= self.not_before.replace(day=1):
                    month_pages_to_parse.append(month_page['url'])

        pages_to_parse = []
        # Pour chaque page de mois, on cherche les pages de RAA
        for month_page in month_pages_to_parse:
            # TODO : il reste à gérer le cas où une page de mois redirige vers un RAA (cela
            # arrive quand la préfecture n'a publié qu'un seul RAA pendant le mois)
            pages = self.get_sub_pages_with_pager(
                month_page,
                'div.fr-card.fr-card--horizontal.fr-card--sm.fr-enlarge-link.fr-mb-3w div.fr-card__body div.fr-card__content h2.fr-card__title a.fr-card__link',
                'nav.fr-pagination ul.fr-pagination__list li a.fr-pagination__link.fr-pagination__link--next.fr-pagination__link--lg-label',
                'div.fr-card.fr-card--horizontal.fr-card--sm.fr-enlarge-link.fr-mb-3w div.fr-card__body div.fr-card__content div.fr-card__end p.fr-card__detail',
                self.hostname
            )[::-1]
            for page in pages:
                guessed_date = datetime.datetime.strptime(page['details'].replace('Publié le ', '').strip(), '%d/%m/%Y')
                if guessed_date.replace(day=1) >= self.not_before.replace(day=1):
                    pages_to_parse.append(page['url'])

        # On ajoute également la page racine, qui peut contenir des RAA mal catégorisés
        pages_to_parse.append(self.raa_page)

        elements = []
        # On parse les pages contenant des RAA
        for page in pages_to_parse:
            page_content = self.get_page(page, 'get').content
            for element in self.get_raa_elements(page_content):
                elements.append(element)

        # On parse les RAA
        self.parse_raa(elements, keywords)

    def get_raa_elements(self, page_content):
        elements = []
        # On charge le parser
        soup = BeautifulSoup(page_content, 'html.parser')

        # On récupère chaque balise a
        for a in soup.select('div.fr-grid-row div.fr-downloads-group.fr-downloads-group--bordered ul li a'):
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
