from Attrap_prefdpt import Attrap_prefdpt

class Attrap_PPRI_05(Attrap_prefdpt):
    # Configuration de la préfecture
    hostname = 'https://www.hautes-alpes.gouv.fr'
    raa_page = f'{hostname}/Actions-de-l-Etat/Environnement-bruit-risques-naturels-et-technologiques/Risques-naturels-et-technologiques/Risques-naturels/Plans-de-Prevention-des-Risques-Naturels-PPRN/PPR-Approuve'
    full_name = 'Préfecture des Hautes-Alpes'
    short_code = 'pref05'
    timezone = 'Europe/Paris'

    def __init__(self):
        super().__init__()

    def send_data_to_attrap():
        super().fetch_name_of_PPRI()

    # Configuration des widgets à analyser
    #year_regex = '(?:(?:[Rr]ecueils{0,1} des [Aa]ctes [Aa]dministratifs de la [Pp]réfecture de l\'Isère[ -]*)|(?:Année ))([0-9]{4})'
    denomation_regex = 'PPRI|PPRL|PPRN'
    Attrap_prefdpt.grey_card['regex']['denomination'] = denomation_regex
    Attrap_prefdpt.white_card['regex']['denomination'] = denomation_regex
    Attrap_prefdpt.white_card['exclude'] = ['Vous recherchez "Le Journal officiel de la République française" ?']
    Attrap_prefdpt.nom_des_rglts = r'\b(R[èe]glement|Rglt)\b'

    # On ajoute un widget de menu déroulant
    Attrap_prefdpt.select_widgets.append(
        Attrap_prefdpt.DptSelectWidget(
            'menu_deroulant',
            regex='([0-9]{1,2}[er]{0,1} [a-zéû]* [0-9]{4})',
            css_path='select#-liste-docs',
            type='year-month-day'
        )
    )

    