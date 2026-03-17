import requests

# connect the database 
import time
import requests

# fastapi
time_start = time.time()
url = "http://0.0.0.0:8000/api/users/v3/1"
response = requests.get(url)
# print(response.json())
time_end = time.time()
print(f"Time taken FastAPI: {time_end - time_start} seconds")


# Django
time_start = time.time()
url = "http://0.0.0.0:8001/api/users/v4/1"
response = requests.get(url)
# print(response.json())
time_end = time.time()
print(f"Time taken Django: {time_end - time_start} seconds")