#include <bits/stdc++.h>
using namespace std;

class Solution {
  public:
    vector<int> leaders(vector<int>& arr) {
        int n = arr.size();
        vector<int> ans;
        int maxi = -1;

        for(int i=n-1;i>=0;i--){
            if(arr[i]>=maxi){
                ans.push_back(arr[i]);
            }
            maxi = max(arr[i],maxi);
        }
        reverse(ans.begin(),ans.end());
        return ans;
    }
};

int main() {
    return 0;
}