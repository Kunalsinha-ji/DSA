#include <bits/stdc++.h>
using namespace std;

class DisjointSet{
    public:
    vector<int> rank,parent;

    DisjointSet(int n){
        rank.resize(n+1,0);
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
    int swimInWater(vector<vector<int>>& grid) {
        int n = grid.size();
        int m = grid[0].size();

        DisjointSet ds(n*m);
        int start = max(grid[0][0],grid[n-1][m-1]);

        int dr[] = {1,0,-1,0};
        int dc[] = {0,1,0,-1};

        while(true){
            for(int r=0;r<n;r++){
                for(int c=0;c<m;c++){
                    if(grid[r][c]<=start){
                        for(int i=0;i<4;i++){
                            int nr = r + dr[i];
                            int nc = c + dc[i];

                            if(nr>=0 && nc>=0 && nc<m && nr<n && grid[nr][nc]<=start){
                                int u = r*m+c;
                                int v = nr*m+nc;
                                ds.UnionByRank(u,v);
                            }
                        }
                    }
                    if(ds.FindUltPar(0)==ds.FindUltPar(n*m-1)){
                        return start;
                    }
                }
            }
            start++;
        }
        return start;
    }
};

int main() {
    return 0;
}