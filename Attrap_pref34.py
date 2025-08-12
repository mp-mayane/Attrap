from Attrap_prefdpt import Attrap_prefdpt


class Attrap_pref34(Attrap_prefdpt):

    # Configuration de la préfecture
    hostname = 'https://www.herault.gouv.fr'
    raa_page = f'{hostname}/Publications/Recueils-des-actes-administratifs'
    full_name = 'Préfecture de l\'Hérault'
    short_code = 'pref34'
    timezone = 'Europe/Paris'

    # Configuration des widgets à analyser
    year_regex = '(?:(?:Recueil des actes administratifs)|(?:Année))[ -]([0-9]{4})'
    Attrap_prefdpt.white_card['regex']['year'] = year_regex
    Attrap_prefdpt.grey_card['regex']['year'] = year_regex
