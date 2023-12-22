from kubernetes import client, config
import time
import sys
import csv 

page_number = sys.argv[1]

def read_predicted_traffic(page_number = page_number):
    traffic_q = []
    with open(f'./testing_traffic/{page_number}_predicted_traffic.csv', 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        for r in csv_reader:
            traffic_q.append(int(r[0]))
    return traffic_q

predicted_traffic = read_predicted_traffic()
start_time = time.time()


def scale():

    config.load_kube_config()
    apps_v1_api = client.AppsV1Api()

    cur_time = time.time()
    index = int(cur_time - start_time)
    desired_replica = int( max(predicted_traffic[ min(index, len(predicted_traffic) - 1) : min(index + 5, len(predicted_traffic))  ]) / 5 )

    apps_v1_api.patch_namespaced_deployment_scale(
        name="http-server",
        namespace="default",
        body={"spec": {"replicas": desired_replica}},
    )

if __name__ == "__main__":
    while time.time() - start_time  < 350:
        scale()
        time.sleep(0.5)