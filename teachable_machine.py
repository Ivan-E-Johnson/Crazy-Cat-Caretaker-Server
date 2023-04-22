from keras.models import load_model  # TensorFlow is required for Keras to work
import cv2  # Install opencv-python
import numpy as np

# This is the one part where we don't actually have support for multiple systems.
# Only our single model is saved. In a production product the models could be generated
# when the account is initially made, then the models could be saved to the cloud or server
# and accessed when classifying.

# Disable scientific notation for clarity
np.set_printoptions(suppress=True)

# Load the model
model = load_model("converted_keras/keras_model.h5", compile=False)

# Load the labels
class_names = open("converted_keras/labels.txt", "r").readlines()

NO_CAT = 'No Cat'

def classify(image):
    np.set_printoptions(suppress=True)
    def get_opencv_img_from_buffer(buffer):
        bytes_as_np_array = np.frombuffer(buffer, dtype=np.uint8)
        return cv2.imdecode(bytes_as_np_array, cv2.IMREAD_COLOR)

    nparr = get_opencv_img_from_buffer(image)
    image = cv2.resize(nparr, (224, 224), interpolation=cv2.INTER_AREA)
    image = np.asarray(image, dtype=np.float32).reshape(1, 224, 224, 3)
    # Normalize the image array
    image = (image / 127.5) - 1

    # Predicts the model
    prediction = model.predict(image, verbose=0)
    index = np.argmax(prediction)
    class_name = class_names[index]
    confidence_score = prediction[0][index]

    # Print prediction and confidence score
    # print("Class:", class_name[2:], index, confidence_score, end="")
    # print("Confidence Score:", str(np.round(confidence_score * 100))[:-2], "%")
    return class_name[2:].strip(), np.round(confidence_score * 100)
