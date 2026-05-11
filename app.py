from flask import Flask, render_template, request
from src.helper import download_hugging_face_embeddings
from langchain_pinecone import PineconeVectorStore
from langchain_groq import ChatGroq
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from src.prompt import system_prompt
from pinecone import Pinecone
import os

app = Flask(__name__)
load_dotenv()

# ---------------- ENV ----------------
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

if not PINECONE_API_KEY:
    raise ValueError("PINECONE_API_KEY is missing")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is missing")

# ---------------- MODEL SETUP ----------------
pc = Pinecone(api_key=PINECONE_API_KEY)

embeddings = download_hugging_face_embeddings()

index = pc.Index("medical-chatbot")

docsearch = PineconeVectorStore(
    index=index,
    embedding=embeddings
)

retriever = docsearch.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 3}
)

llm = ChatGroq(model="openai/gpt-oss-20b")

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{input}")
])

qa_chain = create_stuff_documents_chain(llm, prompt)
rag_chain = create_retrieval_chain(retriever, qa_chain)

# ---------------- ROUTES ----------------
@app.route("/")
def home():
    return render_template("chat.html")

@app.route("/get", methods=["POST"])
def get_response():

    msg = request.form.get("msg")

    if not msg:
        return "No input received"

    response = rag_chain.invoke({"input": msg})

    return response["answer"]

# ---------------- RUN ----------------
if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5001))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False,
        use_reloader=False
    )