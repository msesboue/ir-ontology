"""some utility function used in the `pizza_bisou_demo.ipynb` notebook.

    Mainly encapsulate some SPARQL queries.
"""

import json
from typing import Dict, Optional, Set

from rdflib import Graph, URIRef
from rdflib.namespace import NamespaceManager

import networkx as nx
import matplotlib.pyplot as plt

import requests

def sparql_select(sparql_query: str, db_url: str, repo_id: str, use_inference: bool=False) -> Dict:
    """Run a given SPARQL SElECT query on a specified triple store repository.

    Parameters
    ----------
    sparql_query : str
        The SPARQL SELECT query.
    db_url : str
        The URL to reach the triple store server.
    repo_id : str
        The ID of the repository to target.
    use_inference : bool, optional
        Whether or not to consider inferred triples, by default False.

    Returns
    -------
    Dict
        The query response.
    """
    query_resp = requests.get(
        f"{db_url}/repositories/{repo_id}",
        headers={"Accept": "application/sparql-results+json"},
        params={
            "query": sparql_query,
            "infer": use_inference
        },
        timeout=10
    )

    return query_resp

def show_owl_classes(
        db_url: str, repo_id: str, 
        ns_manager: Optional[NamespaceManager]=None
    ) -> None:
    """Run a SPARQL SElECT query over a triple store to fetch the OWL classes and print them.

        Parameters
        ----------
        db_url : str
            The URL to reach the triple store server.
        repo_id : str
            The ID of the repository to target.
        ns_manager: Optional[NamespaceManager]
            An rdflib namespace manager to print cleaner URIs, by default None.
    """
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

def show_owl_obj_props(db_url: str, repo_id: str, 
                       ns_manager: Optional[NamespaceManager]=None
                    ) -> None:
    """Run a SPARQL SElECT query over a triple store to fetch the OWL object properties and print 
    them.

        Parameters
        ----------
        db_url : str
            The URL to reach the triple store server.
        repo_id : str
            The ID of the repository to target.
        ns_manager: Optional[NamespaceManager]
            An rdflib namespace manager to print cleaner URIs, by default None.
    """
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

def show_instances(class_uri: str, db_url: str, repo_id: str, 
                   ns_manager: Optional[NamespaceManager]=None, 
                   limit: Optional[int]=100
                ) -> None:
    """Run a SPARQL SElECT query over a triple store to fetch the instances of an OWL class and 
    print them.

        Parameters
        ----------
        class_uri: str
            The URI of the class to fetch the instances from.
        db_url : str
            The URL to reach the triple store server.
        repo_id : str
            The ID of the repository to target.
        ns_manager: Optional[NamespaceManager]
            An rdflib namespace manager to print cleaner URIs, by default None.
        limit: Optional[int]
            A maximum number of printed instances, by default 100.
    """
    query_instances = f"""
        PREFIX ir-onto: <http://www.msesboue.org/o/ir-ontology#>
        SELECT ?p WHERE {{
            ?p a <{class_uri}> .
        }} LIMIT {limit}
    """
    resp = sparql_select(
        sparql_query=query_instances,
        db_url=db_url,
        repo_id=repo_id,
        use_inference=True
    )
    json_resp = json.loads(resp.text)
    class_uris = [binding["p"]["value"] for binding in json_resp["results"]["bindings"]]

    if ns_manager is not None:
        class_uris = [ns_manager.curie(uri) for uri in class_uris]

    print(f"Instances of {class_uri}")
    for uri in class_uris:
        print(uri)
    print()

def sparql_update(sparql_query: str, db_url: str, repo_id: str) -> None:
    """Run a given SPARQL UPDATE query on a specified triple store repository.

    Parameters
    ----------
    sparql_query : str
        The SPARQL UPDATE query.
    db_url : str
        The URL to reach the triple store server.
    repo_id : str
        The ID of the repository to target.
    """
    query_resp = requests.post(
        f"{db_url}/repositories/{repo_id}/statements",
        headers={"Content-type": "application/sparql-update"},
        data=sparql_query,
        timeout=10
    )

    if not query_resp.status_code == 204: # check that the triples have been created
        print(f"Something went wrong. HTTP response Code: {query_resp.status_code}")
        print(f"HTTP response body: {query_resp.text}")
    else:
        print("OK")

def insert_graph(graph: Graph, db_url: str, repo_id: str) -> None:
    """Run a given SPARQL INSERT query on a specified triple store repository.

    Parameters
    ----------
    graph: Graph
        The rdflib graph to insert.
    db_url : str
        The URL to reach the triple store server.
    repo_id : str
        The ID of the repository to target.
    """
    graph_ttl = graph.serialize(format="turtle")

    sparql_query = f"""
        INSERT DATA {{
            {graph_ttl}
        }}
        """
    query_resp = requests.post(
        f"{db_url}/repositories/{repo_id}/statements",
        headers={"Content-type": "application/sparql-update"},
        data=sparql_query,
        timeout=10
    )

    if not query_resp.status_code == 204: # check that the triples have been created
        print(f"Something went wrong. HTTP response Code: {query_resp.status_code}")
        print(f"HTTP response body: {query_resp.text}")
    else:
        print("OK")

def delete_graph(graph: Graph, db_url: str, repo_id: str) -> None:
    """Run a given SPARQL DELETE query on a specified triple store repository.

    Parameters
    ----------
    graph: Graph
        The rdflib graph to delete.
    db_url : str
        The URL to reach the triple store server.
    repo_id : str
        The ID of the repository to target.
    """
    graph_ttl = graph.serialize(format="turtle")

    sparql_query = f"""
        DELETE DATA {{
            {graph_ttl}
        }}
        """
    query_resp = requests.post(
        f"{db_url}/repositories/{repo_id}/statements",
        headers={"Content-type": "application/sparql-update"},
        data=sparql_query,
        timeout=10
    )

    if not query_resp.status_code == 204: # check that the triples have been created
        print(f"Something went wrong. HTTP response Code: {query_resp.status_code}")
        print(f"HTTP response body: {query_resp.text}")
    else:
        print("OK")

def end_uri_to_label(end_uri: str) -> str:
    """Extract the label from the end of a URI.

    The end URI string is expected to be in the camel case form 
    beginning with an underscore and a lower case letter.

    Parameters
    ----------
    end_uri : str
        The string to construct the label from.

    Returns
    -------
    str
        The label.
    """
    label = end_uri[1].upper()
    for l in end_uri[2:]:
        if l.isupper():
            label += " "
        label += l

    return label

def show_graph_portion(subject_uris: Set[URIRef], graph: Graph) -> None:
    """Display a graph representation of an RDF graph constructed with a set of source URIs
    and their direct neighbors.

    Parameters
    ----------
    subject_uris: Set[URIRef]
        The source URIs.
    graph: Graph
        The rdflib graph to construct the graph image from.
    """
    nx_graph = nx.Graph()

    for uri in subject_uris:
        query = f"""
            SELECT ?p ?o
            WHERE {{
                <{uri}> ?p ?o .
            }}
        """

        s = end_uri_to_label(uri.partition("#")[2])

        for r in graph.query(query):
            p = r["p"].partition("#")[2]
            o = end_uri_to_label(r["o"].partition("#")[2])
            nx_graph.add_node(s)
            nx_graph.add_node(o)
            nx_graph.add_edge(s, o, label=p)

    # Visualize the graph using Matplotlib
    pos = nx.spring_layout(nx_graph)
    labels = nx.get_edge_attributes(nx_graph, 'label')
    nx.draw(nx_graph, pos, with_labels=True, node_size=700, node_color="skyblue", font_size=8)
    nx.draw_networkx_edge_labels(nx_graph, pos, edge_labels=labels)
    plt.show()


## Failed experiment to use the robot CLI for reasoning 
# reasoner = "hermit" # "ELK"

# error_output = ""

# input_file = "data/temp/pizza_graph_to_infer.ttl"
# temp_file = "./data/temp/inference_temp.ttl"

# robot_command = [
#     JAVA_EXE,
#     "-jar",
#     ROBOT_JAR,
#     "reason",
#     "--reasoner",
#     reasoner,
#     "--create-new-ontology",
#     "true",
#     # "--annotate-inferred-axioms",
#     # "true",
#     "--input",
#     input_file,
#     "--output",
#     temp_file
# ]

# try:
#     output = subprocess.check_output(
#         robot_command, stderr=subprocess.STDOUT)
# except subprocess.CalledProcessError as e:
#     error_output = e.output.decode()