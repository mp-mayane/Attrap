from Attrap_prefdpt import Attrap_prefdpt


class Attrap_pref11(Attrap_prefdpt):

    # Configuration de la préfecture
    hostname = 'https://www.aude.gouv.fr'
    raa_page = f'{hostname}/Publications/Recueil-des-Actes-Administratifs-RAA'
    full_name = 'Préfecture de l\'Aude'
    short_code = 'pref11'
    timezone = 'Europe/Paris'

    # Configuration des widgets à analyser
    Attrap_prefdpt.grey_card['regex']['year'] = 'Année *([0-9]{4})'
