# FastAPI
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel

# LangChain
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.document_loaders import TextLoader
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain

# RAGAs
from langchain.text_splitter import CharacterTextSplitter
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema import Document
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import(
    faithfulness,
    answer_relevancy,
    context_recall,
    context_precision
)

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

# Root Endpoint
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

# Intermship Endpoint
@app.post("/intern")
def rag(user_prompt:Prompt):
    loader = TextLoader("./intern.txt")
    docs = loader.load()

    embeddings = OpenAIEmbeddings(api_key=settings.openai_api_key)

    text_splitter = RecursiveCharacterTextSplitter()
    documents = text_splitter.split_documents(docs)
    vector = FAISS.from_documents(documents, embeddings)

    prompt = ChatPromptTemplate.from_template("""You are a helpful assistant to students seeking internship opportunities, relying solely on the provided context regarding internships at City University of Seattle. Please do not provide too much information at once. Summarize the context in 1 to 2 sentences and provide more details if they ask for them. If students ask about internship eligibility, please provide brief information solely on the internship eligibility section. If students ask for information about past internships, initially provide several brief descriptions of internships, ordered from the most relevant to the least. If a question does not make any sense, or is not factually coherent, or need more information, please kindly explain why instead of answering something not correct. If you do not know the answer to a question, please do not share false information.:

    <context>
    {context}
    </context>

    Question: {input}""")

    document_chain = create_stuff_documents_chain(llm, prompt)

    retriever = vector.as_retriever()
    retrieval_chain = create_retrieval_chain(retriever, document_chain)
    response = retrieval_chain.invoke({"input": f"{user_prompt}"})
    return {"response": response["answer"]}

# RAGAs Evaluation Endpoint
@app.get("/raga")
def raga():
    loader = TextLoader("./intern.txt")
    docs = loader.load()
    text = "\n".join(doc.page_content for doc in docs)

    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    documents = [Document(page_content=chunk) for chunk in chunks]
    llm = ChatOpenAI(api_key=settings.openai_api_key)
    embeddings = OpenAIEmbeddings(api_key=settings.openai_api_key)
    vectorstore = FAISS.from_documents(documents, embeddings)
      
    retriever = vectorstore.as_retriever()

    prompt = ChatPromptTemplate.from_template("""You are a helpful assistant to students seeking internship opportunities, relying solely on the provided context regarding internships at City University of Seattle. Please do not provide too much information at once. Summarize the context in 1 to 2 sentences and provide more details if they ask for them. If students ask about internship eligibility, please provide brief information solely on the internship eligibility section. If students ask for information about past internships, initially provide several brief descriptions of internships, ordered from the most relevant to the least. If a question does not make any sense, or is not factually coherent, or need more information, please kindly explain why instead of answering something not correct. If you do not know the answer to a question, please do not share false information.:

    <context>
    {context}
    </context>

    Question: {question}""")

    rag_chain = (
        {"context": retriever,  "question": RunnablePassthrough()} 
        | prompt 
        | llm
        | StrOutputParser() 
    )

    questions = ["I have completed 1 term at City University of Seattle. Am I eligible to apply for the internship course?","How do I apply for the internship course?", "What is the name of the most recently completed internship by a student?"]
    ground_truths = ["You are eligible to apply for the internship course after completing 3 quarters at City University of Seattle", "You need to obtain an offer letter and a program director’s approval letter by week 5 of the previous quarter.", "One Code Club"]
    answers = []
    contexts = []

    # Inference
    for query in questions:
        answers.append(rag_chain.invoke(query))
        contexts.append([docs.page_content for docs in retriever.get_relevant_documents(query)])

    # To dict
    data = {
        "question": questions,
        "answer": answers,
        "contexts": contexts,
        "ground_truth": ground_truths
    }

    # Convert dict to dataset
    dataset = Dataset.from_dict(data)
    result = evaluate(
    dataset = dataset, 
    metrics=[
        context_precision,
        context_recall,
        faithfulness,
        answer_relevancy,
    ],
    )
    
    df = result.to_pandas()
    print(df)
    return {"df": df}