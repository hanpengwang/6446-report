import asyncio
import aiohttp
import time
import sys
import csv 
import logging
import concurrent.futures
import requests
import random

# for the best average latency, each pod can take 5 request per second

page_number = sys.argv[1]
scaling_type = sys.argv[2]

with open(f'./latency/{page_number}_{scaling_type}_latencyAndError.log', 'w'):
    pass

logging.basicConfig(filename=f'./latency/{page_number}_{scaling_type}_latencyAndError.log', level=logging.INFO)

def read_traffic(page_number = page_number):
    traffic_q = []
    with open(f'./testing_traffic/{page_number}_actual_traffic.csv', 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        for r in csv_reader:
            traffic_q.append(int(r[0]))
    return traffic_q

async def fetch(session):
    start_time = time.time()
    try:
        async with session.get("http://localhost:8080/cpu") as response:
            end_time = time.time()
            latency = end_time - start_time
            logging.info(f"{latency},{start_time}")

    except Exception as e:
        logging.info(f"error, {start_time}")

async def periodic_request():
    '''
    1. read traffic file and push it to a queue
    2. pop queue every second
    3. evenly split number of request within a second 
    4. send those requests to create_task 
    
    '''

    traffic_q = read_traffic()

    async with aiohttp.ClientSession() as session:
        while len(traffic_q) > 0:
            num_requests = traffic_q.pop(0)
            for _ in range(num_requests):
                # await asyncio.sleep(2 / num_requests)
                asyncio.create_task(fetch(session))
            await asyncio.sleep(2) 

asyncio.run(periodic_request())


# def send_request():
#     start_time = time.time()
#     try:
#         resp = requests.get("http://localhost:8080/cpu")
#         latency = time.time() - start_time
#         logging.info(f"{latency},{start_time}")
#     except Exception as e:
#         logging.info(f"error, {start_time}")

# def main():
#     traffic_q = read_traffic()

#     while len(traffic_q) > 0:
#         num_requests = traffic_q.pop(0)
#         with concurrent.futures.ThreadPoolExecutor() as executor:
#             for _ in range(num_requests):  
#                 executor.submit(send_request)
#         time.sleep(2) 

# if __name__ == "__main__":
#     main()