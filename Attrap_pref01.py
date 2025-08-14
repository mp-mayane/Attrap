from Attrap_prefdpt import Attrap_prefdpt


class Attrap_pref01(Attrap_prefdpt):

    # Configuration de la préfecture
    hostname = 'https://www.ain.gouv.fr'
    raa_page = f'{hostname}/Publications/Recueil-des-actes-administratifs-RAA'
    full_name = 'Préfecture de l\'Ain'
    short_code = 'pref01'
    timezone = 'Europe/Paris'

    # Configuration des widgets à analyser
    Attrap_prefdpt.grey_card['regex']['year'] = '(?:Recueil|Recueils) (?:des actes administratifs)(?:[ -])*([0-9]{4})'
