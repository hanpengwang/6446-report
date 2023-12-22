from kubernetes import client, config
import re
import time
import logging
import sys

page_number = sys.argv[1]
scaling_type = sys.argv[2]

with open(f'./pods_analysis/{page_number}_{scaling_type}_pods_analysis.log', 'w'):
    pass

logging.basicConfig(filename=f'./pods_analysis/{page_number}_{scaling_type}_pods_analysis.log', level=logging.INFO)

def parse_quantity(quantity_str):
    """
    Parses a Kubernetes quantity string (like '100Mi' or '2Gi') into a number.
    """
    units = {
        'Ki': 1024,
        'Mi': 1024**2,
        'Gi': 1024**3,
        'Ti': 1024**4,
        'Pi': 1024**5,
        'Ei': 1024**6,
        'k': 1000,
        'M': 1000**2,
        'G': 1000**3,
        'T': 1000**4,
        'P': 1000**5,
        'E': 1000**6,
        'n': (0.1)**6
    }
    pattern = r'(\d+)([a-zA-Z]*)'
    match = re.match(pattern, quantity_str)
    if not match:
        return 0
    
    value, unit = match.groups()
    return int(value) * units.get(unit, 1)

def get_pod_metrics():
    # Load the kubeconfig file
    config.load_kube_config()

    # Create a client for the metrics and core API
    metrics_api = client.CustomObjectsApi()
    core_api = client.CoreV1Api()

    # Fetch the metrics for all pods in all namespaces
    pod_metrics = metrics_api.list_cluster_custom_object(
        group="metrics.k8s.io",
        version="v1beta1",
        plural="pods",
    )

    # Fetch node information
    nodes = core_api.list_node()
    node_resources = {}
    for node in nodes.items:
        allocatable = node.status.allocatable
        alloc_cpu = parse_quantity(allocatable['cpu'])
        alloc_memory = parse_quantity(allocatable['memory'])
        node_resources[node.metadata.name] = {'cpu': alloc_cpu, 'memory': alloc_memory}

    cpu_usages = []
    num_pods = 0

    for pod in pod_metrics.get('items', []):
        if "http-server" not in pod["metadata"]["name"]:
            continue
        num_pods += 1
        for container in pod['containers']:
            cpu_usage = parse_quantity(container['usage']['cpu'])
            cpu_percent = (cpu_usage / 500) * 100
            cpu_usages.append(cpu_percent)
    
    logging.info(f"{num_pods},{max(cpu_usages)},{min(cpu_usages)},{sum(cpu_usages)/len(cpu_usages)},{time.time()}")


if __name__ == "__main__":
    start_time = time.time()
    logging.info(f"{0},{0},{0},{0},{start_time}")
    while time.time() - start_time  < 350:
        get_pod_metrics()
        time.sleep(0.5)