"""Read in model.pkl from binary to callable function."""
from tensorflow import keras
import tensorflow as tf


def ValuePredictor(to_predict):
    """Return first index of result once loading model."""
    model = keras.models.load_model(
        "my_model"
    )
    # keras .predict() methods expect batch of inputs, so let's provide an axis
    # to avoid errors
    prediction_input = tf.expand_dims(int(to_predict), axis=0)
    prediction = model.predict(prediction_input)
    print(f"prediction: {prediction}")
    return prediction
