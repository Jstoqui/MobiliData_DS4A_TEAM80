from flask import Flask, jsonify, request
import pandas as pd
import json
import joblib


app = Flask(__name__)


# CARGAR MODELOS
'''
Request
{
    "steps": 100
}
Response:
3 fields: predicted_mean, lower Cantidad_siniestros, upper Cantidad_siniestros
'''

model = joblib.load("model.joblib")


@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    steps = data.get("steps")
    # 
    pred_uc = model.get_forecast(steps=steps)
    df_response = pd.concat([pred_uc.conf_int(), pred_uc.predicted_mean], axis=1)
    response = df_response.to_json()
    return response


@app.errorhandler(404)
def not_found(error=None):
    message = {"status": 404, "message": "El recurso no existe"}
    response = jsonify(message)
    response.status_code = 404
    return response


# if __name__ == "__main__":
#     import requests
#     import json
#     uri = "https://scenic-kiln-292815.ue.r.appspot.com/predict"
#     data = json.dumps({"steps": 20})
#     headers = {"Content-Type": "application/json"}
#     r = requests.post(uri, data=data, headers=headers)
#     if r.ok:
#         print(r.json())
        