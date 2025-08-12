from Attrap_prefdpt import Attrap_prefdpt


class Attrap_pref05(Attrap_prefdpt):

    # Configuration de la préfecture
    hostname = 'https://www.hautes-alpes.gouv.fr'
    raa_page = f'{hostname}/Publications/Recueil-des-actes-administratifs'
    full_name = 'Préfecture des Hautes-Alpes'
    short_code = 'pref05'
    timezone = 'Europe/Paris'

    # Configuration des widgets à analyser
    Attrap_prefdpt.grey_card['regex']['year'] = 'Année *([0-9]{4})'
    Attrap_prefdpt.grey_card['regex']['month'] = '([A-Za-zéû]* *[0-9]{4})'
