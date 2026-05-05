import requests
url = 'http://localhost:5000/recheck_weird_percent'
#print(check_homework(['eric.mester', 'AlexVasiluta', 'TREYWAY', 'atodo'], ['/problems/1', '/problems/3']))
'''json_data = {'previous_submissions' : [4,6,7,8,9,10],
             #'current_submission' : "#include <bits/stdc++.h> using namespace std; const long long MOD = 1'000'000'007LL; int main() { ios::sync_with_stdio(false); cin.tie(nullptr); int n; long long k; if (!(cin >> n >> k)) return 0; vector<int> v(n); for (int i = 0; i < n; ++i) cin >> v[i]; vector<long long> cnt(n + 2, 0); cnt[0] = k; // all colours unused at start long long answer = 1; for (int i = 0; i < n; ++i) { int t = v[i]; if (cnt[t] == 0) { // impossible answer = 0; break; } answer = (answer * (cnt[t] % MOD)) % MOD; cnt[t]--; cnt[t + 1]++; // colour now used one more time } cout << answer % MOD << ' '; return 0; }"}
             #'current_submission' : "#include <bits/stdc++.h> using namespace std; ifstream fin (""armonica.in""); ofstream fout (""armonica.out""); long long int b; long long int n,nrdiv; vector<long long int>av; vector<long long int>cv; vector<long long int>div_b; unordered_map<long long int, bool>fr; unordered_map<long long int,bool>fr2; int main() { fin>>b; ///b=2ac/(a+c) ///a=cb/(2c-b) ///bc/(2c-b)=b/2+b^2/(2*(2c-b)) ///daca c este valid, trebuie sa respecte si 2c-b = D(+)b^2 ///iterez prin toate posibile ///prea lent, vreau sa ma uit la divizorii lui b ///divizorii lui b^2 sunt di*dj unde di,j=divizori ai lui b, nu neaparat distincti for(long long int d=1LL;d*d<=b;d++) { if(b%d==0LL) { long long int d2=b/d; div_b.push_back(d); nrdiv++; if(d2!=d)div_b.push_back(d2),nrdiv++; } } for(long long int i=0LL;i<nrdiv;i++) { for(long long int j=0LL;j<nrdiv;j++) { long long int div1=div_b[i]*div_b[j]; if(fr.find(div1)==fr.end()) { fr[div1]=true; long long int c=(b+div1)/2LL; if((b+div1)%2LL==0LL and 2LL*c-b!=0LL and b*c%(2LL*c-b)==0LL) { if(fr2.find(c)==fr2.end())fr2[c]=true,cv.push_back(c),av.push_back(b*c/(2LL*c-b)),n++; if(c!=(b*c/(2LL*c-b))) { if(fr2.find(b*c/(2LL*c-b))==fr2.end())fr2[b*c/(2LL*c-b)]=true,cv.push_back(b*c/(2LL*c-b)),n++,av.push_back(c); } } } } } fout<<n<<"" ""; for(long long int i=0LL;i<n;i++) { fout<<av[i]<<"" ""<<cv[i]<<"" ""; } fin.close(); fout.close(); return 0; }"}
             'current_submission' : {
                'solution_id' : 11,
                'user_id': 'eric.mester',
                'problem_id': '/problems/1390',
                'score': '100',
                'timestamp': '1772295751',

                'text' : "#include <fstream> #include <algorithm> using namespace std; ifstream cin(""proiecte.in""); ofstream cout(""proiecte.out""); int v[200001]; int velemente[201]; int vrasp[201]; int main() { int maxim, nrproiecte; cin >> maxim >> nrproiecte; int cntmare=0; for (int i=1; i<=nrproiecte; i++) { int n; cin >> n; for (int i=1; i<=n; i++) { cin >> v[i]; } int cntvoturi=0; int elementcandidat=0; int nrnumere=n; for (int i=1; i<=nrnumere; i++) { if (cntvoturi==0) { elementcandidat=v[i]; cntvoturi++; } else { if (v[i]==elementcandidat) { cntvoturi++; } else cntvoturi--; } } int cnt=0; for (int i=1; i<=nrnumere; i++) { if (v[i]==elementcandidat) cnt++; } if (cnt>nrnumere/2) velemente[++cntmare]=elementcandidat; } sort(velemente+1, velemente+cntmare+1); int cnttemp=1, cntmax=-1, cntrasp=0; for (int i=2; i<=cntmare; i++) { if (velemente[i]==velemente[i-1]) cnttemp++; else { if (cnttemp>cntmax) { cntmax=cnttemp; cntrasp=0; vrasp[++cntrasp]=velemente[i-1]; } else if (cnttemp==cntmax) { vrasp[++cntrasp]=velemente[i-1]; } cnttemp=1; } } if (cnttemp>cntmax) { cntmax=cnttemp; cntrasp=0; vrasp[++cntrasp]=velemente[cntmare]; } else if (cnttemp==cntmax) { vrasp[++cntrasp]=velemente[cntmare]; } for (int i=1; i<=cntrasp; i++) { cout << vrasp[i] << "" ""; } return 0; }"}
                }
            '''             
#json_data = {'solution_id': 11}
json_data = {'previous_submissions' : [4,6,7,8],
             'current_submission' : 11
            }
#json_data = {'solution_ids' : [8,9,10]}
#json_data = {'user_ids' : ['eric.mester' , 'AlexVasiluta'] , 'problem_ids' : ['/problems/1', '/problems/3']}
response = requests.post(url, json=json_data)
print(response.text)
if response.status_code == 200:
    print('JSON data sent successfully!')
else:
    print('Failed to send JSON data:', response.status_code)