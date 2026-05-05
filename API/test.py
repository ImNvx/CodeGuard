import requests
url = 'http://localhost:5000/check_homework'
#print(check_homework(['eric.mester', 'AlexVasiluta', 'TREYWAY', 'atodo'], ['/problems/1', '/problems/3']))
json_data = {'users' : ['eric.mester', 'AlexVasiluta', 'TREYWAY', 'atodo'], 'problems' : ['/problems/1', '/problems/3']}
response = requests.post(url, json=json_data)
print(response.text)
if response.status_code == 200:
    print('JSON data sent successfully!')
else:
    print('Failed to send JSON data:', response.status_code)