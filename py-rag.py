#!/usr/bin/env python3
import os
import time
import kong_pdk.pdk.kong as kong

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

embedding_function = None
vector_dbs = {}

Schema = (
    {"vectordb_name": {"type": "string"}},
)

version = '0.1.0'
priority = 0

# This is an example plugin that add a header to the response

class Plugin(object):
    def __init__(self, config):
        global embedding_function
        self.config = config

        if not embedding_function:
            from generate import DEVICE, embedding_model
            embedding_function=HuggingFaceEmbeddings(model_name=embedding_model, model_kwargs={'device': DEVICE})

    def access(self, kong: kong.kong):
        db_name = self.config['vectordb_name']
        if db_name not in vector_dbs:
            # TODO: lock
            vector_db = Chroma(persist_directory=os.path.join("chroma", db_name), embedding_function=embedding_function)
            vector_dbs[db_name] = vector_db
        else:
            vector_db = vector_dbs[db_name]
        body, err = kong.request.get_body()
        if err or type(body) != dict or "messages" not in body:
            return kong.response.exit(400, "Bad Request")

        next_input = None
        for hist in body["messages"]:
            if hist["role"] == "user":
                next_input = hist
    
        if not next_input: # no user input yet
            return

        start = time.time()
        search_results = vector_db.similarity_search(next_input["content"], k=2)
        some_context = ""
        for result in search_results:
            some_context += result.page_content + "\n\n"
        next_input["content"] = some_context + next_input["content"]
        kong.response.set_header("x-kong-rag-latency", "%.2f" % (time.time() - start))

        print(body)

        return kong.service.request.set_body(body)




# add below section to allow this plugin optionally be running in a dedicated process
if __name__ == "__main__":
    from kong_pdk.cli import start_dedicated_server
    start_dedicated_server("py-rag", Plugin, version, priority, Schema)