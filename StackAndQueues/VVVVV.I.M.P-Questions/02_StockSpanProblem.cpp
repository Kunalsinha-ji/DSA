#include <bits/stdc++.h>
using namespace std;

// Brute force
class StockSpanner {
    vector<int> arr;
public:
    StockSpanner() {
        arr.clear();
    }

    int next(int price) {
        arr.push_back(price);
        int count = 0;
        for(int i=arr.size()-1;i>=0;i--){
            if(arr[i]<=price){
                count++;
            }
            else{
                break;
            }
        }
        return count;
    }
};

// Optimal - Using Stack and using concept of previous greater element
class StockSpanner {
    stack<pair<int,int>> st;
    int ind;
public:
    StockSpanner() {
        ind = -1;
    }

    int next(int price) {
        ind++;
        while(!st.empty() && st.top().first<=price){
            st.pop();
        }
        if(st.empty()){
            st.push({price,ind});
            return ind + 1;
        }
        int last_index = st.top().second;
        st.push({price,ind});
        return ind - last_index;
    }
};

/**
 * Your StockSpanner object will be instantiated and called as such:
 * StockSpanner* obj = new StockSpanner();
 * int param_1 = obj->next(price);
 */

int main() {
    return 0;
}