#include <fstream>

std::ifstream fin("cod.in");
std::ofstream fout("cod.out");

int maxcf(int x)
{
    int maxcif = 0;
    while(x > 0)
    {
        if(x % 10 > maxcif)
        {
            maxcif = x % 10;
        }
        x /= 10;
    }
    return maxcif;
}

int main()
{
    int n, x, maxcif = -1, res;

    fin >> n;

    for(int i = 0; i < n; i++)
    {
        fin >> x;
        if(maxcf(x) > maxcif)
        {
            maxcif = maxcf(x);
            res = x;
        }
        else if(maxcf(x) == maxcif)
        {
            if(x < res)
            {
                res = x;
            }
        }
    }

    fout << res;

	return 0;
}