#include <bits/stdc++.h>
using namespace std;

// User function Template for C++
class DisjointSet{
    vector<int> rank;
    vector<int> size;
    vector<int> parent;

    public:
    DisjointSet (int n){
        rank.resize(n+1,0);
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

    // Union By Rank
    void UnionByRank(int u,int v){
        int ult_pu = FindUltPar(u);
        int ult_pv = FindUltPar(v);

        if(ult_pu==ult_pv)  return;

        if(rank[ult_pu]>rank[ult_pv]){
            parent[ult_pv] = ult_pu;
        }
        else if(rank[ult_pu]<rank[ult_pv]){
            parent[ult_pu] = ult_pv;
        }
        else{
            parent[ult_pv] = ult_pu;
            rank[ult_pu]++;
        }
    }
};
class Solution {
    static bool cmp(vector<int> v1,vector<int> v2){
        return v1[2]<v2[2];
    }
  public:
    int kruskalsMST(int V, vector<vector<int>> &edges) {
        // code here
        DisjointSet ds(V);
        int ans = 0;

        sort(edges.begin(),edges.end(),cmp);

        for(auto it: edges){
            int u = it[0];
            int v = it[1];
            int wt = it[2];

            if(ds.FindUltPar(u)==ds.FindUltPar(v)){
                continue;
            }
            else{
                ds.UnionByRank(u,v);
                ans += wt;
            }
        }
        return ans;
    }
};

int main() {
    return 0;
}