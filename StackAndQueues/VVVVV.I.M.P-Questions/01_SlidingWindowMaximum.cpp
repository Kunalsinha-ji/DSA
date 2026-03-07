#include <bits/stdc++.h>
using namespace std;

// Brute force
class Solution {
public:
    vector<int> maxSlidingWindow(vector<int>& arr, int k) {
        vector<int> ans;
        int n = arr.size();

        for(int i=0;i<n-k+1;i++){
            int maxi = arr[i];
            for(int j=i;j<i+k;j++){
                maxi = max(arr[j],maxi);
            }
            ans.push_back(maxi);
        }
        return ans;
    }
};

// Optimal - Using DEQUE
class Solution {
public:
    vector<int> maxSlidingWindow(vector<int>& nums, int k) {
        int n = nums.size();
        vector<int> ans;
        deque<int> dq;

        for(int i=0;i<n;i++){
            while(!dq.empty() && nums[dq.back()]<=nums[i]){
                dq.pop_back();
            }
            if(!dq.empty() && dq.front()==i-k){
                dq.pop_front();
            }
            dq.push_back(i);
            if(i>=k-1){
                ans.push_back(nums[dq.front()]);
            }
        }
        return ans;
    }
};

int main() {
    return 0;
}