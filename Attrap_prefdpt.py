import datetime

from bs4 import BeautifulSoup
from urllib.parse import unquote

from Attrap import Attrap
from CamemBERT import NERPipeline
import regex as re

import locale
locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8') 

class Attrap_prefdpt(Attrap):

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0'

    # Paramètres par défaut des cartes grises et blanches. Devrait la plupart du temps être surchargés par la classe de préfecture de département
    grey_card = {
        'regex': {
            'denomination': None,
        },
        'css_path': {
            'title': 'div.fr-card.fr-card--sm.fr-card--grey.fr-enlarge-link div.fr-card__body div.fr-card__content h2.fr-card__title a'
        },
        'link_to_raa': False,
        'autodetect_links_to_raa': True,
        'follow_link_on_unrecognised_date': True,
        'exclude': [],
        'add_year_to_months': False
    }
    white_card = {
        'regex': {
            'denomination': None,
            'month': None,
        },
        'css_path': {
            'title': 'div.fr-card.fr-card--horizontal.fr-card--sm.fr-enlarge-link div.fr-card__body div.fr-card__content h2.fr-card__title a.fr-card__link',  # Chemin CSS du titre des cartes blanches
            'details': 'div.fr-card.fr-card--horizontal.fr-card--sm.fr-enlarge-link div.fr-card__body div.fr-card__content div.fr-card__end p.fr-card__detail',  # Chemin CSS du détail des cartes blanches
            'pager': 'ul.fr-pagination__list li a.fr-pagination__link.fr-pagination__link--next.fr-pagination__link--lg-label'  # Chemin CSS du pager des cartes blanches
        },
        'link_to_raa': False,
        'autodetect_links_to_raa': True,
        'follow_link_on_unrecognised_date': True,
        'exclude': [],
        'add_year_to_months': False
    }

    # Liste des widgets à analyser (sera remplie au moment de l'initialisation, mais peut être surchargée par la classe de préfecture de département)
    widgets = []
    select_widgets = []

    # Est-ce qu'on inclue les widgets des cartes blanches et grises ? Par défaut oui, mais il peut être nécessaire de les désactiver sur certaines préfectures
    include_grey_card_widget = True
    include_white_card_widget = True

    # Chemin CSS vers un RAA
    element_css_path = 'div.fr-downloads-group.fr-downloads-group--bordered ul li a,div a.fr-link.fr-link--download'

    # Temporisation (en secondes) entre chaque requête (ne devrait pas avoir à être changée)
    pref_sleep_time = 5

    class DptWidget:
        """Une classe représentant un widget sur le site d'une préfecture de département."""

        def __init__(self, name, regex=None, css_path=None, link_to_raa=False, autodetect_links_to_raa=True, follow_link_on_unrecognised_date=True, exclude=[]):
            self.name = name
            self.regex = regex
            self.css_path = css_path
            self.link_to_raa = link_to_raa
            self.autodetect_links_to_raa = autodetect_links_to_raa
            self.follow_link_on_unrecognised_date = follow_link_on_unrecognised_date
            self.exclude = exclude

        def has_css_path(self, key):
            return self.css_path and self.css_path.get(key, None) is not None

        def get_css_path(self, key):
            if not self.has_css_path(key):
                return None
            else:
                return self.css_path.get(key, None)

        def has_regex(self, key):
            return self.regex and self.regex.get(key, None) is not None

        def get_regex(self, key):
            if not self.has_regex(key):
                return None
            else:
                return self.regex.get(key, None)

    class DptSelectWidget:
        """Une classe représentant un menu déroulant sur le site d'une préfecture de département."""

        def __init__(self, name, regex=None, css_path=None, follow_link_on_unrecognised_date=True, exclude=[], type='year-month-day'):
            self.name = name
            self.regex = regex
            self.css_path = css_path
            self.follow_link_on_unrecognised_date = follow_link_on_unrecognised_date
            self.exclude = exclude
            self.type = type

    def add_url(self, url, date=None):
        if date and date.year == 9999:
            date = None
        self.page_urls_to_parse.append([url, date])

    def get_urls_to_parse(self):
        urls = []
        for url in self.page_urls_to_parse:
            urls.append(url[0])
        return urls

    def __init__(self, data_dir):
        """Une classe générique permettant d'analyser les préfectures de département en fonction de certains paramètres."""

        super().__init__(data_dir, self.user_agent)
        self.set_sleep_time(self.pref_sleep_time)

        self.page_urls_to_parse = []

        if isinstance(self.raa_page, str):
            self.add_url(self.raa_page)
        else:
            for url in self.raa_page:
                self.add_url(url)
        self.elements = []

        # On ajoute les cartes grises et blanches à la liste des widgets à parser
        if self.include_grey_card_widget:
            self.widgets.append(
                Attrap_prefdpt.DptWidget(
                    'grey_card',
                    regex=self.grey_card['regex'],
                    css_path=self.grey_card['css_path'],
                    link_to_raa=self.grey_card['link_to_raa'],
                    autodetect_links_to_raa=self.grey_card['autodetect_links_to_raa'],
                    follow_link_on_unrecognised_date=self.grey_card['follow_link_on_unrecognised_date'],
                    exclude=self.grey_card['exclude']
                )
            )

        if self.include_white_card_widget:
            self.widgets.append(
                Attrap_prefdpt.DptWidget(
                    'white_card',
                    regex=self.white_card['regex'],
                    css_path=self.white_card['css_path'],
                    link_to_raa=self.white_card['link_to_raa'],
                    autodetect_links_to_raa=self.white_card['autodetect_links_to_raa'],
                    follow_link_on_unrecognised_date=self.white_card['follow_link_on_unrecognised_date'],
                    exclude=self.white_card['exclude']
                )
            )

    def get_raa(self, keywords):
        print(self.page_urls_to_parse)
        while not self.page_urls_to_parse == []:
            page_url = self.page_urls_to_parse[-1]
            page_content = self.get_page(page_url[0], 'get').content  # On récupère le HTML de la page
            self.parse_widgets(page_url, page_content)  # On parse les cartes
            self.parse_select_widgets(page_url, page_content)  # On parse les menus déroulants
            for element in self.get_raa_elements(page_content):  # On cherche les RAA
                self.elements.append(element)
            self.page_urls_to_parse.remove(page_url)  # On supprime la page de la liste de celles à parser

#        print(self.widgets)
#        print(self.select_widgets)
        self.parse_raa(self.elements[::-1], keywords)

    def parse_widgets(self, page_url, page_content):
        # Pour chaque widget paramétré qui n'est pas de type select, on le cherche sur la page
        for widget in self.widgets:
            cards = []
            # Si n'appelle pas la même fonction le widget a prévu un pager ou non
            if widget.has_css_path('pager'):
                cards = self.get_sub_pages_with_pager(
                    page_content,
                    widget.get_css_path('title'),  # Titre du lien
                    widget.get_css_path('pager'),  # Pager
                    widget.get_css_path('details'),  # Détails
                    self.hostname
                )
            else:
                cards = self.get_sub_pages(
                    page_content,
                    widget.get_css_path('title'),
                    self.hostname,
                    False
                )
            for card in cards:
                if card['url'] not in self.get_urls_to_parse() and card['name'].strip() not in widget.exclude:
                    date = None
                    date_is_correct = False
#                    self.cards.update({card['url']: card['name'].strip(),
#                                       'children': []})
                    print(card['name'].strip())
                    # Si un regex d'année est spécifié, on parse le titre avec
                    # if widget.has_regex('year'):
                    #     date = Attrap.guess_date(card['name'].strip(), widget.get_regex('year')).replace(day=1, month=1)
                    #     # Si une date a été trouvée (l'année n'est pas 9999) et qu'elle est avant la valeur not_before, on la marque comme correcte
                    #     if date >= self.not_before.replace(day=1, month=1) and date.year < 9999:
                    #         date_is_correct = True

                    # # Si un regex de mois est spécifié et qu'aucune date correcte n'a été trouvée, on teste avec le regex de mois sur le titre
                    # if widget.has_regex('month') and (not date or date.year == 9999):
                    #     # On ajoute l'année au nom du mois à tester si configuré dans le widget
                    #     if widget.add_year_to_months and page_url[1]:
                    #         month = card['name'].strip() + ' ' + str(page_url[1].year)
                    #     else:
                    #         month = card['name'].strip()
                    #     date = Attrap.guess_date(month, widget.get_regex('month')).replace(day=1)
                    #     if date >= self.not_before.replace(day=1) and date.year < 9999:
                    #         date_is_correct = True

                    # Si un chemin CSS vers les détails du widget est spécifié et qu'aucune date correcte n'a été trouvée, on tente de parser la date présente dans les détails
                    if widget.has_css_path('details') and (not date or date.year == 9999):
                        try:
                            date = datetime.datetime.strptime(card['details'].replace('Publié le ', '').strip(), '%d/%m/%Y')
                            if date >= self.not_before:
                                date_is_correct = True
                        except Exception as e:
                            date = datetime.datetime(9999, 1, 1)

                    # Si la configuration indique que les liens renvoient vers un RAA, on ajoute le lien à la liste des éléments
                    if widget.link_to_raa or (widget.autodetect_links_to_raa and card['url'].endswith('.pdf')):
                        raa = Attrap.RAA(card['url'], card['name'].strip())
                        self.elements.append(raa)
                    else:
                        # Si une date a été trouvée, on regarde s'il faut ajouter l'URL à la liste des pages à parser
                        if date_is_correct or ((date is None or date.year == 9999) and widget.follow_link_on_unrecognised_date):
                            self.add_url(card['url'], date)

    def parse_select_widgets(self, page_url, page_content):
        for select_widget in self.select_widgets:
            # Les widgets select fonctionnent différemment : chaque valeur option doit être testée pour trouver une date, et si la date correspond
            # à la date recherchée la requête POST est envoyée, puis le résultat est analysé par get_raa_elements()

            # On charge le parser
            soup = BeautifulSoup(page_content, 'html.parser')

            # On récupère les select
            for select in soup.select(select_widget.css_path):
                # On récupère les option de chaque select
                for option in select.find_all('option'):
                    if not option['value'] == "" and option['title'].strip() not in select_widget.exclude:
                         # On estime la date à partir du nom de fichier
                        date = Attrap.guess_date(option['title'].strip(), select_widget.regex)
                        match select_widget.type:
                            case 'year':
                                date = date.replace(day=1, month=1)
                                not_before = self.not_before.replace(day=1, month=1)
                            case 'year-month':
                                date = date.replace(day=1)
                                not_before = self.not_before.replace(day=1)
                            case _:
                                not_before = self.not_before

                         # Si la date estimée correspond à la plage d'analyse ou si follow_link_on_unrecognised_date est à True,
                         # on demande au serveur les détails du RAA
                        if (date.year < 9999 and date >= not_before) or (date.year == 9999 and select_widget.follow_link_on_unrecognised_date):
                            page_content = self.get_page(
                                page_url[0],
                                'post',
                                {
                                    select['id']: option['value']
                                }
                            ).content
                            for element in self.get_raa_elements(page_content):
                                self.elements.append(element)

    def get_raa_elements(self, page_content):
        elements = []
        # On charge le parser
        soup = BeautifulSoup(page_content, 'html.parser')
        name_of_ppri = soup.find('h1').get_text()
        for a in soup.select(self.element_css_path):
            if a.get('href'):
                if a['href'].startswith('/'): # type: ignore
                    url = f"{self.hostname}{a['href']}" # type: ignore
                else:
                    url = a['href']

                url = unquote(url)
                name = a.find('span').previous_sibling.replace('Télécharger ', '').strip() # type: ignore
                if not name:
                    name = url.split('/')[-1].strip()

                raa = Attrap.RAA(url, name,name_of_ppri) # type: ignore
                elements.append(raa)
        return elements
