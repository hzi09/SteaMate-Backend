# SteaMate 친구처럼 게임을 추천해주는 AI 웹 페이지

## 목차
- [1. 프로젝트 개요](#1-프로젝트-개요)
- [2. 서비스 설명](#2-서비스-설명)
- [3. 화면 별 기능](#3-화면-별-기능)

## 1. 프로젝트 개요
### 아이디어 및 배경
- Steam에는 222,333개의 게임이 있습니다. 하지만 그중에서 나에게 딱 맞는 게임을 찾는 건 쉽지 않죠. 수많은 게임을 스크롤하며 고민해본 적 있으신가요?
- 이런 고민을 해봤다면 SteaMate를 사용해보세요!

### SteaMate 소개
> **SteaMate**는 사용자의 선호 장르, 플레이 스타일, 과거 플레이 데이터를 분석하고, 게임 리뷰 및 메타 데이터를 활용하여 개인 맞춤형 게임 큐레이션을 제공합니다. 이를 통해 사용자가 더 쉽고 빠르게 새로운 게임을 발견할 수 있도록 돕습니다.
> 
> 
> 또한, 추천 이유와 함께 비슷한 유저들의 플레이 경향, 게임 리뷰, 메타 데이터를 제공하여 추천 이유를 확인할 수 있습니다.
> 
> 결과적으로, Steamate는 개인화된 추천을 통해 사용자가 새로운 게임을 더 많이 발견하고, 더욱 재미있게 즐길 수 있도록 도와줍니다. 🎮


| 개발 기간 | 팀명 |SA 문서 | Frontend 레포지토리 |
| :----------:| :-----: | :-------: | ------------------- |
| 2025년 02월 27일 ~ 2025년 03월 31일 | Patch 2.0 | [SA 문서 바로가기](https://www.notion.so/teamsparta/SA-V-3-0-0-1ad2dc3ef514808e9d6ed92aa3f33c77?pvs=4) | [SteaMate-Frontend](https://github.com/hzi09/SteaMate-Frontend) | 

### 팀원 구성


| 이름 | Github | 역할 |
|:----:|:----:|:----:|
| 이현지 | ![이미지] <br> [@hzi09](https://github.com/hzi09) |  |
| 이수관 | ![이미지] <br> [@Orange_00](https://github.com/sugwanlee) |  |
| 박종관 | ![이미지]  <br> [@jonggwanpark](https://github.com/jonggwan-park) | |
| 노호성 | ![이미지] <br> [@bubpen](https://github.com/bubpen)| |


### 기존 추천 시스템과의 차별점

- **단순 추천을 넘어선 분석**
    - 기존의 시스템 : 기존의 추천 시스템은 단순히 게임을 추천해줌
    - **SteaMate** : 각 게임에 대한 **소개**와 **왜 사용자가 이 게임을 좋아할지에 대한 분석**을 포함
- **데이터 활용**
    - 기존의 시스템 : 단순히 게임의 장르나 플레이 스타일에 맞는 게임을 추천
    - **SteaMate : 게임에 대한 장르, 태그, 댓글 등의 정보**를 제공하여 사용자가 해당 게임을 왜 추천받았는지 쉽게 이해할 수 있도록 도움
- **리뷰 기반의 신뢰도 강화**
    - **스팀의 게임 리뷰**와 같은 **사용자 피드백**을 활용하여, 추천의 신뢰도와 정확도를 높임
    - 이로 인해 사용자는 추천된 게임에 대한 **평가**를 바탕으로 더 나은 결정을 할 수 있음




## 2. 서비스 설명
### 서비스 아키텍처

![Image](https://github.com/user-attachments/assets/158852d2-ffb8-4c90-b635-d6645445047b)

<p align="center">
  <table width="100%" style="border-collapse: collapse;">
    <tr style="background-color:#f2f2f2;">
      <th style="text-align:center; padding: 10px;"><b>카테고리</b></th>
      <th style="text-align:center; padding: 10px;"><b>기술 및 설명</b></th>
    </tr>
    <tr>
      <td align="center" style="padding: 10px;"><b>Backend</b></td>
      <td align="left" style="padding: 10px;">
        - <b>Python</b> : Language <br>
        - <b>Django</b> : 웹 백엔드 개발 <br>
        - <b>Django REST Framework (DRF)</b> : RESTful API 개발 <br>
        - <b>Celery</b> : 비동기 작업 처리 및 분산 작업 큐 <br>
        - <b>Redis</b> : 캐싱 및 메시지 브로커 <br>
        - <b>Postman</b> : API 테스트 및 디버깅 <br>
        - <b>Django Channels</b> : 실시간 웹소켓 및 비동기 기능 구현
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



## 3. 화면 별 기능
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