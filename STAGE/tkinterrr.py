import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, r2_score
from datetime import datetime as dt
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# configuring the output of pandas dataframe
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

# creating the columns
eng_cycle_col = ['engine', 'cycle']
setting_col = ['setting1', 'setting2', 'setting3']
sensor_col = ['sensor1', 'sensor2', 'sensor3', 'sensor4', 'sensor5', 'sensor6', 'sensor7', 'sensor8', 'sensor9', 'sensor10', 'sensor11', 'sensor12', 'sensor13', 'sensor14', 'sensor15', 'sensor16', 'sensor17', 'sensor18', 'sensor19', 'sensor20', 'sensor21']
columns = eng_cycle_col + setting_col + sensor_col

# Initialize the Tkinter root
root = tk.Tk()
root.title("Turbofan Engine Data Analysis")
root.geometry("1200x800")

# Function to load data
def load_data():
    global train_data, test_data, true_rul
    train_data_path = filedialog.askopenfilename(title="Select the training data file", filetypes=[("Text files", "*.txt")])
    test_data_path = filedialog.askopenfilename(title="Select the test data file", filetypes=[("Text files", "*.txt")])
    true_rul_path = filedialog.askopenfilename(title="Select the true RUL data file", filetypes=[("Text files", "*.txt")])

    if train_data_path and test_data_path and true_rul_path:
        train_data = pd.read_csv(train_data_path, sep='\s+', names=columns)
        test_data = pd.read_csv(test_data_path, sep='\s+', names=columns)
        true_rul = pd.read_csv(true_rul_path, sep='\s+', names=['RUL'])
        messagebox.showinfo("Data Load", "Data loaded successfully")
    else:
        messagebox.showerror("Data Load Error", "Failed to load data")

# Function to describe data
def data_desc(data):
    desc = data.describe().transpose()
    desc_text.delete("1.0", tk.END)
    desc_text.insert(tk.END, desc.to_string())

# Function to visualize data
def visualize_data():
    max_cycle = train_data[['engine', 'cycle']].groupby(['engine']).count().reset_index().rename(columns={'cycle': 'max_cycles'})

    fig, ax = plt.subplots(figsize=(15, 10))
    sns.barplot(x='engine', y='max_cycles', data=max_cycle, palette='magma', ax=ax)
    sns.set_context(font_scale=0.01)
    ax.set_title('Turbofan Engines LifeTime', fontweight='bold', size=20)
    ax.set_xlabel('engine', fontweight='bold', size=20)
    ax.set_ylabel('cycle', fontweight='bold', size=20)
    ax.set_xticks(rotation=90)
    ax.grid(True)
    fig.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack()

# Function to run Linear Regression
def run_linear_regression():
    global Y_test, Y_predict_test
    clean_train_data = preprocess_data(train_data)

    X_train = clean_train_data
    Y_train = clean_train_data.pop('RUL')
    X_test = preprocess_test_data(test_data)
    
    lm = LinearRegression()
    lm.fit(X_train, Y_train)

    Y_predict_train = lm.predict(X_train)
    Y_predict_test = lm.predict(X_test)
    
    evaluate(Y_train, Y_predict_train, 'train')
    evaluate(Y_test, Y_predict_test)

# Function to preprocess data
def preprocess_data(data):
    data = data.drop(['setting3', 'sensor1', 'sensor10', 'sensor18', 'sensor19'], axis=1)
    data = add_remaining_RUL(data)
    data = data.drop(['setting1', 'setting2', 'sensor6', 'sensor5', 'sensor16'], axis=1)
    return data

# Function to preprocess test data
def preprocess_test_data(data):
    data = data.groupby('engine').last().reset_index()
    data = data.drop(['setting1', 'setting2', 'sensor6', 'sensor5', 'sensor16', 'setting3', 'sensor1', 'sensor10', 'sensor18', 'sensor19'], axis=1)
    return data

# Function to add remaining RUL
def add_remaining_RUL(data):
    train_data_by_engine = data.groupby(by='engine')
    max_cycles = train_data_by_engine['cycle'].max()
    merged = data.merge(max_cycles.to_frame(name='max_cycles'), left_on='engine', right_index=True)
    merged["RUL"] = merged["max_cycles"] - merged['cycle']
    merged = merged.drop("max_cycles", axis=1)
    return merged

# Function to evaluate models
def evaluate(y_true, y_hat, label='test'):
    mse = mean_squared_error(y_true, y_hat)
    rmse = np.sqrt(mse)
    variance = r2_score(y_true, y_hat)
    result_text.insert(tk.END, '{} set RMSE:{}, R2:{}\n'.format(label, rmse, variance))

# Setting up the UI
load_button = tk.Button(root, text="Load Data", command=load_data)
load_button.pack()

desc_button = tk.Button(root, text="Describe Data", command=lambda: data_desc(train_data))
desc_button.pack()

visualize_button = tk.Button(root, text="Visualize Data", command=visualize_data)
visualize_button.pack()

lr_button = tk.Button(root, text="Run Linear Regression", command=run_linear_regression)
lr_button.pack()

desc_text = tk.Text(root, height=10)
desc_text.pack()

result_text = tk.Text(root, height=10)
result_text.pack()

root.mainloop()
