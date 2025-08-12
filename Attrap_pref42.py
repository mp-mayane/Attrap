from Attrap_prefdpt import Attrap_prefdpt


class Attrap_pref42(Attrap_prefdpt):

    # Configuration de la préfecture
    hostname = 'https://www.loire.gouv.fr'
    raa_page = f'{hostname}/Publications/Publications-legales/Recueil-des-Actes-Administratifs'
    full_name = 'Préfecture de la Loire'
    short_code = 'pref42'
    timezone = 'Europe/Paris'

    # Configuration des widgets à analyser
    Attrap_prefdpt.white_card['regex']['year'] = '([0-9]{4})'
