from Attrap_prefdpt import Attrap_prefdpt


class Attrap_pref29(Attrap_prefdpt):

    # Configuration de la préfecture
    hostname = 'https://www.finistere.gouv.fr'
    raa_page = f'{hostname}/Publications/Recueil-des-actes-administratifs'
    full_name = 'Préfecture du Finistère'
    short_code = 'pref29'
    timezone = 'Europe/Paris'

    # Configuration des widgets à analyser
    Attrap_prefdpt.grey_card['regex']['year'] = '(?:Recueils publiés en ).*([0-9]{4})'
