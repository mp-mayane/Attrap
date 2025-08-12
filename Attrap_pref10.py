from Attrap_prefdpt import Attrap_prefdpt


class Attrap_pref10(Attrap_prefdpt):

    # Configuration de la préfecture
    hostname = 'https://www.aube.gouv.fr'
    raa_page = [
        f'{hostname}/Publications/RAA-Recueil-des-Actes-Administratifs',
        f'{hostname}/Publications/RAA-Recueil-des-Actes-Administratifs/RAA-Archives'
    ]

    full_name = 'Préfecture de l\'Aube'
    short_code = 'pref10'
    timezone = 'Europe/Paris'

    # Configuration des widgets à analyser
    Attrap_prefdpt.grey_card['regex']['year'] = 'RAA *([0-9]{4})'

    # On ajoute un widget custom représentant les liens sur la page d'accueil
    Attrap_prefdpt.widgets.append(
        Attrap_prefdpt.DptWidget(
            'homepage_links',
            regex={'year': 'Année *([0-9]{4})'},
            css_path={'title': 'div.fr-text--lead p a.fr-link'}
        )
    )
