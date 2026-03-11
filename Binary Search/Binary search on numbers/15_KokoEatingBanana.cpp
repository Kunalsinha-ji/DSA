#include <bits/stdc++.h>
using namespace std;

class Solution {
    long long int solve(vector<int> &piles,int eats){
        long long int ans = 0;
        for(auto it: piles){
            int rem = it%eats ? 1 : 0;
            ans += (it/eats) + rem;
        }
        return ans;
    }
public:
    int minEatingSpeed(vector<int>& piles, int h) {
        int low = 1;
        int high = *max_element(piles.begin(),piles.end());

        int ans = high;

        while(low<=high){
            int mid = low + (high-low)/2;

            long long int res = solve(piles,mid);
            if(res<=h){
                ans = mid;
                high = mid - 1;
            }
            else{
                low = mid + 1;
            }
        }
        return ans;
    }
};

int main() {
    return 0;
}