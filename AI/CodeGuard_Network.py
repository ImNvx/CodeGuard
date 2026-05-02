import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import torch.optim as optim
import torch.nn.functional as F
import json
from transformers import AutoTokenizer

TRAIN_FILE = 'train.jsonl'

tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base") # in final o sa ii dam load din fisier, nu din huggingface

class DatasetTrain(Dataset):
    def __init__(self, jsonl_file, tokenizer, max_length=512):

        self.tokenizer = tokenizer
        self.max_length = max_length
        self.data = []
        
        with open(jsonl_file, 'r', encoding='utf-8') as f:
            for line in f:
                self.data.append(json.loads(line))

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        row = self.data[idx]
        
        code_1 = row['cod1']
        code_2 = row['cod2']
        label = float(row['label'])
        
        encoded_1 = self.tokenizer(
            code_1,
            padding='max_length',
            truncation=True,
            max_length=self.max_length,
            return_tensors='pt'
        )
        
        encoded_2 = self.tokenizer(
            code_2,
            padding='max_length',
            truncation=True,
            max_length=self.max_length,
            return_tensors='pt'
        )
        
        token_ids_1 = encoded_1['input_ids'].squeeze(0)
        token_ids_2 = encoded_2['input_ids'].squeeze(0)
        
        return token_ids_1, token_ids_2, torch.tensor(label, dtype=torch.float32)

dataset_train = DatasetTrain(TRAIN_FILE, tokenizer=tokenizer)
dataloader_train = DataLoader(dataset_train, batch_size=128, shuffle=True)

class ContrastiveLoss(nn.Module):
    def __init__(self, margin=2.0): #2.0 pentru l2 normalization
        super(ContrastiveLoss, self).__init__()
        self.margin = margin

    def forward(self, vector_1, vector_2, label):
        euclid_d = F.pairwise_distance(vector_1, vector_2, keepdim=True)
        
        label = label.view(-1, 1)
        
        loss_same = label * torch.pow(euclid_d, 2)
        loss_diff = (1 - label) * torch.pow(torch.clamp(self.margin - euclid_d, min=0.0), 2)
        
        return torch.mean(loss_same + loss_diff)


class CodeGuardEncoder(nn.Module):
    def __init__(self, vocab_size, embed_dim=128, hidden_dim=256, output_dim=128):
        super(CodeGuardEncoder, self).__init__()
        self.embedding = nn.Embedding(num_embeddings=vocab_size, embedding_dim=embed_dim)
        
        self.conv1 = nn.Conv1d(in_channels=embed_dim, out_channels=hidden_dim, kernel_size=3, padding=1)
        self.conv2 = nn.Conv1d(in_channels=embed_dim, out_channels=hidden_dim, kernel_size=5, padding=2)
        
        self.fc = nn.Linear(hidden_dim * 2, output_dim)

    def forward(self, x):
        embedded = self.embedding(x)
        
        embedded = embedded.permute(0, 2, 1) #dam permute pentru ca conv1 vrea ordinea [batch_size, channels, seq_len] si noi avem [batch_size, seq_len, channels]
        
        c1 = F.relu(self.conv1(embedded))
        c2 = F.relu(self.conv2(embedded))
        
        p1 = torch.max(c1, dim=2)[0]
        p2 = torch.max(c2, dim=2)[0]
        
        combined = torch.cat((p1, p2), dim=1)
        
        fingerprint = self.fc(combined)
        
        return F.normalize(fingerprint, p=2, dim=1)

vocab_size = tokenizer.vocab_size
model = CodeGuardEncoder(vocab_size=vocab_size)

device = torch.device("cuda")
model = model.to(device)
criterion = ContrastiveLoss()

optimizer = optim.AdamW(model.parameters(), lr=0.001) #adamw in loc de adam pentru smecherie

model.train()
n_epochs = 50

for epoch in range(n_epochs):
    running_loss = 0.0
    
    for code1, code2, labels in dataloader_train:
        code1 = code1.to(device)
        code2 = code2.to(device)
        labels = labels.to(device)
        
        optimizer.zero_grad()
        
        vector_1 = model(code1)
        vector_2 = model(code2)
        
        loss = criterion(vector_1, vector_2, labels)
        
        loss.backward()
        optimizer.step()
        
        running_loss += loss.item()
            
    epoch_loss = running_loss / len(dataloader_train)
    print(f"Epoch {epoch + 1}, Average Loss: {epoch_loss:.4f}")

cod_train_1 = """#include <bits/stdc++.h> using namespace std; ifstream fin ("suma.in"); ofstream fout ("suma.out"); const int nMAX = 63365; const int mMAX = 57; int n; int **mat[mMAX + 1]; int **syn[mMAX + 1]; int **dp[mMAX + 1]; int lvl; bool **apInDrum[nMAX + 1]; bool inside(int lv, int i, int j) { return (1 <= lv && lv <= lvl && 1 <= i && i <= lv && 1 <= j && j <= lv); } int main() { fin >> n; int k = 0; lvl = 1; while (k != n) { mat[lvl] = new int*[lvl+1]{}; syn[lvl] = new int*[lvl+1]{}; dp[lvl] = new int*[lvl+1]{}; apInDrum[lvl] = new bool*[lvl+1]{}; for (int i = 1; i <= lvl; ++i) { mat[lvl][i] = new int[lvl+1]{}; syn[lvl][i] = new int[lvl+1]{}; dp[lvl][i] = new int[lvl+1]{}; apInDrum[lvl][i] = new bool[lvl+1]{}; for (int j = 1; j <= lvl; ++j, ++k) { fin >> mat[lvl][i][j]; syn[lvl][i][j] = k+1; dp[lvl][i][j] = INT_MAX>>1; } } lvl++; } fout << --lvl << ' '; dp[1][1][1] = mat[1][1][1]; for (int lv = 1; lv < lvl; ++lv) { for (int i = 1; i <= lv; ++i) for (int j = 1; j <= lv; ++j) { dp[lv+1][i][j] = min(dp[lv+1][i][j], dp[lv][i][j] + mat[lv+1][i][j]); dp[lv+1][i][j+1] = min(dp[lv+1][i][j+1], dp[lv][i][j] + mat[lv+1][i][j+1]); dp[lv+1][i+1][j] = min(dp[lv+1][i+1][j], dp[lv][i][j] + mat[lv+1][i+1][j]); dp[lv+1][i+1][j+1] = min(dp[lv+1][i+1][j+1], dp[lv][i][j] + mat[lv+1][i+1][j+1]); } } int drummin = INT_MAX>>1; for (int i = 1; i <= lvl; ++i) for (int j = 1; j <= lvl; ++j) drummin = min(drummin, dp[lvl][i][j]); fout << drummin << ' '; for (int i = 1; i <= lvl; ++i) for (int j = 1; j <= lvl; ++j) if (dp[lvl][i][j] == drummin) apInDrum[lvl][i][j] = 1; for (int lv = lvl; lv > 1; --lv) { for (int i = 1; i <= lv; ++i) for (int j = 1; j <= lv; ++j) { if (!apInDrum[lv][i][j]) continue; if (inside(lv-1, i-1, j-1) && dp[lv-1][i-1][j-1] + mat[lv][i][j] == dp[lv][i][j]) apInDrum[lv-1][i-1][j-1] = 1; if (inside(lv-1, i, j-1) && dp[lv-1][i][j-1] + mat[lv][i][j] == dp[lv][i][j]) apInDrum[lv-1][i][j-1] = 1; if (inside(lv-1, i-1, j) && dp[lv-1][i-1][j] + mat[lv][i][j] == dp[lv][i][j]) apInDrum[lv-1][i-1][j] = 1; if (inside(lv-1, i, j) && dp[lv-1][i][j] + mat[lv][i][j] == dp[lv][i][j]) apInDrum[lv-1][i][j] = 1; } } int i = 1, j = 1; fout << 1 << ' '; for (int lv = 2; lv <= lvl; ++lv) { if (apInDrum[lv][i][j]) {} else if (apInDrum[lv][i][j+1]) j++; else if (apInDrum[lv][i+1][j]) i++; else i++, j++; fout << syn[lv][i][j] << ' '; } }"""
cod_train_2 = """#include <bits/stdc++.h> #define lsb(x) (x & -x) using namespace std; const int valMAX = 1e6; int n; long long aib[valMAX + 1]; void updateAddAib(int pos, int val) { while (pos <= valMAX) { aib[pos] += val; pos += lsb(pos); } } long long querySumAib(int ri) { long long sum = 0; while (ri >= 1) { sum += aib[ri]; ri -= lsb(ri); } return sum; } int main() { ios_base::sync_with_stdio(false); cin.tie(0); cout.tie(0); cin >> n; long long ans = 0; while (n--) { int x; cin >> x; if (x == 0) continue; updateAddAib(x, x); ans += querySumAib(x-1); } cout << ans; }"""
cod_train_3 = """#include <bits/stdc++.h> using namespace std; ifstream fin ("investitie.in"); ofstream fout ("investitie.out"); const int nMAX = 100e3; int n, m, q; int v[nMAX + 1]; pair<int, int> viz[nMAX + 1]; // viz[i] .first = in ce comp se afla (comp[.first]); .second = pozitia in comp vector<vector<int>> comp; vector<vector<long long>> scomp; int main() { fin >> n >> m; for (int i = 1; i <= n; ++i) fin >> v[i]; fill(viz + 1, viz + n+1, make_pair(-1, 0)); int fil = 0; for (int i = 1; i <= n; ++i) { if (viz[i].first == -1) { comp.emplace_back(); int k = 0; for (int nr = v[i]; nr != i; nr = v[nr]) { comp[fil].push_back(nr); viz[nr] = {fil, k++}; } comp[fil].push_back(i); viz[i] = {fil, k}; ++fil; } } for (int i = 0; i < fil; ++i) { scomp.emplace_back(); scomp[i].resize(comp[i].size(), 0); scomp[i][0] = comp[i][0]; for (int j = 1; j < comp[i].size(); ++j) scomp[i][j] = scomp[i][j-1] + comp[i][j]; } fin >> q; while (q--) { int zs, ze, cs, ce; fin >> zs >> ze >> cs >> ce; long long sum = 0; for (int i = cs; i <= ce; ++i) { vector<int> *compc = &comp[viz[v[i]].first]; vector<long long> *scompc = &scomp[viz[v[i]].first]; int posc = viz[v[i]].second; if (compc->size() == 1) { sum += 1ll * (*compc)[0] * (ze-zs+1); continue; } int posst = (posc + zs-1) % compc->size(); int posdr = (posc + ze-1) % compc->size(); long long sumi = scompc->back() * ((ze-zs+1) / compc->size()); if (posst <= posdr) if (posst == 0) if (posdr != compc->size() - 1) sumi += (*scompc)[posdr]; else; else sumi += (*scompc)[posdr] - (*scompc)[posst-1]; else // posdr < posst if (posst-posdr >= 2) sumi += scompc->back() - (*scompc)[posst-1] + (*scompc)[posdr]; sum += sumi; } fout << sum << ' '; } }"""
cod_train_4 = """#include <bits/stdc++.h> using namespace std; const int nMAX = 100e3; int n, logn, q; int v[nMAX + 1]; int aibInd[nMAX + 1]; // aibInd[i] = cate elemente am sters in pozitiile i-lsb(i)+1..i int aintMin[4*nMAX + 1]; // aintMin[i] = minimul elementelor din nodul i int tat[nMAX + 2]; // ---- dsu ---- int rad(int nod) { if (tat[nod]) return rad(tat[nod]); return nod; } void changeDads(int nod, int newdad) { if (tat[nod]) changeDads(tat[nod], newdad); tat[nod] = newdad; } // ---- aib ---- int searchRealPos_aibInd(int index) { int pos = 0, sum = 0; for (int i = logn; i >= 0; --i) if (pos + (1 << i) < n && (pos + (1 << i)) - (sum + aibInd[pos + (1 << i)]) < index) { sum += aibInd[pos + (1 << i)]; pos += (1 << i); } return pos + 1; } void updateAdd_aibInd(int pos, int val) { for (; pos <= n; pos += (pos & -pos)) aibInd[pos] += val; } // ---- aint ---- void build_aintMin(int nod, int st, int dr) { if (st == dr) return (void) (aintMin[nod] = v[st]); int mj = st+dr >> 1; build_aintMin(nod<<1, st, mj); build_aintMin(nod<<1|1, mj+1, dr); aintMin[nod] = min(aintMin[nod<<1], aintMin[nod<<1|1]); } void maximizeElement_aintMin(int nod, int st, int dr, int pos) { if (st == dr) return (void) (aintMin[nod] = INT_MAX); int mj = st+dr >> 1; if (pos <= mj) maximizeElement_aintMin(nod<<1, st, mj, pos); else maximizeElement_aintMin(nod<<1|1, mj+1, dr, pos); aintMin[nod] = min(aintMin[nod<<1], aintMin[nod<<1|1]); } int queryMin_aint() { return aintMin[1]; } // ---- main ---- int main() { cin.tie(0)->sync_with_stdio(0);cout.tie(0); cin >> n; logn = 31 - __builtin_clz(n); for (int i = 1; i <= n; ++i) cin >> v[i]; build_aintMin(1, 1, n); cin >> q; while (q--) { int x, y; cin >> x >> y; int xreal = searchRealPos_aibInd(x); int yreal = searchRealPos_aibInd(y); for (int i = xreal; i != 0 && i <= yreal; i = tat[i]) { if (v[i] == INT_MAX) if (tat[i] == 0) tat[i] = i+1; else { int radacina = rad(i); changeDads(i, radacina); } else { maximizeElement_aintMin(1, 1, n, i); updateAdd_aibInd(i, 1); v[i] = INT_MAX; tat[i] = i+1; } } cout << queryMin_aint() << ' '; } }"""
cod_train_5 = """#include <fstream> #include <string> #include <cmath> #include <climits> #include <tuple> using namespace std; ifstream fin ("circular.in"); ofstream fout ("circular.out"); const int MOD = 666013; int distanta(char a, char b) { int d1 = abs(a-b); int d2 = abs(a+26-b); int d3 = abs(a-b-26); return min(d1, min(d2, d3)); } // caracterul minim care se poate insera intre a si b, cate astfel de caractere exista care scot timp minim, distanta minima tuple<char, int, int> charDeInserat(char a, char b, string &src) { int distMin = INT_MAX, dist; int count = 0; char charMin = CHAR_MAX; for (char &c : src) { dist = distanta(a, c) + distanta(c, b); if (dist < distMin) { count = 1; distMin = dist; charMin = c; } else if (dist == distMin) { count ++; } } return make_tuple(charMin, count, distMin); } int main() { int cer, i; string alb, ros; fin >> cer >> alb >> ros; if (cer == 1) { int timp = distanta('A', alb[0]); for (i = 1; i < alb.size(); ++i) timp += distanta(alb[i-1], alb[i]); fout << timp; } if (cer == 2) { int timp; int moduri = 1; string sirMin; tuple<char, int, int> ans; timp = distanta('A', alb[0]); sirMin.push_back(alb[0]); for (i = 1; i < alb.size(); ++i) { ans = charDeInserat(alb[i-1], alb[i], ros); sirMin.push_back(get<0>(ans)); sirMin.push_back(alb[i]); moduri = (1LL * moduri * get<1>(ans)) % MOD; timp += get<2>(ans); } fout << timp << ' ' << moduri << ' ' << sirMin; } }"""

cod_test_real = """#include <cstring> #include <fstream> #include <queue> #include <vector> const char INPUT_FILE[] = "roadtrip.in"; const char OUTPUT_FILE[] = "roadtrip.out"; const int NODES_MAX = 500; const int FUEL_MAX = 500; const int INF = 0x3f3f3f3f; int nodeCount, edgeCount; int startNode, endNode; int refillTime[NODES_MAX + 5]; std::vector<std::pair<int, int>> edges[NODES_MAX + 5]; int fuelCapacity; int dist[NODES_MAX + 5][FUEL_MAX + 5]; struct QNode { int nodeIndex; int fuel; int dist; QNode(int nodeIndex, int fuel, int dist) : nodeIndex(nodeIndex), fuel(fuel), dist(dist) {} bool operator<(const QNode& other) const { return dist > other.dist; } }; void read() { std::ifstream fin(INPUT_FILE); fin >> nodeCount >> edgeCount; for (int i = 1; i <= nodeCount; ++i) { fin >> refillTime[i]; } while (edgeCount--) { int x, y, d; fin >> x >> y >> d; edges[x].emplace_back(y, d); edges[y].emplace_back(x, d); } fin >> startNode >> endNode >> fuelCapacity; } void solve() { std::priority_queue<QNode> q; std::memset(dist, INF, sizeof dist); dist[startNode][fuelCapacity] = 0; q.emplace(startNode, fuelCapacity, 0); while (!q.empty()) { int node = q.top().nodeIndex; int fuel = q.top().fuel; int ds = q.top().dist; q.pop(); if (ds != dist[node][fuel]) { continue; } for (const auto& edge : edges[node]) { if (fuel < edge.second) { continue; } int newDs = ds + edge.second; int fuelLeft = fuel - edge.second; if (newDs < dist[edge.first][fuelLeft]) { dist[edge.first][fuelLeft] = newDs; q.emplace(edge.first, fuelLeft, newDs); } } if (fuel < fuelCapacity) { int newDs = ds + refillTime[node]; if (newDs < dist[node][fuelCapacity]) { dist[node][fuelCapacity] = newDs; q.emplace(node, fuelCapacity, newDs); } } } } void write() { int ans = INF; for (int i = 0; i <= FUEL_MAX; ++i) { ans = std::min(ans, dist[endNode][i]); } std::ofstream(OUTPUT_FILE) << (ans == INF ? -1 : ans) << " "; } int main() { read(); solve(); write(); return 0; }"""
cod_test_diff = """#include <bits/stdc++.h> using namespace std; bool check() { int n; cin >> n; vector <string> a(n); map <string, int> linemap, colmap; for (int i = 0; i < n; i++) cin >> a[i]; for (int i = 0; i < n; i++) { linemap[a[i]]++; if (count(a[i].begin(), a[i].end(), '0') != n / 2) return false; } string s; for (int j = 0; j < n; j++) { int cnt = 0; s = ""; for (int i = 0; i < n; i++) { s += a[i][j]; cnt += (a[i][j] == '0'); } colmap[s]++; if (cnt != n / 2) return false; } if (linemap.size() != 2 || linemap[a[0]] != n / 2 || colmap.size() != 2 || colmap[s] != n / 2) return false; return true; } vector <tuple <char, int, int>> swapElements(string &s, char ch) { vector <tuple <char, int, int>> sol; vector <int> positions[2][2]; for (int i = 0; i < s.size(); i++) positions[s[i] - '0'][i & 1].push_back(i + 1); assert(positions[0][0].size() == positions[1][1].size()); assert(positions[0][1].size() == positions[1][0].size()); if (positions[0][0].size() <= positions[0][1].size()) { while (positions[0][0].size()) { sol.push_back(make_tuple(ch, positions[0][0].back(), positions[1][1].back())); positions[0][0].pop_back(); positions[1][1].pop_back(); } } else { while (positions[0][1].size()) { sol.push_back(make_tuple(ch, positions[0][1].back(), positions[1][0].back())); positions[0][1].pop_back(); positions[1][0].pop_back(); } } return sol; } vector <tuple <char, int, int>> buildSolution() { int n; cin >> n; vector <string> a(n); for (int i = 0; i < n; i++) cin >> a[i]; string s = a[0]; auto v = swapElements(s, 'C'); s = ""; for (int i = 0; i < n; i++) s += a[i][0]; auto vl = swapElements(s, 'L'); v.insert(v.end(), vl.begin(), vl.end()); return v; } int main() { int p, t; cin >> p >> t; while (t--) { if (p == 1) cout << check() << ' '; else { auto v = buildSolution(); cout << v.size() << ' '; if (p == 3) for (auto [lc, l, c] : v) cout << lc << ' ' << l << ' ' << c << ' '; } } return 0; }"""

model.eval()

past_submissions = [
    cod_train_1,
    cod_train_2,
    cod_train_3,
    cod_train_4,
    cod_train_5
]

def test_submission(current_code):
    with torch.no_grad():
        past_encoded = tokenizer(
            past_submissions, padding='max_length', truncation=True, 
            max_length=512, return_tensors='pt'
        ).to(device)

        current_encoded = tokenizer(
            current_code, padding='max_length', truncation=True, 
            max_length=512, return_tensors='pt'
        ).to(device)
        
        past_embeddings = model(past_encoded['input_ids'])
        current_embedding = model(current_encoded['input_ids'])
        
        centroid_vector = past_embeddings.mean(dim=0, keepdim=True)
        
        centroid_similarity = F.cosine_similarity(centroid_vector, current_embedding).item()
        
        print(((centroid_similarity + 1.0) / 2.0) * 100)

test_submission(cod_test_real)
test_submission(cod_test_diff)