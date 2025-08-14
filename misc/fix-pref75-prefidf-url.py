#!/usr/bin/env python3

import argparse
import json
import os
import re

from urllib.parse import unquote

import hashlib

parser = argparse.ArgumentParser(
    prog='./misc/fix-pref75-prefidf-url.py',
    description='Met à jour les URL des RAA de Paris et d\'Idf'
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
    # On ne cherche que les dossiers prefidf et pref75
    if administration == 'prefidf' or administration == 'pref75':
        administration_path = os.path.abspath(data_dir + '/' + administration + '/raa/')
        for raa in os.listdir(administration_path):
            if raa.endswith('.json'):
                raa_id = re.sub('\\.json$', '', raa)
                fixed = False

                raa_path = os.path.abspath(administration_path + '/' + raa)
                txt_path = re.sub('\\.json$', '.txt', raa_path)
                raa_file_read = open(raa_path, 'r')
                raa_json = json.load(raa_file_read)
                raa_file_read.close()

                url = raa_json.get('url')
                if url.startswith('https://www.prefectures-regions.gouv.fr/ile-de-france/ile-de-france/ile-de-france/irecontenu/telechargement/'):
                    raa_json['url'] = url.replace('https://www.prefectures-regions.gouv.fr/ile-de-france/ile-de-france/ile-de-france/irecontenu/telechargement/', 'https://www.prefectures-regions.gouv.fr/ile-de-france/irecontenu/telechargement/')
                    fixed_raa_json = {}
                    for key in raa_json:
                        fixed_raa_json[key] = raa_json[key]
                    fixed_raa_id = hashlib.sha256(unquote(raa_json['url']).encode('utf-8')).hexdigest()
                    fixed_raa_path = raa_path.replace(raa_id, fixed_raa_id)
                    fixed_txt_path = txt_path.replace(raa_id, fixed_raa_id)

                    print(f'{raa_id} -> {fixed_raa_id}:')
                    print(f"    {raa_json['url']}")
                    print('')

                    if not dry_run:
                        raa_file_write = open(fixed_raa_path, 'w')
                        raa_file_write.write(json.dumps(fixed_raa_json))
                        raa_file_write.close()
                        os.remove(raa_path)
                        os.rename(txt_path, fixed_txt_path)
