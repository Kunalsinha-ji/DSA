#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
    vector<int> nextGreaterElements(vector<int>& nums) {
        int n = nums.size();
        vector<int> nge(n,-1);
        stack<int> st;

        for(int i=2*n-1;i>=0;i--){
            int ele = nums[i%n];
            while(!st.empty() && st.top()<=ele){
                st.pop();
            }
            if(!st.empty() && i<n) nge[i] = st.top();
            st.push(ele);
        }
        return nge;
    }
};

int main() {
    return 0;
}