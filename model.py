from tensorflow.keras.datasets import mnist
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import (
    Conv2D, MaxPooling2D, Flatten, Dense, Input, Dropout
)
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.optimizers import Adam
import numpy as np
import cv2
import os

x_extra = []
y_extra = []

base_dir = "resource/"

for digit in range(1,7):
    folder = os.path.join(base_dir, str(digit))
    for file in os.listdir(folder):
        img = cv2.imread(os.path.join(folder, file))
        img = cv2.cvtColor(cv2.resize(img, (28, 28)), cv2.COLOR_BGR2GRAY)
        img = img.astype("float32") / 255.0
        img = img.reshape(28, 28, 1)

        x_extra.append(img)
        y_extra.append(digit-1)

x_extra = np.array(x_extra)
y_extra = np.array(y_extra)

# 1. 載入 MNIST
(x_train, y_train), (x_test, y_test) = mnist.load_data()

# 2. 前處理：變成 (N, 28, 28, 1)
x_train = x_train.reshape(60000, 28, 28, 1).astype("float32") / 255.0
x_test  = x_test.reshape(10000, 28, 28, 1).astype("float32") / 255.0
# 只留 1~6
mask_train = (y_train >= 1) & (y_train <= 6)
mask_test  = (y_test  >= 1) & (y_test  <= 6)

x_train = x_train[mask_train]
y_train = y_train[mask_train]
x_test  = x_test[mask_test]
y_test  = y_test[mask_test]

# label 1~6 → 0~5
y_train -= 1
y_test  -= 1

x_train = np.concatenate((x_train, x_extra), axis=0)
y_train = np.concatenate((y_train, y_extra), axis=0)

y_train = to_categorical(y_train, 6)
y_test  = to_categorical(y_test, 6)

# 3. CNN 模型
model = Sequential([
    Input(shape=(28, 28, 1)),

    Conv2D(32, (3,3), activation="relu"),
    MaxPooling2D(),

    Conv2D(64, (3,3), activation="relu"),
    MaxPooling2D(),
    Dropout(0.2),

    Flatten(),
    Dense(128, activation="relu"),
    Dense(6, activation="softmax")
])

# 4. 編譯
model.compile(
    optimizer=Adam(learning_rate=0.001),
    loss="categorical_crossentropy",
    metrics=["accuracy"]
)

# 5. 訓練
model.fit(
    x_train, y_train,
    validation_data=(x_test, y_test),
    epochs=25,
    batch_size=128,
    verbose=1
)

# 6. 儲存（推薦格式）
model.save("sudoku_digit_cnn_rev3.keras")