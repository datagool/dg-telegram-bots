import requests

r = requests.get('https://evttenorio.com', timeout=5)

print(r.text)
