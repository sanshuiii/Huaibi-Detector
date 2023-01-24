config = {}

# config for catch_huaibi.py (data collection)
config['python_path'] = '~/.conda/envs/huaibi/bin/python' # which python to be used (with gpustat) on the remote machine
config['username'] = 'username' # username on the remote machine, the full address will be username@ip_prefix+ip_suffix
config['ip_prefix'] = '10.127.30.' # ip prefix of the remote machine
config['ip_suffix'] = list(range(0,20)) # ip suffix of the remote machine

# config for web_server.py (web server)
config['web_server_port'] = 12600 # port of the web server (on the local machine)