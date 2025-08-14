from Attrap_prefdpt import Attrap_prefdpt


class Attrap_pref73(Attrap_prefdpt):

    # Configuration de la préfecture
    hostname = 'https://www.savoie.gouv.fr'
    raa_page = f'{hostname}/Publications/Recueils-hebdomadaires-et-speciaux-des-actes-administratifs'
    full_name = 'Préfecture de Savoie'
    short_code = 'pref73'
    timezone = 'Europe/Paris'

    # Configuration des widgets à analyser
    Attrap_prefdpt.grey_card['regex']['year'] = '([0-9]{4})'
