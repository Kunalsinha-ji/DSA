#include <bits/stdc++.h>
using namespace std;

bool check(vector<int>& nums) {
    for(int i=1;i<nums.size();i++){
        if(nums[i]<nums[i-1]){
            return 0;
        }
    }
    return 1;
}

int main() {
    return 0;
}