from Attrap_prefdpt import Attrap_prefdpt


class Attrap_pref44(Attrap_prefdpt):

    # Configuration de la préfecture
    hostname = 'https://www.loire-atlantique.gouv.fr'
    raa_page = f'{hostname}/Publications/Recueil-des-actes-administratifs-RAA-en-Loire-Atlantique'
    full_name = 'Préfecture de la Loire-Atlantique'
    short_code = 'pref44'
    timezone = 'Europe/Paris'

    # Configuration des widgets à analyser
    Attrap_prefdpt.grey_card['regex']['year'] = '([0-9]{4})'
    Attrap_prefdpt.grey_card['regex']['month'] = '([A-Za-zéû]* [0-9]{4})'
    Attrap_prefdpt.grey_card['add_year_to_months'] = True
