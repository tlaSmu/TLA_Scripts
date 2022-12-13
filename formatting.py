from bs4 import BeautifulSoup
import random
from random import choice
import re
import csv


########## Вводные данные ################################

# Путь к сгенерированным статьям
files_path = "glue_new_html_files/"

# Путь к папке для файлов после обработки
processed_files_path = "glue_new_html_files_layout/"

# Классы CSS
ol_div_class = ' class="ol-div-class"' # класс <div> нумерованного списка
ul_div_class = ' class="ul-div-class"' # класс <div> маркированного списка

# Внешние ссылки
link_1 = ['your hands',r'<a href="https://www.cdc.gov/handwashing/faqs.html" target="_blank">your hands</a>']
link_2 = ['cyanoacrylate',r'<a href="https://en.wikipedia.org/wiki/Cyanoacrylate" target="_blank">cyanoacrylate</a>']
link_3 = ['close wounds',r'<a href="https://pubmed.ncbi.nlm.nih.gov/8218722/" target="_blank">close wounds</a>']
link_4 = ['wound',r'<a href="https://pubmed.ncbi.nlm.nih.gov/8218722/" target="_blank">wound</a>']
link_5 = ['putty knife',r'<a href="https://en.wikipedia.org/wiki/Putty_knife" target="_blank">putty knife</a>']
link_6 = ['what adhesive to use',r'<a href="https://d-lab.mit.edu/sites/default/files/inline-files/D-Lab_Learn-It_Adhesives_Jul13.pdf" target="_blank">what adhesive to use</a>']
link_7 = ['types of glues',r'<a href="https://www.gvsu.edu/arttech/glue-and-adhesives-12.htm" target="_blank">types of glues</a>']
link_8 = ['types of adhesives',r'<a href="https://www.gvsu.edu/arttech/glue-and-adhesives-12.htm" target="_blank">types of adhesives</a>']
link_9 = ['methylene chloride',r'<a href="https://pubchem.ncbi.nlm.nih.gov/compound/Dichloromethane" target="_blank">methylene chloride</a>']

#################################################################################################



# Функция замены n-ого элемента в string
def replacenth(string, sub, wanted, n):
    pattern = re.compile(sub)
    where = [m for m in pattern.finditer(string)][n-1]
    before = string[:where.start()]
    after = string[where.end():]
    newString = before + wanted + after

    return newString

# Чтение файлов

filenames_categories = []
categories_list = {}
generated_files = []

with open("slug, category, linking.csv", newline='') as csvfile:
    data = csv.reader(csvfile)
    for row in data:
        filenames_categories.append([row[1], row[8]])

# filename = ["how-to-remove-alteco-glue.html.html", 'Glue']
# for i in range(0,1):
for filename in filenames_categories:
    try:
        file = open(files_path + filename[0], "r")

        categories_list.update({filename[0]: filename[1]})

        # Создание BS
        soup = BeautifulSoup (file, 'html.parser')

        # Название статьи
        title = soup.find_all('h1')[0].get_text().title()

        # Генерация тэглайнов "how to" и остальных видов статей
        if title[:3] == "How":
            titles_taglines = ["Most Comprehensive Guide",
                               "Detailed Guide",
                               "Helpful Guide",
                               "Helpful Recommendations",
                               "Step-by-Step Guide",
                               "Simple & Effective Methods",
                               "Most Effective Methods",
                               "Proven Methods",
                               "Effective Solutions",
                               "Effective Methods",
                               "Tips from an Expert",
                               "Most Effective Ways",
                               "Most Complete Guide",
                               "Best Ideas for Everyone",
                               "A Complete, Foolproof Guide",
                               "Methods That Work"]

            title_tagline_number = random.randint(0,len(titles_taglines)-1)
            title_tagline = titles_taglines[title_tagline_number]

            h1_tagline_number = choice([i for i in range(0,len(titles_taglines)-1) if i not in [title_tagline_number]])
            h1_tagline = titles_taglines[h1_tagline_number]

        else:
            titles_taglines = ["All You Need To Know",
                               "All Facts You Need To Know",
                               "Detailed Information",
                               "Everything You Wanted to Know"]

            title_tagline_number = random.randint(0, len(titles_taglines) - 1)
            title_tagline = titles_taglines[title_tagline_number]

            h1_tagline_number = choice([i for i in range(0, len(titles_taglines) - 1) if i not in [title_tagline_number]])
            h1_tagline = titles_taglines[h1_tagline_number]

        title_with_tagline = title + ": " + title_tagline
        h1_with_tagline = title + ": " + h1_tagline

        # Исключение h1 и первого h2
        soup.h1.extract()
        soup.h2.extract()

        html = soup.prettify()

        # Преобразование html в привычный формат
        html = re.sub(r'\?\n</h2>', '?</h3>', html)
        html = re.sub(r'<h2>\n ', '<h2>', html)
        html = re.sub(r'\n</h2>', '</h2>', html)
        html = re.sub(r'\n</h2>', '</h2>', html)
        html = re.sub(r'\n</p>', '</p>', html)
        html = re.sub(r'<p>\n ', '<p>', html)

        try:
            description = html.split("\n")[0]
            description = re.sub("<p>", "", description)
            description = re.sub("</p>", "", description)
            description = [description.split(". ")[0], description.split(". ")[1]]
            description = ". ".join(description) + "."
            description = re.sub('\.\.', '.', description)
        except:
            continue


        # Замена <h2> на <h3> в заголовках с вопросом
        html_new = []
        for line in html.split("\n"):
            if "</h3>" in line:
                line = re.sub(r'<h2>', '<h3>', line)
                html_new.append(line)
            else:
                html_new.append(line)

        html = "\n".join(html_new)

        # Замена одинаковых приложений
        html_new = []
        h3_line = []

        for line in html.split("\n"):
            if "</h3>" in line:
                h3_line = line
                h3_line = re.sub(r'<h3>', '', h3_line)
                h3_line = re.sub(r'</h3>', '', h3_line)
                html_new.append(line)
            else:
                if line[3:len(h3_line)+3] == h3_line:
                    line = re.sub(h3_line + "\? ", '', line)
                    html_new.append(line)
                elif line[3:len(h3_line)+5] == '"' + str(h3_line) + '"':
                    line = line[len(h3_line)+5:]
                    html_new.append(line)
                else:
                    html_new.append(line)

        html = "\n".join(html_new)

        # Формирование списков из first

        html_new = []
        for line in html.split("\n"):
            if "First, " in line and " 1. " not in line and " 2. " not in line and ": -" not in line and line.count(". ") < 7:
                first_quantity = line.count("First, ")
                if first_quantity == 2:
                    line_del = " First, " + line.split("First, ")[2]
                    line = re.sub(line_del, '', line) + "</p>"
                elif first_quantity == 1:
                    ul_list = [line.split(" First, ")[0] + "</p>"]
                    counter_list = 0
                    counter_iterations = 0
                    # for sentence in line.split(". "): re.split(', |_|-|!', data)
                    for sentence in re.split('\. |\?|!', line):
                        if "First," in sentence:
                            ul_list.append("<div" + ul_div_class + "><ul><li>" + sentence + ".</li>")
                            counter_list += 1
                            counter_iterations += 1
                        elif counter_list == 0:
                            continue
                        elif counter_iterations == len(re.split('\. |\?|!', line.split("First, ")[1]))-1:
                            sentence = re.sub(r'</p>', '', sentence)
                            ul_list.append("<li>" + sentence + "</li></ul></div>")
                        else:
                            ul_list.append("<li>" + sentence + ".</li>")
                            counter_iterations += 1

                    html_new.append("\n".join(ul_list))
                else:
                    html_new.append(line)
            else:
                html_new.append(line)

        html = "\n".join(html_new)


        # Формирование списков из One way

        html_new = []
        for line in html.split("\n"):
            try:
                if "One way" in line and " Then, " not in line and " 1. " not in line and " 2. " not in line and ": -" not in line:
                    if " Another" in line:
                        ul_list = [line.split(" One way")[0] + "</p>"]
                        ul_list.append("<div" + ul_div_class + "><ul><li>One way" + line.split(" One way")[1].split(" Another")[0] + "</li>")
                        if " If" not in line.split(" One way")[1].split(" Another")[1]:
                            if " You can also try" not in line.split(" One way")[1].split(" Another")[1]:
                                ul_list.append(re.sub("</p>", "", "<li>Another" + line.split(" One way")[1].split(" Another")[1] + "</li></ul></div>"))
                            else:
                                ul_list.append("<li>Another" + line.split(" One way")[1].split(" Another")[1].split(" You can also try")[0] + "</li>")
                                ul_list.append(
                                    re.sub("</p>", "", "<li>You can also try" + line.split(" One way")[1].split(" Another")[1].split(" You can also try")[1] + "</li></ul></div>"))
                        else:
                            ul_list.append("<li>Another" + line.split(" One way")[1].split(" Another")[1].split(" If")[0] + "</li>")
                            if " You can also try" not in line.split(" One way")[1].split(" Another")[1].split(" If")[1]:
                                ul_list.append(re.sub("</p>", "", "<li>If" + line.split(" One way")[1].split(" Another")[1].split(" If")[1] + "</li></ul></div>"))
                            else:
                                ul_list.append("<li>If" + line.split(" One way")[1].split(" Another")[1].split(" If")[1].split(" You can also try")[0] + "</li>")
                                ul_list.append(re.sub("</p>", "",
                                                      "<li>You can also try" + line.split(" One way")[1].split(" Another")[1].split(" If")[
                                                          1].split(" You can also try")[1] + "</li></ul></div>"))
                        html_new.append("\n".join(ul_list))

                    else:
                        html_new.append(line)


                else:
                    html_new.append(line)

            except:
                html_new.append(line)

        html = "\n".join(html_new)

        # Формирование списков из First way

        html_new = []
        for line in html.split("\n"):
            try:
                if "The first way" in line and len(re.split('\. |\?|!', line)) < 7  and " 1. " not in line and " 2. " not in line and ": -" not in line:
                    ul_list = []
                    counter_list = 0
                    counter_iterations = 0
                    for sentence in re.split('\. |\?|!', line):
                        if sentence[:13] == "The first way":
                            ul_list.append("<div" + ul_div_class + "><ul><li>" + sentence + ".</li>")
                            counter_list += 1
                            counter_iterations += 1
                        elif counter_list == 0:
                            ul_list.append(sentence + ".</p>")
                            counter_iterations += 1
                        elif counter_iterations == len(re.split('\. |\?|!', line))-1:
                            sentence = re.sub(r'</p>', '', sentence)
                            ul_list.append("<li>" + sentence + "</li></ul></div>")
                        else:
                            ul_list.append("<li>" + sentence + ".</li>")
                            counter_iterations += 1

                    html_new.append("\n".join(ul_list))
                else:
                    html_new.append(line)
            except:
                html_new.append(line)
        html = "\n".join(html_new)


        # Формирование списков из -

        html_new = []
        for line in html.split("\n"):
            try:
                if ": -" in line and " 1. " not in line and " 2. " not in line:
                    ul_list = [line.split(": -")[0] + ":</p>", "<div" +ul_div_class + "><ul>", "<li>"]
                    new_line = re.sub(r' -', '</li>\n<li>', line.split(": -")[1])
                    new_line = re.sub(r'</p>', '</li>', new_line)
                    ul_list.append(new_line)
                    ul_list.append("</ul></div>")

                    html_new.append("\n".join(ul_list))
                else:
                    html_new.append(line)
            except:
                html_new.append(line)

        html = "\n".join(html_new)


        # Формирование нумерованных списков

        html_new = []
        for line in html.split("\n"):
            try:
                if " 1. " in line and " 2. " in line:
                    ul_list = []
                    if " 2. " in line and " 3. " not in line:
                        ul_list.append(line.split(" 1.")[0] + "</p>")
                        ul_list.append("<div" + ol_div_class + "><ol><li>" + line.split(" 1. ")[1].split(" 2. ")[0] + "</li>")
                        ul_list.append(re.sub(r'</p>', "", "<li>" + line.split(" 1. ")[1].split(" 2. ")[1] + "</li></ol></div>"))
                    elif " 3. " in line and " 4. " not in line:
                        ul_list.append(line.split(" 1.")[0] + "</p>")
                        ul_list.append("<div" + ol_div_class + "><ol><li>" + line.split(" 1. ")[1].split(" 2. ")[0] + "</li>")
                        ul_list.append("<li>" + line.split(" 1. ")[1].split(" 2. ")[1].split(" 3. ")[0] + "</li>")
                        ul_list.append(re.sub(r'</p>', "", "<li>" + line.split(" 1. ")[1].split(" 2. ")[1].split(" 3. ")[1] + "</li></ol></div>"))
                    elif " 4. " in line and " 5. " not in line:
                        ul_list.append(line.split(" 1.")[0] + "</p>")
                        ul_list.append("<div" + ol_div_class + "><ol><li>" + line.split(" 1. ")[1].split(" 2. ")[0] + "</li>")
                        ul_list.append("<li>" + line.split(" 1. ")[1].split(" 2. ")[1].split(" 3. ")[0] + "</li>")
                        ul_list.append("<li>" + line.split(" 1. ")[1].split(" 2. ")[1].split(" 3. ")[1].split(" 4. ")[0] + "</li>")
                        ul_list.append(re.sub(r'</p>', "", "<li>" + line.split(" 1. ")[1].split(" 2. ")[1].split(" 3. ")[1].split(" 4. ")[1] + "</li></ol></div>"))
                    elif " 5. " in line and " 6. " not in line:
                        ul_list.append(line.split(" 1.")[0] + "</p>")
                        ul_list.append("<div" + ol_div_class + "><ol><li>" + line.split(" 1. ")[1].split(" 2. ")[0] + "</li>")
                        ul_list.append("<li>" + line.split(" 1. ")[1].split(" 2. ")[1].split(" 3. ")[0] + "</li>")
                        ul_list.append("<li>" + line.split(" 1. ")[1].split(" 2. ")[1].split(" 3. ")[1].split(" 4. ")[0] + "</li>")
                        ul_list.append("<li>" + line.split(" 1. ")[1].split(" 2. ")[1].split(" 3. ")[1].split(" 4. ")[1].split(" 5. ")[0] + "</li>")
                        ul_list.append(re.sub(r'</p>', "", "<li>" + line.split(" 1. ")[1].split(" 2. ")[1].split(" 3. ")[1].split(" 4. ")[1].split(" 5. ")[1] + "</li></ol></div>"))
                    elif " 6. " in line and " 7. " not in line:
                        ul_list.append(line.split(" 1.")[0] + "</p>")
                        ul_list.append("<div" + ol_div_class + "><ol><li>" + line.split(" 1. ")[1].split(" 2. ")[0] + "</li>")
                        ul_list.append("<li>" + line.split(" 1. ")[1].split(" 2. ")[1].split(" 3. ")[0] + "</li>")
                        ul_list.append("<li>" + line.split(" 1. ")[1].split(" 2. ")[1].split(" 3. ")[1].split(" 4. ")[0] + "</li>")
                        ul_list.append("<li>" + line.split(" 1. ")[1].split(" 2. ")[1].split(" 3. ")[1].split(" 4. ")[1].split(" 5. ")[0] + "</li>")
                        ul_list.append(
                            "<li>" + line.split(" 1. ")[1].split(" 2. ")[1].split(" 3. ")[1].split(" 4. ")[1].split(" 5. ")[
                                1].split(" 6. ")[0] + "</li>")
                        ul_list.append(re.sub(r'</p>', "", "<li>" + line.split(" 1. ")[1].split(" 2. ")[1].split(" 3. ")[1].split(" 4. ")[1].split(" 5. ")[
                                1].split(" 6. ")[1] + "</li></ol></div>"))
                    elif " 7. " in line and " 8. " not in line:
                        ul_list.append(line.split(" 1.")[0] + "</p>")
                        ul_list.append("<div" + ol_div_class + "><ol><li>" + line.split(" 1. ")[1].split(" 2. ")[0] + "</li>")
                        ul_list.append("<li>" + line.split(" 1. ")[1].split(" 2. ")[1].split(" 3. ")[0] + "</li>")
                        ul_list.append("<li>" + line.split(" 1. ")[1].split(" 2. ")[1].split(" 3. ")[1].split(" 4. ")[0] + "</li>")
                        ul_list.append("<li>" + line.split(" 1. ")[1].split(" 2. ")[1].split(" 3. ")[1].split(" 4. ")[1].split(" 5. ")[0] + "</li>")
                        ul_list.append(
                            "<li>" + line.split(" 1. ")[1].split(" 2. ")[1].split(" 3. ")[1].split(" 4. ")[1].split(" 5. ")[
                                1].split(" 6. ")[0] + "</li>")
                        ul_list.append(
                            "<li>" + line.split(" 1. ")[1].split(" 2. ")[1].split(" 3. ")[1].split(" 4. ")[1].split(" 5. ")[
                                1].split(" 6. ")[1].split(" 7. ")[0] + "</li>")
                        ul_list.append(re.sub(r'</p>', "", "<li>" + line.split(" 1. ")[1].split(" 2. ")[1].split(" 3. ")[1].split(" 4. ")[1].split(" 5. ")[
                                1].split(" 6. ")[1].split(" 7. ")[1] + "</li></ol></div>"))
                    elif " 8. " in line and " 9. " not in line:
                        ul_list.append(line.split(" 1.")[0] + "</p>")
                        ul_list.append("<div" + ol_div_class + "><ol><li>" + line.split(" 1. ")[1].split(" 2. ")[0] + "</li>")
                        ul_list.append("<li>" + line.split(" 1. ")[1].split(" 2. ")[1].split(" 3. ")[0] + "</li>")
                        ul_list.append("<li>" + line.split(" 1. ")[1].split(" 2. ")[1].split(" 3. ")[1].split(" 4. ")[0] + "</li>")
                        ul_list.append("<li>" + line.split(" 1. ")[1].split(" 2. ")[1].split(" 3. ")[1].split(" 4. ")[1].split(" 5. ")[0] + "</li>")
                        ul_list.append(
                            "<li>" + line.split(" 1. ")[1].split(" 2. ")[1].split(" 3. ")[1].split(" 4. ")[1].split(" 5. ")[
                                1].split(" 6. ")[0] + "</li>")
                        ul_list.append(
                            "<li>" + line.split(" 1. ")[1].split(" 2. ")[1].split(" 3. ")[1].split(" 4. ")[1].split(" 5. ")[
                                1].split(" 6. ")[1].split(" 7. ")[0] + "</li>")
                        ul_list.append(
                            "<li>" + line.split(" 1. ")[1].split(" 2. ")[1].split(" 3. ")[1].split(" 4. ")[1].split(" 5. ")[
                                1].split(" 6. ")[1].split(" 7. ")[1].split(" 8. ")[0] + "</li>")
                        ul_list.append(re.sub(r'</p>', "", "<li>" + line.split(" 1. ")[1].split(" 2. ")[1].split(" 3. ")[1].split(" 4. ")[1].split(" 5. ")[
                                1].split(" 6. ")[1].split(" 7. ")[1].split(" 8. ")[1] + "</li></ol></div>"))
                    elif " 9. " in line and " 10. " not in line:
                        ul_list.append(line.split(" 1.")[0] + "</p>")
                        ul_list.append("<div" + ol_div_class + "><ol><li>" + line.split(" 1. ")[1].split(" 2. ")[0] + "</li>")
                        ul_list.append("<li>" + line.split(" 1. ")[1].split(" 2. ")[1].split(" 3. ")[0] + "</li>")
                        ul_list.append("<li>" + line.split(" 1. ")[1].split(" 2. ")[1].split(" 3. ")[1].split(" 4. ")[0] + "</li>")
                        ul_list.append("<li>" + line.split(" 1. ")[1].split(" 2. ")[1].split(" 3. ")[1].split(" 4. ")[1].split(" 5. ")[0] + "</li>")
                        ul_list.append(
                            "<li>" + line.split(" 1. ")[1].split(" 2. ")[1].split(" 3. ")[1].split(" 4. ")[1].split(" 5. ")[
                                1].split(" 6. ")[0] + "</li>")
                        ul_list.append(
                            "<li>" + line.split(" 1. ")[1].split(" 2. ")[1].split(" 3. ")[1].split(" 4. ")[1].split(" 5. ")[
                                1].split(" 6. ")[1].split(" 7. ")[0] + "</li>")
                        ul_list.append(
                            "<li>" + line.split(" 1. ")[1].split(" 2. ")[1].split(" 3. ")[1].split(" 4. ")[1].split(" 5. ")[
                                1].split(" 6. ")[1].split(" 7. ")[1].split(" 8. ")[0] + "</li>")
                        ul_list.append(
                            "<li>" + line.split(" 1. ")[1].split(" 2. ")[1].split(" 3. ")[1].split(" 4. ")[1].split(" 5. ")[
                                1].split(" 6. ")[1].split(" 7. ")[1].split(" 8. ")[1].split(" 9. ")[0] + "</li>")
                        ul_list.append(re.sub(r'</p>', "", "<li>" + line.split(" 1. ")[1].split(" 2. ")[1].split(" 3. ")[1].split(" 4. ")[1].split(" 5. ")[
                                1].split(" 6. ")[1].split(" 7. ")[1].split(" 8. ")[1].split(" 9. ")[1] + "</li></ol></div>"))
                    elif " 10. " in line and " 11. " not in line:
                        ul_list.append(line.split(" 1.")[0] + "</p>")
                        ul_list.append("<div" + ol_div_class + "><ol><li>" + line.split(" 1. ")[1].split(" 2. ")[0] + "</li>")
                        ul_list.append("<li>" + line.split(" 1. ")[1].split(" 2. ")[1].split(" 3. ")[0] + "</li>")
                        ul_list.append("<li>" + line.split(" 1. ")[1].split(" 2. ")[1].split(" 3. ")[1].split(" 4. ")[0] + "</li>")
                        ul_list.append("<li>" + line.split(" 1. ")[1].split(" 2. ")[1].split(" 3. ")[1].split(" 4. ")[1].split(" 5. ")[0] + "</li>")
                        ul_list.append(
                            "<li>" + line.split(" 1. ")[1].split(" 2. ")[1].split(" 3. ")[1].split(" 4. ")[1].split(" 5. ")[
                                1].split(" 6. ")[0] + "</li>")
                        ul_list.append(
                            "<li>" + line.split(" 1. ")[1].split(" 2. ")[1].split(" 3. ")[1].split(" 4. ")[1].split(" 5. ")[
                                1].split(" 6. ")[1].split(" 7. ")[0] + "</li>")
                        ul_list.append(
                            "<li>" + line.split(" 1. ")[1].split(" 2. ")[1].split(" 3. ")[1].split(" 4. ")[1].split(" 5. ")[
                                1].split(" 6. ")[1].split(" 7. ")[1].split(" 8. ")[0] + "</li>")
                        ul_list.append(
                            "<li>" + line.split(" 1. ")[1].split(" 2. ")[1].split(" 3. ")[1].split(" 4. ")[1].split(" 5. ")[
                                1].split(" 6. ")[1].split(" 7. ")[1].split(" 8. ")[1].split(" 9. ")[0] + "</li>")
                        ul_list.append(
                            "<li>" + line.split(" 1. ")[1].split(" 2. ")[1].split(" 3. ")[1].split(" 4. ")[1].split(" 5. ")[
                                1].split(" 6. ")[1].split(" 7. ")[1].split(" 8. ")[1].split(" 9. ")[1].split(" 10. ")[0] + "</li>")
                        ul_list.append(re.sub(r'</p>', "", "<li>" + line.split(" 1. ")[1].split(" 2. ")[1].split(" 3. ")[1].split(" 4. ")[1].split(" 5. ")[
                                1].split(" 6. ")[1].split(" 7. ")[1].split(" 8. ")[1].split(" 9. ")[1].split(" 10. ")[1] + "</li></ol></div>"))

                    else:
                        ul_list.append(line)

                    html_new.append("\n".join(ul_list))
                else:
                    html_new.append(line)
            except:
                html_new.append(line)

        html = "\n".join(html_new)

        # Удаление пустых списков

        html_new = []
        for line in html.split("\n"):
            if "<li></li>" in line:
                line = re.sub(r'<li></li>', '', line)
                html_new.append(line)
            else:
                html_new.append(line)

        html = "\n".join(html_new)

        # Удаление дефиса после обрезки повторения

        html_new = []
        for line in html.split("\n"):
            if "<p>- " in line:
                line = re.sub(r'<p>- ', '<p>', line)
                html_new.append(line)
            else:
                html_new.append(line)

        html = "\n".join(html_new)

        # Удаление повторяющихся определений

        html_new = []
        counter = 0
        first_three_words = "   "
        for line in html.split("\n"):
            if "</p>" in line and counter > 0:
                if 'is a ' in line.split('. ')[0] or 'is an ' in line.split('. ')[0]:
                    line = re.sub(line.split('. ')[0] + "\. ", "", line)
                    if "It is " in line.split('. ')[0]:
                        line = re.sub(line.split('. ')[0] + "\. ", "", line)
                        html_new.append("<p>" + line)
                    else:
                        html_new.append("<p>" + line)
                else:
                    html_new.append(line)
            else:
                html_new.append(line)
                counter += 1

        html = "\n".join(html_new)


        # Удаление However

        html_new = []
        for line in html.split("\n"):
            if "<p>However, " in line:
                line = re.sub(r'<p>However, ', '<p>', line)
                line = re.sub(line[3], line[3].upper(), line, 1)
                html_new.append(line)
            else:
                html_new.append(line)

        html = "\n".join(html_new)

        # Разбивка длинных абзацев
        html_new = []
        for line in html.split("\n"):
            if "</p>" in line and len(line.split('. ')) > 7 and "1. " not in line:
                line = replacenth(line, '\. ', '.</p>\n<p>', 5)
                print(line)
                html_new.append(line)
            else:
                html_new.append(line)

        html = "\n".join(html_new)

        # Поиск внешних ссылок

        html_new = []
        counter = 0
        for line in html.split("\n"):
            if "</p>" in line and link_1[0] in line and counter == 0:
                line = re.sub(link_1[0], link_1[1], line, 1)
                html_new.append(line)
                counter += 1
            else:
                html_new.append(line)
        html = "\n".join(html_new)

        html_new = []
        counter = 0
        for line in html.split("\n"):
            if "</p>" in line and link_2[0] in line and counter == 0:
                line = re.sub(link_2[0], link_2[1], line, 1)
                html_new.append(line)
                counter += 1
            else:
                html_new.append(line)
        html = "\n".join(html_new)

        html_new = []
        counter = 0
        for line in html.split("\n"):
            if "</p>" in line and link_3[0] in line and counter == 0:
                line = re.sub(link_3[0], link_3[1], line, 1)
                html_new.append(line)
                counter += 1
            else:
                html_new.append(line)
        html = "\n".join(html_new)

        html_new = []
        counter = 0
        for line in html.split("\n"):
            if "</p>" in line and link_4[0] in line and counter == 0:
                line = re.sub(link_4[0], link_4[1], line, 1)
                html_new.append(line)
                counter += 1
            else:
                html_new.append(line)
        html = "\n".join(html_new)

        html_new = []
        counter = 0
        for line in html.split("\n"):
            if "</p>" in line and link_5[0] in line and counter == 0:
                line = re.sub(link_5[0], link_5[1], line, 1)
                html_new.append(line)
                counter += 1
            else:
                html_new.append(line)
        html = "\n".join(html_new)

        html_new = []
        counter = 0
        for line in html.split("\n"):
            if "</p>" in line and link_6[0] in line and counter == 0:
                line = re.sub(link_6[0], link_6[1], line, 1)
                html_new.append(line)
                counter += 1
            else:
                html_new.append(line)
        html = "\n".join(html_new)


        html_new = []
        counter = 0
        for line in html.split("\n"):
            if "</p>" in line and link_7[0] in line and counter == 0:
                line = re.sub(link_7[0], link_7[1], line, 1)
                html_new.append(line)
                counter += 1
            else:
                html_new.append(line)
        html = "\n".join(html_new)


        html_new = []
        counter = 0
        for line in html.split("\n"):
            if "</p>" in line and link_8[0] in line and counter == 0:
                line = re.sub(link_8[0], link_8[1], line, 1)
                html_new.append(line)
                counter += 1
            else:
                html_new.append(line)
        html = "\n".join(html_new)


        html_new = []
        counter = 0
        for line in html.split("\n"):
            if "</p>" in line and link_9[0] in line and counter == 0:
                line = re.sub(link_9[0], link_9[1], line, 1)
                html_new.append(line)
                counter += 1
            else:
                html_new.append(line)
        html = "\n".join(html_new)


        # Добавление заголовка, h1
        html_new.insert(0, "<title>" + title_with_tagline + "</title>")
        html_new.insert(1, '<meta name="description" content="' + description + '" />')
        html_new.insert(2, "<h1>" + h1_with_tagline + "</h1>")


        html = "\n".join(html_new)



        with open(processed_files_path + filename[0], "w") as file:
            file.write(html)

        generated_files.append(filename[0])
    except Exception as e:
        # print(str(e) + " -> " + filename[0])
        continue


print()
print('Файлы с категориями:')
print(categories_list)

print()
print('Сгенерированные статьи:')
print(*generated_files, sep='\n')