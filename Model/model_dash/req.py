import requests
import json

model_url = "https://scenic-kiln-292815.ue.r.appspot.com/predict/generalModel"


data = json.dumps({"start_date": "2020-01-01", "end_date": "2020-01-30"})
headers = {"Content-Type": "application/json"}
r_model = requests.post(model_url, data=data, headers=headers)

print(r_model.json())

prediction = json.loads(r_model.json()["prediction"]["mean_prediction"])
x_time = r_model.json()["prediction"]["time_index"]

print(prediction)
print(type(x_time))


