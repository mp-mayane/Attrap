from Attrap_prefdpt import Attrap_prefdpt


class Attrap_pref52(Attrap_prefdpt):

    # Configuration de la préfecture
    hostname = 'https://www.haute-marne.gouv.fr'
    raa_page = f'{hostname}/Publications/Recueil-des-Actes-Administratifs-RAA'
    full_name = 'Préfecture de la Haute-Marne'
    short_code = 'pref52'
    timezone = 'Europe/Paris'

    # Configuration des widgets à analyser
    Attrap_prefdpt.white_card['regex']['year'] = 'Année ([0-9]{4})'
