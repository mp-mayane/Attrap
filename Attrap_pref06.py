from Attrap_prefdpt import Attrap_prefdpt


class Attrap_pref06(Attrap_prefdpt):

    # Configuration de la préfecture
    hostname = 'https://www.alpes-maritimes.gouv.fr'
    raa_page = f'{hostname}/Publications/Recueil-des-actes-administratifs-RAA'
    full_name = 'Préfecture des Alpes-Maritimes'
    short_code = 'pref06'
    timezone = 'Europe/Paris'

    # Configuration des widgets à analyser
    Attrap_prefdpt.grey_card['regex']['year'] = 'Année *([0-9]{4})'
