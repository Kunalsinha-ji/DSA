#include <bits/stdc++.h>
using namespace std;

/*
https://www.geeksforgeeks.org/problems/top-view-of-binary-tree/1
*/

/*
class Node {
  public:
    int data;
    Node* left;
    Node* right;

    Node(int val) {
        data = val;
        left = nullptr;
        right = nullptr;
    }
};
*/

class Solution {
  public:
    vector<int> topView(Node *root) {
        vector<int> ans;

        map<int,int> mp;

        queue<pair<Node*,int>> q;
        q.push({root,0});

        while(!q.empty()){
            auto node = q.front();
            q.pop();

            Node* nn = node.first;
            int hd = node.second;

            if(mp.find(hd)==mp.end()){
                mp[hd] = nn->data;
            }

            if(nn->left){
                q.push({nn->left,hd-1});
            }
            if(nn->right){
                q.push({nn->right,hd+1});
            }
        }

        for(auto it: mp){
            ans.push_back(it.second);
        }
        return ans;
    }
};

int main() {
    return 0;
}