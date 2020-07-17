# fan.catholic.ac.kr-backend
 ## 참고사항
 ### github 사용전략
  - issue를 통해 업무 할당
  - issue를 통해 branch 생성
  - 업무처리 후 pull request 
  - pull request 된 코드 팀원간 코드리뷰
  - 코드리뷰 후 문제 없으면 팀장 or 오선식이 merge

  ### Commit 주의사항
  - commit message는 간결하고 의미있게 작성
  - .gitignore에 있는 파일 억지로 add 금지

  ### 프로젝트 주의사항
  - 현 Repository pull 하여 virtual environment 구성하여 사용하기(venv) 
  - flaks-request-validator 코드를 수정해야함
    - venv/Lib/site-packages/flask_request_validator/validator.py 파일
    - 95번줄 raise InvalidRequest(errors)위에 return errors 삽입
  - 특정 모듈에 의존하는 코드 작성 시 requirements.txt 파일 업데이트 필수
