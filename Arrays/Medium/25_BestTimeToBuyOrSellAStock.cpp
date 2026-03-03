#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
    int maxProfit(vector<int>& prices) {
        int mini = INT_MAX;
        int n = prices.size();
        int maxi = 0;

        for(int i=0;i<n;i++){
            mini = min(mini,prices[i]);
            maxi = max(maxi,prices[i]-mini);
        }
        return maxi;
    }
};

int main() {
    return 0;
}