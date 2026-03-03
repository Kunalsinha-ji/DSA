#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
    int findKthLargest(vector<int>& nums, int k) {
        int n = nums.size();
        sort(nums.begin(),nums.end());
        return nums[n-k];
    }
};

class Solution {
public:
    // Duplicates allowed
    int findKthLargest(vector<int>& nums, int k) {
        priority_queue<int,vector<int>,greater<int>> pq;

        for(auto it: nums){
            pq.push(it);
            if(pq.size()>k){
                pq.pop();
            }
        }

        if(pq.size()<k) return -1;
        return pq.top();
    }
};

int main() {
    return 0;
}