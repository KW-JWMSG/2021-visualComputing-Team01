# 2021-visualComputing-Team01
2021년도 비주얼컴퓨팅 팀플 01

## 사용법
  ```
  python .\run.py <이미지재조정X>:<이미지재조정Y> <거리보정수치> <이미지1번path> <이미지2번 path> .... <이미지N번 path>
  ```
  
  ```
  (예시1)
  python .\run.py 500:500 0.7 .\imgSets\1.jpeg .\imgSets\2.jpeg .\imgSets\3.jpeg .\imgSets\4.jpeg .\imgSets\5.jpeg
  ```
   ```
  (예시2)
  python .\run.py 800:800 0.7 .\imgTest\1.jpg .\imgTest\2.jpg .\imgTest\3.jpg .\imgTest\4.jpg .\imgTest\5.jpg .\imgTest\6.jpg .\imgTest\7.jpg .\imgTest\8.jpg .\imgTest\9.jpg
  ```
## 충고
* 사진 9장까지는 10초 이내에 다 된다.
* 해상도와 거리보정 수치를 적절히 잘 이용해야 한다.
* 소실점이 있는 3D 입체환경에서는 좀 답이 없을 수 있다. (그러니 되도록 2D에 가까운 환경을 권장한다)
* 진짜루, 해상도와 거리보정 수치를 잘 적당히 조정해야 한다.
* 속도 성능을 잡기위해 메모리 성능을 일부 포기하게 되어, 16기가 램 이하에서는 9장 사진이 무리일 수 있습니다. 만약 9장사진을 돌리고자 하는경우 700 해상도에서 진행해 주시기 바랍니다.
