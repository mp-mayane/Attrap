from Attrap_prefdpt import Attrap_prefdpt


class Attrap_pref2b(Attrap_prefdpt):

    # Configuration de la préfecture
    hostname = 'https://www.haute-corse.gouv.fr'
    raa_page = f'{hostname}/Publications/Publications-administratives-et-legales/Recueils-des-actes-administratifs'
    full_name = 'Préfecture de Haute-Corse'
    short_code = 'pref2b'
    timezone = 'Europe/Paris'

    # Configuration des widgets à analyser
    Attrap_prefdpt.grey_card['regex']['year'] = 'Recueils des actes administratifs ([0-9]{4})'
    Attrap_prefdpt.white_card['regex']['month'] = '([A-Za-zéû]* [0-9]{4})'
