#!/usr/bin/env python3

import os
import argparse
import logging
import datetime
import dateparser
import importlib

from Attrap import Attrap

# Config
__KEYWORDS = os.getenv('KEYWORDS') or ''
__DATA_DIR_ROOT = os.path.dirname(os.path.abspath(__file__)) + '/data/'

if os.getenv('NOT_BEFORE'):
    try:
        relative_date = dateparser.parse(os.getenv('NOT_BEFORE'))
        __NOT_BEFORE = datetime.datetime(year=relative_date.year, month=relative_date.month, day=relative_date.day)
    except Exception as exc:
        __NOT_BEFORE = datetime.datetime.strptime(
            os.getenv('NOT_BEFORE'), '%Y-%m-%d'
        )
else:
    __NOT_BEFORE = datetime.datetime(2025, 1, 1)

# Liste des administrations supportées
available_administrations = [
    'PPRI_38',
]

# Début du script
parser = argparse.ArgumentParser(
    prog='cli.py',
    description='Télécharge les PPRI d\'une Préfécture donnée, recherche la date de publication et de modification, les communes et des mots-clés'
)
parser.add_argument(
    'administration',
    action='store',
    help='Identifiant de l\'administration',
    choices=available_administrations
)
parser.add_argument(
    '-k',
    '--keywords',
    action='store',
    default="PPRI",
    help='liste des termes recherchés, séparés par une virgule (PPRI par défaut)'
)
parser.add_argument(
    '--not-before',
    action='store',
    help='n\'analyse pas les RAA datant d\'avant la date indiquée, au format YYYY-MM-DD (par défaut : 2024-01-01)'
)
parser.add_argument(
    '-v',
    action='store_true',
    help='relève le niveau de verbosité à INFO'
)
parser.add_argument(
    '-vv',
    action='store_true',
    help='relève le niveau de verbosité à DEBUG'
)
args = parser.parse_args()

if (args.v or os.getenv('VERBOSE')) and not args.vv and not os.getenv('VVERBOSE'):
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("stem").setLevel(logging.WARNING)

if args.vv or os.getenv('VVERBOSE'):
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger("stem").setLevel(logging.WARNING)

if args.keywords:
    __KEYWORDS = args.keywords

# if args.not_before:
#     try:
#         relative_date = dateparser.parse(args.not_before)
#         __NOT_BEFORE = datetime.datetime(year=relative_date.year, month=relative_date.month, day=relative_date.day)
#     except Exception as exc:
#         __NOT_BEFORE = datetime.datetime.strptime(args.not_before, '%Y-%m-%d')

__DATA_DIR = f'{__DATA_DIR_ROOT}{args.administration}/raa'

module = importlib.import_module(f'Attrap_{args.administration}')
attrap = getattr(module, f'Attrap_{args.administration}')(__DATA_DIR)

attrap.not_before = __NOT_BEFORE
attrap.get_raa(__KEYWORDS)
