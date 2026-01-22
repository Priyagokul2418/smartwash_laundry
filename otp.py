import requests

url = "http://<ip>:<port>/OtpApi/otpgenerate"
params = {
    "username": "apiuser",
    "password": "apipass",
    "msisdn": "1234567890",
    "msg": "Test OTP",
    "source": "SENDER",
    "otplen": "6",
    "tagname": "test",
    "exptime": "300"
}

response = requests.get(url, params=params)
print("API Response:", response.text)
