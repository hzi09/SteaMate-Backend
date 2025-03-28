# SteaMate : 친구처럼 게임을 추천해주는 AI 웹 페이지

<img src="https://img.shields.io/badge/python-%233776AB.svg?&style=for-the-badge&logo=python&logoColor=white" />
<img src="https://img.shields.io/badge/django-%23092E20.svg?&style=for-the-badge&logo=django&logoColor=white" />
<img src="https://img.shields.io/badge/openai-%23412991.svg?&style=for-the-badge&logo=openai&logoColor=white" />
<img src="https://img.shields.io/badge/react-%2361DAFB.svg?&style=for-the-badge&logo=react&logoColor=black" />


![Image](https://github.com/user-attachments/assets/0e85527b-666c-4201-aff4-777f02b50aa0)

| 개발 기간 | 팀명 |SA 문서 | Frontend 레포지토리 |
| :----------:| :-----: | :-------: | ------------------- |
| 2025년 02월 27일 ~ 2025년 03월 31일 | Patch 2.0 | [SA 문서 바로가기](https://www.notion.so/teamsparta/SA-V-3-0-0-1ad2dc3ef514808e9d6ed92aa3f33c77?pvs=4) | [SteaMate-Frontend](https://github.com/hzi09/SteaMate-Frontend) | 

## 목차
- [1. 프로젝트 개요](#1-프로젝트-개요)
- [2. 서비스 설명](#2-서비스-설명)
- [3. 주요 기능](#3-주요-기능)

## 1. 프로젝트 개요
### 아이디어 및 배경
> Steam에는 222,333개의 게임이 있습니다. 하지만 그중에서 나에게 딱 맞는 게임을 찾는 건 쉽지 않죠. 수많은 게임을 스크롤하며 고민해본 적 있으신가요? 이런 고민을 해봤다면 SteaMate를 사용해보세요!

### SteaMate 소개
- **SteaMate**는 사용자의 선호 장르, 플레이 스타일, 과거 플레이 데이터를 분석하고, 게임 리뷰 및 메타 데이터를 활용하여 개인 맞춤형 게임 큐레이션을 제공합니다. 이를 통해 사용자가 더 쉽고 빠르게 새로운 게임을 발견할 수 있도록 돕습니다.
- 또한, 추천 이유와 함께 비슷한 유저들의 플레이 경향, 게임 리뷰, 메타 데이터를 제공하여 추천 이유를 확인할 수 있습니다.
- 결과적으로, Steamate는 개인화된 추천을 통해 사용자가 새로운 게임을 더 많이 발견하고, 더욱 재미있게 즐길 수 있도록 도와줍니다. 🎮

### 기존 추천 시스템과의 차별점
- **대화를 통한 추천**
    - 기존의 시스템 : 사용자가 검색을 통해 찾거나, 리스트 중에서 스스로 선택해야 하는 일방향 추천 방식
    - **Steamate** :“구스구스덕 같은 게임 없나요?”, “밤에 하기 좋은 감성적인 게임 추천해주세요” 같은 모호하거나 주관적인 질문에도 대화를 통해 이해하고 상황에 맞는 맞춤형 추천을 제공
- **데이터 활용** 
    - 기존의 시스템 : 단순히 게임의 장르나 플레이 스타일에 맞는 게임을 추천
    - **SteaMate** : 게임에 대한 장르, 태그, 댓글 등의 정보를 통해 추천하여 추천 성능을 높임
- **단순 추천을 넘어선 분석**
    - 기존의 시스템 : 기존의 추천 시스템은 단순히 게임을 추천해줌
    - **SteaMate** : 각 게임에 대한 소개와 왜 사용자가 이 게임을 좋아할지에 대한 분석을 포함

### 팀원 구성

<table width="100%" style="border-collapse: collapse; text-align: center;">
  <thead>
    <tr>
      <th style="padding: 10px; text-align: center;">항목</th>
      <th style="padding: 10px; text-align: center;">이현지</th>
      <th style="padding: 10px; text-align: center;">이수관</th>
      <th style="padding: 10px; text-align: center;">박종관</th>
      <th style="padding: 10px; text-align: center;">노호성</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th style="padding: 10px; text-align: center;">GitHub</th>
      <td>
        <img src="https://github.com/user-attachments/assets/9e4487ed-8030-4125-a52b-7d274ec7a417" height="150" width="150"><br>
        <a href="https://github.com/hzi09">@hzi09</a>
      </td>
      <td>
        <img src="https://github.com/user-attachments/assets/4e18241e-2924-447d-8745-7a05556c0fee" height="150" width="150"><br>
        <a href="https://github.com/sugwanlee">@Orange_00</a>
      </td>
      <td>
        <img src="https://github.com/user-attachments/assets/d7475b1d-8720-4813-a0bc-57f55e283bbc" height="150" width="150"><br>
        <a href="https://github.com/jonggwanpark">@jonggwanpark</a>
      </td>
      <td>
        <img src="https://github.com/user-attachments/assets/d5c4499e-4cdf-438f-81ca-f8ebdb3cf4ee" height="150" width="150"><br>
        <a href="https://github.com/bubpen">@bubpen</a>
      </td>
    </tr>
    <tr>
      <th style="padding: 10px; text-align: center;">이메일</th>
      <td>example1@email.com</td>
      <td>example2@email.com</td>
      <td>example3@email.com</td>
      <td>example4@email.com</td>
    </tr>
    <tr>
      <th style="padding: 10px; text-align: center;">역할</th>
      <td>ML, BE Follow, <br> FE Lead(AI기반)</td></td>
      <td>LLM, BE Follow, <br> FE Follow(AI기반)</td>
      <td>서버 구축 Lead, <br> CI/CD, 배포</td>
      <td>BE Lead, <br> 서버 구축 Follow</td>
    </tr>
  </tbody>
</table>


<br>


## 2. 서비스 설명
### 서비스 아키텍처

![Image](https://github.com/user-attachments/assets/158852d2-ffb8-4c90-b635-d6645445047b)

<details>
<summary>기술적 의사결정</summary>
<div markdown="1">

### 🔧 Backend - Django REST Framework (DRF)

- Django 기반 프로젝트인 만큼 DRF를 사용하는 것이 자연스럽고 효율적이라 판단
- 인증, 직렬화, 필터일 등 API 구현에 필요한 기능들을 내장하고 있어 개발 속도와 유지보수 측면에서 유리
- 팀 전체가 Django에 익숙하고, DRF에 대한 학습 부담이 적어 DRF로 결정

<details>
<summary>후보군</summary>

- **FastAPI**
    - 비동기 처리에 강점이 있으며 성능이 우수함.
    - 빠른 응답 속도, Swagger UI 등 자동 문서화 기능 제공
    - 하지만 Django와의 통합성은 떨어짐
- **Django REST Framework (DRF)**
    - Django와 완벽하게 통합됨
    - 인증, 권한, 직렬화 등 다양한 기능을 기본 제공
    - 프로젝트 구성원 대부분이 Django에 익숙함
    - 대규모 커뮤니티와 풍부한 자료 존재

</details>

---

### 🎨 Frontend - React
- Docker-Compose를 사용하여 개발 환경을 구성하는 과정에서 React와 백엔드 서버 간의 연결을 효율적으로 설정 가능
- React는 다양한 오픈 소스 라이브러리와 플러그인을 제공하기 때문에 빠르게 UI를 개발 가능하며 유지 보수가 유리하기 때문에 선정

<details>
<summary>후보군</summary>

- **vanilla JS/HTML/CSS**
    - 별도의 라이브러리나 프레임워크 없이 순수하게 웹의 기본적인 동작 원리를 이해할 수 있음
    - 가벼운 웹 페이지 및 간단한 애플리케이션 개발에 적합
    - 코드 중복, 유지보수 어려움이 발생

- **React**
    - 빠르고 효율적인 렌더링 및 코드 재사용성을 높이고, 컴포넌트 기반 개발이 가능
    - 다양한 라이브러리 및 툴 생태계가 풍부

</details>

---

### 🛢️ Database - PostgreSQL
- PostgreSQL이 ORDBMS로 Django를 사용하는 우리 프로젝트에 적합할 것이라 판단
- 읽기 기능은 물론 쓰기 기능도 사용하는 것에 있어 PostgreSQL로 결정

<details>
<summary>후보군</summary>

- **MySQL**
  - 데이터 읽기에 적절하며, Django ORM에 적용 제한이 있음

- **PostgreSQL**
  - 다방면으로 Python과 호환이 좋으며, Django와 융합이 좋음.
  - ORDBMS : 객체 지향 개념을 지원하는 데이터베이스라 Django와 호환성이 아주 좋음

</details>

---

### 📐 Vector DB - pgVector
- PostgreSQL의 확장 모듈로 벡터 테이블을 저장하여 사용이 가능
- 무료이며 Django와도 호환성이 좋아 채택

<details>
<summary>후보군</summary>

- **Pinecone**
  - 클라우드 기반 vectorDB, 대용량에 적합
  - 무료 제한, 유료 기능 존재

- **FAISS**
  - GPU 가속 및 Python 지원
  - 성능 우수하나, 데이터 영속성 직접 관리 필요

- **pgVector**
  - PostgreSQL과 완벽 통합, 별도 Vector DB 불필요

</details>

---

### 🧠 LLM - gpt-4o-mini
- PostgreSQL의 확장 모듈로 벡터 테이블을 저장하여 사용이 가능
- 무료이며 Django와도 호환성이 좋아 채택

<details>
<summary>후보군</summary>

- **gpt-4o**
  - 고성능 LLM, 높은 비용

- **gpt-4o-mini**
  - 가볍고 빠르며 저렴한 SLM

- **deepseek-chat**
  - 오픈소스, 매우 저렴하나 느림

</details>

---

### 🔎 RAG - Query2doc / RQ-RAG
- Query2doc: 질의를 가상문서(키워드)로 확장하는 전처리
- RQ-RAG: 키워드를 다시 쿼리로 바꿔 검색 정밀도 향상
- [참고 논문](https://arxiv.org/html/2402.19473v6): III-B1 인용

<details>
<summary>후보군</summary>

- **gpt-4o**
  - 고성능 LLM, 높은 비용

- **gpt-4o-mini**
  - 가볍고 빠르며 저렴한 SLM

- **deepseek-chat**
  - 오픈소스, 매우 저렴하나 느림

</details>



---

### 🤖 ML 기반 추천
- **Surprise 라이브러리**
  - 다양한 추천 알고리즘 지원
  - RMSE, MAE 등 지표 제공
- 콘텐츠 기반 + 협업 필터링의 하이브리드 모델 구성


<details>
<summary>후보군</summary>

- **콘텐츠 기반 필터링**  
- **사용자 기반 협업 필터링**  
- **아이템 기반 협업 필터링**  
- **하이브리드 모델**

</details>

---

### 🐳 Docker
- 협업, 배포 시 동일한 환경 보장
- 격리성, 확장성 뛰어나 채택


<details>
<summary>후보군</summary>

- **Docker**
  - 환경 일치, 유지보수 편리
- **전통 방식**
  - 디버깅 편리, 리소스 절약

</details>

---

### ☁️ Deploy - AWS / Vercel
- AWS
  - EC2: Docker, Django 등 서버 설정 유연
  - RDS: DB 분리로 유지보수 용이
  - Route53: 간편한 도메인 관리

- Vercel
  - GitHub 연동 자동 배포
  - 프론트만 빠르게 서버리스 배포


<details>
<summary>후보군</summary>

- **EC2 통합**
  - 단순, 성능 최적화 용이
- **EC2/Vercel 분리**
  - 확장성, 독립적 배포

</details>

---

### ⚙️ CI/CD - GitHub Action
- 직관적인 코드와 높은 자유도
- GitHub 저장소와 통합되어 초보자도 쉽게 사용 가능

<details>
<summary>후보군</summary>

- **AWS CodePipeline**
  - 강력한 AWS 연동, 설정 복잡
- **GitHub Action**
  - 무료, 쉬운 설정

</details>

---

### 🔁 동기 / 비동기 처리
- 인증 이메일, 챗봇 응답 생성 → Celery로 처리  
- Django Channels + WebSocket → 답변 스트리밍 처리

<details>
<summary>후보군</summary>

- 동기 처리만 사용 (간단, 회원 적을 경우)
- 비동기 혼합 (사용자 경험 향상, 안정성)

</details>

---

### 📎 협업 도구
- 인증 이메일, 챗봇 응답 생성 → Celery로 처리  
- Django Channels + WebSocket → 답변 스트리밍 처리

<details>
<summary>후보군</summary>

- Documentation & Recording
  - Notion  
  - Figma

- Version Control
  - Git

- Communication
  - Slack

</details>

</div>
</details>


<br>

<p align="center">
  <table width="100%" style="border-collapse: collapse;">
    <tr style="background-color:#f2f2f2;">
      <th style="text-align:center; padding: 10px;"><b>카테고리</b></th>
      <th style="text-align:center; padding: 10px;"><b>기술 및 설명</b></th>
    </tr>
    <tr>
      <td align="center" style="padding: 10px;"><b>Backend</b></td>
      <td align="left" style="padding: 10px;">
        - <b>Python3.12-slim</b> : Language <br>
        - <b>Django</b> : 웹 백엔드 개발 <br>
        - <b>Django REST Framework (DRF)</b> : RESTful API 개발 <br>
        - <b>Celery</b> : 비동기 작업 처리 및 분산 작업 큐 <br>
        - <b>Redis</b> : 캐싱 및 메시지 브로커 <br>
        - <b>Postman</b> : API 테스트 및 디버깅 <br>
        - <b>Django Channels</b> : 채팅 등의 실시간 웹소켓 및 비동기 기능 구현
      </td>
    </tr>
    <tr>
      <td align="center" style="padding: 10px;"><b>Frontend</b></td>
      <td align="left" style="padding: 10px;">
        - <b>React</b> : 프론트엔드 개발 및 UI 구성
      </td>
    </tr>
    <tr>
      <td align="center" style="padding: 10px;"><b>DataBase</b></td>
      <td align="left" style="padding: 10px;">
        - <b>PostgreSQL</b> : 관계형 데이터베이스 관리 시스템 (RDBMS) <br>
        - <b>pgvector</b> : PostgreSQL용 벡터 검색 확장, 유사도 검색 및 벡터 데이터 저장/조회
      </td>
    </tr>
    <tr>
      <td align="center" style="padding: 10px;"><b>LLM / ML</b></td>
      <td align="left" style="padding: 10px;">
        - <b>OpenAI</b> : 대형 언어 모델(LLM) API 제공, 자연어 처리 및 생성 <br>
        - <b>LangChain</b> : LLM 애플리케이션 구축을 위한 프레임워크, 프롬프트 관리 및 데이터 연결 기능 <br>
        - <b>Surprise</b> : 추천 시스템 개발을 위한 Python 라이브러리로, 협업 필터링(Collaborative Filtering) 기반 알고리즘 구현
      </td>
    </tr>
    <tr>
      <td align="center" style="padding: 10px;"><b>Deploy</b></td>
      <td align="left" style="padding: 10px;">
        - <b>Docker</b> : 컨테이너화된 애플리케이션 관리 <br>
        - <b>Docker Compose</b> : 다중 컨테이너 애플리케이션 구성 <br>
        - <b>Amazon EC2</b> : 클라우드 컴퓨팅을 위한 가상 서버 <br>
        - <b>Vercel</b> : 프론트엔드 및 정적 사이트 배포 플랫폼 <br>
        - <b>Route 53</b> : AWS의 DNS 웹 서비스 <br>
        - <b>Nginx</b> : 리버스 프록시 및 웹 서버 <br>
        - <b>Gunicorn</b> : WSGI 서버, Django 등의 Python 웹 애플리케이션 실행 <br>
        - <b>Uvicorn</b> : ASGI 서버, FastAPI 및 Django Channels 실행 <br>
        - <b>GitHub Actions</b> : CI/CD 자동화 및 워크플로우 관리
      </td>
    </tr>
    <tr>
      <td align="center" style="padding: 10px;"><b>Collaboration Tool</b></td>
      <td align="left" style="padding: 10px;">
        - <b>Slack</b>: 팀 커뮤니케이션 및 실시간 협업 <br>
        - <b>GitHub</b> : 코드 버전 관리 및 협업 <br>
        - <b>Notion</b> : 프로젝트 관리 및 문서 협업 <br>
        - <b>Figma</b> : UI/UX 디자인 및 프로토타이핑
      </td>
    </tr>
  </table>
</p>


## 3. 주요 기능
### HOME

![홈](https://github.com/user-attachments/assets/de56b120-3497-4441-af6e-6f1ea3b54a63)

- 헤더 혹은 화면 가운데의 chatmate나 pickmate로 이동할 수 있는 카드 구현
- 로그인이 되어 있지 않은 경우 : 우측 상단에 로그인과 회원가입 버튼
- 로그인이 되어 있는 경우 : 우측상단에 마이페이지와 로그아웃 버튼

### Signup - 일반회원

![회원가입](https://github.com/user-attachments/assets/01849fe7-33be-43b2-8862-a71a5500535f)

- 아이디와 비밀번호,별명,이메일을 입력하면 입력창에서 바로 유효성 검사 진행, 통과하지 못할 시 각 경고 문구 생성
- 기입한 이메일 주소로 인증 메일이 발송되며 인증을 마치면 로그인 가능

### 로그인

![로그인](https://github.com/user-attachments/assets/4de85fc6-6b3b-4582-b60b-1b895d71e58f)

- 아이디와 비밀번호를 입력하면 로그인
- 유효성 검사 통과하지 못할시 경고 문구 생성
- 이메일 인증 안되었을 시 경고 문구 생성

### 스팀 회원가입

![스팀회원가입](https://github.com/user-attachments/assets/54ba6f3b-1dea-4320-bea9-08082193699c)

- 스팀로그인 버튼을 누르면 스팀페이지로 연결.
- 기존 회원이 아니면 스팀 연동 회원가입으로 연결됨.
- 회원가입 완료시 자동 로그인 되며, 마이페이지로 이동


### 스팀 로그인

![스팀로그인](https://github.com/user-attachments/assets/0a42de33-402e-48a2-adfb-ef23bd46df49)

- 스팀계정으로 회원가입을 하거나, 계정 연동이 되어있는 경우 스팀 로그인 가능
- 스팀으로 로그인 버튼을 클릭하면 스팀 페이지로 연결되며, 스팀 페이지에서 허용하여 SteaMate 소셜 로그인

### 스팀 동기화 및 선호게임 저장

![동기화](https://github.com/user-attachments/assets/3b63d339-a490-46e3-857e-154336c6cb70)

- 스팀아이디에서 가지고 있는 게임 동기화
- 선호게임 저장하여 pickmate 및 chatmate 추천

### ChatMate

![챗메이트](https://github.com/user-attachments/assets/10f1e147-852b-4f50-bbf7-4a32cd09e344)

- 사용자의 선호게임을 기반으로 사용자의 질문에 따라 게임 추천.
- 게임과 무관한 질문에 대한 답변 제한
- 세션 별로 기존 대화 내용을 기억
- 세션을 생성하거나 삭제 가능
- 추천된 게임을 클릭하면 스팀 해당 게임 페이지로 이동

### PickMate

![픽메이트](https://github.com/user-attachments/assets/af126a71-b75a-4d52-9184-dd4eaf08870c)

- 사용자의 선호게임을 기반으로 학습하여 게임 추천
- 선호게임 없을 시 랜덤 추천
- 추천된 게임을 클릭하면 스팀 해당 게임 페이지로 이동



## 5. 기여 가이드 라인
- [GitHub Rules](https://github.com/hzi09/SteaMate-Backend/wiki/GitHub-Rules)
- [Code Convention](https://github.com/hzi09/SteaMate-Backend/wiki/Code-Convention)
- [Project Convention](https://github.com/hzi09/SteaMate-Backend/wiki/Project-Convention)