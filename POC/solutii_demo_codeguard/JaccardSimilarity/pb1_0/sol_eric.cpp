#include <bits/stdc++.h>
#define NMAX 31202

using namespace std;

ifstream fin("ninjago.in");
ofstream fout("ninjago.out");

struct DSU{
    vector <int> T;
    vector <int> sz;

    DSU(int N){
        T.resize(N+2);
        sz.resize(N+2,1);
        iota(T.begin(),T.end(),0);
    }

    int root(int x){
        if(T[x]==x){
            return x;
        }
        return T[x] = root(T[x]);
    }

    bool query(int a,int b)
    {///sunt unite?
        a= root(a);
        b=root(b);
        return a==b;
    }

    void join(int a,int b)
    {
        if(query(a,b) == 1) return;
        a = root(a);
        b=root(b);
        if(sz[b]>sz[a]){
            swap(a,b);
        }///a ii ala mare
        sz[b]+=sz[a];
        T[a] = b;
        return;
    }
};

struct Muchie
{
    int x,y;
    int cost;
    int cnt;
};

bool operator<(const Muchie &m1, const Muchie &m2)
{
    if(m1.cnt !=m2.cnt){
        return m1.cnt < m2.cnt;
    }
    return m1.cost < m2.cost;
}

int cer,N,M;
vector <Muchie> E;
vector <int> G[NMAX];
char vis[NMAX];
int muchii_cu_e;
int euri;
long long apm;
vector <Muchie> adaugate;

void dfs(int node, int&cnt)
{
    cnt++;
    vis[node] = 1;
    for(auto x:G[node]){
        if(!vis[x]) dfs(x,cnt);
    }
    return;
}

int main()
{
    fin >> cer >> N >> M;
    for(int i=1;i<=M;i++){
        int x,y;
        char s[8];
        int cost = 0;
        int cnt =0;
        fin >> x >> y >> s;
        int p5 = 1;
        for(int i=0;i<4;i++){
            if(s[i]!='E'){
                cost+=p5*(s[i]-'A' + 1);
            }else{
                cnt++;
            }
//            cout << (s[i]-'A' + 1);
            p5*=5;
        }
//        cout << "\n";
        if(cnt==0){
            G[x].push_back(y);
            G[y].push_back(x);
        }
        E.push_back({x,y,cost,cnt});
    }
    sort(E.begin(),E.end());
    DSU dsu(N);
    if(cer==1){
        int cnt = 0;
        dfs(1,cnt);
        fout << cnt;
        return 0;
    }
    ///construim apm
    for(auto [x,y,cost,cnt]:E){
        if(!dsu.query(x,y)){
            dsu.join(x,y);
//            adaugate.push_back({x,y,cost,cnt});
            apm+=cost;
//            cout << apm << "\n";
            if(cnt>0){
                muchii_cu_e++;
                euri+=cnt;
            }
        }
    }
    if(cer==2){
        fout << muchii_cu_e << "\n" << euri;
    }else if(cer==3){
        fout << apm;
    }
    return 0;
}