#include <bits/stdc++.h>
using namespace std;

class Solution {
    void sortedInsert(stack<int> &st,int n){
        if(st.empty() || st.top()<n){
            st.push(n);
            return;
        }

        int top = st.top();
        st.pop();
        sortedInsert(st,n);
        st.push(top);
    }
  public:
    void sortStack(stack<int> &st) {
        if(st.empty()){
            return;
        }

        int top = st.top();
        st.pop();
        sortStack(st);
        sortedInsert(st,top);
    }
};


int main() {
    return 0;
}