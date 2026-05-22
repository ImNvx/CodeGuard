#include <fstream>
#include <queue>
#include <utility>
#include <algorithm>
#include <vector>

#define int long long

std::ifstream fin("poseidon.in");
std::ofstream fout("poseidon.out");

const int vm = 1e3 + 3;
const int MOD = 1e9 + 7;

int v[vm][vm], res1, res2 = 1;

int dx[4]{0, -1, 1, 0};
int dy[4]{1, 0, 0, -1};

int dp[vm];

std::queue<std::pair<int, int>> q;
std::vector<std::pair<int, int>> res;

void bordare(int n, int m)
{
    for(int i = 0; i <= n + 1; i++)
    {
        v[i][0] = -1;
        v[i][m + 1] = - 1;
    }
    for(int i = 0; i <= m + 1; i++)
    {
        v[0][i] = -1;
        v[n + 1][i] = -1;
    }
}

std::pair<int, int> fillAlg(int istart, int jstart, int xpos, int ypos)
{
    int cnt = 1, comori = 0;
    bool pose = 0;

    if(xpos == istart && ypos == jstart)
    {
        pose = 1;
    }

    q.push({istart, jstart});

    if(v[istart][jstart] > 0)
    {
        comori++;
    }

    v[istart][jstart] = -1;

    while(!q.empty())
    {
        int ix = q.front().first;
        int iy = q.front().second;
        q.pop();

        for(int p = 0; p < 4; p++)
        {
            int nx = ix + dx[p];
            int ny = iy + dy[p];

            if(v[nx][ny] != -1)
            {
                if(v[nx][ny] > 0)
                {
                    comori++;
                }
                if(nx == xpos && ny == ypos)
                {
                    pose = 1;
                }

                v[nx][ny] = -1;
                cnt++;
                q.push({nx, ny});
            }
        }
    }
    if(pose)
    {
        res1 = comori;
    }
    return {cnt, comori};
}

signed main()
{
    int c, n, m, xps, yps, mx = 0;

    fin >> c >> n >> m;

    for(int i = 1; i <= n; i++)
    {
        for(int j = 1; j <= m; j++)
        {
            fin >> v[i][j];
        }
    }
    bordare(n, m);

    if(c == 1)
    {
        fin >> xps >> yps;
        for(int i = 1; i <= n; i++)
        {
            for(int j = 1; j <= m; j++)
            {
                if(v[i][j] != -1)
                {
                    res.push_back(fillAlg(i, j, xps, yps));
                }
            }
        }
        fout << res1;
    }
    else
    {
        for(int i = 1; i <= n; i++)
        {
            for(int j = 1; j <= m; j++)
            {
                if(v[i][j] != -1)
                {
                    std::pair<int, int> f = fillAlg(i, j, xps, yps);
                    mx = std::max(mx, f.second);
                    res.push_back(f);
                }
            }
        }

        dp[0] = 1;
        for(int i = 2; i <= mx; i++)
        {
            dp[i] = (1ll *(i - 1) * (dp[i - 1] + dp[i - 2])) % MOD;
        }

        for(auto k : res)
        {
            if(k.second > 0)
            {
                res2 = 1ll * res2 * dp[k.second];
                res2 %= MOD;
            }
        }
        fout << res2;
    }
//2 3 2 2 4
//1 2 1 1 9
	return 0;
}