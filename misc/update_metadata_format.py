#!/usr/bin/env python3

import argparse
import datetime
import io
import json
import os
import pytz
import sys
import re
import requests

sys.path.append(os.path.dirname(__file__) + '/../')
from Attrap_pref976 import Attrap_pref976
from Attrap import Attrap

from pypdf import PdfReader

tz_paris = pytz.timezone('Europe/Paris')
session = requests.Session()


def fix_raa_date_v0(raa_json):
    try:
        raa_json['date'] = tz_paris.localize(datetime.datetime.strptime(raa_json['date'], '%d/%m/%Y')).strftime('%Y-%m-%d')
        return raa_json
    except Exception:
        print(f"\033[91m{exc=}, {type(exc)=}\033[0m")
        sys.exit(1)
        return raa_json


def fix_pdf_date_v0(raa_json, json_key):
    if not raa_json[json_key]:
        return raa_json

    try:
        # On tente de parser avec fuseau horaire
        raa_json[json_key] = datetime.datetime.strptime(raa_json[json_key], '%d/%m/%Y %H:%M:%S%z').astimezone(pytz.utc).isoformat(timespec="seconds")
        return raa_json
    except Exception:
        try:
            # Sinon on tente de parser sans fuseau horaire et on retourne une date avec le fuseau de Paris
            raa_json[json_key] = tz_paris.localize(datetime.datetime.strptime(raa_json[json_key], '%d/%m/%Y %H:%M:%S')).astimezone(pytz.utc).isoformat(timespec="seconds")
            return raa_json
        except Exception as exc:
            print(f"\033[91m{exc=}, {type(exc)=}\033[0m")
            sys.exit(1)
            return raa_json


def fix_json(raa_json, raa_id, administration):
    version = raa_json.get('version')

    match version:
        # Si le fichier de métadonnées n'a pas de version, il a été généré avant le 14/11/2024 et doit être corrigé
        # v0 -> v1 : les dates sont au format YYYY-MM-DD et heure locale
        #            les heures sont au format YYYY-MM-DD HH:mm:ss±ZZ:ZZ et heure UTC
        case None:
            print(f"{raa_id}: v0 -> v1")
            date = raa_json['date']
            first_seen_on = raa_json['first_seen_on']
            pdf_creation_date = raa_json['pdf_creation_date']
            pdf_modification_date = raa_json['pdf_modification_date']

            print(f"{administration}: {raa_json['name']} ({raa_id}):")

            fixed_raa_json = fix_raa_date_v0(raa_json)
            if not date == fixed_raa_json['date']:
                print(f"    date: {date} -> {fixed_raa_json['date']}")

            fixed_raa_json = fix_pdf_date_v0(fixed_raa_json, 'first_seen_on')
            if not raa_json == fixed_raa_json:
                print(f"    first_seen_on: {first_seen_on} -> {fixed_raa_json['first_seen_on']}")

            fixed_raa_json = fix_pdf_date_v0(fixed_raa_json, 'pdf_creation_date')
            if not pdf_creation_date == fixed_raa_json['pdf_creation_date']:
                print(f"    pdf_creation_date: {pdf_creation_date} -> {fixed_raa_json['pdf_creation_date']}")

            fixed_raa_json = fix_pdf_date_v0(fixed_raa_json, 'pdf_modification_date')
            if not pdf_modification_date == fixed_raa_json['pdf_modification_date']:
                print(f"    pdf_modification_date: {pdf_modification_date} -> {fixed_raa_json['pdf_modification_date']}")

            ordered_fixed_raa_json = {'version': 1}
            for key in fixed_raa_json:
                ordered_fixed_raa_json[key] = fixed_raa_json[key]

            fixed_raa_json = ordered_fixed_raa_json
            return fix_json(fixed_raa_json, raa_id, administration)

        # Si le fichier de métadonnées est en version 1, il ne contient pas le fuseau horaire de l'administration.
        # v1 -> v2: ajout du fuseau horaire (Europe/Paris sauf Mayotte Indian/Mayotte)
        case 1:
            print(f"{raa_id}: v1 -> v2")
            if administration == 'pref976':
                print('    Téléchargement du RAA pour recalculer les dates avec le fuseau horaire de Mayotte')
                # Il faut retélécharger le RAA pour vérifier que les heures sont dans le bon fuseau
                session.headers.update({'User-Agent': Attrap_pref976.user_agent})
                pdf_resource = session.get(raa_json['url'], timeout=(10, 120), stream=True)
                pdf = io.BytesIO(pdf_resource.content)
                reader = PdfReader(pdf)
                pdf_metadata = reader.metadata

                if pdf_metadata:
                    if pdf_metadata.creation_date:
                        pdf_creation_date = Attrap.get_aware_datetime(pdf_metadata.creation_date, timezone=Attrap_pref976.timezone)
                        raa_json['pdf_creation_date'] = pdf_creation_date.astimezone(pytz.utc).isoformat(timespec="seconds")
                    if pdf_metadata.modification_date:
                        pdf_modification_date = Attrap.get_aware_datetime(pdf_metadata.modification_date, timezone=Attrap_pref976.timezone)
                        raa_json['pdf_modification_date'] = pdf_modification_date.astimezone(pytz.utc).isoformat(timespec="seconds")

            print('    Ajout du fuseau horaire')
            if administration == 'pref976':
                raa_json['timezone'] = Attrap_pref976.timezone
            else:
                raa_json['timezone'] = 'Europe/Paris'
            raa_json['version'] = 2
            return fix_json(raa_json, raa_id, administration)

        case 2:
            return raa_json

        case _:
            print(f'Version inconnue : {version}')
            sys.exit(1)


parser = argparse.ArgumentParser(
    prog='./misc/update_metadata_format.py',
    description='Met à jour le format des fichiers de métadonnées'
)

parser.add_argument(
    '--data-dir',
    action='store',
    help='dossier de données (par défaut: data/)'
)

parser.add_argument(
    '--dry-run',
    action='store_true',
    help='ne modifie aucun fichier, affiche seulement les modifications nécessaires (par défaut: false)'
)

args = parser.parse_args()

if args.data_dir:
    data_dir = args.data_dir
else:
    data_dir = 'data/'
dry_run = args.dry_run

if data_dir.startswith('/'):
    data_dir = os.path.abspath(data_dir)
else:
    data_dir = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + '/../' + data_dir)

for administration in os.listdir(data_dir):
    # On ne cherche que les dossiers ppparis et pref*
    if administration.startswith('pref') or administration == 'ppparis':
        administration_path = os.path.abspath(data_dir + '/' + administration + '/raa/')
        for raa in os.listdir(administration_path):
            if raa.endswith('.json'):
                raa_id = re.sub('\\.json$', '', raa)
                fixed = False

                raa_path = os.path.abspath(administration_path + '/' + raa)
                raa_file_read = open(raa_path, 'r')
                raa_json = json.load(raa_file_read)
                raa_file_read.close()

                version = raa_json.get('version')
                if version != 2:
                    fixed_raa_json = fix_json(raa_json, raa_id, administration)

                    if not dry_run:
                        raa_file_write = open(raa_path, 'w')
                        raa_file_write.write(json.dumps(fixed_raa_json))
                        raa_file_write.close()
    else:
        print(f'On ignore {administration}...')
