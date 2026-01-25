#include <bits/stdc++.h>
using namespace std;

class Solution {
    void insert(stack<int> &st,int num){
        if(st.empty()){
            st.push(num);
            return;
        }

        int n = st.top();
        st.pop();

        insert(st,num);
        st.push(n);
    }
  public:
    void reverseStack(stack<int> &st) {
        if(st.empty()){
            return;
        }

        int num = st.top();
        st.pop();

        reverseStack(st);
        insert(st,num);
    }
};

int main() {
    return 0;
}