#include <bits/stdc++.h>
using namespace std;

// Space O(2N) used
class MinStack {
    stack<pair<int,int>> st;
    // <element,minimum till now>
public:
    MinStack() {
    }

    void push(int val) {
        if(st.size()==0){
            st.push({val,val});
        }
        else{
            int mini = min(st.top().second, val);
            st.push({val,mini});
        }
    }

    void pop() {
        st.pop();
    }

    int top() {
        int ele = st.top().first;
        return ele;
    }

    int getMin() {
        return st.top().second;
    }
};


// O(N) approach
class MinStack {
    stack<int> st;
    int mini;
public:
    MinStack() {

    }

    void push(int val) {
        if(st.empty()){
            st.push(val);
            mini = val;
            return;
        }

        if(val<mini){
            int newVal = 2 * val - mini;
            mini = val;
            st.push(newVal);
        }
        else{
            st.push(val);
        }
    }

    void pop() {
        if(st.empty()){
            return;
        }

        if(st.top()<mini){
            mini = 2*mini - st.top();
        }
        st.pop();
    }

    int top() {
        if(st.top()<mini){
            return mini;
        }
        return st.top();
    }

    int getMin() {
        return mini;
    }
};

// No integer overflow
class MinStack {
    stack<long long> st;
    long long mini;

public:
    MinStack() {

    }

    void push(int val) {
        if(st.empty()){
            st.push(val);
            mini = val;
            return;
        }

        if(val < mini){
            long long newVal = 2LL * val - mini;
            st.push(newVal);
            mini = val;
        }
        else{
            st.push(val);
        }
    }

    void pop() {
        if(st.empty()) return;

        if(st.top() < mini){
            mini = 2 * mini - st.top();
        }
        st.pop();
    }

    int top() {
        if(st.top() < mini) return mini;
        return st.top();
    }

    int getMin() {
        return mini;
    }
};


int main() {
    return 0;
}