import os
from google import genai

client = genai.Client(api_key="AIzaSyDH4pyVDdYfdK_7VOWv9VvKfJCCbcuxMbc")
try:
    for model in client.models.list():
        print(model.name)
except Exception as e:
    print(f"Error: {e}")
