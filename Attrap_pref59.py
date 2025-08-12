from Attrap_prefdpt import Attrap_prefdpt


class Attrap_pref59(Attrap_prefdpt):

    # Configuration de la préfecture
    hostname = 'https://www.nord.gouv.fr'
    raa_page = f'{hostname}/Publications/Recueils-des-actes-administratifs/RAA-du-departement-du-Nord'
    full_name = 'Préfecture du Nord'
    short_code = 'pref59'
    timezone = 'Europe/Paris'

    # Configuration des widgets à analyser
    Attrap_prefdpt.grey_card['regex']['year'] = '([0-9]{4})'
    Attrap_prefdpt.grey_card['regex']['month'] = '([A-Za-zéû]* [0-9]{4})'
    Attrap_prefdpt.grey_card['add_year_to_months'] = True
