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

class Queue{
    int Size;
    Node* start, *end;

    public:
    Queue(){
        Size = 0;
        start = NULL;
        end = NULL;
    }

    void push(int x){
        Node* nn = new Node(x);
        if(Size==0){
            start = end = nn;
        }
        else{
            end->next = nn;
            end = nn;
        }
        Size++;
    }

    void pop(){
        if(Size==0){
            cout<<"Queue is empty"<<endl;
            return;
        }
        Size--;
        Node* temp = start;
        start = start->next;
        if(start == NULL){
            end = NULL;
        }
        delete(temp);
    }

    int size(){
        return Size;
    }

    int front(){
        if(Size==0){
            cout<<"Queue is empty"<<endl;
            return INT_MIN;
        }
        int ele = start->data;
        return ele;
    }
};

int main() {
    Queue q;

    cout << "Initial size: " << q.size() << endl;

    // Try popping from empty queue
    q.pop();

    // Push elements
    cout << "\nPushing elements: 10, 20, 30\n";
    q.push(10);
    q.push(20);
    q.push(30);

    cout << "Current size: " << q.size() << endl;
    cout << "Front element: " << q.front() << endl;

    // Pop one element
    cout << "\nPopping one element\n";
    q.pop();
    cout << "Front element after pop: " << q.front() << endl;
    cout << "Current size: " << q.size() << endl;

    // Pop remaining elements
    cout << "\nPopping remaining elements\n";
    q.pop();
    q.pop();

    cout << "Current size: " << q.size() << endl;

    // Try popping from empty queue again
    q.pop();

    // Try accessing front of empty queue
    cout << "Front element: " << q.front() << endl;

    // Test single element case
    cout << "\nTesting single element case\n";
    q.push(99);
    cout << "Front: " << q.front() << endl;
    q.pop();
    cout << "Size after removing single element: " << q.size() << endl;

    return 0;
}

/*
Initial size: 0
Queue is empty

Pushing elements: 10, 20, 30
Current size: 3
Front element: 10

Popping one element
Front element after pop: 20
Current size: 2

Popping remaining elements
Current size: 0
Queue is empty
Queue is empty
Front element: -2147483648

Testing single element case
Front: 99
Size after removing single element: 0
*/