from transformers import CamembertTokenizer, CamembertForTokenClassification, pipeline,AutoTokenizer, AutoModelForSeq2SeqLM
import torch

class NERPipeline:
    def __init__(self):
        self.tokenizer = CamembertTokenizer.from_pretrained("Jean-Baptiste/camembert-ner")
        self.model = CamembertForTokenClassification.from_pretrained("Jean-Baptiste/camembert-ner")
        self.pipeline = pipeline("ner",model=self.model,tokenizer=self.tokenizer,aggregation_strategy="simple",use_fast=True,device= 0 if torch.cuda.is_available() else -1)

        self.summarizer_tokenizer = AutoTokenizer.from_pretrained("moussaKam/barthez-orangesum-abstract")
        self.summarizer_model = AutoModelForSeq2SeqLM.from_pretrained("moussaKam/barthez-orangesum-abstract")
        self.pipeline_for_summary = pipeline(
            "summarization",
            model=self.summarizer_model,
            tokenizer=self.summarizer_tokenizer,
            device=0 if torch.cuda.is_available() else -1
        )

    def run(self,Communes: str) -> list[str]:
        resultats = []
        for r in self.pipeline(Communes):
            if r['entity_group'] == 'LOC' and r['score'] >= 0.97:
                resultats.append(r['word'].strip(" "))
        return resultats

    def summarize(self, text:str) -> str:
        result = self.pipeline_for_summary(text, do_sample=False)
        return result[0]['summary_text']