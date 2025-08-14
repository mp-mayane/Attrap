from Attrap_prefdpt import Attrap_prefdpt


class Attrap_pref74(Attrap_prefdpt):

    # Configuration de la préfecture
    hostname = 'https://www.haute-savoie.gouv.fr'
    raa_page = f'{hostname}/Publications/Actes-administratifs'
    full_name = 'Préfecture de la Haute-Savoie'
    short_code = 'pref74'
    timezone = 'Europe/Paris'

    # Configuration des widgets à analyser
    Attrap_prefdpt.grey_card['regex']['year'] = '([0-9]{4})'
