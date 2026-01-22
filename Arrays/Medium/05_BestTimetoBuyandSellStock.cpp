#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
    int maxProfit(vector<int>& prices) {
        int profit = 0;
        int mini = prices[0];
        int maxi = prices[0];

        for(int i=0;i<prices.size();i++){
            mini = min(mini,prices[i]);
            profit = max(profit,(prices[i]-mini));
        }
        return profit;
    }
};

int main() {
    return 0;
}