#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
    int missingNumber(vector<int>& nums) {
        int n = nums.size();
        long long int sum1 = (n*(n+1))/2;
        long long int sum2 = 0;
        for(auto it: nums){
            sum2 += it;
        }
        return int(sum1-sum2);
    }
};

int main() {
    return 0;
}