from langchain_community.chat_message_histories import ChatMessageHistory
from langchain.schema import HumanMessage, AIMessage
from cachetools import TTLCache
from .models import ChatMessage

# store를 TTLCache로 변경 (maxsize=1000개, ttl=1800초(30분))
store = TTLCache(maxsize=1000, ttl=1800)

# RDB에 있는 대화 내역을 메모리에 저장하는 함수
def bring_session_history(session_id):
    try:
        # 세션이 없거나 만료되었으면 새로 생성
        if session_id not in store:
            history = ChatMessageHistory()
            for message in ChatMessage.objects.filter(session_id=session_id).order_by('created_at')[:5]:
                history.add_message(HumanMessage(content=message.user_message))
                history.add_message(AIMessage(content=message.chatbot_message))
            store[session_id] = history
        return store[session_id]
    except Exception as e:
        print(f"Session {session_id} expired or error occurred: {e}")
        return None

def delete_messages_from_history(session_id, user_message):
    """
    채팅 히스토리에서 특정 메시지와 그에 대한 AI 응답을 삭제합니다.
    """
    try:
        session_history = store.get(session_id)
        if not session_history:
            print(f"세션 {session_id}의 히스토리를 찾을 수 없습니다.")
            return False
            
        # HumanMessage의 content로 인덱스 찾기
        for i, msg in enumerate(session_history.messages):
            if (isinstance(msg, HumanMessage) and 
                msg.content == user_message):
                # 해당 메시지와 다음 AI 메시지 삭제
                del session_history.messages[i:i+2]
                return True
                
        return False
        
    except Exception as e:
        print(f"메시지 삭제 중 오류 발생: {e}")
        return False
    
# 세션 내역 가져오기
def get_session_history(session_id):
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

def delete_session_history(session_id):
    if session_id in store:
        del store[session_id]

