import openai
from slugify import slugify
import base64
import requests
from bs4 import BeautifulSoup
import json
from serpapi import GoogleSearch
import re
from datetime import datetime
from datetime import timedelta
import random
import gspread
from urllib.parse import urlparse
import time as tm


####### Вводные данные #####################

### !!! Создайте папку "images" в папке, откуда запускаете этот скрипт !!! ###
### !!! Не забудь снять галочку запрета индексирования сайта !!! ###

spreadsheet_id = "xxxxxxxxxxx"  # id рабочего докса проекта

clusters_keywords_sheet = "clean_clusters"  # название рабочего листа c кластерами и ключами
'''Образец таблицы:
Cluster	| Keyword
how tall are horses	| how tall are horses
how tall are horses	| how to measure a horse
how tall are horses	| how many inches in a hand horse measurement
how tall are horses	| how tall is a 16 hand horse
how much does a horse cost	| how much does a horse cost
how much does a horse cost	| how much is a horse
how much does a horse cost	| how much does a horse cost per year
'''

articles_sheet = "articles"  # название листа с данными статей для публикации (кластеры должны совпадать 1 к 1)
'''Образец таблицы:
Cluster | Categories | Internal Linking
how tall are horses | Measurements | tall horses, tall {-3} horses
how much does a horse cost | Cost |	horse cost, horse {-3} cost
'''

openai_api_key = "xxxxxxxx"  # ключ OpenAI
serpapi_key = "xxxxxxxx"  # ключ serpapi

domain = "xxxxxxxxx.com"  # хост
blog_theme = "xxxxx"  # тематика блога

row_start = 2  # Номер строки, с которой нужно начать обрабатывать файл со статьями (1 - заголовок!)
row_end = 3 # Номер строки, которой следует закончить обработку файла со статьями (включая)

publish_now = 50  # Сколько опубликовать сразу (остальное - в отложенный постинг)

tla_sheet = "xxxxxx"  # ID докса TLA
######################################################################################

sleep_seconds = 3

gc = gspread.service_account(filename="creds-google-sheets.json")

sh = gc.open_by_key(spreadsheet_id)
clusters_keywords_sheet = sh.worksheet(clusters_keywords_sheet)
articles_sheet = sh.worksheet(articles_sheet)

clusters_categories_linking = articles_sheet.get_all_values()
del clusters_categories_linking[0]

cluster_keywords = clusters_keywords_sheet.get_all_values()
del cluster_keywords[0]

clusters = articles_sheet.col_values(1)
del clusters[0]

tokens = 0

######### Функции ##############

def get_attractive_headline(cluster, keywords):
  '''запит для отримання заголовку h1/title'''

  order = f"""Write an attractive headline for the article about  "{cluster}" in context of "{blog_theme}". Use \"{cluster}\" keyword first."""
  prompt = order
  openai.api_key = openai_api_key #openAI key

  try:
      response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0.7,
        max_tokens=1000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
      )

  except:
      tm.sleep(sleep_seconds * 2)
      response = openai.Completion.create(
          model="text-davinci-003",
          prompt=prompt,
          temperature=0.7,
          max_tokens=1000,
          top_p=1,
          frequency_penalty=0,
          presence_penalty=0
      )

  global tokens
  tokens += response["usage"]["total_tokens"]
  print("headline:", response['choices'][0]['text'].split('\n'))
  return response['choices'][0]['text'].split('\n')


def get_attractive_description(cluster, keywords):
  '''запит для отримання description'''

  order = f"""\n\nWrite an attractive SEO description for the article about  "{cluster}" in context of "{blog_theme}". Not more than 155 characters."""
  prompt = keywords+order
  openai.api_key = openai_api_key #openAI key

  try:
      response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0.7,
        max_tokens=1000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
      )

  except:
      tm.sleep(sleep_seconds * 2)
      response = openai.Completion.create(
          model="text-davinci-003",
          prompt=prompt,
          temperature=0.7,
          max_tokens=1000,
          top_p=1,
          frequency_penalty=0,
          presence_penalty=0
      )

  global tokens
  tokens += response["usage"]["total_tokens"]
  print("description:", response['choices'][0]['text'].split('\n'))
  return response['choices'][0]['text'].split('\n')

def get_structure(cluster, keywords):
  '''запит для отримання структури'''

  order = f"""\n\nMake a heading hierarchical (use only numbered list, not letters) content structure for an article about "{cluster}" in context of "{blog_theme}", without Heading and FAQs, only structure, at least 10 points. Include Conclusion and References."""
  prompt = keywords+order
  openai.api_key = openai.api_key  #openAI key


  try:
      response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0.7,
        max_tokens=1000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
      )

  except:
      tm.sleep(sleep_seconds * 2)
      response = openai.Completion.create(
          model="text-davinci-003",
          prompt=prompt,
          temperature=0.7,
          max_tokens=1000,
          top_p=1,
          frequency_penalty=0,
          presence_penalty=0
      )
  global tokens
  tokens += response["usage"]["total_tokens"]
  print("structure:", response['choices'][0]['text'].split('\n'))
  return response['choices'][0]['text'].split('\n')

def get_faqs(keywords, title):
  '''запит для отримання списку FAQs'''

  order = f"""\n\nAdd 5 FAQs for article "{title}" in context of "{blog_theme}" using the unique phrases above, no answers, only questions."""
  prompt = keywords+order
  openai.api_key = openai.api_key  #openAI key

  try:
      response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0.7,
        max_tokens=1000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
      )

  except:
      tm.sleep(sleep_seconds * 2)
      response = openai.Completion.create(
          model="text-davinci-003",
          prompt=prompt,
          temperature=0.7,
          max_tokens=1000,
          top_p=1,
          frequency_penalty=0,
          presence_penalty=0
      )

  global tokens
  tokens += response["usage"]["total_tokens"]
  print("faqs:", response['choices'][0]['text'].split('\n'))
  return response['choices'][0]['text'].split('\n')

def write_hierarchical_text(cluster, about):
  '''запит для отримання частини ієрархичного тексту'''

  order = f"""Write text with html h2 and h3 headers as a part of article "{cluster}" (don't use "{cluster}" title as a header) in next structure:
{about}"""
  prompt = order
  openai.api_key = openai.api_key  #openAI key

  try:
      response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0.7,
        max_tokens=3800,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
      )
  except:
      tm.sleep(sleep_seconds * 2)
      response = openai.Completion.create(
          model="text-davinci-003",
          prompt=prompt,
          temperature=0.7,
          max_tokens=3800,
          top_p=1,
          frequency_penalty=0,
          presence_penalty=0
      )

  global tokens
  tokens += response["usage"]["total_tokens"]
  print("text hier:", response['choices'][0]['text'].split('\n'))
  return response['choices'][0]['text'].split('\n')

def write_simple_text_with_header_and_table(cluster, about):
  '''запит для отримання частини звичайного тексту'''

  order = f"""Write in detail "{about}" as a part of an article "{cluster}" (don't use "{cluster}" title as a header). Use "{about}" as h2 html header. \
If possible, use html table."""
  prompt = order
  openai.api_key = openai.api_key  #openAI key

  try:
      response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0.7,
        max_tokens=4000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
      )
  except:
      tm.sleep(sleep_seconds * 2)
      response = openai.Completion.create(
          model="text-davinci-003",
          prompt=prompt,
          temperature=0.7,
          max_tokens=4000,
          top_p=1,
          frequency_penalty=0,
          presence_penalty=0
      )

  global tokens
  tokens += response["usage"]["total_tokens"]
  print("text with header and table:", response['choices'][0]['text'].split('\n'))
  return response['choices'][0]['text'].split('\n')

def write_simple_text_with_header_and_list(cluster, about):
  '''запит для отримання частини звичайного тексту'''

  order = f"""Write in detail "{about}" as a part of an article "{cluster}" (don't use "{cluster}" title as a header). Use "{about}" as h2 html header. \
If possible, use html ul or ol list."""
  prompt = order
  openai.api_key = openai.api_key  #openAI key

  try:
      response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0.7,
        max_tokens=4000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
      )

  except:
      tm.sleep(sleep_seconds * 2)
      response = openai.Completion.create(
          model="text-davinci-003",
          prompt=prompt,
          temperature=0.7,
          max_tokens=4000,
          top_p=1,
          frequency_penalty=0,
          presence_penalty=0
      )

  global tokens
  tokens += response["usage"]["total_tokens"]
  print("text with header and list:", response['choices'][0]['text'].split('\n'))
  return response['choices'][0]['text'].split('\n')

def write_intro(title, about):
  '''запит для отримання вступу'''

  order = f"""Write short "{about}" as a part of an article "{title}"."""
  prompt = order
  openai.api_key = openai.api_key  #openAI key

  try:
      response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0.7,
        max_tokens=4000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
      )
  except:
      tm.sleep(sleep_seconds * 2)
      response = openai.Completion.create(
          model="text-davinci-003",
          prompt=prompt,
          temperature=0.7,
          max_tokens=4000,
          top_p=1,
          frequency_penalty=0,
          presence_penalty=0
      )

  global tokens
  tokens += response["usage"]["total_tokens"]
  print("intro:", response['choices'][0]['text'].split('\n'))
  return response['choices'][0]['text'].split('\n')

def write_text_without_bullets_and_tables(cluster, about):
  '''запит для отримання вступу'''

  order = f"""Write in detail "{about}" as a part of an article "{cluster}". Use "{about}" as h2 html header."""
  prompt = order
  openai.api_key = openai.api_key  #openAI key

  try:
      response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0.7,
        max_tokens=4000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
      )
  except:
      tm.sleep(sleep_seconds * 2)
      response = openai.Completion.create(
          model="text-davinci-003",
          prompt=prompt,
          temperature=0.7,
          max_tokens=4000,
          top_p=1,
          frequency_penalty=0,
          presence_penalty=0
      )

  global tokens
  tokens += response["usage"]["total_tokens"]
  print("text without bullets or tables:", response['choices'][0]['text'].split('\n'))
  return response['choices'][0]['text'].split('\n')


def write_text_faq_answer(cluster, about):
  '''запит для отримання вступу'''

  order = f"""Write in detail "{about}" as a part of an article "{cluster}". Use "{about}" as h3 html header. If possible, use html ul or ol list."""
  prompt = order
  openai.api_key = openai.api_key  #openAI key

  try:
      response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0.7,
        max_tokens=4000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
      )
  except:
      tm.sleep(sleep_seconds * 2)
      response = openai.Completion.create(
          model="text-davinci-003",
          prompt=prompt,
          temperature=0.7,
          max_tokens=4000,
          top_p=1,
          frequency_penalty=0,
          presence_penalty=0
      )

  global tokens
  tokens += response["usage"]["total_tokens"]
  print("text faq answer:", response['choices'][0]['text'].split('\n'))
  return response['choices'][0]['text'].split('\n')

def structure_remake(structure):
    structure_strip = []

    for part in structure:
        structure_strip.append(part.strip())

    new_structure = []
    for i in range(0, len(structure_strip)):
        if 0 < i < 10:
            if structure_strip[i][0] == new_structure[-1][0]:
                temp = new_structure[-1]
                del new_structure[-1]
                new_structure.append(temp + " \n " + structure_strip[i])
            else:
                new_structure.append(structure_strip[i])
        else:
            new_structure.append(structure_strip[i])

    clean_structure = []

    for struct in new_structure:
        clean_structure.append(struct[2:].strip())

    final_structure = []

    print("clean_structure:", clean_structure)
    for st in clean_structure:
        if st[:2] == ". ":
            st = st.replace(". ", "")
        elif "\n 2." in st:
            st = st.replace("\n 2.", "\n ")
        elif "\n 3." in st:
            st = st.replace("\n 3.", "\n ")
        elif "\n 4." in st:
            st = st.replace("\n 4.", "\n ")
        elif "\n 5." in st:
            st = st.replace("\n 5.", "\n ")
        elif "\n 6." in st:
            st = st.replace("\n 6.", "\n ")
        elif "\n 7." in st:
            st = st.replace("\n 7.", "\n ")
        elif "\n 8." in st:
            st = st.replace("\n 8.", "\n ")
        elif "\n 9." in st:
            st = st.replace("\n 9.", "\n ")
        elif "\n 10." in st:
            st = st.replace("\n 10.", "\n ")

        final_structure.append(st)

    print("structure remake:", final_structure)
    return final_structure

def html_clean(html):
    html_new = []
    for code in html:
        html_new.append("\n".join(code))
    html_clean = "\n".join(html_new)
    return html_clean

def extract_domain(link):
  parsed_link = urlparse(link)
  domain = parsed_link.netloc
  return f'{parsed_link.scheme}://{domain}/'

def extract_and_replace_links(html):
  # Parse the HTML using BeautifulSoup
  soup = BeautifulSoup(html, 'html.parser')
  # Find all link elements
  links = soup.find_all('a')
  # Replace the href attribute of each link element with its domain
  for link in links:
      href = link['href']
      domain = extract_domain(href)
      link['href'] = domain
      # Get the modified HTML as a string
  modified_html = str(soup)
  return modified_html




row = 1
posts_count = 0

published_aticles = []
unpublished_aricles = []

now = datetime.utcnow()  # Текущее время UTC

print("Время запуска скрипта:", datetime.now())
print()

for cluster in clusters:

    row += 1
    tokens = 0

    if row_start <= row <= row_end:

        posts_count += 1

        articles_sheet.format('A' + str(row-1), {
            "backgroundColor": {
                "red": 1.0,
                "green": 1.0,
                "blue": 1.0
            }
        })

        articles_sheet.format('A' + str(row), {
            "backgroundColor": {
                "red": 0.0,
                "green": 1.0,
                "blue": 0.0
            }
        })

        if posts_count <= publish_now:
            publish_period = 'publish'
        else:
            publish_period = 'future'

        print(str(posts_count) + ".", "Статья", '"' + cluster + '"', "взята в обработку, строка " + str(row))
        keywords = []
        for cluster_keyword in cluster_keywords:
            if cluster == cluster_keyword[0]:
                keywords.append(cluster_keyword[1])

        slug = slugify(cluster)
        if len(slug) <= 5:
            slug = slug + "-" + blog_theme

        # Генерация текста

        try:
            try:
                print("   - Старт генерации")
                try:
                    title = get_attractive_headline(cluster, '\\n'.join(keywords))[2].replace('"','')
                    tm.sleep(sleep_seconds)
                except:
                    title = get_attractive_headline(cluster, '\\n'.join(keywords))[2].replace('"', '')
                    tm.sleep(sleep_seconds)
                try:
                    h1 = get_attractive_headline(cluster, '\\n'.join(keywords))[2].replace('"','')
                    tm.sleep(sleep_seconds)
                except:
                    h1 = get_attractive_headline(cluster, '\\n'.join(keywords))[2].replace('"', '')
                    tm.sleep(sleep_seconds)
                try:
                    description = get_attractive_description(cluster, '\\n'.join(keywords))[2]
                    tm.sleep(sleep_seconds)
                except:
                    description = get_attractive_description(cluster, '\\n'.join(keywords))[2]
                    tm.sleep(sleep_seconds)
                try:
                    structure = get_structure(cluster, '\\n'.join(keywords))[2:]
                    tm.sleep(sleep_seconds)
                except:
                    structure = get_structure(cluster, '\\n'.join(keywords))[2:]
                    tm.sleep(sleep_seconds)
                try:
                    faqs = get_faqs('\\n'.join(keywords), title)[2:]
                    tm.sleep(sleep_seconds)
                except:
                    faqs = get_faqs('\\n'.join(keywords), title)[2:]
                    tm.sleep(sleep_seconds)
                structure = structure_remake(structure)
            except Exception as e:
                print("Возникла следующая ошибка:", e)
                print("    - Ошибка генерации")
                articles_sheet.update_cell(row, 4, 'Error')
                articles_sheet.update_cell(row, 8, 'No')
                continue

            html = []
            references = structure[-1]
            conclusion = structure[-2]
            del structure[-1]
            del structure[-1]
            for ct in range(0, len(structure)):
                if ct == 0:
                    text = write_intro(title, structure[ct])
                    tm.sleep(sleep_seconds)
                    html.append(text)
                elif "\n" in structure[ct]:
                    text = write_hierarchical_text(cluster, structure[ct])
                    tm.sleep(sleep_seconds)
                    html.append(text)
                # elif structure[ct] == "Conclusion":
                #     text = write_text_without_bullets_and_tables(cluster, structure[ct])
                #     html.append(text)
                #     print(structure[ct], "Gen")
                # elif structure[ct] == "References":
                #     text = write_simple_text_with_header_and_list(cluster, structure[ct])
                #     html.append(text)
                #     print(structure[ct], "Gen")
                else:
                    choice_text_method = random.randint(1,3)
                    if choice_text_method == 1:
                        text = write_simple_text_with_header_and_table(cluster, structure[ct])
                        tm.sleep(sleep_seconds)
                    elif choice_text_method == 2:
                        text = write_simple_text_with_header_and_list(cluster, structure[ct])
                        tm.sleep(sleep_seconds)
                    elif choice_text_method == 3:
                        text = write_text_without_bullets_and_tables(cluster, structure[ct])
                        tm.sleep(sleep_seconds)
                    html.append(text)

            html = html_clean(html)
            html_temp = []
            html_temp.append(html)
            html_temp.append("<h2>Frequently Asked Questions</h2>")
            html = "\n".join(html_temp)

            html_temp = []
            html_temp.append(html)

            for faq in faqs:
                try:
                    text = write_text_faq_answer(cluster, faq)
                    tm.sleep(sleep_seconds)
                except:
                    text = write_text_faq_answer(cluster, faq)
                    tm.sleep(sleep_seconds)
                html_temp.append("\n".join(text))

            conclusion = write_text_without_bullets_and_tables(title, "Conclusion")
            tm.sleep(sleep_seconds)

            references = write_simple_text_with_header_and_list(title, "References")
            tm.sleep(sleep_seconds)
            references = extract_and_replace_links("\n".join(references))

            html_temp.append("\n".join(conclusion))
            html_temp.append(references)

            html = "\n".join(html_temp)

            soup = BeautifulSoup(html, "html.parser")
            words_in_text = len(soup.text.split())

            print("    - Сгенерировано,", words_in_text, "слов")

            price = tokens / 1000 * 0.02

            articles_sheet.update_cell(row, 4, 'OK')
            articles_sheet.update_cell(row, 5, words_in_text)
            articles_sheet.update_cell(row, 6, tokens)
            articles_sheet.update_cell(row, 7, price)

        except Exception as e:
            print("Возникла следующая ошибка:", e)
            print("    - Ошибка генерации")
            articles_sheet.update_cell(row, 4, 'Error')
            articles_sheet.update_cell(row, 8, 'No')
            continue


        # Постинг

        sht = gc.open_by_key(tla_sheet)
        worksheet = sht.worksheet("credits")

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

        cat_ids = []
        for i in range(0, len(articles_sheet.cell(row, 2).value.split(', '))):
            cat_ids.append(categories_ids[articles_sheet.cell(row, 2).value.split(', ')[i]])

        internal_linking = articles_sheet.cell(row, 3).value

        post_images = []

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
                    except Exception as e:
                        print("Возникла следующая ошибка:", e)
                        continue

                if featured == "Yes":
                    for image in all_images_urls:
                        try:
                            if "ytimg.com" in image and image not in post_images:
                                try:
                                    title_image_url = image
                                    post_images.append(title_image_url)

                                    img_res = title_image_url.split(".")[len(title_image_url.split(".")) - 1]
                                    image_name = slugify(image_title + "-" + str(row))
                                    response = requests.get(title_image_url, verify=True, timeout=5)

                                    if response.status_code == 200:
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

                                except Exception as e:
                                    print("Возникла следующая ошибка:", e)
                                    continue
                            else:
                                title_image_url = image
                                post_images.append(title_image_url)

                                img_res = title_image_url.split(".")[len(title_image_url.split(".")) - 1]
                                image_name = slugify(image_title.rsplit(blog_theme, 1)[0] + str(row))
                                response = requests.get(title_image_url, verify=True, timeout=5)

                                if response.status_code == 200:

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
                        except Exception as e:
                            print("Возникла следующая ошибка:", e)
                            continue

                else:
                    for image in all_images_urls:

                        try:
                            if "ytimg.com" not in image and "wikihow.com" not in image and "tipsbulletin.com" not in image and image not in post_images and \
                                    image.split(".")[len(image.split(".")) - 1] in ['jpg', 'jpeg', 'webp', 'png',
                                                                                    'gif', 'tiff']:
                                title_image_url = image
                                post_images.append(title_image_url)
                                img_res = title_image_url.split(".")[len(title_image_url.split(".")) - 1]
                                image_name = slugify(image_title.rsplit(blog_theme, 1)[0] + str(row))
                                response = requests.get(title_image_url, verify=True, timeout=5)

                                if response.status_code == 200:

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
                            else:
                                continue
                        except Exception as e:
                            print("Возникла следующая ошибка:", e)
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

            post_title = h1
            post_seo_title = title

            all_h2 = []
            for i in range(0, len(soup.find_all('h2'))-3):
                all_h2.append(soup.find_all('h2')[i].get_text().title())
            h2_for_youtube = all_h2.pop(-1)

            h2_images = []
            for h2 in all_h2:
                h2_url = image_search(h2 + " " + blog_theme, "No")['url']
                h2_images.append([h2, h2_url])

            youtube_url = youtube_search(h2_for_youtube + " " + blog_theme)

            post_body = html

            # Поиск картинки для Featured Image
            featured_image = cluster
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
                            image_html = '<img class="aligncenter size-large image-in-content" src="' + image_url + '" alt="' + \
                                         h2_title_image[0] + '" />'
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
                    if line.lower() == "<h2>" + h2_for_youtube.lower() + "</h2>":
                        html_new.append(line)
                        html_new.append(
                            '<div class="mycontainer"><iframe src="https://www.youtube.com/embed/' + re.sub('.*\?v=', '',
                                                                                                      youtube_url) + '" frameborder="0" allowfullscreen class="myvideo"></iframe></div>')

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
                        'slug': slug,
                        'categories': cat_ids,
                        'acf': {'seo_title': post_seo_title,
                                'seo_description': description,
                                'internal_linking_keywords': internal_linking}
                        }
            else:
                post = {'title': post_title,
                        'status': publish_period,
                        'content': post_body,
                        'featured_media': featured_image_data['id'],
                        'author': author_id,
                        'format': 'standard',
                        'slug': slug,
                        'categories': cat_ids,
                        'acf': {'seo_title': post_seo_title,
                                'seo_description': description,
                                'internal_linking_keywords': internal_linking}
                        }

            wp_request = requests.post(url + '/posts', headers=headers, json=post)

            published_aticles.append(cluster)

            print(f"    - Опубликовано: https://{domain}/{slug}/")

            articles_sheet.format('A' + str(row), {
                "backgroundColor": {
                    "red": 1.0,
                    "green": 1.0,
                    "blue": 1.0
                }
            })

            articles_sheet.update_cell(row, 8, 'OK')
            if publish_period == 'future':
                articles_sheet.update_cell(row, 9, time_string[:10])
            else:
                articles_sheet.update_cell(row, 9, str(datetime.utcnow().date()))

            articles_sheet.update_cell(row, 10, f'https://{domain}/{slug}/')
            articles_sheet.update_cell(row, 11, title)
            articles_sheet.update_cell(row, 12, description)
            articles_sheet.update_cell(row, 13, h1)
            articles_sheet.update_cell(row, 14, slug)

        except Exception as e:
            print("Ошибка:", e)
            articles_sheet.update_cell(row, 8, 'Error')
            unpublished_aricles.append(cluster)
            continue


    else:
        continue


print()
print('Опубликованные статьи:')
print(*published_aticles, sep="\n")
print()
print('Неопубликованные статьи:')
print(*unpublished_aricles, sep="\n")

print("Done")
