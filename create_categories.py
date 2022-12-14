import base64
import requests
import gspread

######### Вводные данные ##############

domain = "site.com"  # хост
spreadsheet_id = "xxxxxxxxxxxxxxxxxxx"  # id рабочего докса на одном из листов которого есть список категорий
spreadsheet_name = "categories"  # наименование листа, где в колонке A расположены наименования всех категорий (без наименования столбца)

#######################################



gc = gspread.service_account(filename="creds-google-sheets.json")

sh = gc.open_by_key('xxxxxxxxxxxxxxxxxxxx')
worksheet = sh.worksheet("credits")

all_sites_data = worksheet.get_all_values()

for i in range(0, len(all_sites_data)):
    if all_sites_data[i][0] == domain:
        username = all_sites_data[i][2]
        app_password = all_sites_data[i][3]


user = username
password = app_password
url = 'https://' + domain + '/wp-json/wp/v2/categories'

wp_connection = user + ':' + password
token = base64.b64encode(wp_connection.encode())

headers = {'Authorization': 'Basic ' + token.decode('utf-8')}

sh2 = gc.open_by_key(spreadsheet_id)
cat_worksheet = sh2.worksheet(spreadsheet_name)

categories_list = cat_worksheet.col_values(1)

##### Create Categories

for category in categories_list:
    post = {'name': category}
    wp_request_create_categories = requests.post(url, headers=headers, json=post)

print("Done")