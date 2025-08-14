from CamemBERT import NERPipeline

ner = NERPipeline()
# r = ner.run("""RÉPUBLIQUE FRANÇAISECT
# PRÉFET DE L'ISÈRE kLionel BEFFRE
# PLAN DE PRÉVENTION DU RISQUEINONDATION DE LA ROMANCHE AVAL
# Communes de Saint Barthélémy de Séchilienne, Séchilienne, Saint Pierre de Mésage,Notre Dame de Mésage, Montchaboud, Vizille, Champ sur Drac et Jarrie.
# Modification n°1
# Règlement
# DOSSIER D'APPROBATION de la MODIFICATION
# Juillet 2020
# Direction Départementale des Territoires - Service Sécurité et Risques
# Modification n°1 du PPRI Romanche aval approuvé le 5 juillet 2012 1""")  # Example usage
# print(r)
import regex as re

with open('./data/PPRI_38/raa/03 - PPRI BOURBRE MOYENNE/Règlement.txt',encoding="utf-8") as txt:
    communes = re.compile(r'communes', re.IGNORECASE | re.MULTILINE)

    lines = txt.read().splitlines()

    for i, line in enumerate(lines):
        if communes.search(line):
            snippet = " ".join(lines[max(0, i - 2):min(len(lines), i + 5)])
            break
print(snippet)
print('\n\n\n\n Regardez Camembert')
print(ner.run(snippet))           
