from Attrap_prefdpt import Attrap_prefdpt


class Attrap_pref62(Attrap_prefdpt):

    # Config
    hostname = 'https://www.pas-de-calais.gouv.fr'
    raa_page = f'{hostname}/Publications/Recueil-des-actes-administratifs'
    full_name = 'Préfecture du Pas-de-Calais'
    short_code = 'pref62'
    timezone = 'Europe/Paris'

    # Configuration des widgets à analyser
    Attrap_prefdpt.white_card['regex']['year'] = '([0-9]{4})'
