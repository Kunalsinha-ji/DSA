#include <bits/stdc++.h>
using namespace std;

class Solution {
    int Profit(vector<int>& prices, int k) {
        int n = prices.size();

        // Space optimization -> similar to que: 3
        vector<int> prev(2*k+1,0) ,curr (2*k+1,0);
        for(int i=n-1;i>=0;i--){
            for(int cnt=1;cnt<=2*k;cnt++){
                if(cnt%2==0){
                    int take = prev[cnt-1] - prices[i];
                    int ntake = prev[cnt];
                    curr[cnt] = max(take,ntake);
                }
                else{
                    int sell = prev[cnt-1] + prices[i];
                    int nsell = prev[cnt];
                    curr[cnt] = max(sell,nsell);
                }
            }
            prev = curr;
        }
        return prev[2*k];
    }
public:
    int maxProfit(int k, vector<int>& prices) {
        return Profit(prices,k);
    }
};

int main() {
    return 0;
}