# 05. 프로모션 효율 예측 (Random Forest 나무로 숲 만들기)

![image.png](attachment:image.png)

### Random Forest 는 어떻게 만들어졌을까?
- Decision Tree model 에서 발생하는 Overfitting 현상 : Train Set에만 잘 작동해서 test set에서 오히려 에러가 커지는 현상이다. 
- Naive 한 모델인 linear regression 과 Overfitted 된 모델의 중간지점을 찾는 것이 목적이다.
- 이를 이해하려면 Bagging Method 가 무엇인지 알아야 한다.


### Bagging Methond
- 하나의 데이터셋을 여러 subset으로 나누어 각각 모델링하고 이를 종합하는 방법이다.
- 취약한 트리를 모아 다수결의 원리로 성능을 높이는 개념이다.

### Random Forest
- 기존의 Bagging 은 관측치에 대한 샘플링을 진행한다.
- 반면 Random Foreset 는 subset을 구성하는 변수가 결정되는 기준을 제시한다.
- 즉, 특정 subset에서 중요했던 변수가 있다면 다른 subset 에서는 그 변수를 제외하고 다른 변수들로 tree 를 구성하여 결과를 비교하는 방식이다.
- 이 트리들을 앙상블하여 최종 모델을 구성하면 decision tree 나 bagging 보다 높은 성능의 모델을 만들 수 있다.


## 구매 전환율 예측
- 이번 챕터에서는 Conversion (구매 전환 여부)를 랜덤포레스트를 이용하여 예측해볼 것이다.

## Loading module and data


```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings(action = 'ignore')
```


```python
mem = pd.read_csv('member.csv')
tran = pd.read_csv('transaction.csv')
```


```python
mem.head()
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
      <th>id</th>
      <th>recency</th>
      <th>zip_code</th>
      <th>is_referral</th>
      <th>channel</th>
      <th>conversion</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>906145</td>
      <td>10</td>
      <td>Surburban</td>
      <td>0</td>
      <td>Phone</td>
      <td>0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>184478</td>
      <td>6</td>
      <td>Rural</td>
      <td>1</td>
      <td>Web</td>
      <td>0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>394235</td>
      <td>7</td>
      <td>Surburban</td>
      <td>1</td>
      <td>Web</td>
      <td>0</td>
    </tr>
    <tr>
      <th>3</th>
      <td>130152</td>
      <td>9</td>
      <td>Rural</td>
      <td>1</td>
      <td>Web</td>
      <td>0</td>
    </tr>
    <tr>
      <th>4</th>
      <td>940352</td>
      <td>2</td>
      <td>Urban</td>
      <td>0</td>
      <td>Web</td>
      <td>0</td>
    </tr>
  </tbody>
</table>
</div>



- conversion - 구매 전환 여부
- recency - 최근 구매 날짜 10 이면 10일 전에 구매함
- is_referral - 추천인 유무


```python
mem.info()
```

    <class 'pandas.core.frame.DataFrame'>
    RangeIndex: 64000 entries, 0 to 63999
    Data columns (total 6 columns):
     #   Column       Non-Null Count  Dtype 
    ---  ------       --------------  ----- 
     0   id           64000 non-null  int64 
     1   recency      64000 non-null  int64 
     2   zip_code     64000 non-null  object
     3   is_referral  64000 non-null  int64 
     4   channel      64000 non-null  object
     5   conversion   64000 non-null  int64 
    dtypes: int64(4), object(2)
    memory usage: 2.9+ MB
    


```python
mem.describe()
# conversion - 전환률 , mean 값이 0.14이므로 약 14퍼센트의 전환이 이루어짐
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
      <th>id</th>
      <th>recency</th>
      <th>is_referral</th>
      <th>conversion</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>count</th>
      <td>64000.000000</td>
      <td>64000.000000</td>
      <td>64000.000000</td>
      <td>64000.000000</td>
    </tr>
    <tr>
      <th>mean</th>
      <td>550694.137797</td>
      <td>5.763734</td>
      <td>0.502250</td>
      <td>0.146781</td>
    </tr>
    <tr>
      <th>std</th>
      <td>259105.689773</td>
      <td>3.507592</td>
      <td>0.499999</td>
      <td>0.353890</td>
    </tr>
    <tr>
      <th>min</th>
      <td>100001.000000</td>
      <td>1.000000</td>
      <td>0.000000</td>
      <td>0.000000</td>
    </tr>
    <tr>
      <th>25%</th>
      <td>326772.000000</td>
      <td>2.000000</td>
      <td>0.000000</td>
      <td>0.000000</td>
    </tr>
    <tr>
      <th>50%</th>
      <td>551300.000000</td>
      <td>6.000000</td>
      <td>1.000000</td>
      <td>0.000000</td>
    </tr>
    <tr>
      <th>75%</th>
      <td>774914.500000</td>
      <td>9.000000</td>
      <td>1.000000</td>
      <td>0.000000</td>
    </tr>
    <tr>
      <th>max</th>
      <td>999997.000000</td>
      <td>12.000000</td>
      <td>1.000000</td>
      <td>1.000000</td>
    </tr>
  </tbody>
</table>
</div>




```python
tran.head()
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
      <th>id</th>
      <th>num_item</th>
      <th>total_amount</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>906145</td>
      <td>5</td>
      <td>34000</td>
    </tr>
    <tr>
      <th>1</th>
      <td>906145</td>
      <td>1</td>
      <td>27000</td>
    </tr>
    <tr>
      <th>2</th>
      <td>906145</td>
      <td>4</td>
      <td>33000</td>
    </tr>
    <tr>
      <th>3</th>
      <td>184478</td>
      <td>4</td>
      <td>29000</td>
    </tr>
    <tr>
      <th>4</th>
      <td>394235</td>
      <td>4</td>
      <td>33000</td>
    </tr>
  </tbody>
</table>
</div>



- num_item - 한번에 구매한 물품 개수 (*주의!* 특정 회원이 구매한 횟수와 다름)

- total_amount - 취급액


```python
tran.info()
```

    <class 'pandas.core.frame.DataFrame'>
    RangeIndex: 196836 entries, 0 to 196835
    Data columns (total 3 columns):
     #   Column        Non-Null Count   Dtype
    ---  ------        --------------   -----
     0   id            196836 non-null  int64
     1   num_item      196836 non-null  int64
     2   total_amount  196836 non-null  int64
    dtypes: int64(3)
    memory usage: 4.5 MB
    


```python
tran.describe()
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
      <th>id</th>
      <th>num_item</th>
      <th>total_amount</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>count</th>
      <td>196836.000000</td>
      <td>196836.000000</td>
      <td>196836.000000</td>
    </tr>
    <tr>
      <th>mean</th>
      <td>550557.552932</td>
      <td>3.078365</td>
      <td>21837.102969</td>
    </tr>
    <tr>
      <th>std</th>
      <td>259254.795613</td>
      <td>1.478408</td>
      <td>8218.005565</td>
    </tr>
    <tr>
      <th>min</th>
      <td>100001.000000</td>
      <td>1.000000</td>
      <td>8000.000000</td>
    </tr>
    <tr>
      <th>25%</th>
      <td>326719.000000</td>
      <td>2.000000</td>
      <td>15000.000000</td>
    </tr>
    <tr>
      <th>50%</th>
      <td>550918.000000</td>
      <td>3.000000</td>
      <td>22000.000000</td>
    </tr>
    <tr>
      <th>75%</th>
      <td>774916.000000</td>
      <td>4.000000</td>
      <td>29000.000000</td>
    </tr>
    <tr>
      <th>max</th>
      <td>999997.000000</td>
      <td>6.000000</td>
      <td>38000.000000</td>
    </tr>
  </tbody>
</table>
</div>



-----

## How to join the two data sets

- member 는 한 고객당 한 행으로 이루어져 있고 tran 은 한 고객 당 구매한 횟수만큼 여러행으로 이루어져있다.
- 두 데이터 중 어떤 데이터셋을 기준으로 병합해야 할까?
- 궁극적으로 도출하고자 하는 정보가 특정 고객의 ***구매여부*** 이므로 member를 기준으로 join 한다.

### 컬럼 추가생성
- avg_price 로 상품 개수 컬럼생성 
- 거래 몇번 했는지 cnt로 컬럼 생성
- tran_df 로 통합



```python
tran
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
      <th>id</th>
      <th>num_item</th>
      <th>total_amount</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>906145</td>
      <td>5</td>
      <td>34000</td>
    </tr>
    <tr>
      <th>1</th>
      <td>906145</td>
      <td>1</td>
      <td>27000</td>
    </tr>
    <tr>
      <th>2</th>
      <td>906145</td>
      <td>4</td>
      <td>33000</td>
    </tr>
    <tr>
      <th>3</th>
      <td>184478</td>
      <td>4</td>
      <td>29000</td>
    </tr>
    <tr>
      <th>4</th>
      <td>394235</td>
      <td>4</td>
      <td>33000</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>196831</th>
      <td>536246</td>
      <td>5</td>
      <td>24000</td>
    </tr>
    <tr>
      <th>196832</th>
      <td>927617</td>
      <td>5</td>
      <td>26000</td>
    </tr>
    <tr>
      <th>196833</th>
      <td>927617</td>
      <td>3</td>
      <td>22000</td>
    </tr>
    <tr>
      <th>196834</th>
      <td>927617</td>
      <td>3</td>
      <td>18000</td>
    </tr>
    <tr>
      <th>196835</th>
      <td>927617</td>
      <td>3</td>
      <td>20000</td>
    </tr>
  </tbody>
</table>
<p>196836 rows × 3 columns</p>
</div>




```python
# 상품 평균 가격 컬럼 생성
tran['avg_price'] = tran['total_amount']/tran['num_item']
```


```python
# Groupby를 id별 평균 알아보기
tran_mean = tran.groupby('id').mean()
tran_mean
# 전체 데이터 개수 변화에 유의
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
      <th>num_item</th>
      <th>total_amount</th>
      <th>avg_price</th>
    </tr>
    <tr>
      <th>id</th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>100001</th>
      <td>3.500000</td>
      <td>26000.000000</td>
      <td>7500.000000</td>
    </tr>
    <tr>
      <th>100008</th>
      <td>5.000000</td>
      <td>26000.000000</td>
      <td>5200.000000</td>
    </tr>
    <tr>
      <th>100032</th>
      <td>2.666667</td>
      <td>20666.666667</td>
      <td>9366.666667</td>
    </tr>
    <tr>
      <th>100036</th>
      <td>3.000000</td>
      <td>25800.000000</td>
      <td>13273.333333</td>
    </tr>
    <tr>
      <th>100070</th>
      <td>3.250000</td>
      <td>21250.000000</td>
      <td>8537.500000</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>999932</th>
      <td>5.000000</td>
      <td>32000.000000</td>
      <td>6400.000000</td>
    </tr>
    <tr>
      <th>999981</th>
      <td>2.000000</td>
      <td>22750.000000</td>
      <td>12875.000000</td>
    </tr>
    <tr>
      <th>999990</th>
      <td>3.000000</td>
      <td>28000.000000</td>
      <td>10388.888889</td>
    </tr>
    <tr>
      <th>999995</th>
      <td>2.000000</td>
      <td>27000.000000</td>
      <td>13500.000000</td>
    </tr>
    <tr>
      <th>999997</th>
      <td>2.000000</td>
      <td>13000.000000</td>
      <td>6500.000000</td>
    </tr>
  </tbody>
</table>
<p>64000 rows × 3 columns</p>
</div>




```python
#id 기준 거래 몇회 했는지 확인
tran['id'].value_counts().head()
```




    446874    5
    473857    5
    384266    5
    648461    5
    130318    5
    Name: id, dtype: int64




```python
#ID 별 거래 횟수-> tran_cnt 에 지정
tran_cnt = tran['id'].value_counts()
```


```python
# tran_df 에 tran_cnt 병합하기, concat 사용 (concat은 list 형태로 넣어줘야 함)
tran_df = pd.concat([tran_mean, tran_cnt], axis = 1)
```


```python
tran_df.head()
#거래 건수이므로 column 명을 id 가 아닌 count 로 변경해야함.
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
      <th>num_item</th>
      <th>total_amount</th>
      <th>avg_price</th>
      <th>id</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>100001</th>
      <td>3.500000</td>
      <td>26000.000000</td>
      <td>7500.000000</td>
      <td>2</td>
    </tr>
    <tr>
      <th>100008</th>
      <td>5.000000</td>
      <td>26000.000000</td>
      <td>5200.000000</td>
      <td>1</td>
    </tr>
    <tr>
      <th>100032</th>
      <td>2.666667</td>
      <td>20666.666667</td>
      <td>9366.666667</td>
      <td>3</td>
    </tr>
    <tr>
      <th>100036</th>
      <td>3.000000</td>
      <td>25800.000000</td>
      <td>13273.333333</td>
      <td>5</td>
    </tr>
    <tr>
      <th>100070</th>
      <td>3.250000</td>
      <td>21250.000000</td>
      <td>8537.500000</td>
      <td>4</td>
    </tr>
  </tbody>
</table>
</div>




```python
tran_df.columns
```




    Index(['num_item', 'total_amount', 'avg_price', 'id'], dtype='object')




```python
# 컬럼명 변경
tran_df.columns = ['num_item', 'total_amount', 'avg_price', 'count']
```


```python

```

-------

### mem & tran 병합


```python
tran_df
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
      <th>num_item</th>
      <th>total_amount</th>
      <th>avg_price</th>
      <th>count</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>100001</th>
      <td>3.500000</td>
      <td>26000.000000</td>
      <td>7500.000000</td>
      <td>2</td>
    </tr>
    <tr>
      <th>100008</th>
      <td>5.000000</td>
      <td>26000.000000</td>
      <td>5200.000000</td>
      <td>1</td>
    </tr>
    <tr>
      <th>100032</th>
      <td>2.666667</td>
      <td>20666.666667</td>
      <td>9366.666667</td>
      <td>3</td>
    </tr>
    <tr>
      <th>100036</th>
      <td>3.000000</td>
      <td>25800.000000</td>
      <td>13273.333333</td>
      <td>5</td>
    </tr>
    <tr>
      <th>100070</th>
      <td>3.250000</td>
      <td>21250.000000</td>
      <td>8537.500000</td>
      <td>4</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>999932</th>
      <td>5.000000</td>
      <td>32000.000000</td>
      <td>6400.000000</td>
      <td>1</td>
    </tr>
    <tr>
      <th>999981</th>
      <td>2.000000</td>
      <td>22750.000000</td>
      <td>12875.000000</td>
      <td>4</td>
    </tr>
    <tr>
      <th>999990</th>
      <td>3.000000</td>
      <td>28000.000000</td>
      <td>10388.888889</td>
      <td>3</td>
    </tr>
    <tr>
      <th>999995</th>
      <td>2.000000</td>
      <td>27000.000000</td>
      <td>13500.000000</td>
      <td>1</td>
    </tr>
    <tr>
      <th>999997</th>
      <td>2.000000</td>
      <td>13000.000000</td>
      <td>6500.000000</td>
      <td>1</td>
    </tr>
  </tbody>
</table>
<p>64000 rows × 4 columns</p>
</div>




```python
mem
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
      <th>id</th>
      <th>recency</th>
      <th>zip_code</th>
      <th>is_referral</th>
      <th>channel</th>
      <th>conversion</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>906145</td>
      <td>10</td>
      <td>Surburban</td>
      <td>0</td>
      <td>Phone</td>
      <td>0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>184478</td>
      <td>6</td>
      <td>Rural</td>
      <td>1</td>
      <td>Web</td>
      <td>0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>394235</td>
      <td>7</td>
      <td>Surburban</td>
      <td>1</td>
      <td>Web</td>
      <td>0</td>
    </tr>
    <tr>
      <th>3</th>
      <td>130152</td>
      <td>9</td>
      <td>Rural</td>
      <td>1</td>
      <td>Web</td>
      <td>0</td>
    </tr>
    <tr>
      <th>4</th>
      <td>940352</td>
      <td>2</td>
      <td>Urban</td>
      <td>0</td>
      <td>Web</td>
      <td>0</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>63995</th>
      <td>838295</td>
      <td>10</td>
      <td>Urban</td>
      <td>0</td>
      <td>Web</td>
      <td>0</td>
    </tr>
    <tr>
      <th>63996</th>
      <td>547316</td>
      <td>5</td>
      <td>Urban</td>
      <td>1</td>
      <td>Phone</td>
      <td>0</td>
    </tr>
    <tr>
      <th>63997</th>
      <td>131575</td>
      <td>6</td>
      <td>Urban</td>
      <td>1</td>
      <td>Phone</td>
      <td>0</td>
    </tr>
    <tr>
      <th>63998</th>
      <td>603659</td>
      <td>1</td>
      <td>Surburban</td>
      <td>1</td>
      <td>Multichannel</td>
      <td>0</td>
    </tr>
    <tr>
      <th>63999</th>
      <td>254229</td>
      <td>1</td>
      <td>Surburban</td>
      <td>0</td>
      <td>Web</td>
      <td>0</td>
    </tr>
  </tbody>
</table>
<p>64000 rows × 6 columns</p>
</div>



- tran 과 달리 mem 은 id 가 인덱스로 지정되어 있지 않다.
- mem 의 id 를 index로 갖고와야함 (join 활용해서 합치려면 )


```python
# mem 의 id를 index로 설정
mem.set_index('id', inplace = True)
```


```python
mem.join(tran_df)
# 동일한 id 를 지녔으므로 어떤 join 이든 같은 결과값이다
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
      <th>recency</th>
      <th>zip_code</th>
      <th>is_referral</th>
      <th>channel</th>
      <th>conversion</th>
      <th>num_item</th>
      <th>total_amount</th>
      <th>avg_price</th>
      <th>count</th>
    </tr>
    <tr>
      <th>id</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>906145</th>
      <td>10</td>
      <td>Surburban</td>
      <td>0</td>
      <td>Phone</td>
      <td>0</td>
      <td>3.333333</td>
      <td>31333.333333</td>
      <td>14016.666667</td>
      <td>3</td>
    </tr>
    <tr>
      <th>184478</th>
      <td>6</td>
      <td>Rural</td>
      <td>1</td>
      <td>Web</td>
      <td>0</td>
      <td>4.000000</td>
      <td>29000.000000</td>
      <td>7250.000000</td>
      <td>1</td>
    </tr>
    <tr>
      <th>394235</th>
      <td>7</td>
      <td>Surburban</td>
      <td>1</td>
      <td>Web</td>
      <td>0</td>
      <td>4.000000</td>
      <td>20500.000000</td>
      <td>5125.000000</td>
      <td>2</td>
    </tr>
    <tr>
      <th>130152</th>
      <td>9</td>
      <td>Rural</td>
      <td>1</td>
      <td>Web</td>
      <td>0</td>
      <td>1.750000</td>
      <td>20750.000000</td>
      <td>14875.000000</td>
      <td>4</td>
    </tr>
    <tr>
      <th>940352</th>
      <td>2</td>
      <td>Urban</td>
      <td>0</td>
      <td>Web</td>
      <td>0</td>
      <td>3.000000</td>
      <td>31000.000000</td>
      <td>10333.333333</td>
      <td>1</td>
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
      <td>...</td>
    </tr>
    <tr>
      <th>838295</th>
      <td>10</td>
      <td>Urban</td>
      <td>0</td>
      <td>Web</td>
      <td>0</td>
      <td>3.500000</td>
      <td>26000.000000</td>
      <td>8012.500000</td>
      <td>4</td>
    </tr>
    <tr>
      <th>547316</th>
      <td>5</td>
      <td>Urban</td>
      <td>1</td>
      <td>Phone</td>
      <td>0</td>
      <td>1.800000</td>
      <td>17800.000000</td>
      <td>11300.000000</td>
      <td>5</td>
    </tr>
    <tr>
      <th>131575</th>
      <td>6</td>
      <td>Urban</td>
      <td>1</td>
      <td>Phone</td>
      <td>0</td>
      <td>4.000000</td>
      <td>30500.000000</td>
      <td>7833.333333</td>
      <td>2</td>
    </tr>
    <tr>
      <th>603659</th>
      <td>1</td>
      <td>Surburban</td>
      <td>1</td>
      <td>Multichannel</td>
      <td>0</td>
      <td>3.200000</td>
      <td>21600.000000</td>
      <td>7583.333333</td>
      <td>5</td>
    </tr>
    <tr>
      <th>254229</th>
      <td>1</td>
      <td>Surburban</td>
      <td>0</td>
      <td>Web</td>
      <td>0</td>
      <td>3.400000</td>
      <td>24400.000000</td>
      <td>9280.000000</td>
      <td>5</td>
    </tr>
  </tbody>
</table>
<p>64000 rows × 9 columns</p>
</div>




```python
# 할당하기
data = mem.join(tran_df)
```

---------

## 카테고리 변수 처리

- unique 한 범주형 변수를 어떻게 처리할까? 
- 주어진 범주형 변수 : zip_code, channel
- 각각 몇 가지 종류 있는지 확인해보자


```python
data['zip_code'].unique()
```




    array(['Surburban', 'Rural', 'Urban'], dtype=object)




```python
data['zip_code'].nunique()
```




    3




```python
data['channel'].unique()
```




    array(['Phone', 'Web', 'Multichannel'], dtype=object)




```python
data['channel'].nunique()
```




    3



- zip_code와 channel 모두 3가지 범주가 존재한다. 
- 3가지면 컬럼 수가 크게 늘어나지 않으므로 get_dummies 를 써도 무방하다.


```python
#data에 zip_code와 channel 의 binary 변수 생성하고 불필요한 컬럼 제거
data = pd.get_dummies(data, columns = ['zip_code', 'channel'], drop_first = True)
```


```python
data.head()
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
      <th>recency</th>
      <th>is_referral</th>
      <th>conversion</th>
      <th>num_item</th>
      <th>total_amount</th>
      <th>avg_price</th>
      <th>count</th>
      <th>zip_code_Surburban</th>
      <th>zip_code_Urban</th>
      <th>channel_Phone</th>
      <th>channel_Web</th>
    </tr>
    <tr>
      <th>id</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>906145</th>
      <td>10</td>
      <td>0</td>
      <td>0</td>
      <td>3.333333</td>
      <td>31333.333333</td>
      <td>14016.666667</td>
      <td>3</td>
      <td>1</td>
      <td>0</td>
      <td>1</td>
      <td>0</td>
    </tr>
    <tr>
      <th>184478</th>
      <td>6</td>
      <td>1</td>
      <td>0</td>
      <td>4.000000</td>
      <td>29000.000000</td>
      <td>7250.000000</td>
      <td>1</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>1</td>
    </tr>
    <tr>
      <th>394235</th>
      <td>7</td>
      <td>1</td>
      <td>0</td>
      <td>4.000000</td>
      <td>20500.000000</td>
      <td>5125.000000</td>
      <td>2</td>
      <td>1</td>
      <td>0</td>
      <td>0</td>
      <td>1</td>
    </tr>
    <tr>
      <th>130152</th>
      <td>9</td>
      <td>1</td>
      <td>0</td>
      <td>1.750000</td>
      <td>20750.000000</td>
      <td>14875.000000</td>
      <td>4</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>1</td>
    </tr>
    <tr>
      <th>940352</th>
      <td>2</td>
      <td>0</td>
      <td>0</td>
      <td>3.000000</td>
      <td>31000.000000</td>
      <td>10333.333333</td>
      <td>1</td>
      <td>0</td>
      <td>1</td>
      <td>0</td>
      <td>1</td>
    </tr>
  </tbody>
</table>
</div>



----

## Modeling
- 전체적인 순서는 Decision Tree 를 비롯한 기존 모델들과 비슷하다.
1. train, test set을 나눈다.
2. model 을 지정하고 적합한다.
3. 예측한 값과 실제 값을 비교한다


```python
from sklearn.model_selection import train_test_split
```


```python
X_train, X_test, y_train, y_test = train_test_split(data.drop('conversion', axis = 1), data['conversion'], test_size = 0.3, random_state = 100)
```


```python
from sklearn.ensemble import RandomForestClassifier
```


```python
model = RandomForestClassifier(max_depth = 10, random_state = 100)
```


```python
model.fit(X_train, y_train)
```




    RandomForestClassifier(max_depth=10, random_state=100)




```python
pred = model.predict(X_test)
```


```python
from sklearn.metrics import accuracy_score, confusion_matrix
```


```python
accuracy_score(y_test, pred)
```




    0.87515625



### 0.87 의 정확도가 얼마나 정확하다고 할 수 있을까?
- 높은 정확도라고 할 수 없다.
- 원래 conversion 컬럼의 0의 비율이 약 84%였으므로 모두 0으로 예측했다고 해도 정확도는 84 %이기 때문이다.


```python
confusion_matrix(y_test, pred)
```




    array([[16403,    60],
           [ 2337,   400]], dtype=int64)



## Classification Report 의미 해석하기
### Precision, Recall 과 Error
- Precision : 예측한 것 중 맞게 예측한 비율
- Recall : 실제 값 중에 맞게 예측한 비율 
- 문제 상황에 따라 주목해야하는 것이 달라진다. 둘을 종합한 F1 값도 활용할 수 있다.


```python
from sklearn.metrics import classification_report
```


```python
print(classification_report(y_test, pred))
```

                  precision    recall  f1-score   support
    
               0       0.88      1.00      0.93     16463
               1       0.87      0.15      0.25      2737
    
        accuracy                           0.88     19200
       macro avg       0.87      0.57      0.59     19200
    weighted avg       0.87      0.88      0.83     19200
    
    

- 1에 대한 recall 이 0.15로 매우 낮게 나타난다. 
- 즉 데이터에 0 이 많으므로 0 과 관련된 지표는 양호하나 실제 1인 값중 맞게 예측한 비율이 낮다.

## Random Forest Regressor로 확률 예측하기
- 연속형 변수로 전환율 예측


```python
from sklearn.ensemble import RandomForestRegressor
```


```python
rf = RandomForestRegressor(max_depth = 10, random_state = 100)
```


```python
rf.fit(X_train, y_train)
```




    RandomForestRegressor(max_depth=10, random_state=100)




```python
pred = rf.predict(X_test)
```


```python
pd.DataFrame(pred)
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
      <th>0</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0.000000</td>
    </tr>
    <tr>
      <th>1</th>
      <td>0.058584</td>
    </tr>
    <tr>
      <th>2</th>
      <td>0.000000</td>
    </tr>
    <tr>
      <th>3</th>
      <td>0.594169</td>
    </tr>
    <tr>
      <th>4</th>
      <td>0.083316</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
    </tr>
    <tr>
      <th>19195</th>
      <td>0.142431</td>
    </tr>
    <tr>
      <th>19196</th>
      <td>0.000000</td>
    </tr>
    <tr>
      <th>19197</th>
      <td>0.116323</td>
    </tr>
    <tr>
      <th>19198</th>
      <td>0.000000</td>
    </tr>
    <tr>
      <th>19199</th>
      <td>0.054583</td>
    </tr>
  </tbody>
</table>
<p>19200 rows × 1 columns</p>
</div>



- 그런데 결과값이 0이나 1이 아니라 0~1사이의 연속형 변수이다.
- 이를 실제값과 어떻게 비교할것인가?
- 기준점에 따라 0이나 1로 변형할 수 있도록 함수를 생성해보자

## 0~1 사이의 연속형 변수(확률값)를 0과 1로 변환하기

- 방법 1

- 방법 1 : 기준점에 따라 0 or 1 로 나누는 함수 생성해서 예측값 전체에 적용하기
- 예측값 형태에 주의해야 한다


```python
def conv(x):
    if x >= 0.5:
        return 1
    else:
        return 0
```


```python
conv(0.6)
```




    1



- 단 array 형태인 pred 를 생성한 함수 안에 바로 적용할 수 없다.
-->apply 활용


```python
pd.Series(pred).apply(lambda x: conv(x))
```




    0        0
    1        0
    2        0
    3        1
    4        0
            ..
    19195    0
    19196    0
    19197    0
    19198    0
    19199    0
    Length: 19200, dtype: int64




```python
#할당하기 
pd_result = pd.Series(pred).apply(lambda x: conv(x))
```


```python
pd_result
```




    0        0
    1        0
    2        0
    3        1
    4        0
            ..
    19195    0
    19196    0
    19197    0
    19198    0
    19199    0
    Length: 19200, dtype: int64



- 방법2 : 결과값이 들어갈 빈 리스트 생성하여 for 문으로 적용하기


```python
result = []

for i in pred:
    result.append(conv(i))
    
```

- 방법3(List Comprehension)  : function 과 for loop 종합하여 코드 한 줄로 만들기 


```python
result_comp = [1 if x >= 0.5 else 0 for x in pred]
```


```python
# 정확도 확인
accuracy_score(y_test, result_comp)
```




    0.8799479166666667




```python
confusion_matrix(y_test, result_comp)
```




    array([[16313,   150],
           [ 2155,   582]], dtype=int64)




```python
print(classification_report(y_test, result_comp))
```

                  precision    recall  f1-score   support
    
               0       0.88      0.99      0.93     16463
               1       0.80      0.21      0.34      2737
    
        accuracy                           0.88     19200
       macro avg       0.84      0.60      0.63     19200
    weighted avg       0.87      0.88      0.85     19200
    
    

- 임계점을 0.5가 아닌 0.3으로 바꿔 1로 예측하는 비율을 늘려보자
- recall 과 precision 의 변화에 주목!


```python
result_3 = [1 if x >= 0.3 else 0 for x in pred]
```


```python
print(classification_report(y_test, result_3))
```

                  precision    recall  f1-score   support
    
               0       0.90      0.96      0.92     16463
               1       0.55      0.33      0.42      2737
    
        accuracy                           0.87     19200
       macro avg       0.72      0.64      0.67     19200
    weighted avg       0.85      0.87      0.85     19200
    
    

- 1에 대한  recall 은 0.21 -> 0.33으로 늘어났지만 precision 은 0.80에서 0.55 로 낮아진 것을 확인할 수 있다.
- 어떤 결과가 나은지는 business 상황에 따라 다르다.
- 만약 conversion 여부를 정확히 가려내고 싶다면 precision이 높은 쪽을 선택하면 된다.


```python

```

## 파라미터 튜닝하기

- 깊이를 얼마나 깊게 할지, 어떤 조건에서 트리를 나눌지 등의 조건을 바꿔 결과값을 비교해보자
- n_estimators : 트리 개수로 100이 default 
- min_samples_leaf=1, 마지막 노드(leaf)에 관측치가 몇개 이하로 내려가면 멈출 건지, 즉 값이 크면 overfit 방지할 수 있다.


```python
# 처음 결과
rf = RandomForestRegressor(max_depth = 10, random_state = 100)
rf.fit(X_train, y_train)
pred = rf.predict(X_test)
result_comp = [1 if x >=0.5 else 0 for x in pred]

accuracy_score(y_test, result_comp)
```




    0.8799479166666667




```python
# depth 10 ->12
rf = RandomForestRegressor(max_depth = 12, random_state = 100)
rf.fit(X_train, y_train)
pred = rf.predict(X_test)
result_comp = [1 if x >=0.5 else 0 for x in pred]

accuracy_score(y_test, result_comp)
```




    0.8805729166666667



- n_estimators : 트리 개수로 100이 default
- min_sample_leaf : 리프노드가 되기 위해 필요한 최소한의 샘플 데이터수


```python
# n_estimator = 100 이 가장 높은 정확도 보임
rf = RandomForestRegressor(n_estimators = 100, max_depth = 12, random_state = 100)
rf.fit(X_train, y_train)
pred = rf.predict(X_test)
result_comp = [1 if x >=0.5 else 0 for x in pred]

accuracy_score(y_test, result_comp)
```




    0.8805729166666667




```python

```

- 직접 조합을 만드는 것 외에도 Cross Validation 이나 Grid Search 로 최적의 파라미터를 찾을 수 있다. 

------

## 변수 중요도 확인하기

- feature importance는 linear regression 의 coefficient 와 달리 정확히 해석할 순 없으나 상대적인 중요도를 비교할 수 있다.


```python
rf.feature_importances_
```




    array([0.06390282, 0.0229547 , 0.31878145, 0.15857333, 0.25092914,
           0.14468844, 0.00936383, 0.00914032, 0.01179997, 0.009866  ])




```python
X_train.columns
```




    Index(['recency', 'is_referral', 'num_item', 'total_amount', 'avg_price',
           'count', 'zip_code_Surburban', 'zip_code_Urban', 'channel_Phone',
           'channel_Web'],
          dtype='object')



- seaborn 으로 feature importance 중요도 순서대로 막대그래프 그리기


```python
plt.figure(figsize = (20,10))


ft_importance = pd.Series(rf.feature_importances_).sort_values(ascending = False) # array 형태의 importance 를 series로 씌워줌

sns.barplot(x = X_train.columns, y = ft_importance)
```




    <AxesSubplot:>




    
![png](2021-03-06-RandomForest_files/2021-03-06-RandomForest_106_1.png)
    


- num_item, avg_price, total_amount 순서대로 중요하다
- randomforest 에서는 tree 가 너무 많아 tree plot 을 그리기 어렵다

-------

### + Grid Search
- 하이퍼파라미터 튜닝을 위해 grid search 를 활용할 수 있다.
- key, value 형태로 데이터를 받고 value 에 시험해볼 파라미터들을 리스트 형태로 넣는다


```python
rf_param_grid = {
    'n_estimators' : [80,100,120],
    'max_depth' : [8,10,12],
    'min_samples_leaf' : [3,5,7],
    'min_samples_split' : [2,3,5]
}
```


```python
from sklearn.model_selection import GridSearchCV
rf = RandomForestRegressor(random_state = 100)

# Instantiate the grid search model
rf_grid = GridSearchCV(rf, param_grid = rf_param_grid, n_jobs = -1, verbose = 1)
```


```python
rf_grid.fit(X_train, y_train)
```

    Fitting 5 folds for each of 81 candidates, totalling 405 fits
    

    [Parallel(n_jobs=-1)]: Using backend LokyBackend with 12 concurrent workers.
    [Parallel(n_jobs=-1)]: Done  26 tasks      | elapsed:   20.8s
    [Parallel(n_jobs=-1)]: Done 176 tasks      | elapsed:  1.8min
    [Parallel(n_jobs=-1)]: Done 405 out of 405 | elapsed:  4.6min finished
    




    GridSearchCV(estimator=RandomForestRegressor(random_state=100), n_jobs=-1,
                 param_grid={'max_depth': [8, 10, 12],
                             'min_samples_leaf': [3, 5, 7],
                             'min_samples_split': [2, 3, 5],
                             'n_estimators': [80, 100, 120]},
                 verbose=1)




```python
#최적의 grid가 무엇이냐
best_grid = rf_grid.best_params_
rf_grid.best_params_
```




    {'max_depth': 12,
     'min_samples_leaf': 3,
     'min_samples_split': 2,
     'n_estimators': 120}




```python
# min_samples_leaf 
rf = RandomForestRegressor(n_estimators = 100, max_depth = 12, random_state = 100, min_samples_leaf = 5)
rf.fit(X_train, y_train)
pred = rf.predict(X_test)
result_comp = [1 if x >=0.5 else 0 for x in pred]

accuracy_score(y_test, result_comp)
```




    0.8810416666666666




```python
print(classification_report(y_test, result_comp))
```

                  precision    recall  f1-score   support
    
               0       0.88      0.99      0.93     16463
               1       0.79      0.23      0.35      2737
    
        accuracy                           0.88     19200
       macro avg       0.84      0.61      0.64     19200
    weighted avg       0.87      0.88      0.85     19200
    
    

- 1에 대한 recall 과 f1-score가 증가했으므로 grid search를 통해 최적의 파라미터를 찾았다고 할 수 있다.


```python

```
