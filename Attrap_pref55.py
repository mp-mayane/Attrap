from Attrap_prefdpt import Attrap_prefdpt


class Attrap_pref55(Attrap_prefdpt):

    # Configuration de la préfecture
    hostname = 'https://www.meuse.gouv.fr'
    raa_page = f'{hostname}/Publications/Recueil-des-Actes-Administratifs-RAA'
    full_name = 'Préfecture de la Meuse'
    short_code = 'pref55'
    timezone = 'Europe/Paris'

    # On configure le widget de menu déroulant
    Attrap_prefdpt.select_widgets.append(
        Attrap_prefdpt.DptSelectWidget(
            'menu_deroulant',
            regex='RAA année ([0-9]{4})',
            css_path='select#Liste-des-recueils-liste-docs',
            type='year'
        )
    )
