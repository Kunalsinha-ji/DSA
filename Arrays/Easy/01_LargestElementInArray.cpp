#include <bits/stdc++.h>
using namespace std;

class Solution {
  public:
    int largest(vector<int> &arr) {
        int ans = 0;
        for(int i=0;i<arr.size();i++){
            ans = max(ans,arr[i]);
        }
        return ans;
    }
};


int main() {
    return 0;
}