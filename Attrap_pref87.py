from Attrap_prefdpt import Attrap_prefdpt


class Attrap_pref87(Attrap_prefdpt):

    # Configuration de la préfecture
    hostname = 'https://www.haute-vienne.gouv.fr'
    raa_page = f'{hostname}/Publications/Recueil-des-actes-administratifs'
    full_name = 'Préfecture de la Haute-Vienne'
    short_code = 'pref87'
    timezone = 'Europe/Paris'

    # Configuration des widgets à analyser
    Attrap_prefdpt.grey_card['regex']['year'] = '([0-9]{4})'
