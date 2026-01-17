#include <bits/stdc++.h>
using namespace std;

class DisjointSet {
    public:
    vector<int> rank,parent;

    DisjointSet(int n){
        rank.resize(n+1,0);
        parent.resize(n+1);

        for(int i=0;i<=n;i++){
            parent[i] = i;
        }
    }

    // Find Ultimate Parent
    int FindUltPar(int u){
        if(parent[u]==u){
            return u;
        }

        return parent[u] = FindUltPar(parent[u]);
    }

    // Union By Rank
    void UnionByRank(int u,int v){
        int ult_pu = FindUltPar(u);
        int ult_pv = FindUltPar(v);

        if(ult_pu==ult_pv){
            return;
        }

        if(rank[ult_pu]>rank[ult_pv]){
            parent[ult_pv] = ult_pu;
        }
        else if(rank[ult_pv]>rank[ult_pu]){
            parent[ult_pu] = ult_pv;
        }
        else{
            parent[ult_pv] = ult_pu;
            rank[ult_pu]++;
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
            }
            else{
                ds.UnionByRank(u,v);
            }
        }

        int independent_components = 0;

        for(int i=0;i<n;i++){
            if(ds.parent[i]==i){
                independent_components++;
            }
        }

        if(extra_links<independent_components-1){
            return -1;
        }
        return independent_components-1;
    }
};

int main() {
    return 0;
}