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
    int largestIsland(vector<vector<int>>& grid) {
        int n = grid.size(), m = grid[0].size(), res = 0;

        DisjointSet ds(n*m);
        int dr[] = {1,0,-1,0};
        int dc[] = {0,1,0,-1};

        for(int r=0;r<n;r++){
            for(int c=0;c<m;c++){
                if(grid[r][c]){

                    for(int i=0;i<4;i++){
                        int nr = r+dr[i];
                        int nc = c+dc[i];

                        if(nr>=0 && nc>=0 && nc<m && nr<n && grid[nr][nc]){
                            int u = r*m + c;
                            int v = nr*m + nc;
                            ds.UnionBySize(u,v);
                        }
                    }
                }
            }
        }

        for(int i=0;i<n*m;i++){
            if(ds.FindUltPar(i)==i){
                int curr_size = ds.size[i];
                res = max(res,curr_size);
            }
        }

        for(int r=0;r<n;r++){
            for(int c=0;c<m;c++){
                if(grid[r][c]==0){
                    unordered_set<int> parents;
                    for(int i=0;i<4;i++){
                        int nr = r+dr[i];
                        int nc = c+dc[i];

                        if(nr>=0 && nc>=0 && nc<m && nr<n && grid[nr][nc]){
                            int par = ds.FindUltPar(nr*m+nc);
                            parents.insert(par);
                        }
                    }
                    int curr_size = 1;
                    for(auto it: parents){
                        curr_size += ds.size[it];
                    }
                    res = max(res,curr_size);
                }
            }
        }
        return res;
    }
};

int main() {
    return 0;
}