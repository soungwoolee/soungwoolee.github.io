# <이진분류와 1종, 2종오류>
<br/> 

## 1. Binary Classification
<br/> 

### 1-2) 이진 분류란? 🙄

* ***Binary classification*** is the task of classifying the elements of a set into two groups on the basis of a classification rule
* 이진분류란 yes or no 로 나뉘는 분류를 의미한다
    - ex) 죄가 있다 없다/ 질병이 있다 없다 

### 1-2) 실제값과 예측값을 positive, negative로 나타내기

|           |          | Prediction |          |
|:---------:|:--------:|:----------:|:--------:|
|           |          |  positive  | negative |
|    **True**   | positive |     TP     |    FN    |
| **condition** | negative |     FP     |    TN    |

* ***T(F) + P(N) 표기***는 뒷쪽이 예측, 앞쪽이 실제 True condition 이다
<br/>
    * True Positive : positive로 예측하고 실제 값도 positive
    * False Positive : positive로 예측했는데 실제 값은 negative
    * False Negative : negative로 예측했는데 실제 값은 positve
    * True Negative : negative로 예측하고 실제 값도 negative

* 예를들어, 어떤 질병의 양성과 음성을 가려낼 때 FP는 양성(prediction)으로 예측했는데 실제로 음성인 경우를 뜻한다
<br/> 

***
<br/> 

## 2. Type 1 error, Type 2 error

####  이진분류표의 앞부분이 F인 경우에서 , 즉 틀린예측들 중 FP는 type 1 error, FN 은 type 2 error 에 해당한다

### 2-1) Type 1 error

* 정의 : P(귀무가설 기각 ㅣ 귀무가설 True) 귀무가설이 참일 때 이를 기각할 확률 (단 이때 귀무가설은 positive이다)
    * FP는 positive로 예측했는데 실제로는 negative인 경우이므로 type1 error 와 동일한 의미이다
    * 1종 오류는 *억울한 옥살이* 개념에 적용할 수 있다. positive는 유죄, negative는 무죄이다. 죄가 있다고 판단했는데 실제로 죄가 없는 경우 이기 때문이다
    * 또 다른 예로 질병을 양성으로 진단했는데 실제로는 음성인 경우가 있다.
    * type 1 error 가 나타날 확률을 α , 유의수준이라고 한다.

### 2-2) Type 2 error

* 정의 : P(귀무가설 채택 ㅣ 귀무가설 False) , 귀무가설이 틀릴 때 이를 채택할 확률 (단 이때 귀무가설은 positive이다)
    * FN은 negative로 예측했는데 실제로 positive인 경우이므로 type2 error 와 같다
    * 2종오류는 *진범을 풀어줌* 개념에 적용할 수 있다. 무죄라고 판단했는데 실제로 유죄인 경우로 이해하면 된다
    * 추가적으로 병이 없다고 진단했는데 실제로는 있는 경우이다.
    * 상황에 따라 다르지만 보안시스템의 침입여부나 질병의 유무를 판단하는 상황에서, 2종오류는 침입자 혹은 질병을 가려내지 못한 것이므로 1종오류에 비해 치명적이다.😲
    * type 2 error 가 나타날 확률을 β 로 부르고 1-β 를 검정력이라고 한다

***

[출처](https://en.wikipedia.org/wiki/Binary_classification/)
