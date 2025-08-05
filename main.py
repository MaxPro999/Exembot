import random
import sqlite3
from  tkinter import *
from tkinter import messagebox
import tkinter.filedialog as fd
import pandas as pd
from datetime import datetime
from tkinter import ttk
global tests
tests = []
class connect_db:
    def __init__(self, db_name):
        self.db_name = db_name
        self.connector = sqlite3.connect(self.db_name)
        self.cursor = self.connector.cursor()
    def select_sql(self,sql_txt):
        self.sql_txt = sql_txt
        return  self.cursor.execute(self.sql_txt)
    def close_db(self):
        self.connector.commit()
        self.cursor.close()
        self.connector.close()
class mybutton:
    def __init__(self, text, font, x, y, width, window, command):

        self.window = window
        self.command = command
        self.button = Button(text=text,font=font,activebackground="blue",activeforeground="white")
        self.button.place(x=x,y=y,width=width)
        self.button.bind('<Button-1>', lambda event: self.click(self.command))
    def click(self,command):
        if command =="enter":
            self.enter()
        elif command == "show":
            self.show()
        elif command == "reg":
            self.register()
        elif command == "save":
            self.hash_table()
        elif command == "file_get":
            self.filepath_get()
        elif command == "close":
            self.close_test()
        elif command == "get_test":
            self.get_test()
        elif command == "delete":
            self.delete_test()
    def show(self):
        if self.window.entry_password_entry.cget('show') == '':
            self.window.entry_password_entry.config(show='*')
        else:
            self.window.entry_password_entry.config(show='')
    def enter(self):
        global id_user
        global test
        self.value_login = self.window.entry_login.value.get()
        self.value_pass = self.window.entry_password.value.get()
        self.db = connect_db('autoservis_users.db')
        #self.db = connect_db('tg_bot.db')
        self.sql = self.db.select_sql("SELECT * from users")
        self.open = False
        for row in self.sql:
            self.db_id = row[0]
            self.db_login = row[1]
            self.db_pass = row[2]
            if self.value_login == self.db_login and self.value_pass == self.db_pass:
                id_user=self.db_id
                self.open = True
                break
        self.db.close_db()
        if self.open:
            self.db = connect_db('autoservis_users.db')
            self.sql = self.db.select_sql(f"SELECT id,object,type from table_tests where iduser='{id_user}'")
            for row in self.sql:
                self.db_object = row[1]
                self.db_idtest = row[0]
                self.db_type = row[2]
                tests.append(str(self.db_object)+" - "+str(self.db_type)+"; @"+str(self.db_idtest))
            self.db.close_db()
                
            messagebox.showinfo("Внимание!", "Доступ разрешен")
            self.window.destroy_main_window()
            self.window = mywindow("Управление тестами", "1000x1000")
            self.window.widget_for_work_window()
            self.window.visible_window()
            
        else:
            messagebox.showerror("Внимание!", "Не верный логин или пароль")
    def register(self):
        self.user_login = self.window.entry_login.value.get()
        self.user_password = self.window.entry_password.value.get()
        self.db = connect_db('autoservis_users.db')
        #self.db = connect_db('tg_bot.db')
        self.sql = self.db.select_sql("SELECT * from users")
        sim = 0
        for row in self.sql:
            self.db_login = row[1]
            self.db_pass = row[2]
            if self.user_login == self.db_login:
                sim +=1
        if sim>0:
            self.open = False
        else:
            self.open = True
        if self.open:
            self.sql = self.db.select_sql(f"INSERT INTO users (login, password) VALUES('{self.user_login}', '{self.user_password}');")
            self.db.close_db()
            messagebox.showinfo("Внимание!", "Регистрация успешна")
        else:
            messagebox.showerror("Внимание!", "Такой пользователь уже есть")
            self.db.close_db()
    def filepath_get(self):
        global filepath
        filepath = fd.askopenfile()
        self.lable_file = mylabel(filepath, "Arial 10", "lightblue", 210, 300)
    def save_test(self):#
        self.file = filepath
        self.test_file = pd.read_csv(self.file, delimiter=";")
        self.test_object = self.window.entry_object.value.get()
        self.test_type = self.window.entry_type.value.get()
        self.db = connect_db('autoservis_users.db')
        self.sql = self.db.select_sql("SELECT * from table_tests")
        self.open = True
        if self.open:
            self.sql = self.db.select_sql(f"INSERT INTO table_tests (object,type,iduser,count_questions) VALUES('{self.test_object}','{self.test_type}','{id_user}','{self.test_file.shape[0]}');")
        
        self.sql = self.db.select_sql("SELECT * from table_tests")
        for row in self.sql:
            self.db_idtest = row[0]
            self.db_object = row[1]
            self.db_type = row[2]
            self.db_iduser = row[3]
            if self.test_object == self.db_object and self.test_type == self.db_type and id_user == self.db_iduser:
                tests.append(str(self.db_object)+" - "+str(self.db_type)+"; @"+str(self.db_idtest))
                self.sql = self.db.select_sql(f"DROP TABLE IF EXISTS 'Questions{self.db_idtest}'")
                self.sql = self.db.select_sql(f"CREATE TABLE IF NOT EXISTS 'Questions{self.db_idtest}' ("
                                    f" 'id' INTEGER NOT NULL,"
                                    f" 'question' TEXT NOT NULL,"
                                    f" 'count_answer' TEXT NOT NULL,"
                                    f" 'id_answer_true' TEXT NOT NULL,"
                                    f" 'answer' TEXT NOT NULL,"
                                    f" PRIMARY KEY('id' AUTOINCREMENT));")
                self.sql = self.db.select_sql(f"CREATE TABLE IF NOT EXISTS 'Questions{self.db_idtest}_result' ("
                                    f" 'id' INTEGER NOT NULL,"
                                    f" 'question' TEXT NOT NULL,"
                                    f" 'answer_true' TEXT NOT NULL,"
                                    f" 'answer' TEXT NOT NULL,"
                                    f" 'result' TEXT NOT NULL,"
                                    f" 'FIO' TEXT NOT NULL,"
                                    f" 'code_member' TEXT NOT NULL,"
                                    f" PRIMARY KEY('id' AUTOINCREMENT));")

                for j in range(self.test_file.shape[0]):
                    if str(self.test_file.iloc[j, 1]) !="1":
                        self.answer = ""
                        for i in range(3,3+int(self.test_file.iloc[j, 1])):
                            self.answer = self.answer+str(i-2)+": "+str(self.test_file.iloc[j, i])+"; "+"\n"
                    else:
                        
                        self.answer = ""
                        self.answer =self.test_file.iloc[j, 3]
                    self.sql = self.db.select_sql(
                        f"INSERT INTO 'Questions{self.db_idtest}' (question,count_answer,id_answer_true,answer) VALUES('{self.test_file.iloc[j, 0]}','{self.test_file.iloc[j, 1]}','{self.test_file.iloc[j, 2]}','{self.answer}');")  # csv==exel
                self.db.close_db()
                return self.db_idtest
 

    def hash_generate(self,id_test):
        self.id_test = id_test
        self.member_code = (str(id_user)+str(random.randint(1,999999999))+str(id_test))
        self.db = connect_db('autoservis_users.db')
        self.sql = self.db.select_sql("SELECT * from Codes_members")
        sim = 0
        for row in self.sql:
            self.db_code = row[1]
            if self.member_code == self.db_code:
                sim += 1
        if sim > 0:
            self.open = False
        else:
            self.open = True
        if self.open:
            self.sql = self.db.select_sql(
                f"INSERT INTO Codes_members (Code,idtest) VALUES('{self.member_code}','{self.id_test}');")
            self.db.close_db()
            return self.member_code
        else:
            self.db.close_db()
            return self.hash_generate()

    def hash_table(self):
        self.count_hash = self.window.entry_code.value.get()
        self.idtest = self.save_test()
        self.filepath = fd.asksaveasfilename()

        if self.filepath != "":
            # with open(filepath, "w") as file:
            self.file = open(self.filepath, 'w', encoding="utf8")
            self.file.write(' ' + ';' + 'Код ' + '\n')
            for i in range(int(self.count_hash)):
                self.file.write(str(i+1) + ";" + str(self.hash_generate(self.idtest)) + '\n')
            self.file.close()
    def close_test(self):
        self.db = connect_db('autoservis_users.db')
        self.test =self.window.combobox.get()
        on = self.test.find("@")+1
        self.closedidtest=self.test[on:]
        self.sql = self.db.select_sql(f"DROP TABLE IF EXISTS 'Questions{self.closedidtest}'")
        self.sql = self.db.select_sql(f"Delete  from Codes_members where idtest = '{self.closedidtest}'")
        self.db.close_db()
    def get_test(self):
        self.db = connect_db('autoservis_users.db')
        self.test =self.window.combobox.get()
        on = self.test.find("@")+1
        self.closedidtest=self.test[on:]
        self.filepath = fd.asksaveasfilename()
        self.file = open(self.filepath, 'w', encoding="utf8")
        self.file.write('Код'+ ";" + 'ФИО'+ ";" + 'Вопрос'+ ";"+ 'Результат'+ ";"+ 'Ответ'+ ";"+ 'Правильный ответ' + '\n')
        self.sql = self.db.select_sql(f"Select * from 'Questions{self.closedidtest}_result' Order by FIO,id")
        for row in self.sql:
            self.db_question = row[1]
            self.db_answer_true = row[2]
            self.db_answer = row[3]
            self.db_result = row[4]
            self.db_code_member = row[6]
            self.db_FIO= row[5]
            self.file.write(str(self.db_code_member) + ";" + str(self.db_FIO) + ";"+ str(self.db_question) + ";"+ str(self.db_result) + ";"+ str(self.db_answer) + ";"+ str(self.db_answer_true) + ";" +'\n')
        self.db.close_db()
    def delete_test(self):
        self.db = connect_db('autoservis_users.db')
        self.test =self.window.combobox.get()
        on = self.test.find("@")+1
        self.closedidtest=self.test[on:]
        self.sql = self.db.select_sql(f"DROP TABLE IF EXISTS 'Questions{self.closedidtest}_result'")
        self.sql = self.db.select_sql(f"Delete  from table_tests where id = '{self.closedidtest}'")
        self.db.close_db()
        self.window.combobox.set('')


class myentry:
    def __init__(self,font,x,y,width,mask):
        self.value = StringVar()
        if mask == True:
            show = "*"
        else:
            show = ""
        self.entry=Entry(textvariable=self.value, font=font,show=show)
        self.entry.place(x=x,y=y,width=width)
class mylabel:
    def __init__(self,text,font,bg,x,y):
        self.lable = Label(text=text,font=font,bg=bg)
        self.lable.place(x=x,y=y)
class mywindow:
    def __init__(self, title, size):
        self.window = Tk()
        self.window.geometry(size)
        self.window.resizable(False, False)
        self.window.title(title)
        self.window.configure(bg="lightblue")

        self.db = connect_db('users.db')
        self.db.close_db()
    def visible_window(self):
        self.window.mainloop()
    def destroy_main_window(self):
        self.window.destroy()

    def widget_for_start_window(self):
        
        self.lable_title=mylabel("Войти","Arial 20 bold","lightblue", 150,50)
        self.lable_login = mylabel("Логин:","Arial 15","lightblue", 50, 150)
        self.lable_password = mylabel("Пароль:", "Arial 15", "lightblue",50,200)

        self.entry_login = myentry("Arial 15", 150, 150, 150, False)
        self.entry_password = myentry("Arial 15", 150,200,150, True)

        self.entry_password_entry = self.entry_password.entry

        self.entry_btn = mybutton("Войти","Arial 15",150,300,100,self,"enter")
        self.reg_btn = mybutton("Зарегистрироватся", "Arial 15", 100, 350, 200, self, "reg")

        self.show_btn = mybutton("§","Arial 12",310,200,35,self,"show")
    def widget_for_work_window(self):
        global tests
        self.lable_title=mylabel("Загрузка тестов","Arial 20 bold","lightblue", 150,50)
        self.lable_count = mylabel("Кол-во участников:","Arial 15","lightblue", 50, 150)
        self.lable_object = mylabel("Предмет теста:", "Arial 15", "lightblue", 50, 200)
        self.lable_type = mylabel("Тема теста:", "Arial 15", "lightblue", 50, 250)
        self.lable_filepath = mylabel("Путь к тесту:", "Arial 15", "lightblue", 50, 300)

        self.entry_code = myentry("Arial 15", 250, 150, 150, False)
        self.entry_object = myentry("Arial 15", 250, 200, 150, False)
        self.entry_type = myentry("Arial 15", 250, 250, 150, False)

        self.save_btn = mybutton("Сохранить\nтест на сервер", "Arial 15", 150, 350, 150, self, "save")
        self.get_btn = mybutton("Загрузить тест", "Arial 15", 450, 350, 150, self, "file_get")
        self.close_test = mybutton("Закрыть тест", "Arial 10", 350, 500, 150, self, "close")
        self.delete_test = mybutton("Удалить тест", "Arial 10", 500, 500, 150, self, "delete")
        self.get_test = mybutton("Результаты теста", "Arial 10", 650, 500, 150, self, "get_test")
        self.combobox = ttk.Combobox(values=tests,width=250)
        self.combobox.pack(anchor=NW, padx=400, pady=450)
        




start_window = mywindow("Вход","450x450")
start_window.widget_for_start_window()          
start_window.visible_window()