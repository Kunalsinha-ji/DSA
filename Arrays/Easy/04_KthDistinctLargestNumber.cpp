#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
    int findKthLargest(vector<int>& nums, int k) {
        int n = nums.size();
        set<int> st;

        for(auto it: nums){
            st.insert(it);
            if(st.size()>k){
                st.erase(*st.begin());
            }
        }
        return *st.begin();
    }
};

int main() {
    return 0;
}