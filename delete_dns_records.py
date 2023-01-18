import requests

# Скрипт удаляет все DNS записи!!!

####### Вводные данные ##############

api_key = 'xxxxxx'  # Есть в нашем доксе на вкладке CF
zone_id = 'xxxxxx'  # Как узнать ZONE ID домена - https://developers.cloudflare.com/fundamentals/get-started/basic-tasks/find-account-and-zone-ids/
email_cf = 'xxxxxx'  # Почта аккаунта cloudflare

#####################################

headers = {
    'Content-Type': 'application/json',
    'X-Auth-Email': email_cf,
    'X-Auth-Key': api_key
}

url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records?page=1&per_page=1000"

response = requests.get(url, headers=headers)
data = response.json()

for record in data["result"]:
    print(f"Record ID: {record['id']}, Hostname: {record['name']}")

    record_id = record['id']
    endpoint = 'https://api.cloudflare.com/client/v4/zones/' + zone_id + '/dns_records/' + record_id

    response = requests.delete(endpoint, headers=headers)

    if response.status_code == 200:
        print('DNS record successfully deleted')
    else:
        print('Error deleting DNS record')
        print(response.json())
