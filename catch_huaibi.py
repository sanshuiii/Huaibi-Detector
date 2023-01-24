import os
import re
import json
from tqdm import tqdm
import time

from config import config

user = config['username'] # your username
python_path = config['python_path'] # which python to be used
prefix = config['ip_prefix'] # ip prefix
suffix = config['ip_suffix'] # ip suffix

memory_dict = {}
hpc_dict = {}

def add_to_memory_dict(usr, p):
    if usr not in memory_dict:
        memory_dict[usr] = 0
    memory_dict[usr] += p

def add_to_hpc_dict(usr, p):
    if usr not in hpc_dict:
        hpc_dict[usr] = set()
    if p not in hpc_dict[usr]:
        hpc_dict[usr].add(p)

def remove_from_hpc_dict(usr, p):
    if usr in hpc_dict and p in hpc_dict[usr]:
        hpc_dict[usr].remove(p)
        

class GPU:
    def __init__(self, ip, address):
        self.ip = ip
        self.address = address
        self.name = None
        self.last_update_time = None
        self.cuda_version = None
        self.memory_usage = None
        self.usr = []
    
    def update(self, name, last_update_time, cuda_version, memory_usage, usr):
        self.name = name
        self.last_update_time = last_update_time
        self.cuda_version = cuda_version
        self.memory_usage = memory_usage

        for u,p in self.usr:
            # update memory_dict
            add_to_memory_dict(u, -p)
            # update hpc_dict
            remove_from_hpc_dict(u, self.ip)
        del self.usr

        self.usr = usr
        for u,p in self.usr:
            # update memory_dict
            add_to_memory_dict(u, p)
            # update hpc_dict
            add_to_hpc_dict(u, self.ip)
    
    def __str__(self):
        return 'GPU: '+str(self.ip)+'\t'+str(self.name)+'\t'+str(self.last_update_time)+'\t'+str(self.cuda_version)+'\t'+str(self.memory_usage)+'\t'+str(self.usr)

gpus = []
for i in suffix:
    address = user+'@'+prefix+str(i)
    gpus.append(GPU(i, address))


while(1):
    for gpu in tqdm(gpus):
        res = os.popen('ssh -o \"StrictHostKeyChecking no\" ' + gpu.address + ' ' + python_path + ' -m gpustat').read().split()
        if len(res) == 0 or res[10] != '6000':
            name = 'Unknown'
            last_update_time = 'Unknown'
            cuda_version = 'Unknown'
            memory_usage = '99999 MB / 24576 MB'
            usr_split = []
        else:
            name = res[0]
            last_update_time = ' '.join(res[1:6])
            cuda_version = res[6]
            memory_usage = ' '.join(res[16:20])
            usr = res[21:]
            usr_split = [(re.search(r'(.*)\(', x).group(1), int(re.search(r'\((\d+)', x).group(1))) for x in usr]
            del usr

        gpu.update(name, last_update_time, cuda_version, memory_usage, usr_split)

    # output memory usage of each user
    sorted_data = sorted(memory_dict.items(), key=lambda x: x[1], reverse=True)
    new_memory = []
    for k,v in sorted_data:
        new_memory.append({'name': k, 'value': v})
    json_data = json.dumps(new_memory)
    with open('./static/memory.json', 'w') as f:
        f.write(json_data)
    del sorted_data
    del new_memory
    del json_data

    # output memory usage of each machine
    sorted_data = sorted(gpus, key=lambda x: int(x.memory_usage.split()[0]), reverse=False)
    new_memory = []
    for gpu in sorted_data:
        new_memory.append({'name': gpu.name, 'ip':prefix+str(gpu.ip), 'value': gpu.memory_usage, 'time': gpu.last_update_time})
    json_data = json.dumps(new_memory)
    with open('./static/memory_machine.json', 'w') as f:
        f.write(json_data)
    del sorted_data
    del new_memory
    del json_data

    time.sleep(300)