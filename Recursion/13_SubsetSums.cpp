#include <bits/stdc++.h>
using namespace std;

class Solution {
    void solve(vector<int> &arr,int i,int sum,vector<int> &ans){
        if(i==arr.size()){
            ans.push_back(sum);
            return;
        }

        solve(arr,i+1,sum,ans);
        sum += arr[i];
        solve(arr,i+1,sum,ans);
        sum -= arr[i];
    }
  public:
    vector<int> subsetSums(vector<int>& arr) {
        vector<int> ans;
        solve(arr,0,0,ans);
        return ans;
    }
};

int main() {
    return 0;
}