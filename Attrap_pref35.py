from Attrap_prefdpt import Attrap_prefdpt


class Attrap_pref35(Attrap_prefdpt):

    # Configuration de la préfecture
    hostname = 'https://www.ille-et-vilaine.gouv.fr'
    raa_page = f'{hostname}/Publications/Recueil-des-actes-administratifs'
    full_name = 'Préfecture d\'Ille-et-Vilaine'
    short_code = 'pref35'
    timezone = 'Europe/Paris'

    # Configuration des widgets à analyser
    year_regex = 'Recueil des actes administratifs ([0-9]{4})'
    Attrap_prefdpt.white_card['regex']['year'] = year_regex

    # On ajoute un widget de menu déroulant
    Attrap_prefdpt.select_widgets.append(
        Attrap_prefdpt.DptSelectWidget(
            'menu_deroulant',
            regex=year_regex,
            css_path='div.fr-select-group select#Archives-des-RAA-liste-docs.fr-select',
            type='year'
        )
    )
