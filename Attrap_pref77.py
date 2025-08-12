from Attrap_prefdpt import Attrap_prefdpt


class Attrap_pref77(Attrap_prefdpt):

    # Configuration de la préfecture
    hostname = 'https://www.seine-et-marne.gouv.fr'
    raa_page = f'{hostname}/Publications/RECUEILS-DES-ACTES-ADMINISTRATIFS-RAA'
    full_name = 'Préfecture de Seine-et-Marne'
    short_code = 'pref77'
    timezone = 'Europe/Paris'

    # Configuration des widgets à analyser
    Attrap_prefdpt.white_card['regex']['year'] = 'RAA ([0-9]{4})'

    # On ajoute un widget de menu déroulant
    Attrap_prefdpt.select_widgets.append(
        Attrap_prefdpt.DptSelectWidget(
            'menu_deroulant',
            regex='D77-([0-9]{2}-[0-9]{2}-[0-9]{4})',
            css_path='select#Liste-liste-docs',
            type='year-month-day'
        )
    )
