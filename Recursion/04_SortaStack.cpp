#include <bits/stdc++.h>
using namespace std;

class Solution {
    void sortedInsert(stack<int> &st,int num){
        if(st.empty() || st.top()<num){
            st.push(num);
            return;
        }

        int n = st.top();
        st.pop();
        sortedInsert(st,num);
        st.push(n);
    }
  public:
    void sortStack(stack<int> &st) {
        if(st.empty()){
            return;
        }

        int num = st.top();
        st.pop();

        sortStack(st);
        sortedInsert(st,num);
    }
};


int main() {
    return 0;
}