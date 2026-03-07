#include <bits/stdc++.h>
using namespace std;

// Brute force
class Solution {
  public:
    int celebrity(vector<vector<int>>& mat) {
        int n = mat.size();
        vector<int>knowsMe(n,0),iKnow(n,0);

        for(int i=0;i<n;i++){
            for(int j=0;j<n;j++){
                if(i==j)    continue;
                if(mat[i][j]){
                    iKnow[i]++;
                    knowsMe[j]++;
                }
            }
        }

        for(int i=0;i<n;i++){
            if(iKnow[i]==0 && knowsMe[i]==n-1){
                return i;
            }
        }
        return -1;
    }
};

// Optimal - Using 2 pointers top<bottom and top knows bottom or bottom knows top
class Solution {
  public:
    int celebrity(vector<vector<int>>& mat) {
        int n = mat.size();

        int top = 0,bottom = n-1;

        while(top<bottom){
            if(mat[top][bottom]){
                top += 1;
            }
            else if(mat[bottom][top]){
                bottom -= 1;
            }
            else{
                top++;bottom--;
            }
        }

        if(top>bottom){
            return -1;
        }
        if(top==bottom){
            for(int i=0;i<n;i++){
                if(top==i)  continue;
                if(mat[top][i]==1 || mat[i][top]==0){
                    return -1;
                }
            }
        }
        return top;
    }
};

int main() {
    return 0;
}