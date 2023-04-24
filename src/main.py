#importing modules
from bs4 import BeautifulSoup
from ftplib import FTP
import time
import os
import shutil

#constants
assemb = 4
ftp_username = "YOUR_USERNAME"
ftp_password = "YOUR_PASSWORD"
ftp_server  = "YOUR_SERVER"
ftp_data = []

#defining functions
def handle_binary(data):
    ftp_data.append(data)

#initializing ftp_server
ftp = FTP(user="username", passwd="password", host="ftpupload.net")

print(f">>PrHelper v1.1 (сборка {assemb})\nВсе данные берутся из открытых источников, автор программы не несёт ответственности за"
      " корректность"
      " ответов\n\n>>Список доступных дисциплин")

#getting and printing dicp_list
resp = ftp.retrbinary("RETR htdocs/dicp_list.txt", callback=handle_binary)
ftp_data = [a.decode('UTF-8') for a in ftp_data]
dicp_list = ftp_data[0].split('\r\n')
for a in range(len(dicp_list)):
    print(f"{a+1}. {dicp_list[a]}")

#user's input
flag_input = False
while not flag_input:
    try:
        dicp_id = int(input("\n>>Введите номер нужной дисциплины"
                            "\n>>"))
        if 0 < dicp_id <= len(dicp_list):
            print(f"\n>>Выбрана дисциплина: {dicp_list[dicp_id-1]}")
            dicp_filename = dicp_list[dicp_id-1].split(" ")[-1][1:-1]
            flag_input = True
        else:
            print(">>Дисциплины с таким номером не найдено, попробуйте ещё раз")
    except ValueError:
        print(">>Введено некорректное значение, попробуйте ещё раз")

print(">>Ожидание html файла...")

#find current .html file
flag_find_html = False
while not flag_find_html:
    for dirpath, dirnames, filenames in os.walk("."):
        for filename in filenames:
            if ".html" in os.path.join(dirpath, filename) and "block" in os.path.join(dirpath, filename):
                html_file = os.path.join(dirpath, filename)
                print(">>Файл html обнаружен, загрузка...\n\n")
                print(dirpath)
                flag_find_html = True
    time.sleep(1)

with open(html_file, "r", encoding="utf-8") as f:
    contents = f.read()

#getting questions and answers list
ftp.cwd('htdocs/questions')

questions_temp_folder = str(os.getcwd()) + "\\tempo.txt"
with open(questions_temp_folder, 'wb') as ftempo:
    ftp.retrbinary('RETR ' + f"questions_{dicp_filename}.txt", ftempo.write)

with open(questions_temp_folder, 'r', encoding="utf-8") as ftempo:
    questions_list = ftempo.readlines()
    questions_list = [a.strip("\n") for a in questions_list]

#finding current text lines
root = BeautifulSoup(contents, 'lxml')
elts = root.find_all("div", class_="wrapper-problem-response")

#finding and printing current questions list
num_counter = 1
for el in elts:
    question = el.text.split('\n')
    for a in range(len(question)):
        if len(question[a]) != 0:
            x = a
            break
    question = question[x].replace(".", "").replace(",", "").replace(":", "").replace("?", "").\
        replace("-", "").replace("–", "").replace("  ", " ").replace("\"", "").replace("«", "").replace("»", "").\
        replace("(", "").replace(")", "").lower()
    num = question[0:2]
    if num.strip(" ") in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16",
                          "17", "18", "19", "20"]:
        question = question[2:]
    question = question.strip(" ")
    flag = False
    for ans in questions_list:
        if question in ans.split(">>>")[0]:
            print(f"№{num_counter}: {question}\nОтвет: {ans.split('>>>')[1]}\n")
            flag = True
            break
    if not flag:
        print(f"№ {num_counter}: {question}\nОтвет не найден\n")
    num_counter += 1

#removing all files
try:
    os.remove(questions_temp_folder)
    shutil.rmtree(dirpath)
    os.remove(dirpath[:-6] + ".html")
except Exception:
    print('Некоторые файлы в папке, в которой находится приложение, нужные для работы, не получилось удалить. '
          'Сделайте это вручную.')

input("\n>>Нажмите Enter для выхода...")
