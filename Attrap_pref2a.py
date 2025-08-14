from Attrap_prefdpt import Attrap_prefdpt


class Attrap_pref2a(Attrap_prefdpt):

    # Configuration de la préfecture
    hostname = 'https://www.corse-du-sud.gouv.fr'
    raa_page = f'{hostname}/Publications/Recueil-des-actes-administratifs/Recueil-des-actes-administratifs-de-la-prefecture-de-la-Corse-du-Sud'
    full_name = 'Préfecture de la Corse-du-Sud'
    short_code = 'pref2a'
    timezone = 'Europe/Paris'

    # Configuration des widgets à analyser
    Attrap_prefdpt.white_card['regex']['year'] = '([0-9]{4})'
