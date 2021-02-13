"""Read in model.pkl from binary to callable function."""
import numpy as np
import pickle


def ValuePredictor(to_predict_list):
    """Return first index of result once loading model."""
    to_predict = np.array(to_predict_list).reshape(1, 4)
    loaded_model = pickle.load(open("model.pkl", "rb"))
    result = loaded_model.predict(to_predict)
    return result[0]
