from Attrap_prefdpt import Attrap_prefdpt

class Attrap_PPRI_48(Attrap_prefdpt):
    # Configuration de la préfecture
    hostname = 'https://www.lozere.gouv.fr'
    raa_page = f'{hostname}/Actions-de-l-Etat/Environnement-Risques-naturels-et-technologiques/Risques-naturels/Les-plans-de-prevention-des-risques-en-Lozere-PPR/Les-PPR-inondation-approuves'
    full_name = 'Préfecture du Lozère'
    short_code = 'pref48'
    timezone = 'Europe/Paris'

    # Configuration des widgets à analyser
    #year_regex = '(?:(?:[Rr]ecueils{0,1} des [Aa]ctes [Aa]dministratifs de la [Pp]réfecture de l\'Isère[ -]*)|(?:Année ))([0-9]{4})'
    denomation_regex = 'PPRI|PPR|PPRN|PPRi'
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