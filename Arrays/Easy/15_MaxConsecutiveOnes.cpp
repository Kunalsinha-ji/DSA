#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
    int findMaxConsecutiveOnes(vector<int>& nums) {
        int ans = 0;
        int cnt = 0;

        for(auto it: nums){
            if(it==0){
                cnt = 0;
            }
            else{
                cnt += 1;
            }
            ans = max(cnt,ans);
        }
        return ans;
    }
};

int main() {
    return 0;
}