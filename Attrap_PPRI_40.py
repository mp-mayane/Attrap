from Attrap_prefdpt import Attrap_prefdpt

class Attrap_PPRI_40(Attrap_prefdpt):
    # Configuration de la préfecture
    hostname = 'https://www.landes.gouv.fr'
    raa_page = f'{hostname}/index.php/Actions-de-l-Etat/Eau.-Environnement.-Risques-Naturels-et-Technologiques/Prevention-des-Risques/Plans-de-prevention-des-risques-dans-les-Landes/Les-Plans-de-Prevention-des-Risques-Inondations-PPRI-dans-les-Landes'
    full_name = 'Préfecture des Landes'
    short_code = 'pref40'
    timezone = 'Europe/Paris'

    # Configuration des widgets à analyser
    #year_regex = '(?:(?:[Rr]ecueils{0,1} des [Aa]ctes [Aa]dministratifs de la [Pp]réfecture de l\'Isère[ -]*)|(?:Année ))([0-9]{4})'
    denomation_regex = 'PPRI|PPR|PPRN'
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