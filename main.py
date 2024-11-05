import firebase_admin
from firebase_admin import credentials, db
from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
import threading
import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.tree import DecisionTreeClassifier

import warnings
import random

warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)

# Initialize the Firebase Admin SDK
cred = credentials.Certificate("greenhands-29db9-firebase-adminsdk-81d5x-9a4fae824a.json")

firebase_admin.initialize_app(cred, {
    "databaseURL": "https://greenhands-29db9-default-rtdb.asia-southeast1.firebasedatabase.app/29102024"
})

class Crop_Recommendation_App(App):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.new_data = 0

    def build(self):
        # Set the window size to a typical phone size
        Window.size = (375, 667)  # Width, Height in pixels
        Window.title = "Crop Prediction with soil conditions"
        Window.icon = "soil_moisture.png"
        # Load the .kv file
        return Builder.load_file('App_Frontend.kv')

    def submit_parameters(self):
        # Collect the values from the TextInput fields
        # try:
        soil = self.root.ids.input1.text
        ph = self.root.ids.input2.text
        temperature = self.root.ids.input3.text
        rainfall = self.root.ids.input4.text

        # Reference to the Firebase database
        ref = db.reference('parameters')  # Change 'data' to the path where you want to store the single value

        # Set the value in Firebase
        ref.set({"soil": soil, "ph": ph, "temperature": temperature, "rainfall": rainfall})

        # # Update the result label with the submitted values
        # self.root.ids.result_label.text = f"Submitted: {soil}, {ph}, {temperature}, {rainfall}"

        df = pd.read_csv('dataset/Crop_recommendation.csv')
        print(df.head())
        print(df.describe())

        # DATA PREPROCESSING
        c = df.label.astype('category')
        targets = dict(enumerate(c.cat.categories))
        df['target'] = c.cat.codes

        y = df.target
        X = df[['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']]

        X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=1)

        scaler = MinMaxScaler()
        X_train_scaled = scaler.fit_transform(X_train)

        # we must apply the scaling to the test set as well that we are computing for the training set
        X_test_scaled = scaler.transform(X_test)

        clf = DecisionTreeClassifier(random_state=42).fit(X_train, y_train)

        soil = soil.lower()
        nitrogen_values = {
            "clay": random.randint(37, 140),  # Example nitrogen value for Clay in ppm
            "loam": random.randint(37, 140),  # Example nitrogen value for Loam in ppm
            "sandy": random.randint(0, 75)  # Example nitrogen value for Sandy in ppm
        }

        phosphorus_values = {
            "clay": random.randint(20, 120),  # Example nitrogen value for Clay
            "loam": random.randint(28, 145),  # Example nitrogen value for Loam
            "sandy": random.randint(5, 28)  # Example nitrogen value for Sandy
        }

        potassium_values = {
            "clay": random.randint(32, 205),  # Example nitrogen value for Clay
            "loam": random.randint(32, 205),  # Example nitrogen value for Loam
            "sandy": random.randint(5, 32)  # Example nitrogen value for Sandy
        }

        params = np.array([[nitrogen_values.get(soil), phosphorus_values.get(soil), potassium_values.get(soil), temperature, int(self.new_data), ph, rainfall]])
        df = pd.DataFrame(params, columns=['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall'])
        prediction = targets[clf.predict(df)[0]]
        print(f"Prediction: {prediction}")
        self.root.ids.prediction_label.text = f"{prediction}"



    def update_moisture_level(self, moisture_level):
        # Update the moisture level label and progress bar
        self.root.ids.moisture_level.text = f"{moisture_level}%"
        self.root.ids.moisture_progress_bar.value = moisture_level

    def firebase_listener(self):
        # Listen for changes in the specific node
        def listener(event):
            # event will contain the new data
            self.new_data = event.data
            self.update_moisture_level(self.new_data)
        # Start listening on the specific path
        db.reference("29102024/moisture").listen(listener)  # Replace with your data path

    def on_start(self):
        # Start the Firebase listener in a separate thread
        threading.Thread(target=self.firebase_listener, daemon=True).start()

if __name__ == '__main__':
    Crop_Recommendation_App().run()
