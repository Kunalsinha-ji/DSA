#include <bits/stdc++.h>
using namespace std;

class Solution {
    bool check(vector<string> &v, int r,int c,int n){
        for(int i=0;i<n;i++){
            if(v[r][i]=='Q'){
                return 0;
            }
        }

        int i=r,j=c;
        while(i>=0 && j>=0){
            if(v[i][j]=='Q'){
                return 0;
            }
            i--;j--;
        }

        i = r,j =c;
        while(i<n && j>=0){
            if(v[i][j]=='Q'){
                return 0;
            }
            i++;j--;
        }
        return 1;
    }
    bool solve(vector<vector<string>> &ans, vector<string> v,int c,int n){
        if(c==n){
            ans.push_back(v);
            return 1;
        }

        for(int i=0;i<n;i++){
            if(check(v,i,c,n)){
                v[i][c] = 'Q';
                bool k = solve(ans,v,c+1,n);
                if(k==0){
                    v[i][c] = '.';
                }
            }
        }
        return 0;
    }
public:
    vector<vector<string>> solveNQueens(int n) {
        vector<vector<string>> ans;
        string str(n,'.');
        vector<string> v;
        for(int i=0;i<n;i++){
            v.push_back(str);
        }

        solve(ans,v,0,n);
        return ans;
    }
};

int main() {
    return 0;
}