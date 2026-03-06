#include <bits/stdc++.h>
using namespace std;

// Takes more iterations
class Solution {
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
    int sumSubarrayMins(vector<int>& arr) {
        int n = arr.size();
        int mod = 1e9+7;
        vector<int> nse,psee;

        nse = nextSmallerElement(arr);
        psee = prevSmallerEqualElement(arr);

        int sum = 0;
        for(int i=0;i<n;i++){
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


// Takes less iterations
class Solution {
    vector<int> nextSmallerElement(vector<int>& arr) {
        int n = arr.size();
        vector<int> nse(n,-1);
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
    int sumSubarrayMins(vector<int>& arr) {
        int n = arr.size();
        int mod = 1e9+7;
        vector<int> nse,psee(n,-1);
        stack<int> st;

        nse = nextSmallerElement(arr);

        int sum = 0;
        for(int i=0;i<n;i++){
            while(!st.empty() && arr[st.top()]>arr[i]){
                st.pop();
            }
            if(!st.empty()){
                psee[i] = st.top();
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