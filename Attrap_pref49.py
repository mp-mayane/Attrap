from Attrap_prefdpt import Attrap_prefdpt


class Attrap_pref49(Attrap_prefdpt):

    # Configuration de la préfecture
    hostname = 'https://www.maine-et-loire.gouv.fr'
    raa_page = f'{hostname}/Publications/Recueil-des-Actes-Administratifs'
    full_name = 'Préfecture de Maine-et-Loire'
    short_code = 'pref49'
    timezone = 'Europe/Paris'

    # Configuration des widgets à analyser
    Attrap_prefdpt.grey_card['regex']['year'] = '.*([0-9]{4})'
