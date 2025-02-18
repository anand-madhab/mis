/*
Given an integer array nums sorted in non-decreasing order, remove some duplicates in-place such that each unique element appears at most twice. The relative order of the elements should be kept the same.
Return k after placing the final result in the first k slots of nums.
Input: nums = [0,0,1,1,1,1,2,3,3]
Output: 7, nums = [0,0,1,1,2,3,3]
*/

class Solution {
public:
    int removeDuplicates(vector<int>& nums) {
        int c = 1, j = 1, tmp = nums[0];
        for(int i = 1; i < nums.size(); i++) {
            if (tmp == nums[i]) {
                if (c < 2) {
                    nums[j++] = nums[i];
                } else if (i < nums.size() && nums[i] != nums[i+1]) {
                    c = -1;
                }
                c++;
            } else {
                nums[j++] = nums[i];
                tmp = nums[i];
                c = 1;
            }
        }
        return j;
    }
};

int main() {
  Solution s;
  vector<int> nums = {0,0,1,1,1,1,2,3,3};
  int n = s.removeDuplicates(nums);
  for(int i = 0; i < n; i++) {
    cout << nums[i] << ", ";
  }
  return 0;
}
