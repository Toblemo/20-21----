import sqlite3, xlsxwriter, sys
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from PIL import Image
import pandas as pd
from tkinter.messagebox import showerror, showinfo
import os


journal_name=["№", "№ Группы", "№ Студенты", "№ Преподователи", "№ Дисциплины", "оценки", "дата проведения", "отметка о пропуске"]
discipline_name = ["№", "№ тема ", "предмет", ] 
group_name = ["№", "куратор", "номер группы"]
student_name = ["№", "имя", "фамилия", "курс обучения"]
teacher_name = ["№", "имя", "фамилия", "опыт работы"]

class AboutProgramWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("О программе")

        # Информация о программе
        program_name_label = tk.Label(self, text="Название программы: Электронный журнал")
        program_version_label = tk.Label(self, text="Версия: 1.0")
        developer_label = tk.Label(self, text="Разработчик: Полхович Александр, 2023")

        # Рамка для назначения программного средства
        purpose_frame = tk.LabelFrame(self, text="")  # Удалил текст "Назначение программного средства"
        purpose_text = (
            "Данное программное средство «Электронный журнал» "
            "разрабатывается с целью автоматизации процесса введения отчетности"
        )
        purpose_label = tk.Label(purpose_frame, text=purpose_text, anchor="w", wraplength=300)

        # Размещение компонентов
        program_name_label.pack(pady=5)
        program_version_label.pack(pady=5)
        developer_label.pack(pady=5)

        purpose_frame.pack(pady=10, padx=10, ipadx=5, ipady=5)  # Добавлены ipadx и ipady
        purpose_label.pack(pady=5)

        # Кнопка "ОК" для закрытия окна
        ok_button = tk.Button(self, text="ОК", command=self.destroy)
        ok_button.pack(pady=10)


class WindowMain(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title('Электронный журнал')
        self.wm_iconbitmap()
        self.wm_iconbitmap()
        self.iconphoto(True, tk.PhotoImage(file="icon3\\kniger.png"))
        self.last_headers = None
       

        # Создание фрейма для отображения таблицы
        self.table_frame = ctk.CTkFrame(self, width=750, height=500)
        self.resizable(False, False)
        self.table_frame.grid(row=0, column=0, padx=5, pady=5)

        # Загрузка фона
        bg = ctk.CTkImage(Image.open("icon3\\kniger.png"), size=(750, 600))
        lbl = ctk.CTkLabel(self.table_frame, image=bg, text='Электронный журнал', font=("Calibri", 30))
        lbl.place(relwidth=1, relheight=1)
       

        # Создание меню
        self.menu_bar = tk.Menu(self, background='#555', foreground='white')

        # Меню "Файл"
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="Выход", command=self.quit)
        self.menu_bar.add_cascade(label="Файл", menu=file_menu)

        # Меню "Таблицы"
        references_menu = tk.Menu(self.menu_bar, tearoff=0)
        references_menu.add_command(label="Журнал",
                                    command=lambda: self.show_table("SELECT * FROM journal", journal_name))
        references_menu.add_command(label="Дисциплины",
                                    command=lambda: self.show_table("SELECT * FROM discipline", discipline_name))
        references_menu.add_command(label="Группы",
                                    command=lambda: self.show_table("SELECT * FROM 'group'", group_name))
        references_menu.add_command(label="Преподователи",
                                    command=lambda: self.show_table("SELECT * FROM teacher", teacher_name))
        references_menu.add_command(label="Студенты",
                                    command=lambda: self.show_table("SELECT * FROM student", student_name))
        self.menu_bar.add_cascade(label="Таблицы", menu=references_menu)

        # Меню "Отчёты"
        reports_menu = tk.Menu(self.menu_bar, tearoff=0)
        reports_menu.add_command(label="Создать Отчёт", command=self.to_xlsx)
        self.menu_bar.add_cascade(label="Отчёты", menu=reports_menu)

        # Меню "Сервис"
        help_menu = tk.Menu(self.menu_bar, tearoff=0)
        help_menu.add_command(label="Руководство пользователя", command=self.open_rykov)
        help_menu.add_command(label="O программе",command=self.open_about_window)
        self.menu_bar.add_cascade(label="Сервис", menu=help_menu)    
  

        # Настройка цветов меню
        file_menu.configure(bg='#555', fg='white')
        references_menu.configure(bg='#555', fg='white')
        reports_menu.configure(bg='#555', fg='white')
        help_menu.configure(bg='#555', fg='white')

        # Установка меню в главное окно
        self.config(menu=self.menu_bar)

        btn_width = 150
        pad = 5

        # Создание кнопок и виджетов для поиска и редактирования данных
        btn_frame = ctk.CTkFrame(self)
        btn_frame.grid(row=0, column=1)
        ctk.CTkButton(btn_frame, text="добавить", width=btn_width, command=self.add).pack(pady=pad)
        ctk.CTkButton(btn_frame, text="удалить", width=btn_width, command=self.delete).pack(pady=pad)
        ctk.CTkButton(btn_frame, text="изменить", width=btn_width, command=self.change).pack(pady=pad)

        search_frame = ctk.CTkFrame(self)
        search_frame.grid(row=1, column=0, pady=pad)
        self.search_entry = ctk.CTkEntry(search_frame, width=300)
        self.search_entry.grid(row=0, column=0, padx=pad)
        ctk.CTkButton(search_frame, text="Поиск", width=20, command=self.search).grid(row=0, column=1, padx=pad)
        ctk.CTkButton(search_frame, text="Искать далее", width=20, command=self.search_next).grid(row=0, column=2,
                                                                                                  padx=pad)
        ctk.CTkButton(search_frame, text="Сброс", width=20, command=self.reset_search).grid(row=0, column=3, padx=pad)

    def reset_search(self):
        if self.last_headers:
            self.table.selection_remove(self.table.selection())
        self.search_entry.delete(0, 'end')

    def open_about_window(self):
        about_window = AboutProgramWindow(self)
        about_window.geometry("600x250")  # Установите размер окна по вашему усмотрению
        about_window.focus_set()
        about_window.grab_set()
        self.wait_window(about_window)

    def open_rykov(self):
        os.system(r"C:\Users\GIGACHAD\Desktop\proj\справка\main.html") 

    def search_in_table(self, table, search_terms, start_item=None):
        table.selection_remove(table.selection())  # Сброс предыдущего выделения

        items = table.get_children('')
        start_index = items.index(start_item) + 1 if start_item else 0

        for item in items[start_index:]:
            values = table.item(item, 'values')
            for term in search_terms:
                if any(term.lower() in str(value).lower() for value in values):
                    table.selection_add(item)
                    table.focus(item)
                    table.see(item)
                    return item  # Возвращаем найденный элемент

    def reset_search(self):
        if self.last_headers:
            self.table.selection_remove(self.table.selection())
        self.search_entry.delete(0, 'end')

    def search(self):
        if self.last_headers:
            self.current_item = self.search_in_table(self.table, self.search_entry.get().split(','))

    def search_next(self):
        if self.last_headers:
            if self.current_item:
                self.current_item = self.search_in_table(self.table, self.search_entry.get().split(','),
                                                         start_item=self.current_item)

    def to_xlsx(self):
        if self.last_headers == journal_name:
            sql_query = "SELECT * FROM journal"
            table_name = "journal"
        elif self.last_headers == group_name:
            sql_query = "SELECT * FROM 'group'"
            table_name = "group"
        elif self.last_headers == student_name:
            sql_query = "SELECT * FROM student"
            table_name = "student"
        elif self.last_headers == teacher_name:
            sql_query = "SELECT * FROM teacher"
            table_name = "teacher"
        elif self.last_headers == discipline_name:
            sql_query = "SELECT * FROM discipline"
            table_name = "discipline"
        else:
            return

        dir = sys.path[0] + "\\export"
        os.makedirs(dir, exist_ok=True)
        path = dir + f"\\{table_name}.xlsx"

        # Подключение к базе данных SQLite
        conn = sqlite3.connect("journal_bd.db")
        cursor = conn.cursor()
        # Получите данные из базы данных
        cursor.execute(sql_query)
        data = cursor.fetchall()
        # Создайте DataFrame из данных
        df = pd.DataFrame(data, columns=self.last_headers)
        # Создайте объект writer для записи данных в Excel
        writer = pd.ExcelWriter(path, engine='xlsxwriter')
        # Запишите DataFrame в файл Excel
        df.to_excel(writer, 'Лист 1', index=False)
        # Сохраните результат
        writer.close()

        showinfo(title="Успешно", message=f"Данные экспортированы в {path}")

    def add(self):
        if self.last_headers == journal_name:
            Windowjournal_bd("add")        
        elif self.last_headers == discipline_name:
            Windowdiscipline("add")
        elif self.last_headers == student_name:
            WindowStudent("add")
        elif self.last_headers == teacher_name:
            WindowTeacher("add")
        elif self.last_headers == group_name:
            Windowgroup("add")
        else:
            return

        self.withdraw()

    def delete(self):
        if self.last_headers:
            select_item = self.table.selection()
            if select_item:
                item_data = self.table.item(select_item[0])["values"]
            else:
                showerror(title="Ошибка", message="He выбранна запись")
                return
        else:
            return

        if self.last_headers == journal_name:
            Windowjournal_bd("delete", item_data)
        elif self.last_headers == student_name:
            WindowStudent("delete", item_data)
        elif self.last_headers == teacher_name:
            WindowTeacher("delete", item_data)
        elif self.last_headers == group_name:
            Windowgroup("delete", item_data)
        elif self.last_headers == discipline_name:
            Windowdiscipline("delete", item_data)
        else:
            return

        self.withdraw()

    def change(self):
        if self.last_headers:
            select_item = self.table.selection()
            if select_item:
                item_data = self.table.item(select_item[0])["values"]
            else:
                showerror(title="Ошибка", message="He выбранна запись")
                return
        else:
            return
        
        if self.last_headers == journal_name:
            Windowjournal_bd("change", item_data)
        elif self.last_headers == discipline_name:
            Windowdiscipline("change", item_data)
        elif self.last_headers == student_name:
            WindowStudent("change", item_data)
        elif self.last_headers == teacher_name:
            WindowTeacher("change", item_data)
        elif self.last_headers == group_name:
            Windowgroup("change", item_data)
        else:
            return

        self.withdraw()

    def show_table(self, sql_query, headers=None):
        # Очистка фрейма перед отображением новых данных
        for widget in self.table_frame.winfo_children(): widget.destroy()

        # Подключение к базе данных SQLite
        conn = sqlite3.connect("journal_bd.db")
        cursor = conn.cursor()

        # Выполнение SQL-запроса
        cursor.execute(sql_query)
        self.last_sql_query = sql_query

        # Получение заголовков таблицы и данных
        if headers == None:  # если заголовки не были переданы используем те что в БД
            table_headers = [description[0] for description in cursor.description]
        else:  # иначе используем те что передали
            table_headers = headers
            self.last_headers = headers
        table_data = cursor.fetchall()

        # Закрытие соединения с базой данных
        conn.close()

        canvas = ctk.CTkCanvas(self.table_frame, width=865, height=480)
        canvas.pack(fill="both", expand=True)

        x_scrollbar = ttk.Scrollbar(self.table_frame, orient="horizontal", command=canvas.xview)
        x_scrollbar.pack(side="bottom", fill="x")

        canvas.configure(xscrollcommand=x_scrollbar.set)

        self.table = ttk.Treeview(self.table_frame, columns=table_headers, show="headings", height=23)
        for header in table_headers:
            self.table.heading(header, text=header)
            self.table.column(header,
                              width=len(header) * 10 + 15)  # установка ширины столбца исходя длины его заголовка
        for row in table_data: self.table.insert("", "end", values=row)

        canvas.create_window((0, 0), window=self.table, anchor="nw")

        self.table.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

    def update_table(self):
        self.show_table(self.last_sql_query, self.last_headers)
class Windowjournal_bd(ctk.CTkToplevel):
    def __init__(self, operation, select_row=None):
        super().__init__()
        self.protocol('WM_DELETE_WINDOW', lambda: self.quit_win())

        conn = sqlite3.connect("journal_bd.db")

        conn.close

        if select_row:
            self.select_id_journala = select_row[0]
            self.select_id_disciplinea = select_row[1]
            self.select_id_groupea = select_row[2]
            self.select_id_teachera = select_row[3]
            self.select_id_student = select_row[4]
            self.select_marks = select_row[5]
            self.select_date_ofcompetition = select_row[6]
            self.select_pass = select_row[7]

        if operation == "add":
            self.title("Добаление")
            ctk.CTkLabel(self, text="Добаление в таблицу 'Журнал'").grid(row=0, column=0, pady=5, padx=5,
                                                                           columnspan=2)

            ctk.CTkLabel(self, text="id журнала").grid(row=1, column=0, pady=5, padx=5)
            self.id_journala = ctk.CTkEntry(self, width=300)
            self.id_journala.grid(row=1, column=1, pady=5, padx=5)

            ctk.CTkLabel(self, text="id группы").grid(row=2, column=0, pady=5, padx=5)
            self.id_groupea = ctk.CTkEntry(self, width=300)
            self.id_groupea.grid(row=2, column=1, pady=5, padx=5)

            ctk.CTkLabel(self, text="id студенты").grid(row=3, column=0, pady=5, padx=5)
            self.id_student = ctk.CTkEntry(self, width=300)
            self.id_student.grid(row=3, column=1, pady=5, padx=5)

            ctk.CTkLabel(self, text="id преподователи").grid(row=4, column=0, pady=5, padx=5)
            self.id_teachera = ctk.CTkEntry(self, width=300)
            self.id_teachera.grid(row=4, column=1, pady=5, padx=5)
            
            ctk.CTkLabel(self, text="id дисциплины").grid(row=5, column=0, pady=5, padx=5)
            self.id_disciplinea = ctk.CTkEntry(self, width=300)
            self.id_disciplinea.grid(row=5, column=1, pady=5, padx=5)

            ctk.CTkLabel(self, text="оценки").grid(row=6, column=0, pady=5, padx=5)
            self.marksa = ctk.CTkEntry(self, width=300)
            self.marksa.grid(row=6, column=1, pady=5, padx=5)

            ctk.CTkLabel(self, text="дата проведения").grid(row=7, column=0, pady=5, padx=5)
            self.date_ofcompetition = ctk.CTkEntry(self, width=300)
            self.date_ofcompetition.grid(row=7, column=1, pady=5, padx=5)

            ctk.CTkLabel(self, text="отметка о пропуске").grid(row=8, column=0, pady=5, padx=5)
            self.passa = ctk.CTkEntry(self, width=300)
            self.passa.grid(row=8, column=1, pady=5, padx=5)

            ctk.CTkButton(self, text="Отмена", width=100, command=self.quit_win).grid(row=9, column=0, pady=5, padx=5)
            ctk.CTkButton(self, text="Добавить", width=100, command=self.add).grid(row=9 , column=1, pady=5, padx=5, sticky="e")

        elif operation == "delete":
            self.title("Удаление")
            ctk.CTkLabel(self, text="Вы действиельно хотите\n удалить запись из таблицы 'Журнал'?"
                         ).grid(row=0, column=0, pady=5, padx=5, columnspan=2)

            ctk.CTkLabel(self, text=f"{self.select_id_journala}. {self.select_id_groupea}. {self.select_id_teachera}.  {self.select_id_disciplinea}. {self.select_marks} {self.select_date_ofcompetition}. {self.select_pass}"
                         ).grid(row=1, column=0, pady=5, padx=5, columnspan=2)

            ctk.CTkButton(self, text="Нет", width=100, command=self.quit_win).grid(row=2, column=0, pady=5, padx=5, sticky="w")
            ctk.CTkButton(self, text="Да", width=100, command=self.delete).grid(row=2, column=1, pady=5, padx=5, sticky="e")

        elif operation == "change":
            self.title("Изменение в таблице 'Журнал'")
            ctk.CTkLabel(self, text="Назввание поля").grid(row=0, column=0, pady=5, padx=5)
            ctk.CTkLabel(self, text="Текущее значение").grid(row=0, column=1, pady=5, padx=5)
            ctk.CTkLabel(self, text="Новое занчение").grid(row=0, column=2, pady=5, padx=5)

            ctk.CTkLabel(self, text="id журнала").grid(row=1, column=0, pady=5, padx=5)
            ctk.CTkLabel(self, text=self.select_id_journala).grid(row=1, column=1, pady=5, padx=5)
            self.id_journala = ctk.CTkEntry(self, width=300)
            self.id_journala.grid(row=1, column=2, pady=5, padx=5)

            ctk.CTkLabel(self, text="id группы").grid(row=2, column=0, pady=5, padx=5)
            ctk.CTkLabel(self, text=self.select_id_groupea).grid(row=2, column=1, pady=5, padx=5)
            self.id_groupea= ctk.CTkEntry(self, width=300)
            self.id_groupea.grid(row=2, column=2, pady=5, padx=5)

            ctk.CTkLabel(self, text="id студенты").grid(row=3, column=0, pady=5, padx=5)
            ctk.CTkLabel(self, text=self.select_id_student).grid(row=3, column=1, pady=5, padx=5)
            self.id_student = ctk.CTkEntry(self, width=300)
            self.id_student.grid(row=3, column=2, pady=5, padx=5)

            ctk.CTkLabel(self, text="id преподователи").grid(row=4, column=0, pady=5, padx=5)
            ctk.CTkLabel(self, text=self.select_id_teachera).grid(row=4, column=1, pady=5, padx=5)
            self.id_teachera = ctk.CTkEntry(self, width=300)
            self.id_teachera.grid(row=4, column=2, pady=5, padx=5)

            ctk.CTkLabel(self, text="id дисциплины").grid(row=5, column=0, pady=5, padx=5)
            ctk.CTkLabel(self, text=self.select_id_disciplinea).grid(row=5, column=1, pady=5, padx=5)
            self.id_disciplinea = ctk.CTkEntry(self, width=300)
            self.id_disciplinea.grid(row=5, column=2, pady=5, padx=5)

            ctk.CTkLabel(self, text="оценки").grid(row=6, column=0, pady=5, padx=5)
            ctk.CTkLabel(self, text=self.select_marks).grid(row=6, column=1, pady=5, padx=5)
            self.marksa = ctk.CTkEntry(self, width=300)
            self.marksa.grid(row=6, column=2, pady=5, padx=5)

            ctk.CTkLabel(self, text="дата проведения").grid(row=7, column=0, pady=5, padx=5)
            ctk.CTkLabel(self, text=self.select_date_ofcompetition).grid(row=7, column=1, pady=5, padx=5)
            self.date_ofcompetition = ctk.CTkEntry(self, width=300)
            self.date_ofcompetition.grid(row=7, column=2, pady=5, padx=5)

            ctk.CTkLabel(self, text="отметка о пропуске").grid(row=8, column=0, pady=5, padx=5)
            ctk.CTkLabel(self, text=self.select_pass).grid(row=8, column=1, pady=5, padx=5)
            self.passa = ctk.CTkEntry(self, width=300)
            self.passa .grid(row=8, column=2, pady=5, padx=5)

            ctk.CTkButton(self, text="Отмена", width=100, command=self.quit_win).grid(row=9, column=0, pady=5, padx=5)
            ctk.CTkButton(self, text="Сохранить", width=100, command=self.change).grid(row=9, column=2, pady=5, padx=5,
                                                                                       sticky="e")

    def quit_win(self):
        win.deiconify()
        win.update_table()
        self.destroy()

    def add(self):
        new_id_journala = self.id_journala.get()
        new_id_groupea = self.id_groupea.get()
        new_id_discipline = self.id_disciplinea.get()
        new_id_student = self.id_student.get()
        new_id_teachera = self.id_teachera.get()
        new_marks = self.marksa.get()
        new_date_ofcompetition = self.date_ofcompetition.get()
        new_pass = self.passa.get()

        if new_id_journala != "":
            try:
                conn = sqlite3.connect("journal_bd.db")
                cursor = conn.cursor()

                # Проверяем, существует ли уже запись с таким id_journala
                cursor.execute("SELECT id_journal FROM journal WHERE id_journal = ?", (new_id_journala,))
                existing_id = cursor.fetchone()

                if existing_id:
                    showerror(title="Ошибка", message="Запись с таким id_journal уже существует.")
                else:
                    cursor.execute(
                        "INSERT INTO journal (id_journal, id_groupe, id_student, id_teacher, id_discipline, discipline_mark, date_ofcompletion, pass) VALUES (?, ?, ?,?, ?, ?,?,?)",
                        (new_id_journala, new_id_groupea, new_id_student, new_id_teachera, new_id_discipline, new_marks, new_date_ofcompetition, new_pass))
                    conn.commit()
                    conn.close()
                    self.quit_win()
            except sqlite3.Error as e:
                showerror(title="Ошибка", message=str(e))
        else:
            showerror(title="Ошибка", message="Заполните все поля")


    def delete(self):
        try:
            conn = sqlite3.connect("journal_bd.db")
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM journal WHERE id_journal = ?", (self.select_id_journala,))
            conn.commit()
            conn.close()
            self.quit_win()
        except sqlite3.Error as e:
            showerror(title="Ошибка", message=str(e))

    def change(self):
        new_id_journala=self.id_journala.get() or self.select_id_journala
        new_id_groupea = self.id_groupea.get() or self.select_id_groupea
        new_id_discipline = self.id_disciplinea.get() or self.select_id_disciplinea
        new_id_student = self.id_student.get() or self.select_id_student
        new_id_teachera = self.id_teachera.get() or self.select_id_teachera
        new_marks = self.marksa.get() or self.select_marks
        new_date_ofcompetition = self.date_ofcompetition.get() or self.select_date_ofcompetition
        new_pass = self.passa.get() or self.select_pass
        try:
            conn = sqlite3.connect("journal_bd.db")
            cursor = conn.cursor()
            cursor.execute(f"""
                        UPDATE journal SET (id_journal ,id_groupe, id_student, id_teacher, id_discipline, discipline_mark, date_ofcompletion, pass) = (?, ?, ?,?, ?, ?,?,?)  WHERE id_journal= {self.select_id_journala}
                    """, (new_id_journala, new_id_groupea, new_id_student, new_id_teachera, new_id_discipline, new_marks, new_date_ofcompetition, new_pass))
            conn.commit()
            conn.close()
            self.quit_win()
        except sqlite3.Error as e:
            showerror(title="Ошибка", message=str(e))        

class Windowdiscipline(ctk.CTkToplevel):
    def __init__(self, operation, select_row=None):
        super().__init__()
        self.protocol('WM_DELETE_WINDOW', lambda: self.quit_win())

        conn = sqlite3.connect("journal_bd.db")

        conn.close

        if select_row:
            self.select_id_disciplinea = select_row[0]
            self.select_titlea = select_row[1]
            self.select_subjecta = select_row[2]

        if operation == "add":
            self.title("Добаление")
            ctk.CTkLabel(self, text="Добаление в таблицу 'Дисциплины'").grid(row=0, column=0, pady=5, padx=5,
                                                                           columnspan=2)

            ctk.CTkLabel(self, text="id Дисциплины").grid(row=1, column=0, pady=5, padx=5)
            self.id_disciplinea = ctk.CTkEntry(self, width=300)
            self.id_disciplinea.grid(row=1, column=1, pady=5, padx=5)

            ctk.CTkLabel(self, text="тема").grid(row=2, column=0, pady=5, padx=5)
            self.titlea = ctk.CTkEntry(self, width=300)
            self.titlea.grid(row=2, column=1, pady=5, padx=5)

            ctk.CTkLabel(self, text="предмет").grid(row=3, column=0, pady=5, padx=5)
            self.subjecta = ctk.CTkEntry(self, width=300)
            self.subjecta.grid(row=3, column=1, pady=5, padx=5)

            ctk.CTkButton(self, text="Отмена", width=100, command=self.quit_win).grid(row=5, column=0, pady=5, padx=5)
            ctk.CTkButton(self, text="Добавить", width=100, command=self.add).grid(row=5, column=1, pady=5, padx=5, sticky="e")

        elif operation == "delete":
            self.title("Удаление")
            ctk.CTkLabel(self, text="Вы действиельно хотите\n удалить запись из таблицы 'Дисциплины'?"
                         ).grid(row=0, column=0, pady=5, padx=5, columnspan=2)

            ctk.CTkLabel(self, text=f"{self.select_id_disciplinea}. {self.select_titlea}. {self.select_subjecta}"
                         ).grid(row=1, column=0, pady=5, padx=5, columnspan=2)

            ctk.CTkButton(self, text="Нет", width=100, command=self.quit_win).grid(row=2, column=0, pady=5, padx=5, sticky="w")
            ctk.CTkButton(self, text="Да", width=100, command=self.delete).grid(row=2, column=1, pady=5, padx=5, sticky="e")

        elif operation == "change":
            self.title("Изменение в таблице 'Дисциплины'")
            ctk.CTkLabel(self, text="Назввание поля").grid(row=0, column=0, pady=5, padx=5)
            ctk.CTkLabel(self, text="Текущее значение").grid(row=0, column=1, pady=5, padx=5)
            ctk.CTkLabel(self, text="Новое занчение").grid(row=0, column=2, pady=5, padx=5)

            ctk.CTkLabel(self, text="id дисциплины").grid(row=1, column=0, pady=5, padx=5)
            ctk.CTkLabel(self, text=self.select_id_disciplinea).grid(row=1, column=1, pady=5, padx=5)
            self.id_disciplinea = ctk.CTkEntry(self, width=300)
            self.id_disciplinea.grid(row=1, column=2, pady=5, padx=5)
    
            ctk.CTkLabel(self, text="тема").grid(row=2, column=0, pady=5, padx=5)
            ctk.CTkLabel(self, text=self.select_titlea).grid(row=2, column=1, pady=5, padx=5)
            self.titlea = ctk.CTkEntry(self, width=300)
            self.titlea.grid(row=2, column=2, pady=5, padx=5)

            ctk.CTkLabel(self, text="предмет").grid(row=3, column=0, pady=5, padx=5)
            ctk.CTkLabel(self, text=self.select_subjecta).grid(row=3, column=1, pady=5, padx=5)
            self.subjecta = ctk.CTkEntry(self, width=300)
            self.subjecta.grid(row=3, column=2, pady=5, padx=5)        

            ctk.CTkButton(self, text="Отмена", width=100, command=self.quit_win).grid(row=4, column=0, pady=5, padx=5)
            ctk.CTkButton(self, text="Сохранить", width=100, command=self.change).grid(row=4, column=2, pady=5, padx=5,
                                                                                       sticky="e")

    def quit_win(self):
        win.deiconify()
        win.update_table()
        self.destroy()

    def add(self):
        new_id_disciplinea = self.id_disciplinea.get()
        new_titlea = self.titlea.get()
        new_subjecta = self.subjecta.get()

        if new_id_disciplinea != "":
            try:
                conn = sqlite3.connect("journal_bd.db")
                cursor = conn.cursor()

                # Проверяем, существует ли запись с таким id_discipline
                cursor.execute("SELECT * FROM discipline WHERE id_discipline=?", (new_id_disciplinea,))
                existing_record = cursor.fetchone()

                if existing_record:
                    showerror(title="Ошибка", message="Запись с таким id_discipline уже существует.")
                else:
                    # Если запись не существует, добавляем новую
                    cursor.execute(
                    "INSERT INTO discipline (id_discipline, 'title', subject) VALUES (?, ?, ?)",
                    (new_id_disciplinea, new_titlea, new_subjecta))
                    conn.commit()
                    conn.close()
                    self.quit_win()

            except sqlite3.Error as e:
                showerror(title="Ошибка", message=str(e))
        else:
            showerror(title="Ошибка", message="Заполните все поля")


    def delete(self):
        try:
            conn = sqlite3.connect("journal_bd.db")
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM discipline WHERE id_discipline = ?", (self.select_id_disciplinea,))
            conn.commit()
            conn.close()
            self.quit_win()
        except sqlite3.Error as e:
            showerror(title="Ошибка", message=str(e))

    def change(self):
        new_id_disciplinea = self.id_disciplinea.get() or self.select_id_disciplinea
        new_titlea = self.titlea.get() or self.select_titlea
        new_subjecta = self.subjecta.get() or self.select_subjecta
    
        try:
            conn = sqlite3.connect("journal_bd.db")
            cursor = conn.cursor()
            cursor.execute(f"""
                    UPDATE discipline SET (id_discipline, title, subject) = (?, ?, ?)  WHERE id_discipline= {self.select_id_disciplinea}
                """, (new_id_disciplinea, new_titlea, new_subjecta))
            conn.commit()
            conn.close()
            self.quit_win()
        except sqlite3.Error as e:
            showerror(title="Ошибка", message=str(e))

class WindowTeacher(ctk.CTkToplevel):
    def __init__(self, operation, select_row=None):
        super().__init__()
        self.protocol('WM_DELETE_WINDOW', lambda: self.quit_win())

        conn = sqlite3.connect("journal_bd.db")

        conn.close

        if select_row:
            self.select_id_teacher = select_row[0]
            self.select_namea = select_row[1]
            self.select_surnamea = select_row[2]
            self.select_experience = select_row[3]

        if operation == "add":
            self.title("Добаление")
            ctk.CTkLabel(self, text="Добаление в таблицу 'Преподователи'").grid(row=0, column=0, pady=5, padx=5,
                                                                           columnspan=2)

            ctk.CTkLabel(self, text="id Преподователя").grid(row=1, column=0, pady=5, padx=5)
            self.id_teacher = ctk.CTkEntry(self, width=300)
            self.id_teacher.grid(row=1, column=1, pady=5, padx=5)

            ctk.CTkLabel(self, text="Имя").grid(row=2, column=0, pady=5, padx=5)
            self.namea = ctk.CTkEntry(self, width=300)
            self.namea.grid(row=2, column=1, pady=5, padx=5)

            ctk.CTkLabel(self, text="Фамилия").grid(row=3, column=0, pady=5, padx=5)
            self.surnamea = ctk.CTkEntry(self, width=300)
            self.surnamea.grid(row=3, column=1, pady=5, padx=5)

            ctk.CTkLabel(self, text="Стаж").grid(row=4, column=0, pady=5, padx=5)
            self.experience = ctk.CTkEntry(self, width=300)
            self.experience.grid(row=4, column=1, pady=5, padx=5)

            ctk.CTkButton(self, text="Отмена", width=100, command=self.quit_win).grid(row=5, column=0, pady=5, padx=5)
            ctk.CTkButton(self, text="Добавить", width=100, command=self.add).grid(row=5, column=1, pady=5, padx=5, sticky="e")

        elif operation == "delete":
            self.title("Удаление")
            ctk.CTkLabel(self, text="Вы действиельно хотите\n удалить запись из таблицы 'Преподователи'?"
                         ).grid(row=0, column=0, pady=5, padx=5, columnspan=2)

            ctk.CTkLabel(self, text=f"{self.select_id_teacher}. {self.select_namea}. {self.select_surnamea}. {self.select_experience}"
                         ).grid(row=1, column=0, pady=5, padx=5, columnspan=2)

            ctk.CTkButton(self, text="Нет", width=100, command=self.quit_win).grid(row=2, column=0, pady=5, padx=5, sticky="w")
            ctk.CTkButton(self, text="Да", width=100, command=self.delete).grid(row=2, column=1, pady=5, padx=5, sticky="e")

        elif operation == "change":
            self.title("Изменение в таблице 'Преподаватели'")
            ctk.CTkLabel(self, text="Назввание поля").grid(row=0, column=0, pady=5, padx=5)
            ctk.CTkLabel(self, text="Текущее значение").grid(row=0, column=1, pady=5, padx=5)
            ctk.CTkLabel(self, text="Новое занчение").grid(row=0, column=2, pady=5, padx=5)

            ctk.CTkLabel(self, text="id Преподавателя").grid(row=1, column=0, pady=5, padx=5)
            ctk.CTkLabel(self, text=self.select_id_teacher).grid(row=1, column=1, pady=5, padx=5)
            self.id_teacher = ctk.CTkEntry(self, width=300)
            self.id_teacher.grid(row=1, column=2, pady=5, padx=5)

            ctk.CTkLabel(self, text="Имя").grid(row=2, column=0, pady=5, padx=5)
            ctk.CTkLabel(self, text=self.select_namea).grid(row=2, column=1, pady=5, padx=5)
            self.namea = ctk.CTkEntry(self, width=300)
            self.namea.grid(row=2, column=2, pady=5, padx=5)

            ctk.CTkLabel(self, text="Фамилия").grid(row=3, column=0, pady=5, padx=5)
            ctk.CTkLabel(self, text=self.select_surnamea).grid(row=3, column=1, pady=5, padx=5)
            self.surnamea = ctk.CTkEntry(self, width=300)
            self.surnamea.grid(row=3, column=2, pady=5, padx=5)

            ctk.CTkLabel(self, text="Стаж").grid(row=4, column=0, pady=5, padx=5)
            ctk.CTkLabel(self, text=self.select_experience).grid(row=3, column=1, pady=5, padx=5)
            self.experience = ctk.CTkEntry(self, width=300)
            self.experience.grid(row=4, column=2, pady=5, padx=5)

            ctk.CTkButton(self, text="Отмена", width=100, command=self.quit_win).grid(row=5, column=0, pady=5, padx=5)
            ctk.CTkButton(self, text="Сохранить", width=100, command=self.change).grid(row=5, column=2, pady=5, padx=5,
                                                                                       sticky="e")

    def quit_win(self):
        win.deiconify()
        win.update_table()
        self.destroy()

    def add(self):
        new_id_teacher = self.id_teacher.get()
        new_namea = self.namea.get()
        new_surname = self.surnamea.get()
        new_experience= self.experience.get()

        if new_id_teacher != "" and new_id_teacher != "":
            try:
                conn = sqlite3.connect("journal_bd.db")
                cursor = conn.cursor()

                # Проверка наличия записи с таким же id_teacher
                cursor.execute("SELECT * FROM teacher WHERE id_teacher=?", (new_id_teacher,))
                existing_record = cursor.fetchone()

                if existing_record:
                    # Если запись существует, можно обновить ее или выполнить другие действия
                    showerror(title="Ошибка", message="Запись с таким id_teacher уже существует.")
                else:
                    # Если записи не существует, можно выполнить вставку
                    cursor.execute(
                    "INSERT INTO teacher (id_teacher, name, surname, experience) VALUES (?, ?, ?, ?)",
                    (new_id_teacher, new_namea, new_surname, new_experience)
                    )
                    conn.commit()
                    conn.close()
                    self.quit_win()

            except sqlite3.Error as e:
                showerror(title="Ошибка", message=str(e))
        else:
            showerror(title="Ошибка", message="Заполните все поля")

    def delete(self):
        try:
            conn = sqlite3.connect("journal_bd.db")
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM teacher WHERE id_teacher = ?", (self.select_id_teacher,))
            conn.commit()
            conn.close()
            self.quit_win()
        except sqlite3.Error as e:
            showerror(title="Ошибка", message=str(e))

    def change(self):
        new_id_teacher = self.id_teacher.get() or self.select_id_teacher
        new_namea = self.namea.get() or self.select_namea
        new_surname = self.surnamea.get() or self.select_surnamea
        new_experience=self.experience.get() or self.select_experience
        try:
            conn = sqlite3.connect("journal_bd.db")
            cursor = conn.cursor()
            cursor.execute(f"""
                        UPDATE teacher SET (id_teacher, name, surname, experience) = (?, ?, ?,?)  WHERE id_teacher = {self.select_id_teacher}
                    """, (new_id_teacher, new_namea, new_surname, new_experience))
            conn.commit()
            conn.close()
            self.quit_win()
        except sqlite3.Error as e:
            showerror(title="Ошибка", message=str(e))


class WindowStudent(ctk.CTkToplevel):
    def __init__(self, operation, select_row=None):
        super().__init__()
        self.protocol('WM_DELETE_WINDOW', lambda: self.quit_win())

        conn = sqlite3.connect("journal_bd.db")
        conn.close()  # исправление: добавить скобки к методу close

        if select_row:
            self.select_id_student = select_row[0]
            self.select_namei = select_row[1]
            self.select_surnamei = select_row[2]
            self.select_course_ofstudy = select_row[3]

        if operation == "add":
            self.title("Добаление")
            ctk.CTkLabel(self, text="Добаление в таблицу 'Студенты'").grid(row=0, column=0, pady=5, padx=5,
                                                                           columnspan=2)

            ctk.CTkLabel(self, text="id студента").grid(row=1, column=0, pady=5, padx=5)
            self.id_student = ctk.CTkEntry(self, width=300)
            self.id_student.grid(row=1, column=1, pady=5, padx=5)

            ctk.CTkLabel(self, text="Имя").grid(row=2, column=0, pady=5, padx=5)
            self.namei= ctk.CTkEntry(self, width=300)
            self.namei.grid(row=2, column=1, pady=5, padx=5)

            ctk.CTkLabel(self, text="Фамилия").grid(row=3, column=0, pady=5, padx=5)
            self.surnamei = ctk.CTkEntry(self, width=300)
            self.surnamei.grid(row=3, column=1, pady=5, padx=5)

            ctk.CTkLabel(self, text="Курс обучения").grid(row=4, column=0, pady=5, padx=5)
            self.course_ofstudy = ctk.CTkEntry(self, width=300)
            self.course_ofstudy.grid(row=4, column=1, pady=5, padx=5)  

            ctk.CTkButton(self, text="Отмена", width=100, command=self.quit_win).grid(row=5, column=0, pady=5, padx=5)
            ctk.CTkButton(self, text="Добавить", width=100, command=self.add).grid(row=5, column=1, pady=5, padx=5, sticky="e")

        elif operation == "delete":
            self.title("Удаление")
            ctk.CTkLabel(self, text="Вы действиельно хотите\n удалить запись из таблицы 'Студенты'?"
                         ).grid(row=0, column=0, pady=5, padx=5, columnspan=2)

            ctk.CTkLabel(self, text=f"{self.select_id_student}. {self.select_namei}. {self.select_surnamei}. {self.select_course_ofstudy}"
                         ).grid(row=1, column=0, pady=5, padx=5, columnspan=2)

            ctk.CTkButton(self, text="Нет", width=100, command=self.quit_win).grid(row=2, column=0, pady=5, padx=5, sticky="w")
            ctk.CTkButton(self, text="Да", width=100, command=self.delete).grid(row=2, column=1, pady=5, padx=5, sticky="e")

        elif operation == "change":
            self.title("Изменение в таблице 'Студенты'")
            ctk.CTkLabel(self, text="Назввание поля").grid(row=0, column=0, pady=5, padx=5)
            ctk.CTkLabel(self, text="Текущее значение").grid(row=0, column=1, pady=5, padx=5)
            ctk.CTkLabel(self, text="Новое занчение").grid(row=0, column=2, pady=5, padx=5)

            ctk.CTkLabel(self, text="Студенты").grid(row=1, column=0, pady=5, padx=5)
            ctk.CTkLabel(self, text=self.select_id_student).grid(row=1, column=1, pady=5, padx=5)
            self.id_student = ctk.CTkEntry(self, width=300)
            self.id_student.grid(row=1, column=2, pady=5, padx=5)

            ctk.CTkLabel(self, text="Имя").grid(row=2, column=0, pady=5, padx=5)
            ctk.CTkLabel(self, text=self.select_namei).grid(row=2, column=1, pady=5, padx=5)
            self.namei = ctk.CTkEntry(self, width=300)
            self.namei.grid(row=2, column=2, pady=5, padx=5)

            ctk.CTkLabel(self, text="Фамилия").grid(row=3, column=0, pady=5, padx=5)
            ctk.CTkLabel(self, text=self.select_surnamei).grid(row=3, column=1, pady=5, padx=5)
            self.surnamei = ctk.CTkEntry(self, width=300)
            self.surnamei.grid(row=3, column=2, pady=5, padx=5)

            ctk.CTkLabel(self, text="Курс обучения").grid(row=4, column=0, pady=5, padx=5)
            ctk.CTkLabel(self, text=self.select_course_ofstudy).grid(row=4, column=1, pady=5, padx=5)
            self.course_ofstudy = ctk.CTkEntry(self, width=300)
            self.course_ofstudy.grid(row=4, column=2, pady=5, padx=5)

            ctk.CTkButton(self, text="Отмена", width=100, command=self.quit_win).grid(row=5, column=0, pady=5, padx=5)
            ctk.CTkButton(self, text="Сохранить", width=100, command=self.change).grid(row=5, column=2, pady=5, padx=5,
                                                                                       sticky="e")

    def quit_win(self):
        win.deiconify()
        win.update_table()
        self.destroy()

    def add(self):
        new_id_student = self.id_student.get()
        new_namei = self.namei.get()
        new_surnamei = self.surnamei.get()
        new_course_ofstudy = self.course_ofstudy.get()

        if new_id_student != "" and new_id_student != "":
            try:
                conn = sqlite3.connect("journal_bd.db")
                cursor = conn.cursor()

                # Проверка наличия записи с таким же id_student
                cursor.execute("SELECT * FROM student WHERE id_student=?", (new_id_student,))
                existing_record = cursor.fetchone()

                if existing_record:
                    # Если запись существует, можно обновить ее или выполнить другие действия
                    showerror(title="Ошибка", message="Запись с таким id_student уже существует.")
                else:
                    # Если запись не существует, можно выполнить вставку
                    cursor.execute(
                        "INSERT INTO student (id_student, name, surname, course_ofstudy) VALUES (?,?,?,?)",
                        (new_id_student, new_namei, new_surnamei, new_course_ofstudy)
                    )
                    conn.commit()
                    conn.close()
                    self.quit_win()

            except sqlite3.Error as e:
                showerror(title="Ошибка", message=str(e))
        else:
            showerror(title="Ошибка", message="Заполните все поля")
    def delete(self):
        try:
            conn = sqlite3.connect("journal_bd.db")
            cursor = conn.cursor()
            # исправление: передача параметра как кортежа
            cursor.execute(f"DELETE FROM student WHERE id_student = ?", (self.select_id_student,))
            conn.commit()
            conn.close()
            self.quit_win()
        except sqlite3.Error as e:
            showerror(title="Ошибка", message=str(e))

    def change(self):
        new_id_student = self.id_student.get() or self.select_id_student
        new_namei = self.namei.get() or self.select_namei
        new_surnamei = self.surnamei.get() or self.select_surnamei
        new_course_ofstudy = self.course_ofstudy.get() or self.select_course_ofstudy
        try:
            conn = sqlite3.connect("journal_bd.db")
            cursor = conn.cursor()
            cursor.execute(f"""
                        UPDATE student SET (id_student, name, surname, course_ofstudy ) = (?, ?, ?,?)  WHERE id_student= {self.select_id_student}
                    """, (new_id_student, new_namei, new_surnamei, new_course_ofstudy))
            conn.commit()
            conn.close()
            self.quit_win()
        except sqlite3.Error as e:
            showerror(title="Ошибка", message=str(e))


class Windowgroup(ctk.CTkToplevel):
    def __init__(self, operation, select_row=None):
        super().__init__()
        self.protocol('WM_DELETE_WINDOW', lambda: self.quit_win())

        conn = sqlite3.connect("journal_bd.db")

        conn.close()

        if select_row:
            self.select_id_groupe = select_row[0]
            self.select_curatora = select_row[1]
            self.select_number_groupe = select_row[2]
            
        if operation == "add":
            self.title("Добаление")
            ctk.CTkLabel(self, text="Добаление в таблицу 'Группы'").grid(row=0, column=0, pady=5, padx=5,
                                                                           columnspan=2)

            ctk.CTkLabel(self, text="id группы").grid(row=1, column=0, pady=5, padx=5)
            self.id_groupe = ctk.CTkEntry(self, width=300)
            self.id_groupe.grid(row=1, column=1, pady=5, padx=5)

            ctk.CTkLabel(self, text="Куратор ").grid(row=2, column=0, pady=5, padx=5)
            self.curatora = ctk.CTkEntry(self, width=300)
            self.curatora.grid(row=2, column=1, pady=5, padx=5)

            ctk.CTkLabel(self, text="Номер группы").grid(row=3, column=0, pady=5, padx=5)
            self.number_groupe = ctk.CTkEntry(self, width=300)
            self.number_groupe.grid(row=3, column=1, pady=5, padx=5)

            ctk.CTkButton(self, text="Отмена", width=100, command=self.quit_win).grid(row=6, column=0, pady=5, padx=5)
            ctk.CTkButton(self, text="Добавить", width=100, command=self.add).grid(row=6, column=1, pady=5, padx=5, sticky="e")

        elif operation == "delete":
            self.title("Удаление")
            ctk.CTkLabel(self, text="Вы действиельно хотите\n удалить запись из таблицы 'Группы'?"
                         ).grid(row=0, column=0, pady=5, padx=5, columnspan=2)

            ctk.CTkLabel(self, text=f"{self.select_id_groupe}. {self.select_curatora}. {self.select_number_groupe}"
                         ).grid(row=1, column=0, pady=5, padx=5, columnspan=2)

            ctk.CTkButton(self, text="Нет", width=100, command=self.quit_win).grid(row=2, column=0, pady=5, padx=5, sticky="w")
            ctk.CTkButton(self, text="Да", width=100, command=self.delete).grid(row=2, column=1, pady=5, padx=5, sticky="e")

        elif operation == "change":
            self.title("Изменение в таблице 'Группы'")
            ctk.CTkLabel(self, text="Назввание поля").grid(row=0, column=0, pady=5, padx=5)
            ctk.CTkLabel(self, text="Текущее значение").grid(row=0, column=1, pady=5, padx=5)
            ctk.CTkLabel(self, text="Новое занчение").grid(row=0, column=2, pady=5, padx=5)

            ctk.CTkLabel(self, text="id группы").grid(row=1, column=0, pady=5, padx=5)
            ctk.CTkLabel(self, text=self.select_id_groupe).grid(row=1, column=1, pady=5, padx=5)
            self.id_groupe = ctk.CTkEntry(self, width=300)
            self.id_groupe.grid(row=1, column=2, pady=5, padx=5)

            ctk.CTkLabel(self, text="Куратор").grid(row=2, column=0, pady=5, padx=5)
            ctk.CTkLabel(self, text=self.select_curatora).grid(row=2, column=1, pady=5, padx=5)
            self.curatora = ctk.CTkEntry(self, width=300)
            self.curatora.grid(row=2, column=2, pady=5, padx=5)

            ctk.CTkLabel(self, text="Номер группы").grid(row=3, column=0, pady=5, padx=5)
            ctk.CTkLabel(self, text=self.select_number_groupe).grid(row=3, column=1, pady=5, padx=5)
            self.number_groupe = ctk.CTkEntry(self, width=300)
            self.number_groupe.grid(row=3, column=2, pady=5, padx=5)

            ctk.CTkButton(self, text="Отмена", width=100, command=self.quit_win).grid(row=5, column=0, pady=5, padx=5)
            ctk.CTkButton(self, text="Сохранить", width=100, command=self.change).grid(row=5, column=2, pady=5, padx=5,
                                                                                       sticky="e")

    def quit_win(self):
        win.deiconify()
        win.update_table()
        self.destroy()

    def add(self):
        new_id_groupe = self.id_groupe.get()
        new_curatora = self.curatora.get()
        new_number_groupe = self.number_groupe.get()

        if new_id_groupe and new_curatora and new_number_groupe:

            try:
                conn = sqlite3.connect("journal_bd.db")
                cursor = conn.cursor()
                cursor.execute(
                    '''INSERT INTO 'group' (id_groupe, curator, number_groupe) VALUES (?, ?, ?)''',
                    (new_id_groupe, new_curatora, new_number_groupe))
                conn.commit()
                conn.close()
                self.quit_win()
            except sqlite3.Error as e:
                showerror(title="Ошибка", message=str(e))
        else:
            showerror(title="Ошибка", message="Заполните все поля")

    def delete(self):
        try:
            conn = sqlite3.connect("journal_bd.db")
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM 'group' WHERE id_groupe = ?", (self.select_id_groupe,))
            conn.commit()
            conn.close()
            self.quit_win()
        except sqlite3.Error as e:
            showerror(title="Ошибка", message=str(e))

    def change(self):
        new_id_groupe = self.id_groupe.get() or self.select_id_groupe
        new_curatora = self.curatora.get() or self.select_curatora
        new_number_groupe = self.number_groupe.get() or self.select_number_groupe
     
        try:
            conn = sqlite3.connect("journal_bd.db")
            cursor = conn.cursor()
            cursor.execute("""
                        UPDATE 'group' SET id_groupe=?, curator=?, number_groupe=? WHERE id_groupe=?
                        """, (new_id_groupe, new_curatora, new_number_groupe, self.select_id_groupe))

            conn.commit()
            conn.close()
            self.quit_win()
        except sqlite3.Error as e:
            showerror(title="Ошибка", message=str(e))

if __name__ == "__main__":
    win = WindowMain()
    win.mainloop()