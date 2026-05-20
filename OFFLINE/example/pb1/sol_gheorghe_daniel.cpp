#include <fstream>
#include <algorithm>
#include <queue>
#include <cstring>
#include <math.h>
using namespace std;

ifstream cin("poseidon.in");
ofstream cout("poseidon.out");

const int MOD=1e9+7;
const int VMAX=1e6;
const int NMAX=1e3+5;

int c, n, m, xp, yp, mat[NMAX][NMAX], viz[NMAX][NMAX], ans1, ans2=1;
int fact[VMAX+5], invfact[VMAX+5];

int dx[]={0,0,1,-1};
int dy[]={1,-1,0,0};

int expfast(int a, int b){
    int rez=1;
    a=a%MOD;
    while(b){
        if(b&1)rez=(1LL*rez*a)%MOD;
        a=(1LL*a*a)%MOD;
        b=b>>1;
    }
    return rez;
}

void precalc(){
    fact[0]=1;
    for(int i=1;i<=VMAX;i++){
        fact[i]=(1LL*fact[i-1]*i)%MOD;
    }
    invfact[VMAX]=expfast(fact[VMAX], MOD-2);
    for(int i=VMAX-1;i>=0;i--){
        invfact[i]=(1LL*invfact[i+1]*(i+1))%MOD;
    }
}

int C(int n, int k){
    return 1LL*fact[n]*invfact[k]%MOD*invfact[n-k]%MOD;
}

int solve(int n){
    int ans=fact[n];
    for(int i=1;i<n;i++){
        if(i%2==1){
            ans=(ans-(1LL*fact[n-i]*C(n, i))%MOD+MOD)%MOD;
        }
        else{
            ans=(ans+(1LL*fact[n-i]*C(n, i))%MOD)%MOD;
        }
    }
    if(n%2==1)ans=(ans-1+MOD)%MOD;
    else ans=(ans+1)%MOD;
    return ans;
}

bool inmat(int x, int y){
    return 1<=x&&x<=n&&1<=y&&y<=m;
}

void bfs(int i, int j){
    queue<pair<int,int>> q;
    q.push({i,j});
    viz[i][j]=1;
    int cnt=0, ok=0;
    while(!q.empty()){
        int x=q.front().first;
        int y=q.front().second;
        cnt+=mat[x][y]>0;
        if(x==xp&&y==yp)ok=1;
        q.pop();
        for(int d=0;d<4;d++){
            int nx=x+dx[d];
            int ny=y+dy[d];
            if(inmat(nx, ny)&&mat[nx][ny]>=0&&viz[nx][ny]==0){
                viz[nx][ny]=1;
                q.push({nx, ny});
            }
        }
    }
    if(ok==1)ans1=cnt;
    ans2=(1LL*ans2*solve(cnt))%MOD;
}

int main(){
    precalc();
    cin>>c>>n>>m;
    for(int i=1;i<=n;i++){
        for(int j=1;j<=m;j++){
            cin>>mat[i][j];
        }
    }
    if(c==1)cin>>xp>>yp;
    for(int i=1;i<=n;i++){
        for(int j=1;j<=m;j++){
            if(!viz[i][j]&&mat[i][j]>=0){
                bfs(i, j);
            }
        }
    }
    if(c==1){
        cout<<ans1<<'\n';
    }
    else{
        cout<<ans2<<'\n';
    }
}