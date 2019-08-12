# -*- coding: utf-8 -*-
"""multi_step_lstm_v1.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1rb06DIWwWIykb1EKbJo1aI_GeDeQfNmb
"""

import pandas as pd
from keras.models import load_model
from numpy import hstack
from numpy import array
from sklearn.preprocessing import MinMaxScaler
from keras.layers.advanced_activations import LeakyReLU

def split_sequences(df, n_steps_in, n_steps_out):
    from numpy import array
    from sklearn import preprocessing  # pip install sklearn ... if you don't have it!

    for col in df.columns:  # go through all of the columns
        if col != df.columns[-1]:  # normalize all ... except for the target itself!
            df[col] = preprocessing.scale(df[col].values)  # scale between 0 and 1.

    df.dropna(inplace=True)  # cleanup

    df = df.values

    # split a multivariate sequence into samples
    X, y = list(), list()
    for i in range(len(df)):
        # find the end of this pattern
        end_ix = i + n_steps_in
        out_end_ix = end_ix + n_steps_out - 1
        # check if we are beyond the dataset
        if out_end_ix > len(df):
            break
        # gather input and output parts of the pattern
        seq_x, seq_y = df[i:end_ix, :-1], df[end_ix - 1:out_end_ix, -1]
        X.append(seq_x)
        y.append(seq_y)
    return array(X), array(y)

def multi_step_lstm_model(lookback, lookahead, train_x, train_y, validation_x, validation_y, batch_size,epochs=100, model_name="lstm"):
	import time
	from numpy import array
	import tensorflow as tf
	import numpy as np
	from keras.models import Sequential
	from keras.layers import LSTM
	from keras.layers import Dense
	from keras.models import load_model
	from keras.layers import Dropout
	from keras.callbacks import EarlyStopping
	from keras.layers.advanced_activations import LeakyReLU
	from keras.layers import Input

	EPOCHS = epochs #how many passes through our data
	BATCH_SIZE = batch_size  # how many batches? Try smaller batch if you're getting OOM (out of memory) errors.
	NAME = f"{lookback}-SEQ-{lookahead}-PRED-{int(time.time())}"  # a unique name for the model

	# define model
	model = Sequential()
	#input_x = Input(batch_shape=(BATCH_SIZE, lookback, train_x.shape[2]), name='input')
	model.add(LSTM(120,return_sequences=True, batch_input_shape = (BATCH_SIZE,None, 1),stateful=True, input_shape=(train_x.shape[1:])))

	#model.add(BatchNormalization())  # normalizes activation outputs, same reason you want to normalize your input data.
	model.add(LeakyReLU(alpha=0.1))
	model.add(Dropout(0.2))
	model.add(LSTM(80, stateful=True))
	model.add(LeakyReLU(alpha=0.1))
	model.add(Dense(lookahead))
	model.compile(optimizer='adam', loss='mse')
	# callbacks
	# patient early stopping
	es = EarlyStopping(monitor='val_loss', verbose=1, patience=5)
	callbacks = [es]
	#tensorboard = TensorBoard(log_dir="logs/{}".format(NAME))
	#filepath = "LSTM_Final-{epoch:02d}-{val_acc:.3f}"  # unique file name that will include the epoch and the validation acc for that epoch
	#checkpoint = ModelCheckpoint("models/{}.model".format(filepath, monitor='val_acc', verbose=1, save_best_only=True,
	#                                                      mode='max'))  # saves only the best ones
	# fit model
	model.fit(train_x, train_y, epochs=EPOCHS, verbose=1, validation_data=(validation_x, validation_y), callbacks=callbacks, batch_size=BATCH_SIZE)
	model_name = "lstm_right_enc_" + (pd.Timestamp('now')).strftime(
			"%Y_%m_%d") + ".h5"  # save model and architecture to single file
	# Score model
	#score = model.evaluate(validation_x, validation_y, verbose=0)
	#print('Test loss:', score[0])
	#print('Test accuracy:', score[1])
	# Save model
	#model.save("./models/{}".format(model_name))
	model.save(format(model_name))
	print("Saved model : " + model_name + " to disk")

	return model



df = pd.read_csv("test_data.csv")
df = df.set_index('time')
df.columns = ['left_sensor', 'pressure', 'right_sensor']
df.dropna(inplace=True)

df = df[['left_sensor', 'right_sensor']]

lookback = 120  # how long of a preceeding sequence to collect for RNN
lookahead = 1  # how far into the future are we trying to predict?

## here, split away some slice of the future data from the main main_df.
times = df.index.values
last_10pct = df.index.values[-int(0.10*len(times))]

validation_main_df = df[(df.index >= last_10pct)]
main_df = df[(df.index < last_10pct)]

#train_x, train_y = preprocess_df(main_df, lookback)
#validation_x, validation_y = preprocess_df(validation_main_df, lookback)

train_x, train_y = split_sequences(main_df, lookback,lookahead)
validation_x, validation_y = split_sequences(validation_main_df, lookback,lookahead)

print(f"train data: {len(train_x)} validation: {len(validation_x)}")

#train_x
#train_y

def computeHCF(x, y):
    if x > y:
        smaller = y
    else:
        smaller = x
    for i in range(1, smaller+1):
        if((x % i == 0) and (y % i == 0)):
            hcf = i

    return hcf

batch_size= computeHCF(train_x.shape[0], validation_x.shape[0])
#batch_size = 500

model = multi_step_lstm_model(lookback, lookahead, train_x, train_y, validation_x, validation_y,epochs=100, batch_size=batch_size, model_name="lstm")


##### TESTING

df_test = df.iloc[lookback:, :]
test_x, test_y = split_sequences(df_test, lookback,lookahead)

yhat = model.predict(test_x, verbose=0, batch_size=batch_size)
print(len(yhat.flatten()))
#yhat[:1,:].flatten()

df_test.plot()

batch_size

train_x.shape[0]/ validation_x.shape[0]

