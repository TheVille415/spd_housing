"""Read in model.pkl from binary to callable function."""
from tensorflow import keras


def ValuePredictor(to_predict):
    """Return first index of result once loading model."""
    model = keras.models.load_model("../my_model/saved_model.pb")
    print(model)
    return
