from Attrap_prefdpt import Attrap_prefdpt


class Attrap_pref09(Attrap_prefdpt):

    # Configuration de la préfecture
    hostname = 'https://www.ariege.gouv.fr'
    raa_page = f'{hostname}/Publications/Recueil-des-actes-administratifs/Recueils-des-Actes-Administratifs-de-l-Ariege-a-partir-du-28-avril-2015'
    full_name = 'Préfecture de l\'Ariège'
    short_code = 'pref09'
    timezone = 'Europe/Paris'
