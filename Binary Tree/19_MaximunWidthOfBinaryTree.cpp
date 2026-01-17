#include <bits/stdc++.h>
using namespace std;

// this will give integer overflow for large trees
class Solution
{
public:
    int widthOfBinaryTree(TreeNode *root)
    {
        if (root == NULL)
        {
            return 0;
        }
        int ans = 0;
        queue<pair<TreeNode *, int>> q;
        q.push({root, 0});
        q.push({NULL, 0});

        int start = -1;
        int end = -1;

        while (!q.empty())
        {
            TreeNode *node = q.front().first;
            int wd = q.front().second;
            q.pop();

            if (node == NULL)
            {
                ans = max(end - start, ans);
                if (!q.empty())
                {
                    q.push({NULL, 0});
                }
                start = -1;
            }
            else
            {
                if (start == -1)
                {
                    start = wd;
                }
                end = wd;
                if (node->left)
                {
                    q.push({node->left, 2 * wd});
                }
                if (node->right)
                {
                    q.push({node->right, 2 * wd + 1});
                }
            }
        }
        return ans + 1;
    }
};

/**
 * Definition for a binary tree node.
 * struct TreeNode {
 *     int val;
 *     TreeNode *left;
 *     TreeNode *right;
 *     TreeNode() : val(0), left(nullptr), right(nullptr) {}
 *     TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}
 *     TreeNode(int x, TreeNode *left, TreeNode *right) : val(x), left(left), right(right) {}
 * };
 */
class Solution {
public:
    int widthOfBinaryTree(TreeNode* root) {
        if(root==NULL)  return 0;
        int ans = 1;

        queue<pair<TreeNode*,long long int>> q;
        q.push({root,1});

        while(!q.empty()){
            int size = q.size();
            long long int min_index = q.front().second;
            long long int start = 0,end = 0;

            for(int i=0;i<size;i++){
                long long int hd = q.front().second - min_index;
                TreeNode* node = q.front().first;
                q.pop();

                if(i==0){
                    start = hd;
                }
                end = hd;

                if(node->left){
                    q.push({node->left,2*hd});
                }
                if(node->right){
                    q.push({node->right,2*hd+1});
                }
            }
            int wdt = int(end - start) + 1;
            ans = max(ans,wdt);
        }
        return ans;
    }
};
int main()
{
    return 0;
}