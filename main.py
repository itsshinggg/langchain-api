from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import TextLoader
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel

class Settings(BaseSettings):
    openai_api_key: str
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Prompt(BaseModel):
    message: str

@app.get("/")
async def root():
    return {"message": "Hello World"}

llm = ChatOpenAI(api_key=settings.openai_api_key)
loader = TextLoader("./intern.txt")
docs = loader.load()

embeddings = OpenAIEmbeddings(api_key=settings.openai_api_key)

text_splitter = RecursiveCharacterTextSplitter()
documents = text_splitter.split_documents(docs)
vector = FAISS.from_documents(documents, embeddings)

prompt = ChatPromptTemplate.from_template("""You are a helpful assistant to students who could use internship information from previous students to apply for an internship. Answer the following question based only on the provided context:

<context>
{context}
</context>

Question: {input}""")

document_chain = create_stuff_documents_chain(llm, prompt)

retriever = vector.as_retriever()
retrieval_chain = create_retrieval_chain(retriever, document_chain)

@app.post("/intern")
def main(user_prompt:Prompt):
    response = retrieval_chain.invoke({"input": f"{user_prompt}"})
    return {"response": response["answer"]}