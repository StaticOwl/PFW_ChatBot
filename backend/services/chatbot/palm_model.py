"""
# !pip install langchain
# !pip install huggingface_hub
# !pip install faiss-gpu
# !pip install sentence_transformers
# !pip install google.generativeai
# pip install dill
# """

from langchain.llms import GooglePalm
from langchain.embeddings import GooglePalmEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.document_loaders import TextLoader
from langchain.chains.question_answering import load_qa_chain
import os
import dill

DEFAULT_TRAINING_PATH = os.environ['TRAINING_CONTEXT']
DEFAULT_DB_DILL_PATH = os.environ['DB_DILL_PATH']
DEFAULT_CHAIN_DILL_PATH = os.environ['CHAIN_DILL_PATH']
DEFAULT_PALM_THRESHOLD = os.environ['PALM_THRESHOLD']
NO_RESPONSE_MSG = "No response found."
REDIRECTION_MSG = "Please visit https://www.pfw.edu/etcs/computer-science for more information.\n You may also reach out to Seula Daily- Director of CS program- at dailys@pfw.edu"

# with open(DEFAULT_DB_DILL_PATH, "rb") as f:
#     db = dill.load(f)
# with open(DEFAULT_CHAIN_DILL_PATH, "rb") as f:
#     chain = dill.load(f)


def train(path_to_data=DEFAULT_TRAINING_PATH):
    global
    loader = TextLoader(path_to_data)
    documents = loader.load()

    # Convert the content into raw text.
    raw_text = ''
    for i, doc in enumerate(documents):
        text = doc.page_content
        if text:
            raw_text += text

    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=200,
        chunk_overlap=40,
        length_function=len,
    )
    texts = text_splitter.split_text(raw_text)

    embeddings = GooglePalmEmbeddings()
    db = FAISS.from_texts(texts,embeddings)
    chain = load_qa_chain(GooglePalm(), chain_type="stuff")
    # with open("db.dill", "wb") as f:
    #   dill.dump(db, f)
    # with open("chain.dill", "wb") as f:
    #   dill.dump(chain, f)

    return db, chain


def test(query, db, chain, threshold):
    while True:
        query = input("Ask a question (type 'exit' to stop): ")

        if query.lower() == 'exit':
            print("Exiting the loop. Goodbye!")
            break

        docs = db.similarity_search(query)
        try:
            result = chain.run(input_documents=docs, question=query).strip()
            updated_query = f"How accurate/relevant is the {query} to the {result}. Just give score between 0 and 1"
            accuracy = chain.run(input_documents=docs, question=updated_query).strip()
            if float(accuracy) < threshold:
                return REDIRECTION_MSG, accuracy
            else:
                return result, accuracy
        except (IndexError, AttributeError):
            return NO_RESPONSE_MSG

"""
# Usage example:
db,chain=train("backend/services/chatbot/training_data.txt","AIzaSyDacJH5itizG-xyj4nHJRe6-L4PrdoLSuk")
# with open("db.dill", "rb") as f:
#     db = dill.load(f)
# with open("chain.dill", "rb") as f:
#     chain = dill.load(f)
test(db, chain,0.5)
"""