from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser

main_prompt = ChatPromptTemplate.from_messages([
    MessagesPlaceholder(variable_name="chat_history"),
    (
        "system",
        """당신은 스팀 게임 평론가입니다. 반드시 다음 규칙을 따르세요:

        1. 가장 중요한 규칙:
        - 사용자와 게임 관련 대화를 하며 상호작용을 유지하세요
        - 게임과 무관한 대화는 하지 않습니다.
        
        2. 사용자 정보:
        - 선호하는 장르: {genre}
        - 선호하는 게임: {preferred_games}
        - 이전에 플레이 했던 게임: {game}
        - 플레이 타임이 길 수록 중요도가 높음
        
        3. 게임 목록:
        {context}
        
        4. 추천 방식:
        - 위 게임 목록에서 3개의 게임만 선택하여 추천
        - 각 게임에 대해 다음을 고려하여 추천 이유를 작성:
          * 사용자의 선호 장르, 선호 게임과의 연관성
          * 이전에 플레이한 게임과의 유사점
          * 게임의 핵심 특징
          * 사용자 정보에 있는 게임들은 추천하지 않음
        
        5. 답변 형식:
        [게임 제목 1] :: appid
        - 추천 이유 및 설명
        
        [게임 제목 2] :: appid
        - 추천 이유 및 설명
        
        [게임 제목 3] :: appid
        - 추천 이유 및 설명
        
        주의: 각 appid는 게임 제목 1, 2, 3에 맞는 appid여야 합니다.
        주의: 게임과 무관한 대화는 하지 않습니다.
        주의: 사용자 정보에 있는 게임들은 추천하지 않습니다.
        """,
    ),
    ("human", "{input}"),
])


def generate_pseudo_document(user_input, chat, str_outputparser, genre, game, preferred_games, chat_history):
    """Query2doc/HyDE approach to generate a pseudo document."""
    pseudo_doc_prompt = ChatPromptTemplate.from_messages([
        ("system", """
        당신은 게임 특성 분석 전문가입니다. 사용자의 취향과 요구사항을 분석하여 게임 특성 목록을 생성해야 합니다.
        
        사용자는 직접적으로 게임 추천을 요청할 수 있지만, 당신의 임무는 게임 제목을 추천하는 것이 아니라 
        사용자가 원하는 게임의 특성을 키워드 목록으로 분석하는 것입니다.
        
        이전 대화 내역:
        {chat_history}
        
        1. 사용자 입력 해석 방법:
        - "게임 추천해줘", "~한 게임 찾아줘" 등의 직접적인 추천 요청 → 사용자의 취향과 정보를 기반으로 원하는 게임 특성 추출
        - 특정 게임과 유사한 게임 요청 → 언급된 게임의 주요 특성 추출 (실제 게임 이름 제외)
        - 특정 장르나 기능 요청 → 해당 장르/기능의 핵심 특성 추출
        
        2. 사용자 선호도 (참고용):
        - 선호 장르: {genre}
        - 선호 게임: {preferred_games}
        - 플레이 했던 게임: {game}
        - 플레이 타임이 길 수록 중요도가 높음
        - 사용자 정보에 있는 게임들은 추천하지 않음!
        
        3. 다음 측면을 고려하여 키워드를 추출하세요:
        - 게임의 핵심적인 특징
        - 게임의 그래픽 스타일
        - 게임의 플레이 방식
        - 사용자 선호도

        출력 형식:
        - 쉼표로 구분된 15개 이내의 간결한 키워드 목록을 영어로만 작성
        
        주의사항:
        - 직접적인 게임 추천이나 설명을 제공하지 마세요
        - 키워드만 나열하고 문장이나 설명은 포함하지 마세요
        """),
        ("human", "{input}")
    ])
    pseudo_doc_chain = pseudo_doc_prompt | chat | str_outputparser
    return pseudo_doc_chain.invoke({"input": user_input, "genre": genre, "game": game, "preferred_games": preferred_games, "chat_history": chat_history})


def decompose_query(pseudo_doc, chat, str_outputparser):
    """Decompose the pseudo document into sub-queries."""
    decompose_prompt = ChatPromptTemplate.from_messages([
        ("system", """
        주어진 게임 특성 키워드 목록을 분석하여 효과적인 검색 질의어를 생성하세요.

        키워드 목록: {input}    

        고려할 수 있는 측면들:
        - 게임의 핵심적인 특징
        - 게임의 그래픽 스타일
        - 게임의 플레이 방식
        
        가이드라인:
        - 2개의 의미 있는 검색 질의어를 생성하세요
        - 키워드들을 자연스럽게 조합하여 사용하세요
        - 각 줄에 하나의 검색 질의어만 작성하세요
        """)
    ])
    
    decompose_chain = decompose_prompt | chat | str_outputparser
    return [q.strip() for q in decompose_chain.invoke({"input": pseudo_doc}).split('\n') if q.strip()]