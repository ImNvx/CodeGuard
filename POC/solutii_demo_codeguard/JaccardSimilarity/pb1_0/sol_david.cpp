#include <fstream>
#include <algorithm>
#include <vector>
#include <string>
#include <cmath>

std::ifstream fin("ninjago.in");
std::ofstream fout("ninjago.out");

const int vm = 31203;

int mp[256];

int getCost(std::string str)
{
    int res = 0;
    int len = str.length();

    int p = 1;
    for(int i = 0; i < len; i++)
    {
        res += mp[str[i]] * p;
        p *= 5;
    }
    return res;
}

class DSU{
private:
    std::vector<int> t, rank, size;
    int nm;
public:
    DSU(int n)
    {
        nm = n;
        t.resize(n + 1);
        rank.resize(n + 1, 0);
        size.resize(n + 1, 1);
        for(int i = 1; i <= n; i++)
        {
            t[i] = i;
        }
    }

    int find(int x)
    {
        if(t[x] != x)
        {
            t[x] = find(t[x]);
        }
        return t[x];
    }

    void unite(int x, int y)
    {
        int rootX = find(x);
        int rootY = find(y);

        if(rank[rootX] < rank[rootY])
        {
            t[rootX] = rootY;
            size[rootY] += size[rootX];
        }
        else if(rank[rootX] > rank[rootY])
        {
            t[rootY] = rootX;
            size[rootX] += size[rootY];
        }
        else
        {
            t[rootY] = rootX;
            rank[rootX]++;
            size[rootX] += size[rootY];
        }
    }

    int getMaxSize()
    {
        int mx = 1;
        for(int i = 1; i <= nm; i++)
        {
            if(t[i] == i)
            {
                mx = std::max(mx, size[i]);
            }
        }
        return mx;
    }

};

struct muchie {
    int x, y, cost = 0, nrE = 0;
    bool hasE = 0;
};

muchie v[vm];

bool cmp(const muchie &a, const muchie &b)
{
    if(a.hasE != b.hasE)
    {
        return a.hasE < b.hasE;
    }
    if(a.nrE != b.nrE)
    {
        return a.nrE < b.nrE;
    }
    return a.cost < b.cost;
}

int main()
{
    int c, n, m;
    mp['A'] = 1;
    mp['B'] = 2;
    mp['C'] = 3;
    mp['D'] = 4;
    mp['E'] = 0;

    fin >> c >> n >> m;

    DSU dsu(n);

    for(int i = 1; i <= m; i++)
    {
        fin >> v[i].x >> v[i].y;
        std::string str;
        fin >> str;
        v[i].cost = getCost(str);
        for(int j = 0; j < 4; j++)
        {
            if(str[j] == 'E')
            {
                v[i].hasE = 1;
                v[i].nrE++;
            }
        }
    }

    std::sort(v + 1, v + m + 1, cmp);
    if(c == 1)
    {
        for(int i = 1; i <= m; i++)
        {
            if(v[i].hasE)
            {
                continue;
            }
            if(dsu.find(v[i].x) != dsu.find(v[i].y))
            {
                dsu.unite(v[i].x, v[i].y);
            }
        }
        fout << dsu.getMaxSize();
    }
    else if(c == 2)
    {
        int resE = 0, cnt = 0;
        for(int i = 1; i <= m; i++)
        {
            if(dsu.find(v[i].x) != dsu.find(v[i].y))
            {
                dsu.unite(v[i].x, v[i].y);
                if(v[i].hasE)
                {
                    cnt++;
                    resE += v[i].nrE;
                }
            }
        }
        fout << cnt << '\n' << resE;
    }
    else
    {
        int res = 0;
        for(int i = 1; i <= m; i++)
        {
            if(dsu.find(v[i].x) != dsu.find(v[i].y))
            {
                dsu.unite(v[i].x, v[i].y);
                res += v[i].cost;
            }
        }
        fout << res;
    }

    return 0;
}