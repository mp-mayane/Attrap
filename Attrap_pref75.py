import os
import datetime

from bs4 import BeautifulSoup
from urllib.parse import unquote

from Attrap import Attrap


class Attrap_pref75(Attrap):

    # Les RAA de Paris sont sur le site de la préfecture de région
    # Île-de-France. On ne prend en compte que les RAA départementaux.

    # Config
    hostname = 'https://www.prefectures-regions.gouv.fr'
    raa_page = f'{hostname}/ile-de-france/tags/view/Ile-de-France/Documents+et+publications/Recueil+des+actes+administratifs'
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0'
    full_name = 'Préfecture de Paris'
    short_code = 'pref75'
    timezone = 'Europe/Paris'

    def __init__(self, data_dir):
        super().__init__(data_dir, self.user_agent)
        self.enable_tor(10)
        self.set_sleep_time(10)

    def get_raa(self, keywords):
        year_pages_to_parse = []

        # On détermine quelles pages d'année parser
        page_content = self.get_session(self.raa_page, 'main', 6)
        year_pages = self.get_sub_pages(
            page_content,
            'article.news-list-item header h2.news-list-title a',
            self.hostname,
            False,
            selenium=True
        )
        for year_page in year_pages:
            year_date = Attrap.guess_date(year_page['name'].strip(), '(?:.*Paris.*)([0-9]{4})').replace(day=1, month=1)
            if year_date.year >= self.not_before.year and year_date.year < 9999:
                year_pages_to_parse.append(year_page['url'])

        pages_to_parse = []
        for year_page in year_pages_to_parse:
            page_content = self.get_session(year_page, 'main', 6)
            year = BeautifulSoup(page_content, 'html.parser').select('div.breadcrumb div.container p span.active')[0].get_text().split('-')[-1].strip()
            month_pages = self.get_sub_pages(
                page_content,
                'div.sommaire-bloc div.sommaire-content ol li a',
                self.hostname,
                False,
                selenium=True
            )[::-1]
            for month_page in month_pages:
                month_date = Attrap.guess_date(f"{month_page['name']} {year}", "(.*)").replace(day=1)
                if month_date >= self.not_before.replace(day=1):
                    pages_to_parse.append(month_page['url'])

        elements = []
        for page in pages_to_parse[::-1]:
            page_content = self.get_session(page, 'main', 6)
            for element in self.get_raa_elements(page_content):
                elements.append(element)

        self.parse_raa(elements[::-1], keywords)

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
                guessed = Attrap.guess_date(name, '((?:[0-9]{2}(?:-|\\.)[0-9]{2}(?:-|\\.)20[0-9]{2})|(?:20[0-9]{2}(?:-|\\.)[0-9]{2}(?:-|\\.)[0-9]{2})\\D*^)')
                if (guessed == datetime.datetime(9999, 1, 1, 0, 0)):
                    date = None
                else:
                    date = guessed

                raa = Attrap.RAA(url, date, name, timezone=self.timezone)
                elements.append(raa)
        return elements
