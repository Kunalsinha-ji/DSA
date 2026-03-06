#include <bits/stdc++.h>
using namespace std;

class Node{
    public:
    int data;
    Node* next;

    Node(int n){
        this->data = n;
        this->next = NULL;
    }
};

class Stack{
    int Size;
    Node* Top;

    public:
    Stack(){
        Size = 0;
        Top = NULL;
    }

    void push(int x){
        Node* nn = new Node(x);
        nn->next = Top;
        Top = nn;
        Size++;
    }

    void pop(){
        if(Size==0){
            cout<<"Stack is empty can't pop"<<endl;
            return;
        }

        Node* temp = Top;
        Top = Top->next;
        Size--;
        delete(temp);
    }

    int size(){
        return Size;
    }

    int top(){
        if(Size==0){
            cout<<"Stack is empty"<<endl;
            return INT_MIN;
        }

        int ele = Top->data;
        return ele;
    }
};

int main() {
    Stack st;

    cout << "Initial size: " << st.size() << endl;

    // Test popping from empty stack
    st.pop();

    // Push elements
    cout << "\nPushing elements: 10, 20, 30\n";
    st.push(10);
    st.push(20);
    st.push(30);

    cout << "Current size: " << st.size() << endl;
    cout << "Top element: " << st.top() << endl;

    // Pop one element
    cout << "\nPopping one element\n";
    st.pop();
    cout << "Top element after pop: " << st.top() << endl;
    cout << "Current size: " << st.size() << endl;

    // Pop remaining elements
    cout << "\nPopping remaining elements\n";
    st.pop();
    st.pop();

    cout << "Current size: " << st.size() << endl;

    // Try popping from empty stack again
    st.pop();

    // Try accessing top of empty stack
    cout << "Top element: " << st.top() << endl;

    return 0;
}


/*
Initial size: 0
Stack is empty can't pop

Pushing elements: 10, 20, 30
Current size: 3
Top element: 30

Popping one element
Top element after pop: 20
Current size: 2

Popping remaining elements
Current size: 0
Stack is empty can't pop
Stack is empty
Top element: -2147483648
*/