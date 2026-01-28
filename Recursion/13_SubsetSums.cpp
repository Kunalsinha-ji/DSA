#include <bits/stdc++.h>
using namespace std;

class Solution {
    void solve(vector<int> &ans,vector<int> &arr,int i,int sum){
        if(i==arr.size()){
            ans.push_back(sum);
            return;
        }

        solve(ans,arr,i+1,sum);
        solve(ans,arr,i+1,sum+arr[i]);
    }
  public:
    vector<int> subsetSums(vector<int>& arr) {
        vector<int> ans;
        solve(ans,arr,0,0);
        return ans;
    }
};

int main() {
    return 0;
}