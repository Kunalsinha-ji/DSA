#include <bits/stdc++.h>
using namespace std;

/*
class Node {
public:
    int data;
    Node* left;
    Node* right;

    Node(int x) {
        data = x;
        left = right = NULL;
    }
};
*/

class Solution {
  public:
    vector<int> bottomView(Node *root) {
        // code here
        vector<int> ans;
        if(root==NULL){
            return ans;
        }

        queue<pair<Node*,int>> q;
        q.push({root,0});
        map<int,int> mp;

        while(!q.empty()){
            Node* node = q.front().first;
            int hd = q.front().second;
            q.pop();

            mp[hd] = node->data;
            if(node->left){
                q.push({node->left,hd-1});
            }
            if(node->right){
                q.push({node->right,hd+1});
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