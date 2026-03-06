#include <bits/stdc++.h>
using namespace std;

class Queue{
    vector<int> arr;
    int start,end;
    int Size;
    int capacity;

    public:
    Queue(int n){
        capacity = n;
        start = end = -1;
        Size = 0;
        arr.resize(n);
    }

    void push(int x){
        if(Size==capacity){
            cout<<"Queue is full can't push"<<endl;
            return;
        }

        Size++;
        if(start==-1){
            start = end = 0;
            arr[start] = x;
        }
        else{
            end = (end+1)%capacity;
            arr[end] = x;
        }
    }

    void pop(){
        if(Size==0){
            cout<<"Queue is empty can't pop"<<endl;
            return;
        }

        if(Size==1){
            start = end = -1;
        }
        else{
            start = (start+1)%capacity;
        }
        Size--;
    }

    int size(){
        return Size;
    }
    int front(){
        if(Size==0){
            cout<<"Queue is Empty"<<endl;
            return INT_MIN;
        }

        int ele = arr[start];
        return ele;
    }
};

int main() {

    Queue q(5);

    cout << "Initial size: " << q.size() << endl;

    // Underflow test
    q.pop();

    // Push elements
    cout << "\nPushing elements 1,2,3,4,5\n";
    q.push(1);
    q.push(2);
    q.push(3);
    q.push(4);
    q.push(5);

    cout << "Current size: " << q.size() << endl;
    cout << "Front element: " << q.front() << endl;

    // Overflow test
    cout << "\nTrying to push 6 (Overflow case)\n";
    q.push(6);

    // Pop two elements
    cout << "\nPopping two elements\n";
    q.pop();
    q.pop();

    cout << "Front element after popping 2: " << q.front() << endl;
    cout << "Current size: " << q.size() << endl;

    // Wrap-around test
    cout << "\nPushing 6 and 7 (Wrap-around test)\n";
    q.push(6);
    q.push(7);

    cout << "Current size: " << q.size() << endl;
    cout << "Front element: " << q.front() << endl;

    // Empty entire queue
    cout << "\nEmptying queue completely\n";
    while(q.size() > 0){
        cout << "Removing: " << q.front() << endl;
        q.pop();
    }

    cout << "Size after emptying: " << q.size() << endl;

    // Underflow again
    q.pop();
    cout << "Front element: " << q.front() << endl;

    return 0;
}


/*
Initial size: 0
Queue is empty can't pop

Pushing elements 1,2,3,4,5
Current size: 5
Front element: 1

Trying to push 6 (Overflow case)
Queue is full can't push

Popping two elements
Front element after popping 2: 3
Current size: 3

Pushing 6 and 7 (Wrap-around test)
Current size: 5
Front element: 3

Emptying queue completely
Removing: 3
Removing: 4
Removing: 5
Removing: 6
Removing: 7
Size after emptying: 0
Queue is empty can't pop
Queue is Empty
Front element: -2147483648
*/