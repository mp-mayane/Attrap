#!/usr/bin/env python3

import os
import argparse
import logging
import datetime
import dateparser
import importlib
import json

from Attrap import Attrap
# Config
__KEYWORDS = os.getenv('KEYWORDS') or ''
__DATA_DIR_ROOT = os.path.dirname(os.path.abspath(__file__)) + '/data/'
__DOWNLOAD = False

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
    'PPRI_01','PPRI_02','PPRI_2A','PPRI_2B','PPRI_03','PPRI_04','PPRI_05','PPRI_06','PPRI_07','PPRI_08','PPRI_09',
    'PPRI_10','PPRI_11','PPRI_12','PPRI_13','PPRI_14','PPRI_15','PPRI_16','PPRI_17','PPRI_18','PPRI_19',
    'PPRI_20','PPRI_21','PPRI_22','PPRI_23','PPRI_24','PPRI_25','PPRI_26','PPRI_27','PPRI_28','PPRI_29',
    'PPRI_30','PPRI_31','PPRI_32','PPRI_33','PPRI_34','PPRI_35','PPRI_36','PPRI_37','PPRI_38','PPRI_39',
    'PPRI_40','PPRI_41','PPRI_42','PPRI_43','PPRI_44','PPRI_45','PPRI_46','PPRI_47','PPRI_48','PPRI_49',
    'PPRI_50','PPRI_51','PPRI_52','PPRI_53','PPRI_54','PPRI_55','PPRI_56','PPRI_57','PPRI_58','PPRI_59',
    'PPRI_60','PPRI_61','PPRI_62','PPRI_63','PPRI_64','PPRI_65','PPRI_66','PPRI_67','PPRI_68','PPRI_69',
    'PPRI_70','PPRI_71','PPRI_72','PPRI_73','PPRI_74','PPRI_75','PPRI_76','PPRI_77','PPRI_78','PPRI_79',
    'PPRI_80','PPRI_81','PPRI_82','PPRI_83','PPRI_84','PPRI_85','PPRI_86','PPRI_87','PPRI_88','PPRI_89',
    'PPRI_90','PPRI_91','PPRI_92','PPRI_93','PPRI_94','PPRI_95','PPRI_971','PPRI_972','PPRI_973','PPRI_974','PPRI_976',
]

# Début du script
parser = argparse.ArgumentParser(
    prog='__init__.py',
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
    '-d',
    '--download_files',
    action='store',
    default=False,
    help='Si précisé, télécharge les fichiers PDF (Désactivé par défaut)',
)

# parser.add_argument(
#     '--not-before',
#     action='store',
#     help='n\'analyse pas les RAA datant d\'avant la date indiquée, au format YYYY-MM-DD (par défaut : 2024-01-01)'
# )
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
if args.download_files:
    __DOWNLOAD = True

# if args.not_before:
#     try:
#         relative_date = dateparser.parse(args.not_before)
#         __NOT_BEFORE = datetime.datetime(year=relative_date.year, month=relative_date.month, day=relative_date.day)
#     except Exception as exc:
#         __NOT_BEFORE = datetime.datetime.strptime(args.not_before, '%Y-%m-%d')

__DATA_DIR = f'{__DATA_DIR_ROOT}{args.administration}/PPRI'

module = importlib.import_module(f'Attrap_{args.administration}')
attrap = getattr(module, f'Attrap_{args.administration}')(__DATA_DIR)

attrap.not_before = __NOT_BEFORE
attrap.get_raa(__KEYWORDS,__DOWNLOAD)
