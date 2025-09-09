from Attrap_prefdpt import Attrap_prefdpt

class Attrap_PPRI_03(Attrap_prefdpt):
    # Configuration de la préfecture
    hostname = 'https://www.allier.gouv.fr'
    raa_page = f'{hostname}/Actions-de-l-Etat/Risques-naturels-et-technologiques/Plans-de-Prevention-des-Risques-Naturels-et-Technologiques/PPR-naturels-et-technologiques-approuves-selectionner-la-lettre-correspondant-a-la-commune-recherchee/%28namefilter%29/B?utm_'
    full_name = 'Préfecture de l\'Allier'
    short_code = 'pref03'
    timezone = 'Europe/Paris'

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