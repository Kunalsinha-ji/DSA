#include <bits/stdc++.h>
using namespace std;

class Solution {
  public:
    vector<int> kLargest(vector<int>& nums, int k) {
        int n = nums.size();
        set<int> st;

        for(auto it: nums){
            st.insert(it);
            if(st.size()>k){
                st.erase(*st.begin());
            }
        }

        vector<int> ans;
        for(auto it: st){
            ans.push_back(it);
        }
        reverse(ans.begin(),ans.end());
        return ans;
    }
};

// If duplicates are considered
class Solution {
  public:
    vector<int> kLargest(vector<int>& nums, int k) {
        priority_queue<int,vector<int>,greater<int>> pq;

        for(auto it: nums){
            pq.push(it);
            if(pq.size()>k){
                pq.pop();
            }
        }

        vector<int> ans;
        while(!pq.empty()){
            ans.push_back(pq.top());
            pq.pop();
        }
        reverse(ans.begin(),ans.end());
        return ans;
    }
};


int main() {
    return 0;
}