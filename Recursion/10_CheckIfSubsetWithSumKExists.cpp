#include <bits/stdc++.h>
using namespace std;

class Solution {
    bool solve(vector<int> &arr,int sum,int i){
        if(sum==0){
            return 1;
        }
        if(i<0){
            return 0;
        }

        bool ntake = solve(arr,sum,i-1);
        if(arr[i]<=sum){
            bool take = solve(arr,sum-arr[i],i-1);
            ntake = take | ntake;
        }
        return ntake;
    }
  public:
    bool checkSubsequenceSum(int n, vector<int>& arr, int k) {
        return solve(arr,k,n-1);
    }
};

int main() {
    return 0;
}