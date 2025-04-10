import tensorflow as tf
import numpy as np
import pandas as pd
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from PIL import Image
import os

# === Load CSV Dataset ===
df = pd.read_csv("help.csv")  # your dataset CSV file with 'path' and 'summary'

# === Text Preprocessing ===
tokenizer = Tokenizer(num_words=1000, oov_token="<OOV>")
tokenizer.fit_on_texts(df['summary'])
vocab_size = len(tokenizer.word_index) + 1
max_len = 20

sequences = tokenizer.texts_to_sequences(df['summary'])
padded_sequences = pad_sequences(sequences, maxlen=max_len, padding='post')

# === Image Preprocessing ===
def preprocess_image(image_path):
    image = Image.open(os.path.join("dashboard_images", image_path)).resize((224, 224)).convert("RGB")
    image = np.array(image) / 255.0
    return image

image_data = np.array([preprocess_image(path) for path in df['path']])

# === Encoder (CNN) ===
def build_encoder():
    inputs = tf.keras.Input(shape=(224, 224, 3))
    x = tf.keras.layers.Conv2D(32, 3, activation='relu')(inputs)
    x = tf.keras.layers.MaxPooling2D()(x)
    x = tf.keras.layers.Conv2D(64, 3, activation='relu')(x)
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    x = tf.keras.layers.Dense(256, activation='relu')(x)
    return tf.keras.Model(inputs, x, name="encoder")

# === Decoder (LSTM) ===
def build_decoder(vocab_size, max_len):
    image_features = tf.keras.Input(shape=(256,))
    seq_input = tf.keras.Input(shape=(max_len,))

    x = tf.keras.layers.Embedding(vocab_size, 128)(seq_input)
    repeated_img = tf.keras.layers.RepeatVector(max_len)(image_features)
    x = tf.keras.layers.Concatenate()([repeated_img, x])
    x = tf.keras.layers.LSTM(256, return_sequences=True)(x)
    x = tf.keras.layers.TimeDistributed(tf.keras.layers.Dense(vocab_size, activation='softmax'))(x)

    return tf.keras.Model([image_features, seq_input], x)

# === Combine Encoder & Decoder ===
encoder = build_encoder()
decoder = build_decoder(vocab_size=vocab_size, max_len=max_len)

img_input = tf.keras.Input(shape=(224, 224, 3))
seq_input = tf.keras.Input(shape=(max_len,))
encoded_img = encoder(img_input)
output = decoder([encoded_img, seq_input])

model = tf.keras.Model(inputs=[img_input, seq_input], outputs=output)
model.compile(optimizer='adam', loss='sparse_categorical_crossentropy')

# === Prepare Training Labels ===
output_labels = np.expand_dims(padded_sequences, -1)

# === Train Model ===
model.fit([image_data, padded_sequences], output_labels, epochs=10)

# === Save or Evaluate ===
model.summary()
model.save("dashboard_summary_model.keras")  # Corrected file extension

# === Save Tokenizer ===
import pickle
with open("tokenizer.pkl", "wb") as f:
    pickle.dump(tokenizer, f)
