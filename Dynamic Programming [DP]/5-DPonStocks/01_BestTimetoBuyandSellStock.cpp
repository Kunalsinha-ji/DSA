#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
    int maxProfit(vector<int>& prices) {
        int ans = 0;
        int mini = 1e9;

        for(int i=0;i<prices.size();i++){
            mini = min(mini,prices[i]);
            int diff = prices[i]-mini;
            ans = max(ans,diff);
        }
        return ans;
    }
};

int main() {
    return 0;
}