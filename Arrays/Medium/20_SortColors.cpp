#include <bits/stdc++.h>
using namespace std;

// This is counting solution
class Solution {
public:
    void sortColors(vector<int>& nums) {
        int zero = 0,one = 0;
        int n = nums.size();

        for(int i=0;i<n;i++){
            if(nums[i]==0){
                zero++;
            }
            if(nums[i]==1){
                one++;
            }
        }

        for(int i=0;i<n;i++){
            if(zero){
                nums[i] = 0;
                zero--;
            }
            else if(one){
                nums[i] = 1;
                one--;
            }
            else{
                nums[i] = 2;
            }
        }
    }
};

// better approach
class Solution {
public:
    void sortColors(vector<int>& nums) {
        int n = nums.size();
        int i = 0,j = 0,k = n-1;

        while(j<=k){
            if(nums[j]==0){
                swap(nums[i],nums[j]);
                i++;
                j++;
            }
            else if(nums[j]==2){
                swap(nums[j],nums[k]);
                k--;
            }
            else{
                j++;
            }
        }
    }
};

int main() {
    return 0;
}