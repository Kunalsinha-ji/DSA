#include <bits/stdc++.h>
using namespace std;

// Takes more iterations
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
public:
    int sumSubarrayMaxs(vector<int>& arr) {
        int n = arr.size();
        int mod = 1e9+7;
        vector<int> nge,pgee;

        nge = nextGreaterElement(arr);
        pgee = prevGreaterEqualElement(arr);

        int sum = 0;
        for(int i=0;i<n;i++){
            long long int num = arr[i];
            long long int prev = pgee[i];
            long long int next = nge[i];

            long long int lm = i - prev;
            long long int rm = next - i;
            long long int add = ((lm*rm)%mod * num * 1LL)%mod;
            sum = (sum+add)%mod;
        }
        return int(sum);
    }
};

// Takes less iterations
class Solution {
    vector<int> nextGreaterElement(vector<int>& arr) {
        int n = arr.size();
        vector<int> nge(n,-1);
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

public:
    int sumSubarrayMaxs(vector<int>& arr) {
        int n = arr.size();
        int mod = 1e9+7;
        vector<int> nge,pgee(n,-1);
        stack<int> st;

        nge = nextGreaterElement(arr);

        int sum = 0;
        for(int i=0;i<n;i++){
            while(!st.empty() && arr[st.top()]<arr[i]){
                st.pop();
            }
            if(!st.empty()){
                pgee[i] = st.top();
            }
            st.push(i);
            long long int num = arr[i];
            long long int prev = psee[i];
            long long int next = nse[i];

            long long int lm = i - prev;
            long long int rm = next - i;
            long long int add = ((lm*rm)%mod * num * 1LL)%mod;
            sum = (sum+add)%mod;
        }
        return int(sum);
    }
};


int main() {
    return 0;
}