from Attrap_prefdpt import Attrap_prefdpt


class Attrap_pref76(Attrap_prefdpt):

    # Configuration de la préfecture
    hostname = 'https://www.seine-maritime.gouv.fr'
    raa_page = f'{hostname}/Publications/Recueils-des-actes-administratifs-RAA'
    full_name = 'Préfecture de la Seine-Maritime'
    short_code = 'pref76'
    timezone = 'Europe/Paris'

    # Configuration des widgets à analyser
    Attrap_prefdpt.grey_card['regex']['year'] = '([0-9]{4})'
    Attrap_prefdpt.grey_card['regex']['month'] = '([A-Za-zéû]* [0-9]{4})'
    Attrap_prefdpt.grey_card['follow_link_on_unrecognised_date'] = False
