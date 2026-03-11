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
public:
    MinStack() {

    }

    void push(int val) {

    }

    void pop() {

    }

    int top() {

    }

    int getMin() {

    }
};

/**
 * Your MinStack object will be instantiated and called as such:
 * MinStack* obj = new MinStack();
 * obj->push(val);
 * obj->pop();
 * int param_3 = obj->top();
 * int param_4 = obj->getMin();
 */

int main() {
    return 0;
}