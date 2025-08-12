from Attrap_prefdpt import Attrap_prefdpt


class Attrap_pref63(Attrap_prefdpt):

    # Configuration de la préfecture
    hostname = 'https://www.puy-de-dome.gouv.fr'
    raa_page = f'{hostname}/Publications/Recueils-des-actes-administratifs/Recueils-des-actes-administratifs-Puy-de-Dome'
    full_name = 'Préfecture du Puy-de-Dôme'
    short_code = 'pref63'
    timezone = 'Europe/Paris'

    # Configuration des widgets à analyser
    Attrap_prefdpt.grey_card['regex']['year'] = '([0-9]{4})'
