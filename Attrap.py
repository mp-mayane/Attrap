import os
import sys
import re
import random
import ssl
import subprocess
import shutil
import string
import logging
import requests
import time
from types import SimpleNamespace
import datetime
import json
from urllib.parse import quote
import locale

locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8') 

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions

import pytz
import dateparser
import urllib3

from bs4 import BeautifulSoup
from pyvirtualdisplay import Display

from pypdf import PdfReader
from pypdf import PdfWriter
from pypdf.generic import NameObject, NumberObject
from pypdf.errors import PdfStreamError
from pypdf.errors import EmptyFileError

import hashlib
import smtplib
import email

import ftfy
from CamemBERT import NERPipeline

logger = logging.getLogger(__name__)

anti_join = ['Communes  de ','Commune de','Commune de  ','Commune','Communes','communes','Commune de la','Commune du','Commune des','Commune d\'']

ner = NERPipeline()

class Attrap:
    class RAA:
        """La classe représentant un Recueil des actes administratifs. La plupart du temps, il s'agit d'un PDF avec plusieurs arrêtés."""

        url = ""
        date = None
        name = ""
        sha256 = ""
        pdf_creation_date = None
        pdf_modification_date = None

        def __init__(self, url, name,name_of_ppri=""):
            if not url == "":
                self.url = url
            if not name == "":
                self.name = name
            if not name_of_ppri == "" or name_of_ppri is not None:
                self.name_of_ppri = name_of_ppri.strip()
            self.pdf_creation_date = None
            self.pdf_modification_date = None

        def get_sha256(self):
            """Calcule et met en cache le hash sha256 de l'URL du PDF, pour servir d'identifiant unique."""
            if (self.sha256 == ""):
                self.sha256 = hashlib.sha256(self.url.encode('utf-8')).hexdigest()
            return self.sha256

        # def get_pdf_dates(self, data_dir):
        #     """Extrait les dates des PDF pour les ajouter à l'objet du RAA."""
        #     raa_data_dir = f'{data_dir}/raa/'

        #     reader = PdfReader(f'{raa_data_dir}{self.get_sha256()}.pdf')
        #     pdf_metadata = reader.metadata

        #     if pdf_metadata:
        #         if pdf_metadata.creation_date:
        #             self.pdf_creation_date = Attrap.get_aware_datetime(pdf_metadata.creation_date, timezone=self.timezone)
        #             if self.date is None:
        #                 self.date = Attrap.get_aware_datetime(pdf_metadata.creation_date, timezone=self.timezone)

        #         if pdf_metadata.modification_date:
        #             self.pdf_modification_date = Attrap.get_aware_datetime(pdf_metadata.modification_date, timezone=self.timezone)
        #             if self.date is None:
        #                 self.date = Attrap.get_aware_datetime(pdf_metadata.modification_date, timezone=self.timezone)

        def extract_content(self, data_dir):
            """Extrait le contenu du PDF OCRisé pour l'écrire dans le fichier qui servira à faire la recherche de mots-clés. Supprime tous les PDF à la fin."""
            raa_data_dir = os.path.join(f'{data_dir}',self.name_of_ppri)

            reader_pdf = PdfReader(f'{raa_data_dir}/{self.get_sha256()}.pdf')
            pdf_metadata = reader_pdf.metadata
            print(pdf_metadata)

            text = ""

            reader = PdfReader(f'{raa_data_dir}/{self.get_sha256()}.ocr.pdf')
            ftfy_config = ftfy.TextFixerConfig(unescape_html=False, explain=False)
            for page in reader.pages:
                try:
                    text = text + "\n" + ftfy.fix_text(page.extract_text(), config=ftfy_config)
                except Exception as e:
                    logger.warning(f'ATTENTION: Impossible d\'extraire le texte du fichier {self.get_sha256()}.pdf : {e}')

            # Écrit le texte du PDF dans un fichier texte pour une analyse future
            f = open(f'{raa_data_dir}/{self.name}.txt', 'w', encoding='utf-8')
            f.write(text)
            f.close()

            # Supprime le PDF d'origine et la version OCRisée
            os.remove(f'{raa_data_dir}/{self.get_sha256()}.pdf')
            os.remove(f'{raa_data_dir}/{self.get_sha256()}.ocr.pdf')
            os.remove(f'{raa_data_dir}/{self.get_sha256()}.flat.pdf')

        def write_properties(self, data_dir):
            """Écris les propriétés du RAA dans un fichier JSON."""
            raa_data_dir = os.path.join(f'{data_dir}',self.name_of_ppri)

            pdf_creation_date_json = None
            pdf_modification_date_json = None

            if self.pdf_creation_date:
                pdf_creation_date_json = self.pdf_creation_date.astimezone(pytz.utc).isoformat(timespec="seconds")
            if self.pdf_modification_date:
                pdf_modification_date_json = self.pdf_modification_date.astimezone(pytz.utc).isoformat(timespec="seconds")

            properties = {
                'version': 2,
                'name': self.name,
                'url': quote(self.url, safe='/:'),
                'first_seen_on': datetime.datetime.now(pytz.utc).isoformat(timespec="seconds"),
                'pdf_creation_date': pdf_creation_date_json,
                'pdf_modification_date': pdf_modification_date_json
            }
            f = open(f'{raa_data_dir}/{self.get_sha256()}.json', 'w')
            f.write(json.dumps(properties))
            f.close()

        def parse_metadata(self, data_dir):
            """Lance l'extraction des dates du PDF puis l'écriture de ses propriétés dans un fichier JSON."""
            # self.get_pdf_dates(data_dir)
            self.write_properties(data_dir)

    def __init__(self, data_dir, user_agent=''):
        """
        Initialise Attrap et le dossier de données.
        data_dir -- le dossier où sont situées les données
        user_agent -- le user_agent utilisé pour les requêtes
        """
        logger.debug('Initialisation de Attrap')

        # On crée le dossier de téléchargement
        os.makedirs(data_dir, exist_ok=True)

        self.session = requests.Session()
        self.data_dir = data_dir
        self.found = False
        self.output_file_path = os.path.dirname(os.path.abspath(__file__)) + f'/output_{self.short_code}.log'
        self.sleep_time = 0
        self.last_http_request = 0
        self.tor_enabled = False
        self.tor_max_requests = 0
        self.tor_requests = 0
        self.tor_socks5_key = None
        self.not_before = datetime.datetime(2024, 1, 1)
        self.smtp_configured = False
        self.safe_mode = False

        self.update_user_agent(user_agent)

        f = open(self.output_file_path, 'w')
        f.write('')
        f.close()

        self.print_output(str(self.__class__.__name__))

        # Si le safe mode est activé, on configure un long délai entre chaque requête
        if os.getenv('SAFE_MODE'):
            self.safe_mode = True
            logger.warning('ATTENTION: le safe mode est activé, configuration d\'un délai entre chaque requête')
            self.sleep_time = 30

    def enable_tor(self, max_requests=0):
        """Active l'utilisation de Tor pour effectuer les requêtes."""
        if not self.safe_mode:
            self.tor_enabled = True
            self.tor_max_requests = max_requests
            self.tor_get_new_id()
        else:
            logger.warning('ATTENTION: le safe mode est activé, Tor n\'a pas été activé')

    def disable_tor(self):
        """Désactive l'utilisation de Tor."""
        proxies = {}
        self.tor_enabled = False
        self.tor_max_requests = 0
        self.tor_requests = 0
        self.session.proxies.update(proxies)

    def tor_get_new_id(self):
        """Change de circuit Tor. Cela permet de changer de noeud de sortie donc d'IP."""
        if self.tor_enabled:
            self.tor_socks5_key = 'attrap_' + ''.join(random.choices(string.ascii_lowercase, k=20))
            proxies = {
                "http": f"socks5h://attrap:{self.tor_socks5_key}@127.0.0.1:9050",
                "https": f"socks5h://attrap:{self.tor_socks5_key}@127.0.0.1:9050",
            }
            self.session.proxies.update(proxies)
            self.tor_requests = 0

    def get_sub_pages(self, page_content, element, host, recursive_until_pdf, selenium=False):
        """
        Récupère, à partir d'un chemin CSS, les sous-pages d'une page.

        page_content -- Un contenu HTML à analyser
        element -- Le chemin CSS vers l'objet renvoyant vers la sous-page recherchée
        host -- Le nom d'hôte du site
        recursive_until_pdf -- Un booléen pour savoir s'il faut rechercher un fichier PDF dans le chemin CSS. Le cas échéant, relance la recherche sur la sous-page si le lien n'est pas un PDF.
        selenium -- lance un navigateur avec Selenium pour contourner les protections anti-robots
        """
        soup = BeautifulSoup(page_content, 'html.parser')
        sub_pages = []
        for a in soup.select(element):
            if a.get('href'):
                url = f"{host}{a['href']}"
                if recursive_until_pdf:
                    sub_page_content = self.get_page(url, 'get').content
                    if not self.has_pdf(sub_page_content):
                        logger.info(
                            f'{url} ne contient pas de PDF, on récupère ses sous-pages'
                        )
                        for sub_sub_page in self.get_sub_pages(
                            sub_page_content,
                            element,
                            host,
                            recursive_until_pdf,
                            selenium=selenium
                        ):
                            sub_pages.append(sub_sub_page)
                    else:
                        sub_page = {
                            'url': url,
                            'name': a.get_text().strip()
                        }
                        sub_pages.append(sub_page)
                else:
                    sub_page = {
                        'url': url,
                        'name': a.get_text().strip()
                    }
                    sub_pages.append(sub_page)
        return sub_pages

    def get_sub_pages_with_pager(self, page, sub_page_element, pager_element, details_element, host, selenium=False):
        """
        Récupère, à partir d'un chemin CSS, les sous-pages d'une page contenant un pager.

        page -- L'URL ou le contenu HTML de la page à analyser
        sub_page_element -- Le chemin CSS vers l'objet renvoyant vers la sous-page recherchée
        pager_element -- Le chemin CSS vers le lien de page suivante du pager
        details_element -- Le chemin CSS vers l'objet contenant les détails de la sous-page recherchée
        host -- Le nom d'hôte du site
        selenium -- lance un navigateur avec Selenium pour contourner les protections anti-robots
        """
        pages = []
        if isinstance(page, bytes):
            page = page.decode('utf-8')
        if page.startswith('https://') or page.startswith('http://'):
            page_content = self.get_page(page, 'get', selenium=selenium).content
        else:
            page_content = page

        # On initialise le parser
        soup = BeautifulSoup(page_content, 'html.parser')

        # On recherche les sous-pages
        sub_pages = soup.select(sub_page_element)
        sub_pages_details = None
        if details_element is not None:
            sub_pages_details = soup.select(details_element)
        i = 0
        for sub_page in sub_pages:
            if sub_page.get('href'):
                page = {
                    'url': f"{host}{sub_page['href']}",
                    'name': sub_page.get_text().strip(),
                    'details': ''
                }
                if details_element is not None:
                    page['details'] = sub_pages_details[i].get_text().strip()
                pages.append(page)
                i = i + 1

        # On recherche un pager, et si on le trouve on le suit
        pager = soup.select(pager_element)
        if pager and pager[0] and pager[0].get('href'):
            for sub_page in self.get_sub_pages_with_pager(
                f"{host}{pager[0]['href']}",
                sub_page_element,
                pager_element,
                details_element,
                host,
                selenium=selenium
            ):
                pages.append(sub_page)

        return pages

    def get_raa_with_pager(self, pages_list, pager_element, host, filter_from_last_element_date=False, selenium=False):
        """
        Récupère et analyse les RAA d'une page contenant un pager.

        pages_list -- Un tableau contenant la liste des pages
        pager_element -- Le chemin CSS vers le lien de page suivante du pager
        host -- Le nom d'hôte du site
        filter_from_last_element_date -- (Optionnel) Si la date du dernier élément de la dernière page parsée
        n'est pas dans la plage temporelle voulue, ne charge pas les pages suivantes. Par défaut à False. Ne doit
        être activé que si l'ordre des éléments est chronologique.
        selenium -- lance un navigateur avec Selenium pour contourner les protections anti-robots
        """
        elements = []
        # On parse chaque page passée en paramètre
        for page in pages_list:
            page_content = self.get_page(page, 'get', selenium=selenium).content

            # Pour chaque page, on récupère les PDF
            for raa in self.get_raa_elements(page_content):
                elements.append(raa)

            # Si la date du dernier RAA est dans la plage temporelle voulue,
            # on regarde également s'il n'y aurait pas un pager
            if not filter_from_last_element_date or (filter_from_last_element_date and (elements[-1].date >= Attrap.get_aware_datetime(self.not_before, timezone=self.timezone))):
                sub_pages = []
                for sub_page in self.get_sub_pages(
                    page_content,
                    pager_element,
                    host,
                    True
                ):
                    sub_pages.append(sub_page['url'])
                for sub_raa in self.get_raa_with_pager(
                    sub_pages,
                    pager_element,
                    host,
                    filter_from_last_element_date=filter_from_last_element_date
                ):
                    elements.append(sub_raa)
        return elements

    def set_sleep_time(self, sleep_time):
        """Configure le temps de temporisation"""
        self.sleep_time = sleep_time

    def has_pdf(self, page_content):
        """
        Renvoie un booléen Vrai si la page contient un lien vers un PDF

        page_content -- Un contenu HTML à analyser
        """
        elements = []
        soup = BeautifulSoup(page_content, 'html.parser')
        for a in soup.find_all('a', href=True):
            if a['href'].endswith('.pdf'):
                return True
        return False

    # On démarre le navigateur
    def get_session(self, url, wait_element, remaining_retries=0):
        """
        Lance un navigateur avec Selenium.

        url -- URL à interroger
        wait_element -- Élement (désigné par son identifiant CSS) qui indique que la page est chargée
        remaining_retries -- Nombre d'échecs autorisé avant de soulever une erreur
        """
        webdriver_options = webdriver.ChromeOptions()
        webdriver_options.add_argument("--no-sandbox")
        webdriver_options.add_argument("--disable-extensions")
        webdriver_options.add_argument("--disable-gpu")
        webdriver_options.add_argument("--disable-dev-shm-usage")
        webdriver_options.add_argument("--use_subprocess")
        webdriver_options.add_argument("--disable-blink-features=AutomationControlled")
        webdriver_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        webdriver_options.add_experimental_option('useAutomationExtension', False)

        if not self.user_agent == "":
            webdriver_options.add_argument(f"--user-agent={self.user_agent}")

        if self.tor_enabled:
            webdriver_options.add_argument(f'--proxy-server=socks5://127.0.0.1:9050')

        webdriver_options.add_argument("--headless=new")
        webdriver_options.add_argument("--start-maximized")
        display = Display(visible=False, size=(1024, 768))
        display.start()

        browser = webdriver.Chrome(options=webdriver_options)

        # Téléchargement de l'URL
        browser.get(url)

        if wait_element is not None:
            # On attend que le navigateur ait passé les tests anti-robots et
            # que le contenu s'affiche
            try:
                WebDriverWait(browser, 60).until(
                    expected_conditions.presence_of_element_located(
                        (
                            By.ID,
                            wait_element
                        )
                    )
                )
            except TimeoutException as exc:
                logger.warning(f'TimeoutException: {exc}')
                if remaining_retries > 0:
                    time.sleep(5)
                    if self.tor_enabled:
                        self.tor_get_new_id()
                    return self.get_session(url, wait_element, (remaining_retries - 1))
                else:
                    raise TimeoutException(exc)

        page_content = browser.page_source

        # On récupère les cookies du navigateur pour les réutiliser plus tard
        for cookie in browser.get_cookies():
            self.session.cookies.set(cookie['name'], cookie['value'])

        # On arrête le navigateur
        browser.quit()
        display.stop()

        return page_content

    def print_output(self, data):
        """Affiche dans le terminal et dans le fichier de log un texte"""
        print(data)
        data = data.replace('\033[92m', '')
        data = data.replace('\033[0m', '')
        data = data.replace('\033[1m', '')
        f = open(self.output_file_path, 'a',encoding='utf-8')
        f.write(data + "\n")
        f.close()

    def get_page(self, url, method, data={}, selenium=False):
        """
        Récupère le contenu HTML d'une page web

        url -- L'URL de la page demandée
        method -- 'post' ou 'get', selon le type de requête
        data -- Un dictionnaire contenant les données à envoyer au site
        selenium -- lance un navigateur avec Selenium pour contourner les protections anti-robots
        """
        try:
            logger.debug(f'Chargement de la page {url}')

            # Si un délai a été configuré, on vérifie qu'il n'est pas trop tôt pour lancer la requête
            if self.sleep_time > 0:
                current_time = int(time.mktime(datetime.datetime.today().timetuple()))
                remaining_sleep_time = self.last_http_request + self.sleep_time - current_time

                if remaining_sleep_time > 0:
                    time.sleep(remaining_sleep_time)
                self.last_http_request = int(time.mktime(datetime.datetime.today().timetuple()))

            page = None
            if selenium and method == 'get':
                page_content = self.get_session(url, None, 6)
                page = {'content': page_content, 'status_code': 200}
                page = SimpleNamespace(**page)
            else:
                if method == 'get':
                    page = self.session.get(url, timeout=(10, 120))
                if method == 'post':
                    page = self.session.post(url, data=data, timeout=(10, 120))

            if page.status_code == 429:
                logger.warning('Erreur 429 Too Many Requests reçue, temporisation...')
                self.tor_get_new_id()
                time.sleep(1)
                return self.get_page(url, method, data)

            if self.tor_enabled:
                self.tor_requests += 1
                if self.tor_max_requests > 0 and \
                   self.tor_requests > self.tor_max_requests:
                    self.tor_get_new_id()

            return page
        except requests.exceptions.ConnectionError:
            logger.warning(f'Erreur de connexion, temporisation...')
            self.tor_get_new_id()
            time.sleep(30)
            return self.get_page(url, method, data)
        except requests.exceptions.Timeout:
            logger.warning(f'Timeout, on relance la requête...')
            return self.get_page(url, method, data)
        except urllib3.exceptions.ProtocolError:
            logger.warning(f'Erreur de connexion, on relance la requête...')
            return self.get_page(url, method, data)

    def update_user_agent(self, user_agent):
        """Change la valeur du user-agent"""
        self.user_agent = user_agent
        self.session.headers.update({'User-Agent': self.user_agent})


    def download_file(self, raa,is_map:bool):
        """Télécharge un RAA"""
        safe_name = re.sub(r'[\\/"\']', '_', raa.name)

        dirname = (f'{self.data_dir}/{raa.name_of_ppri}/Cartes/{safe_name}.pdf' if is_map else f'{self.data_dir}/{raa.name_of_ppri}/{raa.get_sha256()}.pdf')
        print(dirname)
        try:
            os.makedirs(
                os.path.dirname(dirname),
                exist_ok=True
            )

            with open(dirname, 'wb') as f:
                f.write(self.get_page(raa.url, 'get').content)
            # file = self.get_page(raa.url, 'get')
            # f = open(f'{self.data_dir}/{raa.name_of_ppri}/{raa.get_sha256()}.pdf', 'wb')
            # f.write(file.content)
            # f.close()
        except (requests.exceptions.ConnectionError,
                requests.exceptions.ChunkedEncodingError):
            logger.warning(f'ATTENTION: la connexion a été interrompue pendant le téléchargement de {raa.url}, nouvelle tentative...')
            self.download_file(raa,is_map=is_map)
        except Exception as exc:
            logger.warning(f'ATTENTION: Impossible de télécharger le fichier {raa.url}: {exc}')

    def ocr(self, raa, retry_on_failure=True):
        """OCRise un RAA"""
        print("Oyez Oyez, voici l'ocrisation du RAA",self.data_dir,raa.name_of_ppri,raa.get_sha256())
        cmd = [
            'ocrmypdf',
            '-l', 'fra',
            '--output-type', 'pdf',
            '--redo-ocr',
            '--skip-big', '250',
            '--max-image-mpixels', '250',
            '--invalidate-digital-signatures',
            '--optimize', '0',
            f'{self.data_dir}/{raa.name_of_ppri}/{raa.get_sha256()}.flat.pdf',
            f'{self.data_dir}/{raa.name_of_ppri}/{raa.get_sha256()}.ocr.pdf'
        ]   
        logger.debug(f'Lancement de ocrmypdf: {cmd}')
        try:
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as exc:
            if exc.returncode == 2 and retry_on_failure:
                logger.warning('ATTENTION : Le fichier n\'est pas un PDF correct, nouvelle tentative de le télécharger')
                if self.tor_enabled:
                    self.tor_get_new_id()
                self.download_file(raa,is_map=False)
                self.ocr(raa, False)
            elif (not exc.returncode == 6) and (not exc.returncode == 10) and (not exc.returncode == 4):
                logger.warning('ATTENTION : Impossible d\'OCRiser le document', exc.returncode, exc.output)
                shutil.copy(f'{self.data_dir}/{raa.name_of_ppri}/{raa.get_sha256()}.pdf', f'{self.data_dir}/raa/{raa.name_of_ppri}/{raa.get_sha256()}.ocr.pdf')

    def flatten_pdf(self, raa):
        """Supprime les formulaires d'un PDF pour pouvoir les OCRiser après dans OCRmyPDF."""
        reader = PdfReader(f'{self.data_dir}/{raa.name_of_ppri}/{raa.get_sha256()}.pdf')
        writer = PdfWriter()

        for page in reader.pages:
            if page.get('/Annots'):
                for annot in page.get('/Annots'):
                    writer_annot = annot.get_object()
                    writer_annot.update({
                        NameObject("/Ff"): NumberObject(1)
                    })
            writer.add_page(page)
        writer.write(f'{self.data_dir}/{raa.name_of_ppri}/{raa.get_sha256()}.flat.pdf')


    def search_keywords(self, raa, keywords):
        """Recherche des mots-clés dans le texte extrait du PDF"""

        if keywords and not keywords == '':
            text = open(f'{self.data_dir}/{raa.name_of_ppri}/{raa.name}.txt',encoding="utf-8").read()

            datum = re.search(r'(?:.*?)(?:approuvé[e]?\s+.*?le\s+.*?:?|DDE\/SPE|prescrit\s+.*?le\s+.*?:?|r[ée]glement[\s–-]*?(.*?)[\s–-]*?da)\s*(\d{1,2}\s+[a-zéû]+\s+\d{4}|\d{2}\/\d{2}\/\d{4})', text, re.IGNORECASE | re.MULTILINE).group(0)
            date_mod = re.search(r'^(.*)modifié[e]?\s+(.*)le\s+(.*):?\s*(\d{1,2}\s+[a-zéû]+\s+\d{4}|\d{2}/\d{2}/\d{4})', text, re.IGNORECASE | re.MULTILINE)

            try:
                date = datetime.datetime.strptime(re.search(r"\d{1,2}\s+[a-zéû]+\s+\d{4}", datum).group(0), '%d %B %Y').date()
            except AttributeError:
                date = datetime.datetime.strptime(re.search(r"\d{2}/\d{2}/\d{4}", datum).group(0), '%d/%m/%Y').date()
                        
            if date_mod is not None:
                try:
                    date_mod = datetime.datetime.strptime(re.search(r"\d{1,2}\s+[a-zéû]+\s+\d{4}", date_mod.group(0)).group(0), '%d %B %Y').date()
                except AttributeError:
                    date_mod = datetime.datetime.strptime(re.search(r"\d{2}/\d{2}/\d{4}", date_mod.group(0)).group(0), '%d %B %Y').date()

                if date_mod > date:
                    date = date_mod
            print("Voici la date regardez bien : ",date)

            communes = re.compile(r'communes', re.IGNORECASE | re.MULTILINE)

            lines = text.splitlines()

            for i, line in enumerate(lines):
                if communes.search(line):
                    snippet = " ".join(lines[max(0, i - 2):min(len(lines), i + 5)])
                    break

            for anti in anti_join:
                if anti in snippet:
                    snippet = snippet.strip(anti)

            name = ner.run(snippet)

            print(name)

            self.print_output(f'Le PPRI {raa.name} ({raa.url}) a été trouvé le {date.strftime("%d/%m/%Y")}.')
            self.print_output(f'Le PPRI {raa.name} ({raa.url}) a été trouvé pour les communes suivantes : {", ".join(name)}')
            found = False
            found_keywords = []
            for keyword in keywords.split(','):
                if re.search(keyword, text, re.IGNORECASE | re.MULTILINE):
                    if not found:
                        url = quote(raa.url, safe='/:')

                        # self.print_output(f'\033[92m{raa.name}\033[0m ({date_str})')
                        #self.print_output(f'URL : {url}')
                        found = True
                        self.found = True
                    self.print_output(f'Le terme \033[1m{keyword}\033[0m a été trouvé.')
                    found_keywords.append(keyword)
            if found:
                self.print_output('')
                url = quote(raa.url, safe='/:')
                found_keywords_str = ', '.join(
                    [str(x) for x in found_keywords]
                )
                logger.info(f'Le RAA {raa.name} ({url}) contient les mots-clés suivants : {found_keywords_str}')
            os.remove(f'{self.data_dir}/{raa.name_of_ppri}/{raa.get_sha256()}.json')


    def parse_raa(self, elements, keywords):
        keywords= keywords.strip()
        """
        Démarre l'analyse des RAA.

        elements -- Un tableau contenant les RAA à analyser
        keywords -- Les mots-clés à rechercher dans chaque RAA
        """
        self.print_output(f'Termes recherchés: {keywords}')
        self.print_output('')

        for raa in elements:
            print(f'Document:{raa.name} - URL: {raa.url} - PPRI: {raa.name_of_ppri}')
            # Si le fichier n'a pas déjà été parsé et qu'il est postérieur à la
            # date maximale d'analyse, on le télécharge et on le parse
            if re.search(r'R[èe]glement', raa.name, re.IGNORECASE):
                if not os.path.isfile(f'{self.data_dir}/{raa.name_of_ppri}/{raa.get_sha256()}.txt'): #and (not raa.date or (raa.date >= Attrap.get_aware_datetime(self.not_before, timezone=self.timezone))):
                    url = quote(raa.url, safe='/:')
                    #print(f'Ce fichier n\'a pas encore été analysé: {raa.name} ({url})')          
                    try:
                        self.download_file(raa,False)
                        raa.parse_metadata(self.data_dir)
                    # Lorsque la date du RAA n'est pas connue, on a dû télécharger le PDF pour récupérer la date de ses métadonnées.
                    # Donc on vérifie à nouveau ici si la date correspond à ce qu'on veut analyser
                    # if not raa.date:
                    #     os.remove(f'{self.data_dir}/raa/{raa.get_sha256()}.pdf')
                    #     os.remove(f'{self.data_dir}/raa/{raa.get_sha256()}.json')
                    #     logger.error(f'ERREUR: le RAA {raa.name} n\'a pas de date !')
                    #     sys.exit(1)
                    
                    #     date_str = raa.date.strftime("%d/%m/%Y")
                    #    logger.info(f'Nouveau fichier : {raa.name} ({date_str}). URL : {url}')
                        self.flatten_pdf(raa)
                        self.ocr(raa, True)
                        raa.extract_content(self.data_dir)
                        self.search_keywords(raa, keywords)                        
                    except PdfStreamError as exc:
                        print(f'ATTENTION: le fichier {raa.name} n\'est pas un PDF valide : {exc}')
                        logger.warning(f'ATTENTION: le RAA à l\'adresse {raa.url} n\'est pas valide ! On l\'ignore...')
                        os.remove(f'{self.data_dir}/{raa.name_of_ppri}/{raa.get_sha256()}.pdf')
                        os.remove(f'{self.data_dir}/{raa.name_of_ppri}/{raa.get_sha256()}.json')
                    except EmptyFileError as exc:
                        print(f'ATTENTION: le fichier {raa.name} est vide : {exc}')
                        logger.warning(f'ATTENTION: le RAA à l\'adresse {raa.url} est vide ! On l\'ignore...')
                        os.remove(f'{self.data_dir}/{raa.name_of_ppri}/{raa.get_sha256()}.pdf')
                        os.remove(f'{self.data_dir}/{raa.name_of_ppri}/{raa.get_sha256()}.json')
            else:
                #self.download_file(raa,True)
                print('Ce document ne nous intérèsse pas, on ne l\'analyse pas')
                # On supprime le fichier de metadonnées puisqu'on ne le parsera pas


    def get_raa(self, page_content):
        logger.error('Cette fonction doit être surchargée')
