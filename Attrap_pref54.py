from Attrap_prefdpt import Attrap_prefdpt


class Attrap_pref54(Attrap_prefdpt):

    # Configuration de la préfecture
    hostname = 'https://www.meurthe-et-moselle.gouv.fr'
    raa_page = f'{hostname}/Publications/Recueil-des-actes-administratifs'
    full_name = 'Préfecture de Meurthe-et-Moselle'
    short_code = 'pref54'
    timezone = 'Europe/Paris'

    # Configuration des widgets à analyser
    Attrap_prefdpt.white_card['regex']['year'] = '([0-9]{4})'

    # On ajoute un widget de menu déroulant
    Attrap_prefdpt.select_widgets.append(
        Attrap_prefdpt.DptSelectWidget(
            'menu_deroulant',
            regex='.* du ([0-9]*(?:er|ER)? [A-Za-zéÉûÛ]* [0-9]*)',
            css_path='select#Liste-liste-docs',
            type='year-month-day'
        )
    )
