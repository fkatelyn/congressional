import os
import cv2
import random
import numpy as np
import pandas as pd
import tensorflow as tf
import keras.api.keras as keras
import scikeras

from keras.layers import * # import all, including Dense, add, Flatten, etc.
from keras.models import Model, Sequential
from scikeras.wrappers import KerasClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, roc_auc_score, accuracy_score
from keras.applications.mobilenet import MobileNet

# Download dataset: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/DBW86T
X = np.load("X.npy")
y = np.load("y.npy")
IMG_WIDTH = 100
IMG_HEIGHT = 75

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.4, random_state=101)
y_train, y_test = train_test_split(X, y, test_size=0.4, random_state=101)

X_train = X_train.astype(np.float32)
X_test = X_test.astype(np.float32)

y_train_onehot = np.zeros((y_train.size, y_train.max().astype(int)+1))
y_train_onehot[np.arange(y_train.size), y_train.astype(int)] = 1
y_train_onehot = y_train_onehot.astype(np.float32)

y_test_onehot = np.zeros((y_test.size, y_test.max().astype(int)+1))
y_test_onehot[np.arange(y_test.size), y_test.astype(int)] = 1
y_test_onehot = y_test_onehot.astype(np.float32)

X_val = X_val.astype(np.float32)
y_val_onehot = np.zeros((y_val.size, y_val.max().astype(int)+1))
y_val_onehot[np.arange(y_val.size), y_val.astype(int)] = 1
y_val_onehot = y_val_onehot.astype(np.float32)
X_test_small, X_val, y_test_small, y_val = train_test_split(X_test, y_test, test_size=0.5, random_state=101)

X_train = X_train.astype(np.float32)


def transfer_learning_model():
  mobilenet_model = MobileNet(input_shape=(IMG_HEIGHT, IMG_WIDTH, 3), include_top=False, pooling="max")

  transfer_model = Sequential()
  transfer_model.add(mobilenet_model)
  transfer_model.add(Dropout(0.1))
  transfer_model.add(BatchNormalization())
  transfer_model.add(Dense(256, activation="relu"))
  transfer_model.add(Dropout(0.1))
  transfer_model.add(BatchNormalization())
  transfer_model.add(Dense(7, activation="softmax"))

  return transfer_model

opt = keras.optimizers.RMSprop(learning_rate=0.0001, decay=1e-6)
transfer_model = transfer_learning_model()
transfer_model.compile(loss='categorical_crossentropy', metrics=[keras.metrics.AUC()])
transfer_model.fit(X_train, y_train_onehot,
    batch_size=10,
    epochs=20,
    validation_split=0.2,
    validation_batch_size=10,
    validation_data=(X_test, y_test_onehot))


!pip install coremltools
from keras.models import load_model
import coremltools
import coremltools as ct
#class_labels = ['akiec', 'bcc', 'bkl', 'df', 'mel', 'nv', 'vasc']

class_labels = ['Actinic Keratosis', 'Basal Cell (cancer)', 'Benign Keratosis', 'Skin bump', 'Melanoma (cancer)', 'Mole', 'Birthmark']
classifier_config = ct.ClassifierConfig(class_labels)

image_input = ct.ImageType()
model_from_tf = ct.convert(transfer_model, inputs=[image_input], classifier_config=classifier_config)

model_from_tf.save('skincancerkeras.mlmodel')
