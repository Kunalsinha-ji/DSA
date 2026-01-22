#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
    int missingNumber(vector<int>& nums) {
        int n = nums.size();

        long long int sum = (n*(n+1))/2;

        for(int i=0;i<nums.size();i++){
            long long int k = nums[i];
            sum -= k;
        }
        return int(sum);
    }
};

int main() {
    return 0;
}