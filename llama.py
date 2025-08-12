from transformers import pipeline

pipe = pipeline(
    "text-generation",
    model="gpt2",
    torch_dtype="auto",
    device_map="auto",
)

prompt = """Extract all the name of the communes from the following text inside this json:Le périmètre du présent Plan de Prévention des Risq ues Naturels Prévisibles d'Inondation 
(PPRI) de la "Bourbre Moyenne" correspond à l'intég ralité du territoire des communes de Saint 
Clair de la Tour, la Tour du Pin, Saint Jean de Sou dain, Rochetoirin, Sérézin de la Tour, 
Cessieu, Ruy Montceau, Bourgoin Jallieu, l'Isle d'A beau, Meyrié, Maubec, Vaulx Milieu, 
Saint Marcel Bel Accueil, Frontonas, La Verpillère,  Villefontaine, Saint Quentin Fallavier , 
tel que défini par l'arrêté préfectoral n° 2004-0640 8 du 17 mai 2004 """

outputs = pipe(prompt,max_new_tokens=256)
print(outputs[0]["generated_text"])
