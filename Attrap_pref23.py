from Attrap_prefdpt import Attrap_prefdpt


class Attrap_pref23(Attrap_prefdpt):

    # Configuration de la préfecture
    hostname = 'https://www.creuse.gouv.fr'
    raa_page = f'{hostname}/Publications/Les-Recueils-des-actes-administratifs'
    full_name = 'Préfecture de la Creuse'
    short_code = 'pref23'
    timezone = 'Europe/Paris'

    # Configuration des widgets à analyser
    Attrap_prefdpt.grey_card['regex']['year'] = '(?:Année)(?:[ -])*([0-9]{4})'
