#include <bits/stdc++.h>
using namespace std;

// Brute force
class Solution {
public:
    int maxProduct(vector<int>& nums) {
        int n = nums.size();

        int res = INT_MIN;
        for(int i=0;i<n;i++){
            for(int j=i;j<n;j++){
                int prod = 1;
                for(int k=i;k<=j;k++){
                    prod *= nums[k];
                }
                res = max(prod,res);
            }
        }
        return res;
    }
};

// Better
class Solution {
public:
    int maxProduct(vector<int>& nums) {
        int n = nums.size();

        int res = INT_MIN;
        for(int i=0;i<n;i++){
            int prod = 1;
            for(int j=i;j<n;j++){
                prod *= nums[j];
                res = max(prod,res);
            }
        }
        return res;
    }
};

// Optimal
class Solution {
public:
    int maxProduct(vector<int>& nums) {
        int n = nums.size();
        int res = INT_MIN;

        int prod1 = 1, prod2 = 1;
        for(int i=0;i<n;i++){
            if(prod1==0)  prod1 = 1;
            if(prod2==0)  prod2 = 1;

            prod1 *= nums[i];
            prod2 *= nums[n-1-i];
            res = max({res,prod1,prod2});
        }
        return res;
    }
};
int main() {
    return 0;
}