from Attrap_prefdpt import Attrap_prefdpt


class Attrap_pref30(Attrap_prefdpt):

    # Configuration de la préfecture
    hostname = 'https://www.gard.gouv.fr'
    raa_page = f'{hostname}/Publications/Recueil-des-Actes-Administratifs'
    full_name = 'Préfecture du Gard'
    short_code = 'pref30'
    timezone = 'Europe/Paris'

    # Configuration des widgets à analyser
    Attrap_prefdpt.grey_card['regex']['year'] = '([0-9]{4})'
