#include <bits/stdc++.h>
using namespace std;

// Type - 1
class Solution {
  public:
    vector<int> nextLargerElement(vector<int>& arr) {
        int n = arr.size();
        vector<int> nge(n,-1);
        stack<int> st;

        for(int i=n-1;i>=0;i--){
            while(!st.empty() && st.top()<=arr[i]){
                st.pop();
            }
            if(st.empty())  nge[i] = -1;
            else nge[i] = st.top();
            st.push(arr[i]);
        }
        return nge;
    }
};

// Type - 2
class Solution {
public:
    vector<int> nextGreaterElement(vector<int>& nums1, vector<int>& nums2) {
        stack<int> st;
        int n = nums2.size();
        unordered_map<int,int> nge;

        for(int i=n-1;i>=0;i--){
            while(!st.empty() && st.top()<=nums2[i]){
                st.pop();
            }
            if(st.empty()){
                nge[nums2[i]] = -1;
            }
            else{
                nge[nums2[i]] = st.top();
            }
            st.push(nums2[i]);
        }

        for(int i=0;i<nums1.size();i++){
            nums1[i] = nge[nums1[i]];
        }
        return nums1;
    }
};

int main() {
    return 0;
}