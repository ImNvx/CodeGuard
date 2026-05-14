import torch
from transformers import AutoTokenizer
from .CodeGuardEncoder import CodeGuardHybrid, getFeatures
import torch.nn.functional as F

class CodeGuard(): # am facut clasa pana la urma ca daca era functie simpla trebuia sa dai load la model de mai multe ori si e mai elegant asa
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("AI/CodeGuard_tokenizer")
        self.model = CodeGuardHybrid(vocab_size=self.tokenizer.vocab_size)
        self.model.load_state_dict(torch.load("AI/CodeGuard_encoder_v2.pth", map_location=torch.device('cpu')))
        self.model.eval()

    def checkSubmission(self, previous_submissions, current_submission):
        with torch.no_grad():
            past_encoded = self.tokenizer(previous_submissions, padding='max_length', truncation=True, max_length=512, return_tensors='pt')
            past_style = torch.tensor([getFeatures(c) for c in previous_submissions], dtype=torch.float32)
            past_embeddings = self.model(past_encoded['input_ids'], past_encoded['attention_mask'], past_style)
            
            centroid_vector = past_embeddings.mean(dim=0, keepdim=True)
            
            if isinstance(current_submission, str):
                current_submission = [current_submission] # trebuie lista pentru loop cu getFeatures()
                
            current_encoded = self.tokenizer(current_submission, padding='max_length', truncation=True, max_length=512, return_tensors='pt')
            current_style = torch.tensor([getFeatures(c) for c in current_submission], dtype=torch.float32)
            current_embedding = self.model(current_encoded['input_ids'], current_encoded['attention_mask'], current_style)
            
            similarity = F.cosine_similarity(centroid_vector, current_embedding).item()
            return max(0.0, (similarity - 0.2) / 0.8) * 100 # mapez intervalul [0.2, 1] pe [0, 100]; (0.2 = loss margin)