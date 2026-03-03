#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
    vector<int> majorityElement(vector<int>& nums) {
        int n = nums.size();
        int ele1 = -1;
        int ele2 = -1;
        int c1 = 0,c2 = 0;

        for(auto it: nums){
            if(c1==0 && it!=ele2){
                c1++;
                ele1 = it;
            }
            else if(c2==0 && it!=ele1){
                c2++;
                ele2 = it;
            }
            else if(it==ele1){
                c1++;
            }
            else if(it==ele2){
                c2++;
            }
            else{
                c1--;c2--;
            }
        }

        c1=0,c2=0;

        for(int i=0;i<n;i++){
            if(nums[i]==ele1){
                c1++;
            }
            else if(nums[i]==ele2){
                c2++;
            }
        }

        vector<int> ans;
        if(c1>n/3){
            ans.push_back(ele1);
        }
        if(c2>n/3){
            ans.push_back(ele2);
        }

        return ans;
    }
};

int main() {
    return 0;
}