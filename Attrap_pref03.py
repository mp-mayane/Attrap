from Attrap_prefdpt import Attrap_prefdpt


class Attrap_pref03(Attrap_prefdpt):

    # Configuration de la préfecture
    hostname = 'https://www.allier.gouv.fr'
    raa_page = f'{hostname}/Publications/Recueil-des-actes-administratifs-arretes'
    full_name = 'Préfecture de l\'Allier'
    short_code = 'pref03'
    timezone = 'Europe/Paris'

    # Configuration des widgets à analyser
    Attrap_prefdpt.grey_card['regex']['year'] = '([0-9]{4})'
