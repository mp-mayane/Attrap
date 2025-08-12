from Attrap_prefdpt import Attrap_prefdpt


class Attrap_pref25(Attrap_prefdpt):

    # Configuration de la préfecture
    hostname = 'https://www.doubs.gouv.fr'
    raa_page = f'{hostname}/Publications/Publications-Legales/Recueil-des-Actes-Administratifs-RAA'
    full_name = 'Préfecture du Doubs'
    short_code = 'pref25'
    timezone = 'Europe/Paris'

    # Configuration des widgets à analyser
    Attrap_prefdpt.grey_card['regex']['year'] = '([0-9]{4})'
    Attrap_prefdpt.grey_card['follow_link_on_unrecognised_date'] = False
