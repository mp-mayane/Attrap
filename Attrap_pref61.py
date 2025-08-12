from Attrap_prefdpt import Attrap_prefdpt


class Attrap_pref61(Attrap_prefdpt):

    # Configuration de la préfecture
    hostname = 'https://www.orne.gouv.fr'
    raa_page = f'{hostname}/Publications/Recueil-des-Actes-Administratifs-RAA/Recueil-des-Actes-Administratifs-RAA'
    full_name = 'Préfecture de l\'Orne'
    short_code = 'pref61'
    timezone = 'Europe/Paris'

    # Configuration des widgets à analyser
    Attrap_prefdpt.grey_card['regex']['year'] = 'Le Recueil des actes administratifs ([0-9]{4})'
    Attrap_prefdpt.grey_card['regex']['month'] = '([A-Za-zéû]* [0-9]{4})'
    Attrap_prefdpt.grey_card['add_year_to_months'] = True
    Attrap_prefdpt.white_card['regex']['month'] = '([A-Za-zéû]* [0-9]{4})'
    Attrap_prefdpt.white_card['add_year_to_months'] = True
