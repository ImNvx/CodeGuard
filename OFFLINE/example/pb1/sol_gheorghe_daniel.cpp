#include <bits/stdc++.h>
using namespace std;
const int MOD = 1e9 + 7;
int main() {
    freopen("poseidon.in", "r", stdin);
    freopen("poseidon.out", "w", stdout);

    cin.tie(0); cout.tie(0);
    ios_base::sync_with_stdio(false);

    int C; cin >> C;
    int N, M;
    cin >> N >> M;
    vector<vector<int>>v(N + 3, vector<int>(M + 3));
    for(int i = 1; i <= N; i++) {
        for(int j = 1; j <= M; j++) {
            cin >> v[i][j];
        }
    }
    vector<vector<int>>viz(N + 3, vector<int>(M + 3));
    vector<int>di = {-1, 1, 0, 0};
    vector<int>dj = {0, 0, 1, -1};
    auto bfs = [&] (int i, int j, int &counter, auto self) ->void{
        viz[i][j] = 1;
        counter += (v[i][j] != 0);
        for(int d = 0; d < 4; d++) {
            int inou = i + di[d]; int jnou = j + dj[d];
            if(inou >= 1 && inou <= N && jnou >= 1 && jnou <= M && !viz[inou][jnou] && v[inou][jnou] != -1) {
                self(inou, jnou, counter, self);
            }
        }   
    };
    vector<int>D(N * M + 3);
    D[2] = 1;
    for(int i = 3; i <= N * M; i++) {
        D[i] = (1LL * (D[i - 1] + D[i - 2]) * (i - 1)) % MOD; 
    }

    long long ans = 1;
    int count = 0;
    if(C == 2) {
    for(int i = 1; i <= N; i++) {
        for(int j = 1; j <= M; j++) {
            int counter;
            if(!viz[i][j] && v[i][j] != -1) {
                counter = 0;
                bfs(i, j, counter, bfs);
                ans *= D[counter];
                ans %= MOD;
            }
        }
    }
    cout << ans << '\n';
    }
    else {
        int x, y;
        cin >> x >> y;
        int counter = 0;
        bfs(x, y, counter, bfs);
        cout << counter;
    }
}