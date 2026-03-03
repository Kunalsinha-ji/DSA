#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
    int majorityElement(vector<int>& nums) {
        int n = nums.size();
        int ele = -1;
        int cnt = 0;

        for(auto it: nums){
            if(cnt==0){
                ele = it;
                cnt++;
            }
            else if(ele==it){
                cnt++;
            }
            else{
                cnt--;
            }
        }

        // Check
        int c = 0;
        for(auto it: nums){
            if(it==ele){
                c++;
            }
        }

        if(c<=n/2){
            return -1;
        }
        return ele;
    }
};

int main() {
    return 0;
}