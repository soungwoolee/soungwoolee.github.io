# 01. 고객 연간 지출액 예측 (Linear Regression)
# Data load


```python
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings(action='ignore')
```


```python
data = pd.read_csv('ecommerce.csv')
```

# EDA


```python
data
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Email</th>
      <th>Address</th>
      <th>Avatar</th>
      <th>Avg. Session Length</th>
      <th>Time on App</th>
      <th>Time on Website</th>
      <th>Length of Membership</th>
      <th>Yearly Amount Spent</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>mstephenson@fernandez.com</td>
      <td>835 Frank Tunnel\nWrightmouth, MI 82180-9605</td>
      <td>Violet</td>
      <td>34.497268</td>
      <td>12.655651</td>
      <td>39.577668</td>
      <td>4.082621</td>
      <td>587.951054</td>
    </tr>
    <tr>
      <th>1</th>
      <td>hduke@hotmail.com</td>
      <td>4547 Archer Common\nDiazchester, CA 06566-8576</td>
      <td>DarkGreen</td>
      <td>31.926272</td>
      <td>11.109461</td>
      <td>37.268959</td>
      <td>2.664034</td>
      <td>392.204933</td>
    </tr>
    <tr>
      <th>2</th>
      <td>pallen@yahoo.com</td>
      <td>24645 Valerie Unions Suite 582\nCobbborough, D...</td>
      <td>Bisque</td>
      <td>33.000915</td>
      <td>11.330278</td>
      <td>37.110597</td>
      <td>4.104543</td>
      <td>487.547505</td>
    </tr>
    <tr>
      <th>3</th>
      <td>riverarebecca@gmail.com</td>
      <td>1414 David Throughway\nPort Jason, OH 22070-1220</td>
      <td>SaddleBrown</td>
      <td>34.305557</td>
      <td>13.717514</td>
      <td>36.721283</td>
      <td>3.120179</td>
      <td>581.852344</td>
    </tr>
    <tr>
      <th>4</th>
      <td>mstephens@davidson-herman.com</td>
      <td>14023 Rodriguez Passage\nPort Jacobville, PR 3...</td>
      <td>MediumAquaMarine</td>
      <td>33.330673</td>
      <td>12.795189</td>
      <td>37.536653</td>
      <td>4.446308</td>
      <td>599.406092</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>495</th>
      <td>lewisjessica@craig-evans.com</td>
      <td>4483 Jones Motorway Suite 872\nLake Jamiefurt,...</td>
      <td>Tan</td>
      <td>33.237660</td>
      <td>13.566160</td>
      <td>36.417985</td>
      <td>3.746573</td>
      <td>573.847438</td>
    </tr>
    <tr>
      <th>496</th>
      <td>katrina56@gmail.com</td>
      <td>172 Owen Divide Suite 497\nWest Richard, CA 19320</td>
      <td>PaleVioletRed</td>
      <td>34.702529</td>
      <td>11.695736</td>
      <td>37.190268</td>
      <td>3.576526</td>
      <td>529.049004</td>
    </tr>
    <tr>
      <th>497</th>
      <td>dale88@hotmail.com</td>
      <td>0787 Andrews Ranch Apt. 633\nSouth Chadburgh, ...</td>
      <td>Cornsilk</td>
      <td>32.646777</td>
      <td>11.499409</td>
      <td>38.332576</td>
      <td>4.958264</td>
      <td>551.620145</td>
    </tr>
    <tr>
      <th>498</th>
      <td>cwilson@hotmail.com</td>
      <td>680 Jennifer Lodge Apt. 808\nBrendachester, TX...</td>
      <td>Teal</td>
      <td>33.322501</td>
      <td>12.391423</td>
      <td>36.840086</td>
      <td>2.336485</td>
      <td>456.469510</td>
    </tr>
    <tr>
      <th>499</th>
      <td>hannahwilson@davidson.com</td>
      <td>49791 Rachel Heights Apt. 898\nEast Drewboroug...</td>
      <td>DarkMagenta</td>
      <td>33.715981</td>
      <td>12.418808</td>
      <td>35.771016</td>
      <td>2.735160</td>
      <td>497.778642</td>
    </tr>
  </tbody>
</table>
<p>500 rows × 8 columns</p>
</div>




```python
# 자료형 확인 가능
data.info()
```

    <class 'pandas.core.frame.DataFrame'>
    RangeIndex: 500 entries, 0 to 499
    Data columns (total 8 columns):
     #   Column                Non-Null Count  Dtype  
    ---  ------                --------------  -----  
     0   Email                 500 non-null    object 
     1   Address               500 non-null    object 
     2   Avatar                500 non-null    object 
     3   Avg. Session Length   500 non-null    float64
     4   Time on App           500 non-null    float64
     5   Time on Website       500 non-null    float64
     6   Length of Membership  500 non-null    float64
     7   Yearly Amount Spent   500 non-null    float64
    dtypes: float64(5), object(3)
    memory usage: 31.4+ KB
    


```python
# 간단한 통계 확인
data.describe()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Avg. Session Length</th>
      <th>Time on App</th>
      <th>Time on Website</th>
      <th>Length of Membership</th>
      <th>Yearly Amount Spent</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>count</th>
      <td>500.000000</td>
      <td>500.000000</td>
      <td>500.000000</td>
      <td>500.000000</td>
      <td>500.000000</td>
    </tr>
    <tr>
      <th>mean</th>
      <td>33.053194</td>
      <td>12.052488</td>
      <td>37.060445</td>
      <td>3.533462</td>
      <td>499.314038</td>
    </tr>
    <tr>
      <th>std</th>
      <td>0.992563</td>
      <td>0.994216</td>
      <td>1.010489</td>
      <td>0.999278</td>
      <td>79.314782</td>
    </tr>
    <tr>
      <th>min</th>
      <td>29.532429</td>
      <td>8.508152</td>
      <td>33.913847</td>
      <td>0.269901</td>
      <td>256.670582</td>
    </tr>
    <tr>
      <th>25%</th>
      <td>32.341822</td>
      <td>11.388153</td>
      <td>36.349257</td>
      <td>2.930450</td>
      <td>445.038277</td>
    </tr>
    <tr>
      <th>50%</th>
      <td>33.082008</td>
      <td>11.983231</td>
      <td>37.069367</td>
      <td>3.533975</td>
      <td>498.887875</td>
    </tr>
    <tr>
      <th>75%</th>
      <td>33.711985</td>
      <td>12.753850</td>
      <td>37.716432</td>
      <td>4.126502</td>
      <td>549.313828</td>
    </tr>
    <tr>
      <th>max</th>
      <td>36.139662</td>
      <td>15.126994</td>
      <td>40.005182</td>
      <td>6.922689</td>
      <td>765.518462</td>
    </tr>
  </tbody>
</table>
</div>




```python
# 산점도
sns.pairplot(data)
```




    <seaborn.axisgrid.PairGrid at 0x21f69542b80>




    
![png](http://soungwoolee.github.io/images/regression_8_1.png)


# Data Preprocessing


```python
data.drop(['Email','Address','Avatar'], axis =1, inplace =True)
```

# Spliting train, test set


```python
from sklearn.model_selection import train_test_split
```


```python
X = data.drop('Yearly Amount Spent', axis=1) # column drop
```


```python
y = data['Yearly Amount Spent']
```


```python
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.3, random_state=100)
```

# Modeling


```python
# 모듈 다운 - 자세한 summary 가 장점이다
import statsmodels.api as sm
```


```python
# y_train 부터 들어가는 순서에 주의
# OLS - 선형회귀 함수 - Ordinary Least Square 최소 제곱법( 선형회귀식 도출하는 방법 )
# lm 에 모델 훈련한 결과 저장
lm = sm.OLS(y_train, X_train).fit()
```


```python
lm.summary()
```




<table class="simpletable">
<caption>OLS Regression Results</caption>
<tr>
  <th>Dep. Variable:</th>    <td>Yearly Amount Spent</td> <th>  R-squared (uncentered):</th>      <td>   0.998</td> 
</tr>
<tr>
  <th>Model:</th>                    <td>OLS</td>         <th>  Adj. R-squared (uncentered):</th> <td>   0.998</td> 
</tr>
<tr>
  <th>Method:</th>              <td>Least Squares</td>    <th>  F-statistic:       </th>          <td>4.105e+04</td>
</tr>
<tr>
  <th>Date:</th>              <td>Fri, 26 Feb 2021</td>   <th>  Prob (F-statistic):</th>           <td>  0.00</td>  
</tr>
<tr>
  <th>Time:</th>                  <td>12:09:49</td>       <th>  Log-Likelihood:    </th>          <td> -1596.0</td> 
</tr>
<tr>
  <th>No. Observations:</th>       <td>   350</td>        <th>  AIC:               </th>          <td>   3200.</td> 
</tr>
<tr>
  <th>Df Residuals:</th>           <td>   346</td>        <th>  BIC:               </th>          <td>   3215.</td> 
</tr>
<tr>
  <th>Df Model:</th>               <td>     4</td>        <th>                     </th>              <td> </td>    
</tr>
<tr>
  <th>Covariance Type:</th>       <td>nonrobust</td>      <th>                     </th>              <td> </td>    
</tr>
</table>
<table class="simpletable">
<tr>
            <td></td>              <th>coef</th>     <th>std err</th>      <th>t</th>      <th>P>|t|</th>  <th>[0.025</th>    <th>0.975]</th>  
</tr>
<tr>
  <th>Avg. Session Length</th>  <td>   12.1440</td> <td>    0.930</td> <td>   13.062</td> <td> 0.000</td> <td>   10.315</td> <td>   13.973</td>
</tr>
<tr>
  <th>Time on App</th>          <td>   34.1355</td> <td>    1.212</td> <td>   28.168</td> <td> 0.000</td> <td>   31.752</td> <td>   36.519</td>
</tr>
<tr>
  <th>Time on Website</th>      <td>  -14.3109</td> <td>    0.868</td> <td>  -16.482</td> <td> 0.000</td> <td>  -16.019</td> <td>  -12.603</td>
</tr>
<tr>
  <th>Length of Membership</th> <td>   61.2897</td> <td>    1.250</td> <td>   49.025</td> <td> 0.000</td> <td>   58.831</td> <td>   63.749</td>
</tr>
</table>
<table class="simpletable">
<tr>
  <th>Omnibus:</th>       <td> 0.331</td> <th>  Durbin-Watson:     </th> <td>   1.991</td>
</tr>
<tr>
  <th>Prob(Omnibus):</th> <td> 0.848</td> <th>  Jarque-Bera (JB):  </th> <td>   0.454</td>
</tr>
<tr>
  <th>Skew:</th>          <td>-0.048</td> <th>  Prob(JB):          </th> <td>   0.797</td>
</tr>
<tr>
  <th>Kurtosis:</th>      <td> 2.852</td> <th>  Cond. No.          </th> <td>    55.0</td>
</tr>
</table><br/><br/>Notes:<br/>[1] R² is computed without centering (uncentered) since the model does not contain a constant.<br/>[2] Standard Errors assume that the covariance matrix of the errors is correctly specified.



# Prediction and Conclusion


```python
predictions = lm.predict(X_test)
```


```python
predictions
```




    69     417.904446
    29     567.655141
    471    535.668742
    344    425.644960
    54     474.949637
              ...    
    308    625.574018
    171    462.810969
    457    527.178727
    75     443.949278
    311    488.476740
    Length: 150, dtype: float64




```python
y_test
```




    69     451.575685
    29     554.722084
    471    541.049831
    344    442.722892
    54     522.404141
              ...    
    308    604.841319
    171    439.891280
    457    534.771485
    75     478.719357
    311    506.132342
    Name: Yearly Amount Spent, Length: 150, dtype: float64




```python
# 예측값과 관측값 비교
plt.figure(figsize = (10,10)) # 같은 비율로 보기 위해 사이즈 설정
sns.scatterplot(y_test,predictions)
```




    <AxesSubplot:xlabel='Yearly Amount Spent'>





![png](http://soungwoolee.github.io/images/regression_24_1.png)    


대체로 잘 예측한 모습을 확인할 수 있다.

## MSE 평균 제곱 오차 예측
- 추정값과 예측값의 평균 제곱 차이로 예측이 얼마나 잘 이루어졌는지 나타냄
- 스케일 크면 자연스럽게 커짐 -> 상대적인 수치로 받아들여야 함


```python
from sklearn import metrics
```


```python
#예측값 관측값 차이 
print('MSE:', metrics.mean_squared_error(y_test, predictions))
print('RMSE:', np.sqrt(metrics.mean_squared_error(y_test, predictions))) #크기 줄임
```

    MSE: 473.2679612616115
    RMSE: 21.754722734652617
    

## 회귀식에 대입해보기


```python
session_length = 36
time_app= 13
time_web = 35
member_len= 4
```


```python
expenditure = 12.1440*(session_length) + 34.1355 * (time_app) -14.3109*(time_web) + 61.2897*(member_len)
expenditure
```




    625.2228



- 각각의 설명변수 값이 위와 같을 때 연간 지출액의 추정치는 625.2228 이다. 
- 선형회귀는 예측력이 떨어지지만 독립변수 값이 주어졌을 때 종속변수 값을 쉽게 구할 수 있고 해석에 용이하다.


```python
jupyter nbconvert --to markdown 'regression.ipynb'
```


      File "<ipython-input-8-d35521921022>", line 1
        jupyter nbconvert --to markdown 'regression.ipynb'
                ^
    SyntaxError: invalid syntax
    



```python

```
