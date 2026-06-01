import requests

response = requests.post(
    "http://127.0.0.1:5000/browser_activity",
    json={
        "title": "LeetCode",
        "url": "https://leetcode.com"
    }
)

print(response.status_code)
print(response.text)