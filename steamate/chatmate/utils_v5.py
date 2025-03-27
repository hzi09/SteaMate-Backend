from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from .prompt import decompose_query, generate_pseudo_document
from .vectorstore import initialize_vectorstore
from .history import get_session_history
from config.settings import OPENAI_API_KEY, TAVILY_API_KEY
from langchain_core.runnables import RunnableWithMessageHistory
from langchain.agents import AgentExecutor, create_tool_calling_agent
from .prompt import main_prompt, choice_prompt, game_info_agent_prompt, agent_prompt
from langchain_community.tools import TavilySearchResults
import logging
import sys

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)  # stdout으로 로그 출력
    ]
)

logger = logging.getLogger(__name__)

# 챗봇 모델 설정
chat = ChatOpenAI(model="gpt-4o-mini", api_key=OPENAI_API_KEY, temperature=0, streaming=True)
choice_chat = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=OPENAI_API_KEY,
    temperature=0,
    tools=[{
        "type": "function",
        "function": {
            "name": "search_game_info",
            "description": "게임 정보 검색이 필요할 때 호출되는 함수입니다",
            "parameters": {
                "type": "object",
                "properties": {
                    "needs_search": {
                        "type": "boolean",
                        "description": "게임 정보 검색이 필요한지 여부"
                    }
                },
                "required": ["needs_search"]
            }
        }
    }]
)
# 파서 설정
str_outputparser = StrOutputParser()

# 벡터 스토어 초기화
vector_store = initialize_vectorstore()

# 게임 정보 검색 도구 생성
search = TavilySearchResults(
    name="game_info_search",
    description="특정 게임에 관한 정보를 검색합니다. 게임의 스펙,게임 간 비교, 리뷰, 플레이 방법, 캐릭터, 스토리 등 게임 자체에 대한 질문에만 사용하세요.",
    max_results=2,
    topic="game",
    tavily_api_key=TAVILY_API_KEY
)

tools = [search]

agent = create_tool_calling_agent(
    llm=chat,
    tools=tools,
    prompt=game_info_agent_prompt
)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    return_intermediate_steps=True,
    verbose=True
)

main_chain = main_prompt | chat | str_outputparser

choice_chain = choice_prompt | choice_chat

agent_chain = agent_prompt | chat | str_outputparser
# 체인을 묶어 기억해줄 객체
chain_with_history = RunnableWithMessageHistory(
    main_chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
)

agent_with_history = RunnableWithMessageHistory(
    agent_chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
)


async def get_chatbot_message(user_input, session_id, genre, game, appid, preferred_games):
    # 1. Get chat history
    chat_history = get_session_history(session_id)
    
    choice_response = choice_chain.invoke({"input": user_input})
    
    if choice_response.additional_kwargs.get('tool_calls'):
        
        retriever = vector_store.as_retriever(search_kwargs={"k": 3})
        
        context = retriever.invoke(user_input) 
        
        agent_response = agent_executor.invoke({"input": user_input})
        
        
        async for chunk in agent_with_history.astream(
            {
                "input": user_input,
                "context": context,
                "agent_response": agent_response,
            },
            config={"configurable": {"session_id": session_id}}
        ):
            yield chunk
    else:
        # 5. 스트리밍 응답 생성 및 yield# 2. Generate pseudo document
        pseudo_doc = generate_pseudo_document(user_input, chat, str_outputparser, genre, game, preferred_games, chat_history)
        # 3. Decompose the generated pseudo document into sub-queries
        sub_queries = decompose_query(pseudo_doc, chat, str_outputparser)
        # 4. Perform search for each sub-query
        all_contexts = []

        # 검색 파라미터 설정
        retriever = vector_store.as_retriever(search_kwargs={"k": 8, "filter": {"appid": {"$nin": appid}}})
        

        # Search based on sub-queries
        for sub_query in sub_queries:
            sub_results = retriever.invoke(sub_query)
            all_contexts.extend(sub_results)
            
        all_contexts.extend(retriever.invoke(user_input))

        # 4. 검색 결과 통합 및 중복 제거 (page_content 한 번만 접근)
        context = "\n".join({doc.page_content for doc in all_contexts})
    
    
        async for chunk in chain_with_history.astream(
            {
                "input": user_input,
                "context": context,
                "genre": ", ".join(genre),
                "game": ", ".join(game),
                "preferred_games": ", ".join(preferred_games),
            },
            config={"configurable": {"session_id": session_id}}
        ):
            yield chunk