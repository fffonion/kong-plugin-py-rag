from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader
import os
import sys
import torch
import time

if torch.cuda.is_available():
    DEVICE = "cuda"
elif torch.backends.mps.is_available():
    DEVICE = "mps"
else:
    DEVICE = "cpu"

print("Using device: " + DEVICE)

embedding_model = "sentence-transformers/all-MiniLM-L6-v2"


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: generate.py document_directory output_name")
        sys.exit(1)
    
    if not os.path.exists("chroma"):
        os.mkdir("chroma")

    outd = os.path.join("chroma", sys.argv[2])

    os.system("rm -rf %s" % outd)

    loaders = [
        DirectoryLoader(sys.argv[1])
    ]

    docs = []
    for file in loaders:
        docs.extend(file.load())
    #split text to chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = text_splitter.split_documents(docs)
    embedding_function = HuggingFaceEmbeddings(model_name=embedding_model, model_kwargs={'device': DEVICE})

    start = time.time()
    vectorstore = Chroma.from_documents(docs, embedding_function, persist_directory=outd)

    print("%d documents loaded in %.2fs" % (vectorstore._collection.count(), time.time() - start))