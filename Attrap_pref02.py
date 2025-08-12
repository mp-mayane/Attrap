from Attrap_prefdpt import Attrap_prefdpt


class Attrap_pref02(Attrap_prefdpt):

    # Configuration de la préfecture
    hostname = 'https://www.aisne.gouv.fr'
    raa_page = f'{hostname}/Publications/Recueil-des-Actes-Administratifs'
    full_name = 'Préfecture de l\'Aisne'
    short_code = 'pref02'
    timezone = 'Europe/Paris'

    # Configuration des widgets à analyser
    Attrap_prefdpt.grey_card['regex']['year'] = 'RAA [Aa]nnée ([0-9]{4})'
