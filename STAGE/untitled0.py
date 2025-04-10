
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

#configuring the output of pandas dataframe
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

#creating the columns
eng_cycle_col=['engine', 'cycle']
setting_col=['setting1', 'setting2', 'setting3']
sensor_col = ['sensor1',
       'sensor2', 'sensor3', 'sensor4', 'sensor5', 'sensor6', 'sensor7',
       'sensor8', 'sensor9', 'sensor10', 'sensor11', 'sensor12', 'sensor13',
       'sensor14', 'sensor15', 'sensor16', 'sensor17', 'sensor18', 'sensor19',
       'sensor20', 'sensor21' ]
columns=eng_cycle_col+setting_col+sensor_col

#importing the dataset
train_data=pd.read_csv("train_FD001.txt",sep='\s+',names=columns)
test_data=pd.read_csv("test_FD001.txt",sep='\s+',names=columns)
true_rul=pd.read_csv("RUL_FD001.txt",sep='\s+',names=['RUL'])


#first let's print out our data and check its shape
print(train_data)
print(train_data.shape)
#we an see that the data contains 20631 rows and 26 columns

#now we will creat a function to describe our data
def data_desc(data):
    print('Data description:')
    return data.describe().transpose()

print(data_desc(train_data))

def check_missing_values(data):
    print('Verifing the existance of null data:')
    return data.isnull().sum()

print(check_missing_values(train_data))

#we see that everything is fine and we have no missing data
#looking further in the summary of the data we see that some columns have a standard deviation equqal to 0 so this means that this value
#is constant through all of the cycles of every engine so it wont affect the degradation and thus we can just drop them for a faster calculation time


def find_max_cycle(data):
    print('The max cycles of each engine: ')
    max_cycle = data[['engine', 'cycle']].groupby(['engine']).count().reset_index().rename(columns={'cycle': 'max_cycles'})
    return max_cycle

max_cycle=find_max_cycle(train_data)
print(max_cycle)

#i.e we can see that engine 1 failed after 192 cyclees and engin 2 failed after 287 cycles as it goes throw each engine
#these cyclce will serve us in wuhile plotting the data since we are going to use this late in the data plotting as an x axis


#So acutally let's plot this for better understanding
def barplt(data):
       plt.figure(figsize=(15,10))
       sns.barplot(x='engine', y='max_cycles', data=data,palette='magma')
       sns.set_context(font_scale=0.01)
       plt.title('Turbofan Engines LifeTime',fontweight='bold',size=20)
       plt.xlabel('engine',fontweight='bold',size=20)
       plt.ylabel('cycle',fontweight='bold',size=20)
       plt.xticks(rotation=90)
       plt.grid(True)
       plt.tight_layout()
barplt(max_cycle)
#this graph shows us that theengine number 69 wroked the most cycles with a value of 362 which is was already confirmed from the summary of the data shown before


#then what about the distrubtion?
def distribution(data):
       plt.figure(figsize=(15, 10))
       sns.histplot(data=data['max_cycles'],kde='True',bins=15)
       sns.set_context(font_scale=0.01)
       plt.title('Turbofan Engines LifeTime',fontweight='bold',size=20)
       plt.xlabel('cycle',fontweight='bold',size=20)
       plt.ylabel('frequency',fontweight='bold',size=20)
       plt.grid(True)
       plt.tight_layout()
distribution(max_cycle)
#we interpret from this graphic that most of the engines fail after reaching an approximat value  between  190 and 210 cycles
#Earlier we talked abbout how some settings and sensors have a standard deviation of 0 so they won't have any use in our analysis since it means they have  constant value
#so let's check again the summary discription of these sensors and settings
print(data_desc(train_data[sensor_col]))
print(data_desc(train_data[setting_col]))
#from this analysis we can interpret that sesnors [1,10,18,19] will have no effect on the performance of the engine and next to that setting 3 TOO



#after this we can plot the correlation matrix and the box plot of  the remaining data t better understand the realtionship between the variables of the data

#but first let's add the rmaining RUL of the each engine after each cylce meaning that we will add the column of the RUL descending each time by 1
#such as for engine 1 that has a maximum RUL of 192 we will print 191 in the first cyclethen 190 in the second cycle and go on

def add_remaining_RUL(data):
    train_data_by_engine = data.groupby(by='engine')
    max_cycles = train_data_by_engine['cycle'].max()
    merged = data.merge(max_cycles.to_frame(name='max_cycles'), left_on='engine',right_index=True)
    merged["RUL"] = merged["max_cycles"] - merged['cycle']
    merged = merged.drop("max_cycles", axis=1)
    return merged
train_data=add_remaining_RUL(train_data)


#and for more specific anaylsis this a function that shows plots the behavior of the sensors for a specific given engine number
#and this, along its remaining RUL
def info_plotting_per_engine(eng_num,data):
    engine_data = data[data['engine'] == eng_num]

    columns_to_plot = ['setting1', 'setting2', 'setting3'] + [f'sensor{i}' for i in range(1, 22)]

    num_columns = 6
    num_rows = (len(columns_to_plot) + num_columns - 1) // num_columns
    fig, axes = plt.subplots(num_rows, num_columns, figsize=(20, num_rows * 3), sharex=True)

    for ax, column in zip(axes.flatten(), columns_to_plot):
        ax.plot(engine_data['cycle'], engine_data[column], label=column)
        ax.set_title(f'{column} over Cycles')
        ax.set_xlabel('Cycle')
        ax.set_ylabel('Value')
        ax.legend()
        ax.grid(True)

    plt.tight_layout()
    plt.show()
#just select the desired engine number
info_plotting_per_engine(20,train_data)

#now let's really see the correlation between data
def corr_matrix(data):
    plt.figure(figsize=(15, 10))
    sns.set_context(font_scale=0.01)
    sns.heatmap(data.corr(), annot=True, cmap='RdYlGn')
    plt.grid(False)


corr_matrix(train_data)


# this graph concluds our analysis about the sensors that we left and it is clear that they have strong
# relation with the rmaining RUL  of each engine
# for more clearfication in the correlaion matriw the closer the number to 1 or -1 the better the relationship between the variabes is
# and ofc if the number is closer to 0 then there is no relationship between them
# so according to this graph wecal also drop the 6th, 5th and 16th  sensor along with the operaional settings 1 and 2


#now let'us  drop them from our data
clean_train_data=train_data.drop(['setting1','setting2','sensor6','sensor5','sensor16','setting3','sensor1','sensor10','sensor18','sensor19'],axis=1)
clean_test_data=test_data.drop(['setting1','setting2','sensor6','sensor5','sensor16','setting3','sensor1','sensor10','sensor18','sensor19'],axis=1)
print('Data after our cleaning: ')
print(clean_train_data)

sens_names={
 'sensor2': '(LPC outlet temperature) (◦R)',
 'sensor3': '(HPC outlet temperature) (◦R)',
 'sensor4': '(LPT outlet temperature) (◦R)',
 'sensor7': '(HPC outlet pressure) (psia)',
 'sensor8': '(Physical fan speed) (rpm)',
 'sensor9': '(Physical core speed) (rpm)',
 'sensor11': '(HPC outlet Static pressure) (psia)',
 'sensor12': '(Ratio of fuel flow to Ps30) (pps/psia)',
 'sensor13': '(Corrected fan speed) (rpm)',
 'sensor14': '(Corrected core speed) (rpm)',
 'sensor15': '(Bypass Ratio) ',
 'sensor17': '(Bleed Enthalpy)',
 'sensor20': '(High-pressure turbines Cool air flow)',
 'sensor21': '(Low-pressure turbines Cool air flow)'}

def plot_sensor(sensor_name,sens_names,data):
    for S in sensor_name:

        if S in data.columns:
            plt.figure(figsize=(13, 5))
            for i in data['engine'].unique():

                if (i % 5 == 0):

                    plt.plot('RUL', S,
                             data=data[data['engine']==i].rolling(8).mean())


            plt.xlim(250, 0)
            plt.xticks(np.arange(0, 275, 25))
            plt.ylabel(sens_names[S])
            plt.xlabel('Remaining Usefull Life ')
            plt.grid(True)
            plt.show()
plot_sensor(sensor_col,sens_names,clean_train_data)

#we can see from thses readings from the temperature sensors, that the tempreture starts raising more and more as the engines ages
#and their RUL descreses and we can say that this raising in temperature is starts at a value of 100 RULs left
#SO ofc as the temperature raises wesee that most of the fan speeds starts to go up too
#also the pressure in the hpc outlet has a signifant descrese
#and the bleed enthlapy was raising too and next to it the fuel flow to ps30 was decreasing so much
#And we can notice that the change of the curve in all tehse graphs was done at almmost the same RUL value remaining
#for all of the engines which is around 100



# now we have finished the EDA and we will start working on our prediction models



#but we wil a mke a function that can evalute the efiiency of our models by calculating the rmse(root mean squared error)
#this method acctually mesures the average differencec cbetween the prdicted values and the actual values sincce they ware provide for us
#we can use them to see how good our model is and the lower the value of the rmse is the better our model is
#next to it we will use also the R2 score this is also an evalutiaon method for our model and more pricesely how good of a fit it is to our data set
#and this is all done by mesuring how well correlated the real values and the predicted value and of course it wi^ll be between 0 and 1
# the close this value is to 1 the better our model is.
#Here we will scale the training data too using the MinMax scaler one the fof most common and easy to unsdertand scaling methods
scaler=MinMaxScaler()
scaled_data=scaler.fit_transform(clean_train_data.drop(['engine','cycle','RUL'],axis=1))
scaled_data=pd.DataFrame(scaled_data, columns=clean_train_data.drop(['engine','cycle', 'RUL'], axis=1).columns)

print('Cheking the scaled data')
print(scaled_data)
def evaluate(y_true, y_hat, label='test'):
    mse = mean_squared_error(y_true, y_hat)
    rmse = np.sqrt(mse)
    variance = r2_score(y_true, y_hat)
    print('{} set RMSE:{}, R2:{}'.format(label, rmse, variance))

#since our values in the dataset are contunious, numerical and it contains the targetted outcome we will be using supervised ML algorithms
# and one of  the simplest and most common models that we will be using at first is Linear Regression
#Linear regression predicts the relationship between two variables by assuming they have a straight-line connection.
# It finds the best line that minimizes the differences between predicted and actual values.
#preparin the data for ML models the X defines the data we are using for the training and Y is the desired prediction
X_train = clean_train_data
Y_train = clean_train_data.pop('RUL')
X_test = test_data.groupby('engine').last().reset_index().drop(['setting1','setting2','sensor6','sensor5','sensor16','setting3','sensor1','sensor10','sensor18','sensor19'], axis=1)
#Here wwe will scale the test data using the same method
scaled_test_data=scaler.transform(X_test.drop(['engine','cycle'],axis=1))
scaled_test_data=pd.DataFrame(scaled_test_data, columns=X_test.drop(['engine','cycle'], axis=1).columns)
Y_test= true_rul
X_train_s=scaled_data
X_test_s=scaled_test_data

#TEST 1 liinear regression
start_1=dt.now()
lm=LinearRegression()
lm.fit(X_train_s,Y_train)
Y_predict_train=lm.predict(X_train_s)
Y_predict_test = lm.predict(X_test_s)
print('Linear Regression evaluation score: ')
print('run time equals: '+str((dt.now() - start_1).seconds)+'s')
evaluate(Y_train, Y_predict_train, 'train')
evaluate(Y_test, Y_predict_test)
fig = plt.figure(figsize=(18,10))
plt.plot(Y_test,color='red', label='RUL')
plt.plot(Y_predict_test, label='Linear regression prediction')
plt.legend(loc='upper left')
plt.grid(True)


#we will also make a second model a bit more complicatiod called Random forest regressor
#It works by creating many decision trees, each built on randomly chosen subsets of the data.
# The model then aggregates the outputs of all of these decision trees to make an overall prediction for unseen data points.
# In this way, it can process larger datasets and capture more complex associations than individual decision trees.
#and  a little explanation about a dicision tree, it is a decision support hierarchical model use a tree-like model that containes the deicisons and their possible outcomes

#test 2 decision tree
start_2=dt.now()
rf = RandomForestRegressor(max_features="sqrt", random_state=42)
rf.fit(X_train_s,Y_train)
Y_predict_train_rf=rf.predict(X_train_s)
Y_predict_test_rf = rf.predict(X_test_s)
print('Random Forest Regressor evaluation: ')
print('run time equals: '+str((dt.now() - start_2).seconds)+'s')
evaluate(Y_train, Y_predict_train_rf, 'train')
evaluate(Y_test, Y_predict_test_rf)
plt.plot(Y_predict_test_rf,color='orange', label='Random forest prediction')
plt.legend(loc='upper left')
plt.grid(True)



#But alaso the most now efficent supervise alogrithm is support vector machine (SVM)
start_3 = dt.now()
svm= SVR(kernel='linear')
svm.fit(X_train_s,Y_train)
svm_train_prediction=svm.predict(X_train_s)
svm_test_predict=svm.predict(X_test_s)
print('Support vector machine evaluation')
print('run time equals: '+str((dt.now() - start_3).seconds)+'s')
evaluate(Y_train,svm_train_prediction,'train')
evaluate(Y_test,svm_test_predict)
plt.plot(svm_test_predict,color='black',label='SVM prediction')
plt.legend(loc='upper left')
plt.grid(True)
plt.show()
#so testing our 3 ML models we notice that the random forest regressor was the most efficent and accurate in both scaled and none scaled data
#and veery noticable thing is that scaled data performeed worse than the normal data