import base64
import requests
from bs4 import BeautifulSoup
import json
from serpapi import GoogleSearch
import csv
import re
from datetime import datetime
from datetime import timedelta
import random
import gspread

########## Вводные данные ###############

domain = "site.com"  # хост
filename_with_posts_data = "to_posting_example.csv"  # файл с данными
path_with_generated_files = "glue_new_html_files_layout/"  # папка с сгенерированными статьями
serpapi_key = "xxxxxxxxxxxxxxxxxxxx"  # ключ serpapi
publish_period = 'future'  # когда публиковать: 'future' - в будущем, 'publish' - сразу
#### !!! В папке, откуда запускается скрипт, должна быть создана папка "images"

#########################################

gc = gspread.service_account(filename="creds-google-sheets.json")

sh = gc.open_by_key('xxxxxxxxxxxxxxx')
worksheet = sh.worksheet("credits")

all_sites_data = worksheet.get_all_values()



for i in range(0, len(all_sites_data)):
    if all_sites_data[i][0] == domain:
        username = all_sites_data[i][2]
        app_password = all_sites_data[i][3]
        author_id = all_sites_data[i][4]


# Получение ID категорий
user = username
password = app_password
url = 'https://' + domain + '/wp-json/wp/v2/categories'

wp_connection = user + ':' + password
token = base64.b64encode(wp_connection.encode())

headers = {'Authorization': 'Basic ' + token.decode('utf-8')}

wp_request = requests.get(url, headers=headers, params={'per_page': 100})

response = wp_request.json()

categories_ids = {}
for category in response:
    categories_ids.update({category['name']: category['id']})
#########################################

# Постинг

count_posts = 1
filenames_linking_categories = []

with open(filename_with_posts_data, newline='') as csvfile:
    data = csv.reader(csvfile)
    for row in data:
           cat_ids = []
           for i in range(0, len(row[3].split(', '))):
               cat_ids.append(categories_ids[row[3].split(', ')[i]])
           filenames_linking_categories.append([row[1], row[2], row[3], cat_ids])

post_images = []
published_aticles = []
unpublished_aricles = []

now = datetime.utcnow() # Текущее время UTC

for article in filenames_linking_categories:
    filename = article[0]

    # Генерация даты постинга

    hours = random.randint(2, 3)
    minutes = random.randint(0, 59)
    seconds = random.randint(0, 59)

    delta = timedelta(
        hours=hours,
        minutes=minutes,
        seconds=seconds
    )
    time = now + delta
    time_string = time.strftime("%Y-%m-%dT%H:%M:%S")
    now = time

    try:

        # Image Search, download and upload

        def image_search(image_title, featured):
            params = {
                "q": image_title,
                "tbm": "isch",
                "ijn": "0",
                "tbs": "isz:l&sa=X&ved=0CAIQpwVqFwoTCMi7icmOxPsCFQAAAAAdAAAAABAC&biw=1083&bih=700",
                "api_key": serpapi_key
            }

            search = GoogleSearch(params)
            results = search.get_dict()
            images_results = results["images_results"]
            all_images_urls = []
            for i in range(0, len(images_results)):
                try:
                    all_images_urls.append(images_results[i]['original'])
                except:
                    continue

            if featured == "Yes":
                for image in all_images_urls:
                    try:
                        if "ytimg.com" in image and image not in post_images:
                            try:
                                title_image_url = image
                                post_images.append(title_image_url)

                                img_res = title_image_url.split(".")[len(title_image_url.split(".")) - 1]
                                image_name = image_title.lower().replace(" ", "-")
                                response = requests.get(title_image_url)
                                image_slug = f"images/{image_name}.{img_res}"
                                file = open(image_slug, "wb")
                                file.write(response.content)
                                file.close()

                                post_images.append(title_image_url)

                                media = {
                                    'file': open(image_slug, 'rb'),
                                }

                                image = requests.post(url + '/media', headers=headers, files=media)

                                imageDATA = {'id': str(json.loads(image.content)['id']),
                                             'url': str(json.loads(image.content)['guid']['rendered'])}

                                return imageDATA

                            except:
                                continue
                        else:
                            title_image_url = image
                            post_images.append(title_image_url)

                            img_res = title_image_url.split(".")[len(title_image_url.split(".")) - 1]
                            image_name = image_title.lower().replace(" ", "-")
                            response = requests.get(title_image_url)
                            image_slug = f"images/{image_name}.{img_res}"
                            file = open(image_slug, "wb")
                            file.write(response.content)
                            file.close()

                            post_images.append(title_image_url)

                            media = {
                                'file': open(image_slug, 'rb'),
                            }

                            image = requests.post(url + '/media', headers=headers, files=media)

                            imageDATA = {'id': str(json.loads(image.content)['id']),
                                         'url': str(json.loads(image.content)['guid']['rendered'])}

                            return imageDATA
                    except:
                        continue

            else:
                for image in all_images_urls:
                    try:
                        if "ytimg.com" not in image and "wikihow.com" not in image and "tipsbulletin.com" not in image and image not in post_images and image.split(".")[len(image.split(".")) - 1] in ['jpg', 'jpeg', 'webp', 'png', 'gif', 'tiff']:
                            title_image_url = image
                            post_images.append(title_image_url)

                            img_res = title_image_url.split(".")[len(title_image_url.split(".")) - 1]
                            image_name = image_title.lower().replace(" ", "-")
                            response = requests.get(title_image_url)
                            image_slug = f"images/{image_name}.{img_res}"
                            file = open(image_slug, "wb")
                            file.write(response.content)
                            file.close()

                            post_images.append(title_image_url)

                            media = {
                                'file': open(image_slug, 'rb'),
                            }

                            image = requests.post(url + '/media', headers=headers, files=media)

                            imageDATA = {'id': str(json.loads(image.content)['id']),
                                         'url': str(json.loads(image.content)['guid']['rendered'])}

                            return imageDATA
                        else:
                            continue
                    except:
                        continue


        def youtube_search(keyword):
            params = {
                "engine": "youtube",
                "search_query": keyword,
                "api_key": serpapi_key
            }

            search = GoogleSearch(params)
            results = search.get_dict()

            return results['video_results'][0]['link']

        user = username
        password = app_password
        url = 'https://' + domain + '/wp-json/wp/v2'

        wp_connection = user + ':' + password
        token = base64.b64encode(wp_connection.encode())

        headers = {'Authorization': 'Basic ' + token.decode('utf-8')}

        file = open(path_with_generated_files + filename, "r")
        soup = BeautifulSoup(file, 'html.parser')

        post_title = soup.find_all('h1')[0].get_text().title()
        post_seo_title = soup.find_all('title')[0].get_text().title()

        all_h2 = []
        for i in range(0, len(soup.find_all('h2'))):
            all_h2.append(soup.find_all('h2')[i].get_text().title())

        h2_images = []
        for h2 in all_h2:
            h2_url = image_search(h2, "No")['url']
            h2_images.append([h2, h2_url])

        all_h3 = []
        for i in range(0, len(soup.find_all('h3'))):
            all_h3.append(soup.find_all('h3')[i].get_text().title())

        if all_h3 != []:
            youtube_url = youtube_search(all_h3[-1])
        else:
            youtube_url = None

        soup.h1.extract()
        soup.title.extract()
        description = str(soup.meta.extract())
        description = description[15:].split('" name="description"/>')[0]

        post_body = str(soup)
        post_body = re.sub("\n\n\n","",post_body)


        # Поиск картинки для Featured Image
        featured_image = post_title.split(": ")[0]
        featured_image_data = image_search(featured_image, "Yes")

        # Вставка картинок

        html_new = []
        for line in post_body.split("\n"):
            if "</h2>" in line:
                html_new.append(line)

                h2_headline = re.sub('<h2>', '', line)
                h2_headline = re.sub('</h2>', '', h2_headline)

                image_url = ""
                for h2_title_image in h2_images:
                    if h2_headline.title() == h2_title_image[0]:
                        image_url = h2_title_image[1]
                    else:
                        image_url = ""

                    if image_url != "":
                        image_html = '<img class="aligncenter size-large image-in-content" src="' + image_url + '" alt="' + h2_title_image[0] + '" />'
                        html_new.append(image_html)
                    else:
                        image_html = ""
            else:
                html_new.append(line)

        post_body = "\n".join(html_new)


        # Вставка видео

        if youtube_url != None:
            html_new = []
            for line in post_body.split("\n"):
                if line.lower() == "<h3>" + all_h3[-1].lower() + "</h3>":
                    html_new.append(line)
                    html_new.append('<div class="mycontainer"><iframe src="//www.youtube.com/embed/' + re.sub('.*\?v=', '', youtube_url) + '" frameborder="0" allowfullscreen class="myvideo"></iframe></div>')
                else:
                    html_new.append(line)

            post_body = "\n".join(html_new)

        if publish_period == 'future':
            post = {'title': post_title,
                    'date_gmt': time_string,
                    'status': publish_period,
                    'content': post_body,
                    'featured_media': featured_image_data['id'],
                    'author': author_id,
                    'format': 'standard',
                    'slug': filename.split(".")[0],
                    'categories': article[3],
                    'acf': {'seo_title': post_seo_title,
                            'seo_description': description,
                            'internal_linking_keywords': article[1]}
                    }
        else:
            post = {'title': post_title,
                    'status': publish_period,
                    'content': post_body,
                    'featured_media': featured_image_data['id'],
                    'author': author_id,
                    'format': 'standard',
                    'slug': filename.split(".")[0],
                    'categories': article[3],
                    'acf': {'seo_title': post_seo_title,
                            'seo_description': description,
                            'internal_linking_keywords': article[1]}
                    }

        wp_request = requests.post(url + '/posts', headers=headers, json=post)

        published_aticles.append(filename)

        print(str(count_posts) + ".", 'Статья', filename, 'опубликована' )

        count_posts += 1

    except Exception as e:
        print("Ошибка:", e)
        unpublished_aricles.append(filename)
        continue

print('Опубликованные статьи:')
print(*published_aticles, sep="\n")
print()
print('Неопубликованные статьи:')
print(*unpublished_aricles, sep="\n")
