#include <bits/stdc++.h>
using namespace std;

class MyStack {
    queue<int> q;
public:
    MyStack() {

    }

    void push(int x) {
        if(q.empty()){
            q.push(x);
        }
        else{
            int currSize = q.size();
            q.push(x);

            while(currSize--){
                int ele = q.front();
                q.pop();
                q.push(ele);
            }
        }
    }

    int pop() {
        int ele = q.front();
        q.pop();
        return ele;
    }

    int top() {
        return q.front();
    }

    bool empty() {
        return q.empty();
    }
};

/**
 * Your MyStack object will be instantiated and called as such:
 * MyStack* obj = new MyStack();
 * obj->push(x);
 * int param_2 = obj->pop();
 * int param_3 = obj->top();
 * bool param_4 = obj->empty();
 */

int main() {
    return 0;
}