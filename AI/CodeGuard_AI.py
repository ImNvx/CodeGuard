import torch
from transformers import AutoTokenizer
from .CodeGuard_Network import CodeGuardEncoder
import torch.nn.functional as F

class CodeGuard(): # am facut clasa pana la urma ca daca era functie simpla trebuia sa dai load la model de mai multe ori si e mai elegant asa
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("AI/CodeGuard_tokenizer")
        self.model = CodeGuardEncoder(vocab_size=self.tokenizer.vocab_size)
        self.model.load_state_dict(torch.load("AI/CodeGuard.pth"), map_location=torch.device('cpu'))

    def checkSubmission(self, previous_submissions, current_submission):
        with torch.no_grad():
            past_encoded = self.tokenizer(previous_submissions, padding='max_length', truncation=True, 
                    max_length=512, return_tensors='pt'
                    )
            current_encoded = self.tokenizer(current_submission, padding='max_length', truncation=True,
                    max_length=512, return_tensors='pt'
                    )
            
            past_embeddings = self.model(past_encoded['input_ids'])
            current_embedding = self.model(current_encoded['input_ids'])

            centroid_vector = past_embeddings.mean(dim=0, keepdim=True)

            similarity = F.cosine_similarity(centroid_vector, current_embedding).item()

            return ((similarity + 1.0) / 2.0) * 100 # calculez media aritmetica si apoi o transform in procent, valoarea similarity e intre [-1, 1]