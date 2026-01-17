#include <bits/stdc++.h>
using namespace std;

// User function Template for C++
class DisjointSet{
    vector<int> rank,size,parent;

    public:
    DisjointSet(int n){
        rank.resize(n+1,0);
        size.resize(n+1,1);
        parent.resize(n+1);

        for(int i=0;i<=n;i++){
            parent[i] = i;
        }
    }

    // Find ultimate parent
    int FindUltPar(int u){
        if(parent[u]==u){
            return u;
        }

        return parent[u] = FindUltPar(parent[u]); // Path compression
    }

    // Union By Size
    void UnionBySize(int u,int v){
        int ult_pu = FindUltPar(u);
        int ult_pv = FindUltPar(v);

        if(ult_pu==ult_pv){
            return;
        }

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
    static bool cmp(vector<int> &v1,vector<int> &v2){
        return v1[2]<v2[2];
    }
  public:
    int kruskalsMST(int V, vector<vector<int>> &edges) {
        int ans = 0;
        DisjointSet ds(V);
        sort(edges.begin(),edges.end(),cmp);

        for(auto it: edges){
            int u = it[0];
            int v = it[1];
            int w = it[2];

            if(ds.FindUltPar(u)!=ds.FindUltPar(v)){
                ds.UnionBySize(u,v);
                ans += w;
            }
        }
        return ans;
    }
};

int main() {
    return 0;
}