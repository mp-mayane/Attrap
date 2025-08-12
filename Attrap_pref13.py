from Attrap_prefdpt import Attrap_prefdpt


class Attrap_pref13(Attrap_prefdpt):

    # Configuration de la préfecture
    hostname = 'https://www.bouches-du-rhone.gouv.fr'
    raa_page = [
        f'{hostname}/Publications/RAA-et-Archives',
        f'{hostname}/Publications/RAA-et-Archives/Archives-RAA-des-Bouches-du-Rhone'
    ]
    full_name = 'Préfecture des Bouches-du-Rhône'
    short_code = 'pref13'
    timezone = 'Europe/Paris'

    # Configuration des widgets à analyser
    Attrap_prefdpt.grey_card['regex']['year'] = 'RAA[- ]*([0-9]{4})'
    Attrap_prefdpt.grey_card['follow_link_on_unrecognised_date'] = False
