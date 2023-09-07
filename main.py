import sys,os,hashlib,json
from tree import Tree
from datetime import datetime

# refs/heads contains all branches
# while there is only one branch, head is always pointing to master
# as soon as you create a branch, head points to that branch

def read_content(path):
    with open(path,'r') as f:
        return f.read()

def write_content(path,content):
    with open(path, 'w') as f:
        f.write(content)

def write_json(new_data, ref_path = os.path.join('.ignore','refs','ref-map.json')):
    try:
        with open(ref_path, 'r') as file:
            file_data = json.load(file)
    except (json.JSONDecodeError, FileNotFoundError):
        file_data = {"hash-map": []}

    file_data["hash-map"].append(new_data)
    with open(ref_path, 'w') as file:
        json.dump(file_data, file, indent=4)

def assign_id(content,type):
    id = hashlib.sha1(content.encode('utf-8')).hexdigest()
    path = os.path.join('.ignore','objects',id)
    data = f"object type:{type} "+"\x00"+content
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path),exist_ok=True)
        write_content(path,data)
    return id
    
def init(repo):
    os.mkdir(repo)
    os.mkdir(os.path.join(repo,'.ignore'))
    for path in ['objects','staging_area','refs','refs/heads','HEAD']:
        os.mkdir(os.path.join(repo,'.ignore',path))
    print(f"Initialized empty repository in {repo}")

def read_object(object_id):
    path = f".ignore/objects/{object_id}"
    if not os.path.exists(path):
        print(f"object with sha1 {object_id} not found")
        return 
    data = read_content(path)
    arr = data.split('\x00')
    return arr

def add_file(file_path):
    content = read_content(file_path)
    blob_id = assign_id(content,'blob')
    x = {file_path:blob_id}
    write_json(x)
    blob_path = os.path.join('.ignore','objects',blob_id)
    write_content(blob_path,content)
    blob_path = os.path.join('.ignore','staging_area',blob_id)
    write_content(blob_path,content)

def add_dir(dir_path):
     for root, _, files in os.walk(dir_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            add_file(file_path)

def add(path):
    if not os.path.exists(path):
        print(f"File/Directory not found: {path}")
        return
    if os.path.isfile(path):
        add_file(path)
    else:
        add_dir(path)

def commit(message, author=None):
    staging_path = "./.ignore/staging_area"
    if not os.listdir(staging_path):
        print("Nothing to commit, working tree clean")
        return 
    destination = "./.ignore/commits.json"
    files = []
    for file in os.listdir(staging_path):
        files.append(file)
    hash = hashlib.sha1(files.encode('utf-8')).hexdigest()
    now = datetime.now()
    commit_time = now.strftime("%H:%M:%S")
    commit_message = message
    commit_object = {
        "time":commit_time,
        "message":commit_message,
        "author":author,
        "commit_hash":hash
    }
    try:
        with open(destination, 'r') as file:
            file_data = json.load(file)
    except (json.JSONDecodeError, FileNotFoundError):
        file_data = {"commits": []}

    file_data["commits"].append(commit_object)
    with open(destination, 'w') as file:
        json.dump(file_data, file, indent=4)
    return hash

def branch(branch_name):
    # create a new file called branch_name under refs/heads and put the id of commit at which branch_name is pointing to
    os.mkdir(os.path.join('./.ignore/refs/heads',branch_name))
    print(f"New branch {branch_name} created")

def print_branches():
    path = "./.ignore/refs/heads"
    for branch in os.listdir(path):
        print(branch)

if __name__ == '__main__':
    if sys.argv[1] == "init":
        if len(sys.argv) < 3:
            print("Expected 2 arguments but got 1")
        else:
            init(sys.argv[2])

    if sys.argv[1] == "add":
        if len(sys.argv) < 3:
            print("Nothing specified, nothing added")
        else:
            add(sys.argv[2])

    if sys.argv[1] == "commit":
        message = input("Please enter the commit message for your changes:\n")
        commit(message=message)

    if sys.argv[1] == "push":
        pass

    if sys.argv[1] == "branch":
        if len(sys.argv) < 3:
            print_branches()
        else:
            branch(sys.argv[2])

    if sys.argv[1] == "merge":
        pass

    if sys.argv[1] == "rebase":
        pass