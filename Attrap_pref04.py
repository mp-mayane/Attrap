from Attrap_prefdpt import Attrap_prefdpt


class Attrap_pref04(Attrap_prefdpt):

    # Configuration de la préfecture
    hostname = 'https://www.alpes-de-haute-provence.gouv.fr'
    raa_page = f'{hostname}/Publications/Publications-administratives-et-legales/Recueil-des-Actes-Administratifs'
    full_name = 'Préfecture des Alpes-de-Haute-Provence'
    short_code = 'pref04'
    timezone = 'Europe/Paris'

    # Configuration des widgets à analyser
    Attrap_prefdpt.grey_card['regex']['year'] = '([0-9]{4})'
