import requests

url = "http://127.0.0.1:5000/test_login"
data = {
    "email": "adrianna_jr@o2.pl",
    "password": "1234567890"
}

response = requests.post(url, json=data)

print("Status code:", response.status_code)
print("Response:", response.json())
