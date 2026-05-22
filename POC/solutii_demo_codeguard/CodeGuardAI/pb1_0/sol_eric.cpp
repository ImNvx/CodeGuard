#include <bits/stdc++.h>

using namespace std;

ifstream fin("poseidon.in");
ofstream fout("poseidon.out");

const int nm=1000,mo=1000000007;
int c,n,m,a,xp,yp,k;
int_fast8_t v[nm+2][nm+2];
long long int ans,moduri[nm*nm+2];

void cnt(int x,int y,int &k) ///cati de 2 is pe insula care contine y,x?
{
    if(v[x][y]==0 || v[x][y]>2) {
        return;
    }
    if(v[x][y]==2) {
        k++;
    }
    v[x][y]+=10; ///adugam un plus ca sa nu mai mergem odata
    cnt(x+1,y,k);
    cnt(x,y+1,k);
    cnt(x-1,y,k);
    cnt(x,y-1,k);
}

int main()
{
    fin >> c >> n >> m;
    for(int i=1; i<=n; i++) {
        for(int j=1; j<=m; j++) {
            fin >> a;
            a=min(a,1); ///simplificam la
            a++;        /// 0=apa, 1=uscat, 2=comoara
            v[i][j]=a;
        }
    }
    if(c==1) { ///cerinta 1
        fin >> xp >> yp;
        cnt(xp,yp,k);
        fout << k;
    } else {
        moduri[2]=1;
        for(long long int i=3; i<=nm*nm; i++) { ///formula recursiva pentru dearanjari
            moduri[i]=(i-1)*((moduri[i-1]+moduri[i-2])%mo)%mo;
        }
        ans=1;
        for(int i=1;i<=n;i++){///parcurgem matricea si daca nu am mai fost aici si este
            for(int j=1;j<=m;j++){///pamant, numar cate comori is
                if(v[i][j]==1 || v[i][j]==2){
                    k=0;
                    cnt(i,j,k);
                    ans=(ans*moduri[k])%mo; ///apoi inmultesc raspunsul cu moduri[nr_comori]
                }
            }
        }
        fout << ans;
    }
}