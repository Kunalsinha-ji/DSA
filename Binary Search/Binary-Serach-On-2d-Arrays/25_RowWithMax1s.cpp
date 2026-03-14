#include <bits/stdc++.h>
using namespace std;

// User function template for C++
class Solution {
  public:
    int rowWithMax1s(vector<vector<int>> &arr) {
        int ans = -1;
        int maxCnt = 0;
        int n = arr.size();
        int m = arr[0].size();

        for(int i=0;i<n;i++){
            int low = 0, high = m-1;

            int ind = -1;
            while(low<=high){
                int mid = low + (high-low)/2;

                if(arr[i][mid]==0){
                    ind = mid;
                    low = mid + 1;
                }
                else{
                    high = mid - 1;
                }
            }
            if(ind==-1){
                return i;
            }
            int cntZeroes = ind + 1;
            int ones = m - cntZeroes;
            if(ones>maxCnt){
                maxCnt = ones;
                ans = i;
            }
        }
        return ans;
    }
};

int main() {
    return 0;
}