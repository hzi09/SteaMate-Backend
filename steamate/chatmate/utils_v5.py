from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
from .prompt import decompose_query, generate_pseudo_document
from .vectorstore import initialize_vectorstore
from .history import get_session_history
from config.settings import OPENAI_API_KEY
from langchain_core.runnables import RunnableWithMessageHistory
from .prompt import main_prompt
# 챗봇 모델 설정
chat = ChatOpenAI(model="gpt-4o-mini", api_key=OPENAI_API_KEY, temperature=0.7, streaming=True)

# 파서 설정
str_outputparser = StrOutputParser()

# 벡터 스토어 초기화
vector_store = initialize_vectorstore()

# 체인
chain = main_prompt | chat | str_outputparser

# 체인을 묶어 기억해줄 객체
chain_with_history = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
)

async def get_chatbot_message(user_input, session_id, genre, game, appid, preferred_games):
    # 1. Get chat history
    chat_history = get_session_history(session_id)
    # 2. Generate pseudo document
    pseudo_doc = generate_pseudo_document(user_input, chat, str_outputparser, genre, game, preferred_games, chat_history)
    # 3. Decompose the generated pseudo document into sub-queries
    sub_queries = decompose_query(pseudo_doc, chat, str_outputparser)
    # 4. Perform search for each sub-query
    all_contexts = []
    
    # 검색 파라미터 설정
    retriever = vector_store.as_retriever(search_kwargs={"k": 8, "filter": {"appid": {"$nin": appid}}})
    # retriever = vector_store.as_retriever(search_kwargs={"k": 8})
    
    # Search based on sub-queries
    for sub_query in sub_queries:
        sub_results = retriever.invoke(sub_query)
        all_contexts.extend(sub_results)
        
    all_contexts.extend(retriever.invoke(user_input))
    
    # 4. 검색 결과 통합 및 중복 제거 (page_content 한 번만 접근)
    context = "\n".join({doc.page_content for doc in all_contexts})
    
    # 5. 스트리밍 응답 생성 및 yield
    async for chunk in chain_with_history.astream(
        {
            "input": user_input,
            "context": context,
            "genre": ", ".join(genre),
            "game": ", ".join(game),
            "preferred_games": ", ".join(preferred_games)
        },
        config={"configurable": {"session_id": session_id}}
    ):
        yield chunk