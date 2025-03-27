# SteaMate
게임을 추천해주는 AI 웹페이지


### 페이지별 기능

#### [초기화면]
- 서비스 접속 초기화면입니다.
    - 상단이나 화면 가운데 chatmate나 pickmate로 이동할 수 있는 버튼 구현.
    - 로그인이 되어 있지 않은 경우 : 우측 상단에 로그인과 회원가입 버튼 생성.
    - 로그인이 되어 있는 경우 : 우측상단에 마이페이지와 로그아웃 버튼 생성. 

![홈](https://github.com/user-attachments/assets/de56b120-3497-4441-af6e-6f1ea3b54a63)

#### [회원가입]
- 아이디와 비밀번호,별명,이메일을 입력하면 입력창에서 바로 유효성 검사 진행, 통과하지 못할 시 각 경고 문구 생성.

- 기입한 이메일 주소로 인증 메일이 발송되며 인증을 마치면 로그인 가능.


![회원가입](https://github.com/user-attachments/assets/01849fe7-33be-43b2-8862-a71a5500535f)

#### 로그인
- 아이디와 비밀번호를 입력하면 로그인
- 유효성 검사 통과하지 못할시 경고 문구 생성
- 이메일 인증 안되었을 시 경고 문구 생성

![로그인](https://github.com/user-attachments/assets/4de85fc6-6b3b-4582-b60b-1b895d71e58f)

#### 스팀 회원가입
- 스팀로그인 버튼을 누르면 스팀페이지로 연결.
- 기존 회원이 아니면 스팀 연동 회원가입으로 연결됨.
- 회원가입 완료시 자동 로그인 되며, 마이페이지로 이동

![스팀회원가입](https://github.com/user-attachments/assets/54ba6f3b-1dea-4320-bea9-08082193699c)

#### 스팀 로그인
- 스팀계정으로 회원가입을 하거나, 계정 연동이 되어있는 경우 스팀 로그인 가능
- 스팀으로 로그인 버튼을 클릭하면 스팀 페이지로 연결되며, 스팀 페이지에서 로그인 하면 steamate에서도 로그인 됨.

![스팀로그인](https://github.com/user-attachments/assets/0a42de33-402e-48a2-adfb-ef23bd46df49)

#### 스팀 동기화 및 선호게임 저장
- 스팀아이디에서 가지고 있는 게임 동기화
- 선호게임 저장하여 pickmate 및 chatmate 추천

![동기화](https://github.com/user-attachments/assets/3b63d339-a490-46e3-857e-154336c6cb70)

#### ChatMate
- 사용자의 선호게임을 기반으로 사용자의 질문에 따라 게임 추천.
- 게임과 무관한 질문에 대한 답변 제한
- 세션 별로 기존 대화 내용을 기억
- 세션을 생성하거나 삭제 가능
- 추천된 게임을 클릭하면 스팀 해당 게임 페이지로 이동

![챗메이트](https://github.com/user-attachments/assets/10f1e147-852b-4f50-bbf7-4a32cd09e344)

#### PickMate
- 사용자의 선호게임을 기반으로 학습하여 게임 추천
- 선호게임 없을 시 랜덤 추천
- 추천된 게임을 클릭하면 스팀 해당 게임 페이지로 이동

![픽메이트](https://github.com/user-attachments/assets/af126a71-b75a-4d52-9184-dd4eaf08870c)

