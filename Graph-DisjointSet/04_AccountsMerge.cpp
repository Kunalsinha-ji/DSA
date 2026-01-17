#include <bits/stdc++.h>
using namespace std;

class DisjointSet{
    public:

    vector<int> size;
    vector<int> parent;
    DisjointSet (int n){
        size.resize(n+1,1);
        parent.resize(n+1);

        for(int i=0;i<=n;i++){
            parent[i] = i;
        }
    }

    // Find Ultimate Parent
    int FindUltPar(int u){
        if(parent[u]==u)    return u;

        return parent[u] = FindUltPar(parent[u]);
    }

    // Union By Size
    void UnionBySize(int u,int v){
        int ult_pu = FindUltPar(u);
        int ult_pv = FindUltPar(v);

        if(ult_pu==ult_pv)  return;

        if(size[ult_pu]>=size[ult_pv]){
            size[ult_pu] += size[ult_pv];
            parent[ult_pv] = ult_pu;
        }
        else{
            size[ult_pv] += size[ult_pu];
            parent[ult_pu] = ult_pv;
        }
    }
};

class Solution {
public:
    vector<vector<string>> accountsMerge(vector<vector<string>>& accounts) {
        int n = accounts.size();
        DisjointSet ds(n);
        unordered_map<string,int> mp;

        for(int i=0;i<n;i++){
            for(int j=1;j<accounts[i].size();j++){
                string str = accounts[i][j];
                if(mp.find(str)!=mp.end()){
                    int ind = mp[str];
                    int curr_ind = i;
                    ds.UnionBySize(ind,curr_ind);
                }
                else{
                    mp[str] = i;
                }
            }
        }

        vector<vector<string>> temp(n);

        for(auto it: mp){
            int ind = it.second;
            string str = it.first;
            ind = ds.FindUltPar(ind);

            temp[ind].push_back(str);
        }

        vector<vector<string>> res;
        for(int i=0;i<n;i++){
            if(temp[i].size()==0)   continue;
            vector<string> v;
            v.push_back(accounts[i][0]);

            sort(temp[i].begin(),temp[i].end());
            for(auto it: temp[i]){
                v.push_back(it);
            }
            res.push_back(v);
        }
        return res;
    }
};


int main() {
    return 0;
}