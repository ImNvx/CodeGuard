#include <fstream>
#include <algorithm>

std::ifstream fin("credite.in");
std::ofstream fout("credite.out");

const int vm = 1e4 + 3;

struct prob{
    int cred, t;
};

prob v[vm];

bool cmp1(const prob &a, const prob &b)
{
    return a.t < b.t;
}

bool cmp2(const prob &a, const prob &b)
{
    return a.cred > b.cred;
}

int main()
{
    int n, t = 1, res = 0, mx = 0;
    fin >> n;

    for(int i = 1; i <= n; i++)
    {
        fin >> v[i].cred >> v[i].t;
        mx = std::max(mx, v[i].t);
    }

    std::sort(v + 1, v + n + 1, cmp2);

    for(t = mx; t >= 1; t--)
    {
         for(int i = 1; i <= n; i++)
            {
                if(v[i].t >= t)
                {
                    res += v[i].cred;
                    v[i].t = 0;
                    break;
                }
            }
    }

    fout << res;

    return 0;
}