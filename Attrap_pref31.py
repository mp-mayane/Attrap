from Attrap_prefdpt import Attrap_prefdpt


class Attrap_pref31(Attrap_prefdpt):

    # Configuration de la préfecture
    hostname = 'https://www.haute-garonne.gouv.fr'
    raa_page = f'{hostname}/Publications/Recueil-des-Actes-Administratifs/Recueil-des-Actes-Administratifs-Haute-Garonne'
    full_name = 'Préfecture de la Haute-Garonne'
    short_code = 'pref31'
    timezone = 'Europe/Paris'

    # Configuration des widgets à analyser
    Attrap_prefdpt.grey_card['regex']['month'] = '([A-Za-zéû]* [0-9]{4})'
