#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
    int minimumEffortPath(vector<vector<int>>& heights) {
        int n = heights.size(), m = heights[0].size();

        vector<vector<int>> effort(n,vector<int> (m,1e9));
        effort[0][0] = 0;

        priority_queue<pair<int,pair<int,int>>, vector<pair<int,pair<int,int>>>, greater<pair<int,pair<int,int>>>> q;
        q.push({0,{0,0}});

        int dr[] = {1,0,-1,0};
        int dc[] = {0,1,0,-1};
        while(!q.empty()){
            int maxEff = q.top().first;
            int r = q.top().second.first;
            int c = q.top().second.second;
            if(r==n-1 && c==m-1)    return maxEff;
            q.pop();

            for(int i=0;i<4;i++){
                int nr = r + dr[i];
                int nc = c + dc[i];

                if(nr>=0 && nc>=0 && nr<n && nc<m){
                    int eff = abs(heights[r][c]-heights[nr][nc]);
                    if(effort[nr][nc]>max(maxEff,eff)){
                        effort[nr][nc] = max(maxEff,eff);
                        q.push({effort[nr][nc],{nr,nc}});
                    }
                }
            }
        }
        return effort[n-1][m-1];
    }
};

int main() {
    return 0;
}