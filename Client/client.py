
#coding=utf-8
import requests
url = "http://39.100.154.163:8080"
path = r"C:\Users\dtk26\Desktop\client\test.png"
print (path)
files = {'file': open(path, 'rb')}
r = requests.post(url, files=files)
print (r.url)
print (r.text)