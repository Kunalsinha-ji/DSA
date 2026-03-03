#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
    vector<int> rearrangeArray(vector<int>& nums) {
        int n = nums.size();
        vector<int> pos,neg;

        for(int k=0;k<n;k++){
            if(nums[k]<0){
                neg.push_back(nums[k]);
            }
            else{
                pos.push_back(nums[k]);
            }
        }

        for(int k=0;k<min(pos.size(),neg.size());k++){
            nums[k*2] = pos[k];
            nums[k*2+1] = neg[k];
        }

        if(pos.size()>neg.size()){
            for(int i=neg.size();i<pos.size();i++){
                nums.push_back(pos[i]);
            }
        }
        else{
            for(int i=pos.size();i<neg.size();i++){
                nums.push_back(neg[i]);
            }
        }
        return nums;
    }
};

int main() {
    return 0;
}