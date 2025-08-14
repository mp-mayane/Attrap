from transformers import CamembertTokenizer, CamembertForTokenClassification, pipeline

class NERPipeline:
    def __init__(self):
        super()
        self.tokenizer = CamembertTokenizer.from_pretrained("Jean-Baptiste/camembert-ner")
        self.model = CamembertForTokenClassification.from_pretrained("Jean-Baptiste/camembert-ner")
        self.pipeline = pipeline("ner",model=self.model,tokenizer=self.tokenizer,aggregation_strategy="simple",use_fast=True,device=0)

    def run(self,Communes: str) -> list[str]:
        resultats = []
        for r in self.pipeline(Communes):
            if r['entity_group'] == 'LOC' and r['score'] >= 0.97:
                resultats.append(r['word'].strip(" "))
        return resultats
