#include <fstream>
std::ifstream fin("gradina.in");
std::ofstream fout("gradina.out");

const int vm = 1e3 + 3;

bool v[vm][vm];

int s[vm][vm];

int main()
{
    int n, q, k, x, y, res = 1, nr = 1;

    fin >> n >> q >> k;

    while(q--)
    {
        fin >> x >> y;
        v[x][y] = 1;
    }

    for(int i = 1; i <= n; i++)
    {
        for(int j = 1; j <= n; j++)
        {
            s[i][j] = s[i - 1][j] + s[i][j - 1] - s[i - 1][j - 1] + v[i][j];
        }
    }

    for(int i = k; i <= n; i++)
    {
        for(int j = k; j <= n; j++)
        {
            int f = s[i][j] - s[i - k][j] - s[i][j - k] + s[i - k][j - k];
            if(f > res)
            {
                res = f;
                nr = 1;
            }
            else if(f == res)
            {
                nr++;
            }
        }
    }

    fout << res << '\n' << nr;

	return 0;
}