from Attrap_prefdpt import Attrap_prefdpt


class Attrap_pref33(Attrap_prefdpt):

    # Configuration de la préfecture
    hostname = 'https://www.gironde.gouv.fr'
    raa_page = f'{hostname}/Publications/Recueil-des-Actes-Administratifs'
    full_name = 'Préfecture de la Gironde'
    short_code = 'pref33'
    timezone = 'Europe/Paris'

    # Configuration des widgets à analyser
    Attrap_prefdpt.grey_card['regex']['year'] = 'Recueils{0,1} des [Aa]ctes [Aa]dministratifs de l\'année ([0-9]{4})'
    Attrap_prefdpt.grey_card['regex']['month'] = '([A-Za-zéû]* [0-9]{4})'
    Attrap_prefdpt.grey_card['follow_link_on_unrecognised_date'] = False
