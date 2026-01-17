#include <bits/stdc++.h>
using namespace std;

// User function Template for C++

class Solution {
    int mod = 100000;
  public:
    int minimumMultiplications(vector<int>& arr, int start, int end) {
        // code here
        vector<int> vis(100000,1e9);
        queue<pair<int,int>> q;
        q.push({0,start});
        vis[start] = 1;

        while(!q.empty()){
            int num = q.front().second;
            int muls = q.front().first;
            q.pop();

            if(num==end)    return muls;

            for(int i=0;i<arr.size();i++){
                int new_num = (num*arr[i])%mod;

                if(vis[new_num]>muls+1){
                    vis[new_num] = muls+1;
                    q.push({muls+1,new_num});
                }
            }
        }
        return -1;
    }
};


int main() {
    return 0;
}