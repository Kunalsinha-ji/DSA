#include <bits/stdc++.h>
using namespace std;

class Solution {
    vector<int> nextSmallerEle(vector<int>& arr) {
        int n = arr.size();
        vector<int> nse(n,n);
        stack<int> st;

        for(int i=n-1;i>=0;i--){
            while(!st.empty() && arr[st.top()]>=arr[i]){
                st.pop();
            }
            if(!st.empty())
                nse[i] = st.top();
            st.push(i);
        }
        return nse;
    }
public:
    int largestRectangleArea(vector<int>& heights) {
        int n = heights.size();
        vector<int> prevSmaller(n,-1);
        stack<int> st;

        vector<int> nextSmaller = nextSmallerEle(heights);

        int maxArea = 0;

        for(int i=0;i<n;i++){
            while(!st.empty() && heights[st.top()]>=heights[i]){
                st.pop();
            }
            if(!st.empty()){
                prevSmaller[i] = st.top();
            }
            st.push(i);

            int length = heights[i];
            int base = nextSmaller[i] - prevSmaller[i] - 1;
            int currArea = length * base;
            maxArea = max(maxArea,currArea);
        }
        return maxArea;
    }
};

int main() {
    return 0;
}