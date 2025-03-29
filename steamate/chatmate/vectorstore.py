from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document
from langchain_community.vectorstores import PGVector # pgvector용 모듈
from config.settings import CONNECTION_STRING
import os
import pandas as pd


# 임베딩 모델 설정
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
)

# 데이터 불러오기
def load_and_chunk_csv(chunk_size=100):
    try:
        file_path = os.path.abspath('chatmate/data/games_v3.csv')
        data = pd.read_csv(file_path, encoding="utf-8")
    except Exception as e:
        print(f"데이터 불러오기 중 오류 :: {e}")
        return None
    
    chunks = []
    for i in range(0, len(data), chunk_size):
        chunk = data.iloc[i:i+chunk_size]
        chunk_documents = [
            Document(
                page_content=" | ".join([f"{col}: {value}" for col, value in row.items()]),
                metadata={"appid": row["appid"], "genres": row["genres"]}
            )
            for _, row in chunk.iterrows()
        ]
        chunks.append(chunk_documents)
    
    return chunks

# 벡터 스토어 생성
def create_vectorstore_from_chunks(chunks):
    vector_store = None
    for chunk in chunks:
        if vector_store is None:
            vector_store = PGVector.from_documents(
                documents=chunk,
                embedding=embeddings,
                connection_string=CONNECTION_STRING,
                collection_name="games_collection",
                use_jsonb=True
            )
        else:
            vector_store.add_documents(chunk)
    
    return vector_store


# 벡터 스토어 초기화
def initialize_vectorstore():
    
    try: 
        # 벡터 스토어 로드 시도
        vector_store = PGVector(
            embedding_function=embeddings,
            connection_string=CONNECTION_STRING,
            collection_name="games_collection",
            use_jsonb=True
        )
        
            # 데이터 비어있는지 확인
        sample = vector_store.similarity_search("test", k=1)
        if not sample:
            print("PGVector 벡터 DB가 비어 있습니다. 데이터를 생성합니다.")
            chunks = load_and_chunk_csv()
            vector_store = create_vectorstore_from_chunks(chunks)
        else:
            print("기존 PGVector 벡터 DB를 로드했습니다.")
    # 우선 모든에러처리
    except Exception as e: 
        print(f"벡터 db 초기화 중 오류 :: {e}")
    
    
    return vector_store