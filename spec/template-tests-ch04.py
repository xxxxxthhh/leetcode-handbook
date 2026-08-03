from collections import deque

# 模板 A:下一个更大元素(递减栈)
def next_greater(nums):
    n = len(nums)
    ans = [-1] * n
    stack = []
    for i, x in enumerate(nums):
        while stack and nums[stack[-1]] < x:
            j = stack.pop()
            ans[j] = x
        stack.append(i)
    return ans

# 模板 A 变形:739 Daily Temperatures(答案改为下标差)
def daily_temperatures(t):
    n = len(t)
    ans = [0] * n
    stack = []
    for i, x in enumerate(t):
        while stack and t[stack[-1]] < x:
            j = stack.pop()
            ans[j] = i - j
        stack.append(i)
    return ans

# 模板 B:单调队列(239 Sliding Window Maximum)
def max_sliding_window(nums, k):
    q = deque()
    ans = []
    for i, x in enumerate(nums):
        while q and nums[q[-1]] <= x:
            q.pop()
        q.append(i)
        if q[0] <= i - k:
            q.popleft()
        if i >= k - 1:
            ans.append(nums[q[0]])
    return ans

# 84 Largest Rectangle(模板 A + 末尾哨兵,验证"清算时机"翻车点的解法)
def largest_rectangle(heights):
    heights = heights + [0]
    stack = []
    best = 0
    for i, h in enumerate(heights):
        while stack and heights[stack[-1]] >= h:
            j = stack.pop()
            left = stack[-1] if stack else -1
            best = max(best, heights[j] * (i - left - 1))
        stack.append(i)
    return best

assert next_greater([2,1,2,4,3]) == [4,2,4,-1,-1]
assert daily_temperatures([73,74,75,71,69,72,76,73]) == [1,1,4,2,1,1,0,0]
assert max_sliding_window([1,3,-1,-3,5,3,6,7], 3) == [3,3,5,5,6,7]
assert largest_rectangle([2,1,5,6,2,3]) == 10
assert largest_rectangle([2,4]) == 4
print("all templates pass")
