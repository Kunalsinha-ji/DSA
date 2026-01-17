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

        if(size[ult_pu]>size[ult_pv]){
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
    int makeConnected(int n, vector<vector<int>>& connections) {
        DisjointSet ds(n);

        int extra_links = 0;
        for(auto it: connections){
            int u = it[0];
            int v = it[1];

            if(ds.FindUltPar(u)==ds.FindUltPar(v)){
                extra_links++;
                continue;
            }
            else{
                ds.UnionBySize(u,v);
            }
        }

        int independent_comp = 0;
        for(int i=0;i<n;i++){
            if(ds.parent[i]==i){
                independent_comp++;
            }
        }

        if(independent_comp-1<=extra_links) return independent_comp-1;
        return -1;
    }
};

int main() {
    return 0;
}