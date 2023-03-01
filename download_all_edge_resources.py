import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import mysql.connector
import sys
import zipfile
import os
from os import path
import shutil
import zipfile as zp
import re
import pyutil
import json
import requests
import upload_n_deploy
import zip_n_unzip
import logging
from pathlib import Path

def download_all_apps(app_name,org,token):
      url = "https://api.enterprise.apigee.com/v1/organizations/"+org+"/apps/"+app_name
      payload={}
      headers = {'Authorization': 'Bearer '+token}
      response = requests.request("GET", url, headers=headers, data=payload)
      status_code = response.status_code
      path="data_edge/apps/"
      if status_code == 200:
        Path(path).mkdir(parents=True, exist_ok=True)
        target_path = path+"/"+app_name+".json"
        with open(target_path, "w") as file:
          file.write(response.text)
        file.close()  

def download_all_products(product_name,org,token):
      url = "https://api.enterprise.apigee.com/v1/organizations/"+org+"/apiproducts/"+product_name
      payload={}
      headers = {'Authorization': 'Bearer '+token}
      response = requests.request("GET", url, headers=headers, data=payload)
      status_code = response.status_code
      if status_code == 200:
        path="data_edge/apiproducts/"
        Path(path).mkdir(parents=True, exist_ok=True)
        target_path = path+"/"+product_name+".json"
        with open(target_path, "w") as file:
          file.write(response.text)
        file.close()  

def download_all_developers(developer_name,org,token):
      url = "https://api.enterprise.apigee.com/v1/organizations/"+org+"/developers/"+developer_name
      payload={}
      headers = {'Authorization': 'Bearer '+token}
      response = requests.request("GET", url, headers=headers, data=payload)
      status_code = response.status_code
      if status_code == 200:
        path="data_edge/developers/"
        Path(path).mkdir(parents=True, exist_ok=True)
        target_path = path+"/"+developer_name
        with open(target_path, "w") as file:
          file.write(response.text)
        file.close()

def download_all_target_servers(ts_name,org,token,env):
      url = "https://api.enterprise.apigee.com/v1/organizations/"+org+"/environments/"+env+"/targetservers/"+ts_name
      payload={}
      headers = {'Authorization': 'Bearer '+token}
      response = requests.request("GET", url, headers=headers, data=payload)
      status_code = response.status_code
      if status_code == 200:
        path="data_edge/targetservers/"+env
        Path(path).mkdir(parents=True, exist_ok=True)
        target_path = path+"/"+ts_name
        response = response.text
        with open(target_path, "w") as file:
          file.write(response)
        file.close()

def download_all_keyvaluemaps(kvm_name,org,token,env):
      url = "https://api.enterprise.apigee.com/v1/organizations/"+org+"/environments/"+env+"/keyvaluemaps/"+kvm_name
      payload={}
      headers = {'Authorization': 'Bearer '+token}
      response = requests.request("GET", url, headers=headers, data=payload)
      status_code = response.status_code
      if status_code == 200:
        path="data_edge/keyvaluemaps/"+env
        Path(path).mkdir(parents=True, exist_ok=True)
        target_path = path+"/"+kvm_name
        response = response.text
        with open(target_path, "w") as file:
          file.write(response)
        file.close()

def download_all_keyvaluemaps_org_level(kvm_name,org,token):
      url = "https://api.enterprise.apigee.com/v1/organizations/"+org+"/keyvaluemaps/"+kvm_name
      payload={}
      headers = {'Authorization': 'Bearer '+token}
      response = requests.request("GET", url, headers=headers, data=payload)
      status_code = response.status_code
      if status_code == 200:
        path="data_edge/keyvaluemaps"
        target_path = path+"/org"
        Path(target_path).mkdir(parents=True, exist_ok=True)
        target_path = target_path+"/"+kvm_name        
        response = response.text
        with open(target_path, "w") as file:
          file.write(response)
        file.close()

def get_list_of_resources_by_env(org_name,token,env,resource_type):
    url = "https://api.enterprise.apigee.com/v1/organizations/"+org_name+"/environments/"+env+"/"+resource_type
    payload={}
    headers = {'Authorization': 'Bearer '+token}
    response = requests.request("GET", url, headers=headers, data=payload)
    response = response.json()
    return response 

def unzip_files(folder_path,filename):
    with zipfile.ZipFile(folder_path+"\\"+filename, 'r') as zip_ref:
        filename = filename.replace(".zip",'')
        zip_ref.extractall(folder_path+"\\"+filename)


def download_all_proxies(proxy_name,org,token):
    url = "https://api.enterprise.apigee.com/v1/organizations/"+org+"/apis/"+proxy_name+"/revisions"
    payload={}
    headers = {'Authorization': 'Bearer '+token}
    response = requests.request("GET", url, headers=headers, data=payload)
    path="data_edge/proxies/"
    match_multiple_revisions = re.search('\,', response.text)
    if match_multiple_revisions:
        proxies_revision_names_arr=response.text.split(',')
        rev_no=len(proxies_revision_names_arr)
        url = "https://api.enterprise.apigee.com/v1/organizations/"+org+"/apis/"+proxy_name+"/revisions/"+str(rev_no)+"?format=bundle"
        payload={}
        headers = {'Authorization': 'Bearer '+token}
        response = requests.request("GET", url, headers=headers, data=payload)
        Path(path).mkdir(parents=True, exist_ok=True)
        target_path = path+"/"+proxy_name+".zip"
        response = requests.request("GET", url, headers=headers, data=payload, stream=True)
        handle = open(target_path, "wb")
        for chunk in response.iter_content(chunk_size=512):
            if chunk:  # filter out keep-alive new chunks
                handle.write(chunk)
        handle.close()
    else:
        url = "https://api.enterprise.apigee.com/v1/organizations/"+org+"/apis/"+proxy_name+"/revisions/1"+"?format=bundle"
        payload={}
        headers = {'Authorization': 'Bearer '+token}
        response = requests.request("GET", url, headers=headers, data=payload)
        Path(path).mkdir(parents=True, exist_ok=True)
        target_path = path+"/"+proxy_name+".zip"
        response = requests.request("GET", url, headers=headers, data=payload, stream=True)
        handle = open(target_path, "wb")
        for chunk in response.iter_content(chunk_size=512):
            if chunk:  # filter out keep-alive new chunks
                handle.write(chunk)
        handle.close()


def download_all_sharedflows(sf_name,org,token):
    url = "https://api.enterprise.apigee.com/v1/organizations/"+org+"/sharedflows/"+sf_name+"/revisions"
    payload={}
    headers = {'Authorization': 'Bearer '+token}
    response = requests.request("GET", url, headers=headers, data=payload)
    path="data_edge/sharedflows/"
    match_multiple_revisions = re.search('\,', response.text)
    if match_multiple_revisions:
        proxies_revision_names_arr=response.text.split(',')
        rev_no=len(proxies_revision_names_arr)
        url = "https://api.enterprise.apigee.com/v1/organizations/"+org+"/sharedflows/"+sf_name+"/revisions/"+str(rev_no)+"?format=bundle"
        payload={}
        headers = {'Authorization': 'Bearer '+token}
        response = requests.request("GET", url, headers=headers, data=payload)
        Path(path).mkdir(parents=True, exist_ok=True)
        target_path = path+"/"+sf_name+".zip"
        response = requests.request("GET", url, headers=headers, data=payload, stream=True)
        handle = open(target_path, "wb")
        for chunk in response.iter_content(chunk_size=512):
            if chunk:  # filter out keep-alive new chunks
                handle.write(chunk)
        handle.close()
    else:
        url = "https://api.enterprise.apigee.com/v1/organizations/"+org+"/sharedflows/"+sf_name+"/revisions/1"+"?format=bundle"
        payload={}
        headers = {'Authorization': 'Bearer '+token}
        response = requests.request("GET", url, headers=headers, data=payload)
        Path(path).mkdir(parents=True, exist_ok=True)
        target_path = path+"/"+sf_name+".zip"
        response = requests.request("GET", url, headers=headers, data=payload, stream=True)
        handle = open(target_path, "wb")
        for chunk in response.iter_content(chunk_size=512):
            if chunk:  # filter out keep-alive new chunks
                handle.write(chunk)
        handle.close()

def count_more_than_1000(startKey,resource,org,token):
    url = "https://api.enterprise.apigee.com/v1/organizations/"+org+"/"+resource+"?startKey="+startKey+"&count=1000"
    print(url)
    payload={}
    headers = {'Authorization': 'Bearer '+token}
    response = requests.request("GET", url, headers=headers, data=payload)
    response = response.json()
    return response


def remove_existing_folder(resource):
    path_only_access="data_edge/"+resource+"/"
    if os.path.exists(path_only_access):
        shutil.rmtree(path_only_access)

def get_list_of_resources(org_name,token,resource_type):
    url = "https://api.enterprise.apigee.com/v1/organizations/"+org_name+"/"+resource_type
    payload={}
    headers = {'Authorization': 'Bearer '+token}
    response = requests.request("GET", url, headers=headers, data=payload)
    response = response.json()
    return response 



def replace_from_string(string_name):    
    string_name = string_name.replace("'status': 'approved'",'')    
    string_name = string_name.replace("[",'')
    string_name = string_name.replace("]",'')
    string_name = string_name.replace("'",'')
    string_name = string_name.replace("{",'')
    string_name = string_name.replace("}",'')
    string_name = string_name.replace(":",'')
    string_name = string_name.replace("'",'')
    string_name = string_name.replace("apiproduct",'')
    string_name = string_name.replace(", ,",',')
    string_name = string_name.replace("   ",' ')
    string_name = string_name.strip(" ")
    string_name = string_name.strip(",")
    return string_name

def create_developer_id_files(folderpath,developer_file):
    f = open(folderpath+"\\"+developer_file)
    data = json.load(f)
    f.close()
    developer_id = data["developerId"]
    developer_email = data["email"]
    dictionary = {
    "developerId": developer_id,
    "email": developer_email
    }     
    json_object = json.dumps(dictionary, indent=4)    
    # Writing to sample.json
    with open(developers_folder_path+"\\"+developer_id+".json", "w") as outfile:
        outfile.write(json_object)

# List of URLs to fetch
edge_org_name = "nitinmahavir2021-eval"
edge_token ="eyJhbGciOiJSUzI1NiJ9.eyJqdGkiOiJkOTBiNTgzYi1lYjc2LTQwNzUtYWRiOS1lNWI3NDhkOGJjZDYiLCJzdWIiOiIyOTliNDA1Ni03NWM0LTQ3YzItYmE2My1mZDljNmI4NThlZTUiLCJzY29wZSI6WyJzY2ltLmVtYWlscy5yZWFkIiwic2NpbS5tZSIsIm9wZW5pZCIsInBhc3N3b3JkLndyaXRlIiwiYXBwcm92YWxzLm1lIiwic2NpbS5pZHMucmVhZCIsIm9hdXRoLmFwcHJvdmFscyJdLCJjbGllbnRfaWQiOiJlZGdlY2xpIiwiY2lkIjoiZWRnZWNsaSIsImF6cCI6ImVkZ2VjbGkiLCJncmFudF90eXBlIjoicGFzc3dvcmQiLCJ1c2VyX2lkIjoiMjk5YjQwNTYtNzVjNC00N2MyLWJhNjMtZmQ5YzZiODU4ZWU1Iiwib3JpZ2luIjoidXNlcmdyaWQiLCJ1c2VyX25hbWUiOiJuaXRpbm1haGF2aXIyMDIxQGdtYWlsLmNvbSIsImVtYWlsIjoibml0aW5tYWhhdmlyMjAyMUBnbWFpbC5jb20iLCJhdXRoX3RpbWUiOjE2Nzc2NTgyMDUsImFsIjowLCJyZXZfc2lnIjoiZGQ5ZDFkN2YiLCJpYXQiOjE2Nzc2NTgyMDUsImV4cCI6MTY3NzcwMTQwNSwiaXNzIjoiaHR0cHM6Ly9sb2dpbi5hcGlnZWUuY29tIiwiemlkIjoidWFhIiwiYXVkIjpbImVkZ2VjbGkiLCJzY2ltLmVtYWlscyIsInNjaW0iLCJvcGVuaWQiLCJwYXNzd29yZCIsImFwcHJvdmFscyIsInNjaW0uaWRzIiwib2F1dGgiXX0.juW1VMCNLNxJCP9gLIUHc8QGvbS7Xx33IVK1opMJwNggxWipGipLIaiJhJVWEEDrlReooAc-EpP6SjEF0fv1LB22_a3utUbGwxIUBL1Ybdxef4AGscCK8oeF7DGaOuui7hNSsP7vnZovZIgClB_tpAxZMwR7KcEBQI43EPsAEKP-7XOVkGB805lRcHrGnRpaGXVT9EH03UzcgzWN6dMEKEYpP04q4CvX_9Dc2lF5bx8BOTzdY6RE9KNaGrwKU2_LfLjhn02xFrx69VbtLvZyFDKlIgU9Lvu-8THDuUDHnUe0hCpPlyI8i0qljnKD45Idt10Q1VDAHvDB39VkRIiJ5g"
current_path="data_edge"


#########################################  code for products #################################################################
remove_existing_folder("apiproducts") 
product_folder_path=current_path+"\\apiproducts"
response =get_list_of_resources(edge_org_name,edge_token,"apiproducts")
product_names =[]
count =0
for product_name in response:
    product_names.append(product_name)
workers = len(product_names)
startKey=product_names[workers-1]
for product_name in product_names:
    count = count+1
    print("Count -> "+str(count)+" Product Name : "+product_name)
    download_all_products(product_name,edge_org_name,edge_token)

more_than_1000_prods = True
no_of_iterations=0
total_products=0
total_products = total_products + workers

if workers < 1000:
    more_than_1000_prods = False
while more_than_1000_prods:
    current_iteration_response=count_more_than_1000(startKey,"apiproducts",edge_org_name,edge_token)
    arr = []
    for app_id in current_iteration_response:
        arr.append(app_id)
        product_names.append(app_id)
        current_iteration_length = len(arr)
    startKey=arr[current_iteration_length-1]    
    no_of_iterations=no_of_iterations+1
    total_products = total_products + current_iteration_length
    for product_name in arr:
        count = count+1
        print("Count -> "+str(count)+" Product Name : "+product_name)
        download_all_products(product_name,edge_org_name,edge_token)
    if current_iteration_length != 1000:
        more_than_1000_prods = False
total_products = total_products - no_of_iterations
product_names = replace_from_string(str(product_names))
print("Product Names :"+str(product_names)+" |")
print("Total Products :"+str(total_products)+" |")

#########################################  code for developers #################################################################
remove_existing_folder("developers") 
count =0
developers_folder_path=current_path+"\\developers"
response =get_list_of_resources(edge_org_name,edge_token,"developers")
developers_names =[]
for developers_name in response:
    developers_names.append(developers_name)
workers = len(developers_names)
startKey=developers_names[workers-1]
for developers_name in developers_names:
    count = count+1
    print("Count -> "+str(count)+" Developer Name : "+developers_name)
    download_all_developers(developers_name,edge_org_name,edge_token)
more_than_1000_dev = True
no_of_iterations=0
total_dev = 0
total_dev = total_dev + workers
if workers < 1000:
    more_than_1000_dev = False
while more_than_1000_dev:
    current_iteration_response=count_more_than_1000(startKey,"developers",edge_org_name,edge_token)
    arr = []
    for app_id in current_iteration_response:
        arr.append(app_id)
        developers_names.append(app_id)
        current_iteration_length = len(arr)
    startKey=arr[current_iteration_length-1]    
    no_of_iterations=no_of_iterations+1
    total_dev = total_dev + current_iteration_length
    for developers_name in arr:
        count = count+1
        print("Count -> "+str(count)+" Developer Name : "+developers_name)
        download_all_developers(developers_name,edge_org_name,edge_token)
    if current_iteration_length != 1000:
        more_than_1000_dev = False
total_dev = total_dev - no_of_iterations
developers_names = replace_from_string(str(developers_names))
filenames = os.listdir(developers_folder_path)
developers_names =[]
for developer_name in filenames:
    developers_names.append(developer_name)
workers = len(developers_names)
if workers > 0:
    for developers_name in developers_names:
        create_developer_id_files(developers_folder_path,developers_name)
developers_names = replace_from_string(str(developers_names))
print("Developer Names :"+str(developers_names)+" |")
print("Total Developers :"+str(total_dev)+" |")
# #########################################  code for apps #################################################################
remove_existing_folder("apps")
count =0
app_folder_path=current_path+"\\apps"
response =get_list_of_resources(edge_org_name,edge_token,"apps")
app_names =[]
total_apps= 0
for app_name in response:
    app_names.append(app_name)
workers = len(app_names)
startKey=app_names[workers-1]
for app_name in app_names:
    count =count +1
    print("Count -> "+str(count)+" App Name : "+app_name)
    download_all_apps(app_name,edge_org_name,edge_token)
more_than_1000_app = True
no_of_iterations=0
total_apps = 0
total_apps = total_apps + workers
if workers < 1000:
    more_than_1000_app = False
while more_than_1000_app:
    current_iteration_response=count_more_than_1000(startKey,"apps",edge_org_name,edge_token)
    arr = []
    for app_id in current_iteration_response:
        arr.append(app_id)
        app_names.append(app_id)
        current_iteration_length = len(arr)
    startKey=arr[current_iteration_length-1]    
    no_of_iterations=no_of_iterations+1
    total_apps = total_apps + current_iteration_length
    for app_name in arr:
        count = count +1
        print("Count -> "+str(count)+" App Name : "+app_name)
        download_all_apps(app_name,edge_org_name,edge_token)
    if current_iteration_length != 1000:
        more_than_1000_app = False
total_apps = total_apps - no_of_iterations
app_names = replace_from_string(str(app_names))
print("Total Apps :"+str(total_apps)+" |")
print("APP Names :"+str(app_names)+" |")
# # #########################################  proxies #################################################################
remove_existing_folder("proxies")
count =0
apis_folder_path=current_path+"\\proxies"
response =get_list_of_resources(edge_org_name,edge_token,"apis")
apis_names =[]
for api_name in response:
    apis_names.append(api_name)
for api_name in apis_names:
    count =count +1
    print("Count -> "+str(count)+" Api Name : "+api_name)
    download_all_proxies(api_name,edge_org_name,edge_token)
    unzip_files(apis_folder_path,api_name+".zip")

print("Total APIs :"+str(len(apis_names))+" |")
print("API Names :"+str(apis_names)+" |")
# # #########################################  sharedflows #################################################################
remove_existing_folder("sharedflows") 
sf_folder_path=current_path+"\\sharedflows"
count =0 
response =get_list_of_resources(edge_org_name,edge_token,"sharedflows")
sf_names =[]
for sf_name in response:
    sf_names.append(sf_name)
for sf_name in sf_names:
    count =count +1
    print("Count -> "+str(count)+" SF Name : "+sf_name)
    download_all_sharedflows(sf_name,edge_org_name,edge_token)
    unzip_files(sf_folder_path,sf_name+".zip")

print("Total SFs :"+str(len(sf_names))+" |")
print("SF Names :"+str(sf_names)+" |")
# # #########################################  KVMs Org Level #################################################################
remove_existing_folder("keyvaluemaps") 
kvm_folder_path=current_path+"\\keyvaluemaps"
count =0 
response =get_list_of_resources(edge_org_name,edge_token,"keyvaluemaps")
kvm_names =[]
for kvm_name in response:
    kvm_names.append(kvm_name)
for kvm_name in kvm_names:
    count =count +1
    print("Count -> "+str(count)+" Org Level KVM Name : "+kvm_name)
    download_all_keyvaluemaps_org_level(kvm_name,edge_org_name,edge_token)
print("Total KVMs :"+str(len(kvm_names))+" |")
print("KVM Names :"+str(kvm_names)+" |")
# # #########################################  KVMs Env Level #################################################################
response =get_list_of_resources(edge_org_name,edge_token,"environments")
env_names =[]
for env_name in response:
    env_names.append(env_name)
for env_name in env_names:
    resource_type="keyvaluemaps"
    response=get_list_of_resources_by_env(edge_org_name,edge_token,env_name,resource_type)
    kvm_names =[]
    for kvm_name in response:
        kvm_names.append(kvm_name)
    for kvm_name in kvm_names:
        count =count +1
        print("Count -> "+str(count)+" " +env_name+"  Environment KVM Name : "+kvm_name)
        download_all_keyvaluemaps(kvm_name,edge_org_name,edge_token,env_name)
    print("Total KVMs :"+str(len(kvm_names))+" |")
    print("KVM Names :"+str(kvm_names)+" |")
# # #########################################  Target Server Env Level #################################################################
remove_existing_folder("targetservers") 
response =get_list_of_resources(edge_org_name,edge_token,"environments")
env_names =[]
for env_name in response:
    env_names.append(env_name)
for env_name in env_names:
    resource_type="targetservers"
    response=get_list_of_resources_by_env(edge_org_name,edge_token,env_name,resource_type)
    ts_names =[]
    count =0
    for ts_name in response:
        ts_names.append(ts_name)
    for ts_name in ts_names:
        count =count +1
        print("Count -> "+str(count)+" " +env_name+"  Environment Target Server Name : "+ts_name)
        download_all_target_servers(ts_name,edge_org_name,edge_token,env_name)
    print("Total Target Servers :"+str(len(ts_names))+" |")
    print("Target Server Names :"+str(ts_names)+" |")


