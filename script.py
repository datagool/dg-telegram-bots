import requests

r = requests.get('https://www.evttenorio.com', timeout=5)

print(r.text)
