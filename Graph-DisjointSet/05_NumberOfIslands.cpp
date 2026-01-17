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
  public:
    vector<int> numOfIslands(int n, int m, vector<vector<int>> &operators) {
        vector<int> ans;

        DisjointSet ds(n*m);

        vector<vector<int>> grid(n,vector<int> (m,0));
        int dr[] = {1,0,-1,0};
        int dc[] = {0,1,0,-1};

        int count = 0;
        for(auto it: operators){
            int r = it[0];
            int c = it[1];

            if(grid[r][c]){
                ans.push_back(count);
                continue;
            }

            grid[r][c] = 1;
            count++;

            for(int i=0;i<4;i++){
                int nr = r + dr[i];
                int nc = c + dc[i];

                if(nr>=0 && nc>=0 && nc<m && nr<n && grid[nr][nc]){
                    int u = r*m + c;
                    int v = nr*m+nc;

                    if(ds.FindUltPar(u)!=ds.FindUltPar(v)){
                        count--;
                        ds.UnionBySize(u,v);
                    }
                }
            }
            ans.push_back(count);
        }
        return ans;
    }
};


int main() {
    return 0;
}