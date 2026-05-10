from flask import Flask, render_template, request, jsonify
from src.helper import download_hugging_face_embeddings
from langchain_pinecone import PineconeVectorStore
from langchain_groq import ChatGroq
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from src.prompt import *
import os
from pinecone import Pinecone

app = Flask(__name__)
load_dotenv()



PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not PINECONE_API_KEY:
    raise ValueError("PINECONE_API_KEY is missing")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is missing")

pc = Pinecone(api_key=PINECONE_API_KEY)

embeddings = download_hugging_face_embeddings()
index_name = "medical-chatbot"
docsearch = PineconeVectorStore(
     index=pc.Index(index_name),
    embedding=embeddings
)


retriever = docsearch.as_retriever(search_type="similarity", search_kwargs={"k": 3})
chatModel = ChatGroq(model="openai/gpt-oss-20b")

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{input}")
    ]
)

question_answering_chain = create_stuff_documents_chain(chatModel, prompt)
rag_chain = create_retrieval_chain(retriever, question_answering_chain)


@app.route('/')
def index():
    return render_template('chat.html')



@app.route("/get", methods=["GET", "POST"])
def chat():
    msg=request.form["msg"]
    input = msg
    print(input)
    response = rag_chain.invoke({"input": msg})
    print("Response: ", response["answer"])
    return str(response["answer"])


port = int(os.environ.get("PORT", 5000))
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=port, debug=True)