from flask import Flask, jsonify, request
import pandas as pd
import json
import joblib
from utils import get_feature_matrix


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


@app.route("/predict", methods=["POST", "GET"])
def predict_sarima():
    data = request.get_json()
    model = joblib.load("model.joblib")
    if request.method == 'POST':
        steps = data.get("steps")
        # 
        pred_uc = model.predict(steps=steps)
        df_response = pd.concat([pred_uc.conf_int(), pred_uc.predicted_mean], axis=1)
        response = df_response.to_json()
        return response
    else:
        return {"message": "Utilice el método POST.", "success": False}

'''
Request
{
    "start_date": "",
    "end_date": ""
}
Response:
{   
    "time_index": "",
    "mean_prediction": ""
}
'''

@app.route("/predict/generalModel", methods=["POST", "GET"])
def predict_xgboost():
    data = request.get_json()
    model = joblib.load("model_xgboost_final.joblib")
    if request.method == 'POST':
        start_date, end_date = data.get("start_date"), data.get("end_date")
        feat_mat_df = get_feature_matrix(start_date, end_date)
        try:
            prediction = model.predict(feat_mat_df)
            response = {
                "prediction": {
                    "time_index": str(list(feat_mat_df.index.array)),
                    "mean_prediction": str(list(prediction))
                },
                "success": True
            }
        except:
            response = {
                "prediction": None,
                "success": True
            }
        return response
    else:
        return {"message": "Utilice el método POST.", "success": False}


@app.route("/predict/v1", methods=["POST", "GET"])
def predict_1():
    return {"modelo": 1}


@app.route("/predict/v2", methods=["POST", "GET"])
def predict_2():
    return {"modelo": 2}


@app.route("/predict/v3", methods=["POST", "GET"])
def predict_3():
    return {"modelo": 3}


@app.errorhandler(404)
def not_found(error=None):
    message = {"status": 404, "message": "El recurso no existe. Intente la ruta /predict con método POST"}
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
        