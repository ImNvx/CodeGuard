import scipy.sparse.linalg # ceva pt multiprocesare idk dadea eroare
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import torch.optim as optim
import torch.nn.functional as F
from transformers import AutoTokenizer
from datasets import load_from_disk
from tqdm import tqdm
import math
import re
import os

def getFeatures(code):
    features = []
    
    words = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', code)
    if not words:
        words = ["0"] # ca sa nu impart la 0 in final
        
    camel_case = sum(1 for w in words if re.match(r'^[a-z]+(?:[A-Z][a-z0-9]+)+$', w)) # ex: getMax
    snake_case = sum(1 for w in words if re.match(r'^[a-z]+(?:_[a-z0-9]+)+$', w)) # ex: get_max
    pascal_case = sum(1 for w in words if re.match(r'^[A-Z][a-z0-9]+(?:[A-Z][a-z0-9]+)+$', w)) # ex: GetMax
    upper_snake = sum(1 for w in words if re.match(r'^[A-Z]+(?:_[A-Z0-9]+)+$', w)) # ex: GET_MX, define-uri in principal
    single_letter = sum(1 for w in words if len(w) == 1) # ex: i, j, k (variabile denumite cu o singura litera)
    
    features.append(camel_case / len(words))
    features.append(snake_case / len(words))
    features.append(pascal_case / len(words))
    features.append(upper_snake / len(words))
    features.append(single_letter / len(words))
    
    total_braces = code.count('{')
    if total_braces == 0:
        total_braces = 1
        
    kr_braces = len(re.findall(r' \s*\{', code)) # spatiu inainte de {
    allman_braces = len(re.findall(r'\n\s*\{', code)) # '\n' inainte de {
    
    features.append(kr_braces / total_braces)
    features.append(allman_braces / total_braces)
    
    total_ops = len(re.findall(r'[=+\-*/<>]', code))
    if total_ops == 0:
        total_ops = 1
    spaced_ops = len(re.findall(r' [=+\-*/<>] ', code)) # operatori de genul a= sau a =
    features.append(spaced_ops / total_ops)
    
    # indentare (tab sau spatiu)
    lines = code.split('\n')
    indented_lines = [l for l in lines if l.startswith(' ') or l.startswith('\t')]
    if not indented_lines:
        features.append(0.0)
    else:
        tab_lines = sum(1 for l in indented_lines if l.startswith('\t'))
        features.append(tab_lines / len(indented_lines))
        
    return features


class PositionalEncoding(nn.Module):
    def __init__(self, d_model, max_len=512):
        super(PositionalEncoding, self).__init__()
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        self.register_buffer('pe', pe) # pentru antrenare pe cuda

    def forward(self, x):
        seq_len = x.size(1)
        return x + self.pe[:seq_len, :].unsqueeze(0) 


class CodeGuardHybrid(nn.Module):
    def __init__(self, vocab_size=50000, embed_dim=256, num_heads=4, num_layers=2, output_dim=128):
        super(CodeGuardHybrid, self).__init__()
        
        self.embedding = nn.Embedding(num_embeddings=vocab_size, embedding_dim=embed_dim, padding_idx=1)
        self.pos_encoder = PositionalEncoding(d_model=embed_dim)
        
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=embed_dim, nhead=num_heads, 
            dim_feedforward=embed_dim * 2, dropout=0.1, batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        
        self.style_mlp = nn.Sequential(
            nn.Linear(9, 32), # 9 feature-uri momentan
            nn.ReLU(),
            nn.Dropout(0.1)
        )
        
        self.fc = nn.Linear(embed_dim + 32, output_dim)

    def forward(self, input_ids, attention_mask, style_features):
        # partea de transformer
        x = self.embedding(input_ids)
        x = self.pos_encoder(x)
        
        padding_mask = (attention_mask == 0)
        encoded = self.transformer(x, src_key_padding_mask=padding_mask)
        
        mask_expanded = attention_mask.unsqueeze(-1).expand(encoded.size()).float()
        sum_embeddings = torch.sum(encoded * mask_expanded, 1)
        sum_mask = torch.clamp(mask_expanded.sum(1), min=1e-9)
        mean_pooled = sum_embeddings / sum_mask
        
        # mlp simplu pe style features
        style_encoded = self.style_mlp(style_features)
        
        # partea de concatenare pt hybrid
        fused = torch.cat((mean_pooled, style_encoded), dim=1)
        fingerprint = self.fc(fused)
        
        return F.normalize(fingerprint, p=2, dim=1)


if __name__ == "__main__":
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    #print(f"device: {device}")

    tokenizer = AutoTokenizer.from_pretrained("CodeGuard_tokenizer")
    dataset = load_from_disk("hf_dataset") # am trecut pe ds de huggingface ca e de 10 ori mai rapid

    #num_workers = min(4, os.cpu_count() or 1)
    num_workers = 12
    dataloader_train = DataLoader(dataset, batch_size=32, shuffle=True, num_workers=num_workers, pin_memory=True, persistent_workers=True) 

    model = CodeGuardHybrid(vocab_size=tokenizer.vocab_size)
    model = model.to(device)
    
    criterion = nn.CosineEmbeddingLoss(margin=0.2)
    optimizer = optim.AdamW(model.parameters(), lr=5e-4, weight_decay=1e-4)
    
    n_epochs = 50
    total_steps = len(dataloader_train) * n_epochs
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=total_steps, eta_min=1e-6) # scheduler de LR pentru fine-tuning catre ultimile epoci
    
    
    scaler = torch.cuda.amp.GradScaler(enabled=torch.cuda.is_available()) # antrenare mai rapida
    
    model.train()
    
    for epoch in range(n_epochs):
        running_loss = 0.0
        
        progress_bar = tqdm(dataloader_train, desc=f"Epoch {epoch + 1}/{n_epochs}")
        for batch in progress_bar:
            input_ids_1 = batch['input_ids_1'].to(device)
            attention_mask_1 = batch['attention_mask_1'].to(device)
            style_features_1 = batch['style_features_1'].to(device)
            
            input_ids_2 = batch['input_ids_2'].to(device)
            attention_mask_2 = batch['attention_mask_2'].to(device)
            style_features_2 = batch['style_features_2'].to(device)
            
            labels = batch['label'].to(device)
            
            optimizer.zero_grad(set_to_none=True) # set_to_none pt ca e mai rapid aparent 
            
            with torch.cuda.amp.autocast(enabled=torch.cuda.is_available()):
                vector_1 = model(input_ids_1, attention_mask_1, style_features_1)
                vector_2 = model(input_ids_2, attention_mask_2, style_features_2)
                loss = criterion(vector_1, vector_2, labels)
            
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
            
            scheduler.step()
            
            running_loss += loss.item()
            progress_bar.set_postfix({'loss': loss.item(), 'lr': f"{scheduler.get_last_lr()[0]:.6f}"})
                
        epoch_loss = running_loss / len(dataloader_train)
        print(f"Epoch {epoch + 1}, Average Loss: {epoch_loss:.4f}")

    torch.save(model.state_dict(), "CodeGuard_encoder_v1.pth")