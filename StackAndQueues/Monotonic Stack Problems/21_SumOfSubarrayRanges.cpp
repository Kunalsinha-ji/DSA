#include <bits/stdc++.h>
using namespace std;

// Takes more Iterations
class Solution {
    vector<int> nextGreaterElement(vector<int>& arr) {
        int n = arr.size();
        vector<int> nge(n,n);
        stack<int> st;

        for(int i=n-1;i>=0;i--){
            while(!st.empty() && arr[st.top()]<=arr[i]){
                st.pop();
            }
            if(st.empty())  nge[i] = n;
            else nge[i] = st.top();
            st.push(i);
        }
        return nge;
    }
    vector<int> prevGreaterEqualElement(vector<int>& arr) {
        int n = arr.size();
        vector<int> pgee(n,-1);
        stack<int> st;

        for(int i=0;i<n;i++){
            while(!st.empty() && arr[st.top()]<arr[i]){
                st.pop();
            }
            if(st.empty())  pgee[i] = -1;
            else pgee[i] = st.top();
            st.push(i);
        }
        return pgee;
    }
    vector<int> nextSmallerElement(vector<int>& arr) {
        int n = arr.size();
        vector<int> nse(n,n);
        stack<int> st;

        for(int i=n-1;i>=0;i--){
            while(!st.empty() && arr[st.top()]>=arr[i]){
                st.pop();
            }
            if(st.empty())  nse[i] = n;
            else nse[i] = st.top();
            st.push(i);
        }
        return nse;
    }
    vector<int> prevSmallerEqualElement(vector<int>& arr) {
        int n = arr.size();
        vector<int> psee(n,-1);
        stack<int> st;

        for(int i=0;i<n;i++){
            while(!st.empty() && arr[st.top()]>arr[i]){
                st.pop();
            }
            if(st.empty())  psee[i] = -1;
            else psee[i] = st.top();
            st.push(i);
        }
        return psee;
    }
public:
    long long subArrayRanges(vector<int>& nums) {
        int n = nums.size();
        vector<int> nge,pgee,psee,nse;
        nge = nextGreaterElement(nums);
        pgee = prevGreaterEqualElement(nums);
        nse = nextSmallerElement(nums);
        psee = prevSmallerEqualElement(nums);

        long long sumMins = 0;
        for(int i=0;i<n;i++){
            long long int num = nums[i];
            long long int prev = psee[i];
            long long int next = nse[i];

            long long int lm = i - prev;
            long long int rm = next - i;
            long long int add = ((lm*rm) * num * 1LL);
            sumMins = (sumMins+add);
        }

        long long sumMaxs = 0;
        for(int i=0;i<n;i++){
            long long int num = nums[i];
            long long int prev = pgee[i];
            long long int next = nge[i];

            long long int lm = i - prev;
            long long int rm = next - i;
            long long int add = ((lm*rm) * num * 1LL);
            sumMaxs = (sumMaxs+add);
        }
        return sumMaxs-sumMins;
    }
};

// Takes less iterations
class Solution {
    vector<int> nextGreaterElement(vector<int>& arr) {
        int n = arr.size();
        vector<int> nge(n,n);
        stack<int> st;

        for(int i=n-1;i>=0;i--){
            while(!st.empty() && arr[st.top()]<=arr[i]){
                st.pop();
            }
            if(st.empty())  nge[i] = n;
            else nge[i] = st.top();
            st.push(i);
        }
        return nge;
    }
    vector<int> nextSmallerElement(vector<int>& arr) {
        int n = arr.size();
        vector<int> nse(n,n);
        stack<int> st;

        for(int i=n-1;i>=0;i--){
            while(!st.empty() && arr[st.top()]>=arr[i]){
                st.pop();
            }
            if(st.empty())  nse[i] = n;
            else nse[i] = st.top();
            st.push(i);
        }
        return nse;
    }
public:
    long long subArrayRanges(vector<int>& nums) {
        int n = nums.size();
        vector<int> nge,pgee(n,-1),psee(n,-1),nse;
        nge = nextGreaterElement(nums);
        nse = nextSmallerElement(nums);

        stack<int>s1,s2;

        long long sumMins = 0;
        for(int i=0;i<n;i++){
            while(!s1.empty() && nums[s1.top()]>nums[i]){
                s1.pop();
            }
            if(!s1.empty()){
                psee[i] = s1.top();
            }
            s1.push(i);
            long long int num = nums[i];
            long long int prev = psee[i];
            long long int next = nse[i];

            long long int lm = i - prev;
            long long int rm = next - i;
            long long int add = ((lm*rm) * num * 1LL);
            sumMins = (sumMins+add);
        }

        long long sumMaxs = 0;
        for(int i=0;i<n;i++){
            while(!s2.empty() && nums[s2.top()]<nums[i]){
                s2.pop();
            }
            if(!s2.empty()){
                pgee[i] = s2.top();
            }
            s2.push(i);
            long long int num = nums[i];
            long long int prev = pgee[i];
            long long int next = nge[i];

            long long int lm = i - prev;
            long long int rm = next - i;
            long long int add = ((lm*rm) * num * 1LL);
            sumMaxs = (sumMaxs+add);
        }
        return sumMaxs-sumMins;
    }
};

int main() {
    return 0;
}