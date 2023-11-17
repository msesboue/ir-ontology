import json
from typing import Dict, Optional, Tuple

from rdflib import Graph
from rdflib.namespace import NamespaceManager

import requests


DB_IP = "localhost"
DB_PORT = "7200"
DB_URL = f"http://{DB_IP}:{DB_PORT}"
REPOSITORY_ID = "ir-onto-demo"

def sparql_select(sparql_query: str, db_url: str, repo_id: str, use_inference: bool=False) -> Dict:
    
    query_resp = requests.get(
        f"{db_url}/repositories/{repo_id}",
        headers={"Accept": "application/sparql-results+json"},
        params={
            "query": sparql_query,
            "infer": use_inference
        }
    )

    return query_resp

def show_owl_classes(db_url: str, repo_id: str, ns_manager: Optional[NamespaceManager]=None) -> None:

    query_classes = """
            SELECT ?p
            WHERE {
                ?p rdf:type owl:Class .
            }
        """
    resp = sparql_select(sparql_query=query_classes, db_url=db_url, repo_id=repo_id)
    json_resp = json.loads(resp.text)
    class_uris = [binding["p"]["value"] for binding in json_resp["results"]["bindings"]]

    if ns_manager is not None:
        class_uris = [ns_manager.curie(uri) for uri in class_uris]

    for uri in class_uris:
        print(uri)

def show_owl_obj_props(db_url: str, repo_id: str, ns_manager: Optional[NamespaceManager]=None) -> None:

    query_classes = """
            SELECT ?p
            WHERE {
                ?p rdf:type owl:ObjectProperty .
            }
        """
    resp = sparql_select(sparql_query=query_classes, db_url=db_url, repo_id=repo_id)
    json_resp = json.loads(resp.text)
    class_uris = [binding["p"]["value"] for binding in json_resp["results"]["bindings"]]

    if ns_manager is not None:
        class_uris = [ns_manager.curie(uri) for uri in class_uris]

    for uri in class_uris:
        print(uri)

def show_instances(class_uri: str, db_url: str, repo_id: str, ns_manager: Optional[NamespaceManager]=None, limit: int=100) -> None:
    query_instances = f"""
        PREFIX ir-onto: <http://www.msesboue.org/o/ir-ontology#>
        SELECT ?p WHERE {{
            ?p a <{class_uri}> .
        }} LIMIT {limit}
    """
    
    resp = sparql_select(sparql_query=query_instances, db_url=db_url, repo_id=repo_id, use_inference=True)
    json_resp = json.loads(resp.text)
    class_uris = [binding["p"]["value"] for binding in json_resp["results"]["bindings"]]

    if ns_manager is not None:
        class_uris = [ns_manager.curie(uri) for uri in class_uris]

    print(f"Instances of {class_uri}")
    for uri in class_uris:
        print(uri)
    print()

def sparql_update(sparql_query: str, db_url: str, repo_id: str) -> None:
    
    query_resp = requests.post(
        f"{db_url}/repositories/{repo_id}/statements",
        headers={"Content-type": "application/sparql-update"},
        data=sparql_query
    )

    if not query_resp.status_code == 204: # check that the triples have been created
        print(f"Something went wrong. HTTP response Code: {query_resp.status_code}")
        print(f"HTTP response body: {query_resp.text}")
    else:
        print("OK")

def insert_graph(graph: Graph, db_url: str, repo_id: str) -> None:
    
    graph_ttl = graph.serialize(format="turtle")

    sparql_query = f"""
        INSERT DATA {{
            {graph_ttl}
        }}
        """
    query_resp = requests.post(
        f"{db_url}/repositories/{repo_id}/statements",
        headers={"Content-type": "application/sparql-update"},
        data=sparql_query
    )

    if not query_resp.status_code == 204: # check that the triples have been created
        print(f"Something went wrong. HTTP response Code: {query_resp.status_code}")
        print(f"HTTP response body: {query_resp.text}")
    else:
        print("OK")

def delete_graph(graph: Graph, db_url: str, repo_id: str) -> None:
    
    graph_ttl = graph.serialize(format="turtle")

    sparql_query = f"""
        DELETE DATA {{
            {graph_ttl}
        }}
        """
    query_resp = requests.post(
        f"{db_url}/repositories/{repo_id}/statements",
        headers={"Content-type": "application/sparql-update"},
        data=sparql_query
    )

    if not query_resp.status_code == 204: # check that the triples have been created
        print(f"Something went wrong. HTTP response Code: {query_resp.status_code}")
        print(f"HTTP response body: {query_resp.text}")
    else:
        print("OK")