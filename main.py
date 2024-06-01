from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.document_loaders import TextLoader
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_text_splitters import CharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain

# FastAPI app initialization
app = FastAPI()

# CORS Middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define Pydantic models
class Prompt(BaseModel):
    message: str

class Settings(BaseSettings):
    openai_api_key: str
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
llm = ChatOpenAI(api_key=settings.openai_api_key)

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Hello World!"}

# GPT endpoint
@app.post("/gpt")
def gpt(user_prompt:Prompt):
    gpt_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a world class chatbot."),
        ("user", "{input}")
    ])

    output_parser = StrOutputParser()
    chain = gpt_prompt | llm | output_parser
    llm_response = chain.invoke({"input": f"{user_prompt}"})
    return {"response": llm_response}

# Intermship endpoint
@app.post("/intern")
def rag(user_prompt:Prompt):
    loader = TextLoader("./intern.txt")
    docs = loader.load()

    embeddings = OpenAIEmbeddings(api_key=settings.openai_api_key)

    text_splitter = RecursiveCharacterTextSplitter(
        separator='\n',
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    documents = text_splitter.split_documents(docs)

    # text_splitter = CharacterTextSplitter(
    #     separator='\n',
    #     chunk_size=1000,
    #     chunk_overlap=200,
    #     length_function=len
    # )
    # documents = text_splitter.split_text(docs)

    vector = FAISS.from_documents(documents, embeddings)

    prompt = ChatPromptTemplate.from_template("""You are a helpful assistant to students seeking internship opportunities, relying solely on the provided context regarding internships at City University of Seattle. Please do not provide too much information at once. Summarize the context in 1 to 2 sentences and provide more details if they ask for them. If students ask about internship eligibility, please provide brief information solely on the internship eligibility section. If students ask for information about past internships, initially provide several brief descriptions of internships, ordered from the most relevant to the least.:

    <context>
    {context}
    </context>

    Question: {input}""")

    document_chain = create_stuff_documents_chain(llm, prompt)

    retriever = vector.as_retriever()
    retrieval_chain = create_retrieval_chain(retriever, document_chain)
    response = retrieval_chain.invoke({"input": f"{user_prompt}"})
    return {"response": response["answer"]}