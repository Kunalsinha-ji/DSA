#include <bits/stdc++.h>
using namespace std;

// Approach 1 less push more other operations
class MyQueue {
    stack<int> s1,s2;
public:
    MyQueue() {

    }

    void push(int x) {
        while(!s1.empty()){
            s2.push(s1.top());
            s1.pop();
        }
        s1.push(x);
        while(!s2.empty()){
            s1.push(s2.top());
            s2.pop();
        }
    }

    int pop() {
        int ele = s1.top();
        s1.pop();
        return ele;
    }

    int peek() {
        int ele = s1.top();
        return ele;
    }

    bool empty() {
        return s1.empty();
    }
};

/**
 * Your MyQueue object will be instantiated and called as such:
 * MyQueue* obj = new MyQueue();
 * obj->push(x);
 * int param_2 = obj->pop();
 * int param_3 = obj->peek();
 * bool param_4 = obj->empty();
 */


// Approach 2 less other operations more push
class MyQueue {
    stack<int> s1,s2;
public:
    MyQueue() {

    }

    void push(int x) {
        s1.push(x);
    }

    int pop() {
        if(!s2.empty()){
            int ele = s2.top();
            s2.pop();
            return ele;
        }
        else{
            while(!s1.empty()){
                s2.push(s1.top());
                s1.pop();
            }
            int ele = s2.top();
            s2.pop();
            return ele;
        }
    }

    int peek() {
        if(!s2.empty()){
            int ele = s2.top();
            return ele;
        }
        else{
            while(!s1.empty()){
                s2.push(s1.top());
                s1.pop();
            }
            int ele = s2.top();
            return ele;
        }
    }

    bool empty() {
        return s1.empty() && s2.empty();
    }
};

/**
 * Your MyQueue object will be instantiated and called as such:
 * MyQueue* obj = new MyQueue();
 * obj->push(x);
 * int param_2 = obj->pop();
 * int param_3 = obj->peek();
 * bool param_4 = obj->empty();
 */
int main() {
    return 0;
}