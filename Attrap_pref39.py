from Attrap_prefdpt import Attrap_prefdpt


class Attrap_pref39(Attrap_prefdpt):

    # Configuration de la préfecture
    hostname = "https://www.jura.gouv.fr"
    raa_page = f'{hostname}/Publications/Publications-legales/Recueil-des-Actes-Administratifs'
    full_name = "Préfecture du Jura"
    short_code = "pref39"
    timezone = 'Europe/Paris'

    # Configuration des widgets à analyser
    Attrap_prefdpt.grey_card['regex']['year'] = 'Année ([0-9]{4})'
