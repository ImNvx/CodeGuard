#include <bits/stdc++.h>
using namespace std;

signed main()
{
    cin.tie(nullptr)->sync_with_stdio(false);

#ifndef LOCAL
    freopen("cod.in", "r", stdin);
    freopen("cod.out", "w", stdout);
#endif

    int n;
    cin >> n;

    pair<int, int> rez = {-1, -1};

    for (int i = 0; i < n; ++i)
    {
        int x;
        cin >> x;

        int cop = x;

        do
        {
            if (cop % 10 > rez.first)
            {
                rez = {cop % 10, x};
            }
            else if (cop % 10 == rez.first)
            {
                rez.second = min(rez.second, x);
            }

            cop /= 10;
        }
        while (cop);
    }

    cout << rez.second;

    return 0;
}
```
