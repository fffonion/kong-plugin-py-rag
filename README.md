# Kong Retrieval Augmented Generation Plugin

A RAG plugin to boost your AI experience in Kong. Embeddings are handled locally.


## Usage

Install dependencies:

```shell
pip3 install -r requirements.txt
```

Generate the vector DB from documents:

```shell
# Usage python3 ./generate.py <path to documents> <vectordb_name>
python3 ./generate.py examples/mars-companies mars-companies
```

Enable the plugin in Kong:

Sample declarative config:
```
_format_version: "1.1"
services:
- protocol: http
  host: localhost
  port: 1234
  routes:
  - protocols:
    - http
    paths:
    - /
    plugins:
    - name: py-rag
      config:
        vectordb_name: mars-companies
```

Sample Kong config:

```
declarative_config=kong-rag.yml
plugins=bundled,py-rag
pluginserver_names=py_rag
pluginserver_py_rag_socket=/tmp/py-rag.sock
pluginserver_py_rag_query_cmd=/path/to/kong-plugin-py-rag/py-rag.py --dump
pluginserver_py_rag_start_cmd=/path/to/kong-plugin-py-rag/py-rag.py -p /tmp/ --socket-name py-rag.sock

```
