#include <fstream>
#include <algorithm>
#include <iostream>
std::ifstream fin("aeriana.in");
std::ofstream fout("aeriana.out");

int sumCif(int x)
{
    int res = 0;
    while(x > 0)
    {
        res += x % 10;
        x /= 10;
    }
    return res;
}

bool isPrime(int x)
{
    if(x < 2)
    {
        return false;
    }
    for(int i = 2; i * i <= x; i++)
    {
        if(x % i == 0)
        {
            return false;
        }
    }
    return true;
}

int main()
{
    int n, c, a1, a2, h1, m1, h2, m2, hres = 0, mres = 0, maxD = -1;

    fin >> c >> n;

    if(c == 1)
    {
        while(n--)
        {
            fin >> a1 >> a2 >> h1 >> m1 >> h2 >> m2;

            int zbor1 = 60 * h1 + m1;
            int zbor2 = 60 * h2 + m2;

            int res = std::abs(zbor1 - zbor2);

            if(zbor1 >= zbor2)
            {
                res = 24 * 60 - zbor1 + zbor2;
                if(res < 0)
                {
                    res += 60 * 24;
                }
                if(res > maxD)
                {
                    maxD = res;

                    hres = res / 60;
                    mres = res % 60;
                }
            }
            else
            {
                res = zbor2 - zbor1;
                if(res > maxD)
                {
                    maxD = res;

                    hres = res / 60;
                    mres = res % 60;
                }
            }

        }
        fout << hres << ' ' << mres;
    }
    else
    {
        while(n--)
        {
            fin >> a1 >> a2 >> h1 >> m1 >> h2 >> m2;\

            if(isPrime(a1) && (a2 % sumCif(a1) == 0))
            {
                std::swap(h1, h2);
                std::swap(m1, m2);
            }
            int zbor1 = 60 * h1 + m1;
            int zbor2 = 60 * h2 + m2;

            int res = std::abs(zbor1 - zbor2);

            if(zbor1 >= zbor2)
            {
                res = 24 * 60 - zbor1 + zbor2;
                if(res < 0)
                {
                    res += 60 * 24;
                }
                if(res > maxD)
                {
                    maxD = res;

                    hres = res / 60;
                    mres = res % 60;
                }
            }
            else
            {
                res = zbor2 - zbor1;
                if(res > maxD)
                {
                    maxD = res;

                    hres = res / 60;
                    mres = res % 60;
                }
            }

        }
        fout << hres << ' ' << mres;
    }

	return 0;
}