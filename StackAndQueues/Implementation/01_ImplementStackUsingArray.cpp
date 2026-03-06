#include <bits/stdc++.h>
using namespace std;

class Stack{
    int Size;
    int Top;
    vector<int> arr;
    int capacity;

    public:
    Stack(int n){
        capacity = n;
        arr.resize(n);
        Top = -1;
        Size = 0;
    }

    void push(int x){
        if(Size==capacity){
            cout<<"Stack is full can't push"<<endl;
            return;
        }

        Size++;
        Top = (Top+1);
        arr[Top] = x;
    }

    void pop(){
        if(Size==0){
            cout<<"Stack is empty can't pop"<<endl;
            return;
        }

        Size--;
        Top--;
    }

    int size(){
        return Size;
    }

    int top(){
        if(Size==0){
            cout<<"Stack is empty"<<endl;
            return INT_MIN;
        }
        return arr[Top];
    }

};

int main() {

    Stack st(5);

    cout << "Initial size: " << st.size() << endl;

    // Underflow test
    st.pop();

    // Push elements
    cout << "\nPushing elements: 10, 20, 30, 40, 50\n";
    st.push(10);
    st.push(20);
    st.push(30);
    st.push(40);
    st.push(50);

    cout << "Current size: " << st.size() << endl;
    cout << "Top element: " << st.top() << endl;

    // Overflow test
    cout << "\nTrying to push 60 (Overflow case)\n";
    st.push(60);

    // Pop two elements
    cout << "\nPopping two elements\n";
    st.pop();
    st.pop();

    cout << "Top after popping 2 elements: " << st.top() << endl;
    cout << "Current size: " << st.size() << endl;

    // Empty the stack completely
    cout << "\nEmptying stack completely\n";
    while(st.size() > 0){
        cout << "Removing: " << st.top() << endl;
        st.pop();
    }

    cout << "Size after emptying: " << st.size() << endl;

    // Underflow again
    st.pop();
    cout << "Top element: " << st.top() << endl;

    return 0;
}

/*
Initial size: 0
Stack is empty can't pop

Pushing elements: 10, 20, 30, 40, 50
Current size: 5
Top element: 50

Trying to push 60 (Overflow case)
Stack is full can't push

Popping two elements
Top after popping 2 elements: 30
Current size: 3

Emptying stack completely
Removing: 30
Removing: 20
Removing: 10
Size after emptying: 0
Stack is empty can't pop
Stack is empty
Top element: -2147483648
*/