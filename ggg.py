import tkinter as tk
from tkinter import ttk
import psycopg2
from config import DATABASE, USER, PASSWORD, HOST, PORT
import hashlib
# Глобальные переменные для подключения и авторизации
conn = None
cursor = None
current_user = None

# Функции для работы с базой данных
def connect_to_db():
    global conn, cursor
    try:
        conn = psycopg2.connect(
            database=DATABASE,
            user=USER,
            password=PASSWORD,
            host=HOST,
            port=PORT
        )
        cursor = conn.cursor()
        message_label.config(text="Подключено к базе данных!")
        show_login_window()  # Показываем окно авторизации после успешного подключения
    except Exception as e:
        message_label.config(text=f"Ошибка подключения: {e}")

def disconnect_from_db():
    global conn, cursor
    if conn:
        cursor.close()
        conn.close()
        message_label.config(text="Отключено от базы данных!")


# class login(tk.Toplevel):
#     def __init__(self, master, **kwargs):
#         tk.Toplevel.__init__(self, master, **kwargs)
#         self.geometry('400x300')
#         self.focus_set()
#         master.attributes('-disabled', True)
#         self.protocol("WM_DELETE_WINDOW", self.close)

# Функции для авторизации
def show_login_window():

    global login_window
    login_window = tk.Toplevel(window)
    login_window.geometry('400x300')
    login_window.focus_set()
    window.attributes('-disabled', True)
    # login_window.protocol("WM_DELETE_WINDOW", self.close)
    login_window.attributes('-topmost', True)
    login_window.title("Авторизация")

    username_label = tk.Label(login_window, text="Имя пользователя:")
    username_label.pack()
    global username_entry
    username_entry = tk.Entry(login_window)
    username_entry.pack()

    password_label = tk.Label(login_window, text="Пароль:")
    password_label.pack()
    global password_entry
    password_entry = tk.Entry(login_window, show="*")
    password_entry.pack()

    login_button = tk.Button(login_window, text="Войти", command=login_user)
    login_button.pack()
    login_window.protocol("WM_DELETE_WINDOW", window.destroy)

def login_user():

    username = username_entry.get()
    password_hash = hashlib.md5(password_entry.get().encode('utf-8')).hexdigest()

    try:
        cursor.execute(
            "SELECT * FROM users WHERE username=%s AND password=%s",
            (username, password_hash)
        )
        user = cursor.fetchone()

        if user:
            global current_user
            current_user = user
            login_window.destroy()
            message_label.config(text=f"Авторизация успешна! Добро пожаловать, {username}!")
            window.attributes('-disabled', False)
            window.attributes('-topmost', True)
            enable_app(user[2])  # Включаем интерфейс после авторизации
        else:
            message_label.config(text="Неверный логин или пароль!")
    except Exception as e:
        message_label.config(text=f"Ошибка авторизации: {e}")

# Функции для работы с телефонным справочником (доступны только после авторизации)
def add_contact():
    name = name_entry.get()
    phone = phone_entry.get()
    position = position_entry.get()
    address = address_entry.get()
    relatives = relatives_entry.get()
    notes = notes_entry.get()

    if name and phone:
        try:
            cursor.execute(
                "INSERT INTO contacts (name, phone, position, address, relatives, notes) VALUES (%s, %s, %s, %s, %s, %s)",
                (name, phone, position, address, relatives, notes)
            )
            conn.commit()
            clear_entries()
            update_listbox()
            message_label.config(text="Контакт добавлен!")
        except Exception as e:
            message_label.config(text=f"Ошибка добавления контакта: {e}")
    else:
        message_label.config(text="Введите имя и телефон!")

def delete_contact():
    try:
        selected_index = contact_listbox.curselection()[0]
        selected_id = contact_listbox.get(selected_index)[0]
        cursor.execute("DELETE FROM contacts WHERE id=%s", (selected_id,))
        conn.commit()
        update_listbox()
        message_label.config(text="Контакт удален!")
    except IndexError:
        message_label.config(text="Выберите контакт для удаления!")
    except Exception as e:
        message_label.config(text=f"Ошибка удаления контакта: {e}")

def update_contact():
    try:
        selected_index = contact_listbox.curselection()[0]
        selected_id = contact_listbox.get(selected_index)[0]
        name = name_entry.get()
        phone = phone_entry.get()
        position = position_entry.get()
        address = address_entry.get()
        relatives = relatives_entry.get()
        notes = notes_entry.get()

        if name and phone:
            cursor.execute(
                "UPDATE contacts SET name=%s, phone=%s, position=%s, address=%s, relatives=%s, notes=%s WHERE id=%s",
                (name, phone, position, address, relatives, notes, selected_id)
            )
            conn.commit()
            clear_entries()
            update_listbox()
            message_label.config(text="Контакт обновлен!")
        else:
            message_label.config(text="Введите имя и телефон!")
    except IndexError:
        message_label.config(text="Выберите контакт для обновления!")
    except Exception as e:
        message_label.config(text=f"Ошибка обновления контакта: {e}")

def clear_entries():
    name_entry.delete(0, tk.END)
    phone_entry.delete(0, tk.END)
    position_entry.delete(0, tk.END)
    address_entry.delete(0, tk.END)
    relatives_entry.delete(0, tk.END)
    notes_entry.delete(0, tk.END)

def update_listbox():
    contact_listbox.delete(0, tk.END)
    cursor.execute("SELECT * FROM contacts")
    contacts = cursor.fetchall()
    for contact in contacts:
        contact_listbox.insert(tk.END, f"{contact[0]} {contact[1]} {contact[2]} {contact[3]} {contact[4]} {contact[5]}")

def search_contact():
    search_term = search_entry.get()
    if search_term:
        try:
            cursor.execute(
                "SELECT * FROM contacts WHERE LOWER(name) LIKE LOWER(%s) OR LOWER(phone) LIKE LOWER(%s) OR LOWER(position) LIKE LOWER(%s)",
                (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%")
            )
            contacts = cursor.fetchall()
            contact_listbox.delete(0, tk.END)
            for contact in contacts:
                contact_listbox.insert(
                    tk.END, f"{contact[0]} {contact[1]} {contact[2]} {contact[3]} {contact[4]} {contact[5]}"
                )
        except Exception as e:
            message_label.config(text=f"Ошибка поиска: {e}")
    else:
        update_listbox()

# Функции для управления интерфейсом
def enable_app(user_state):
    # Включаем элементы интерфейса после авторизации
    if user_state =="admin":
        name_entry.config(state=tk.NORMAL)
        phone_entry.config(state=tk.NORMAL)
        position_entry.config(state=tk.NORMAL)
        address_entry.config(state=tk.NORMAL)
        relatives_entry.config(state=tk.NORMAL)
        notes_entry.config(state=tk.NORMAL)
        add_button.config(state=tk.NORMAL)
        delete_button.config(state=tk.NORMAL)
        update_button.config(state=tk.NORMAL)
    search_entry.config(state=tk.NORMAL)
    search_button.config(state=tk.NORMAL)

def disable_app():
    # Отключаем элементы интерфейса до авторизации
    name_entry.config(state=tk.DISABLED)
    phone_entry.config(state=tk.DISABLED)
    position_entry.config(state=tk.DISABLED)
    address_entry.config(state=tk.DISABLED)
    relatives_entry.config(state=tk.DISABLED)
    notes_entry.config(state=tk.DISABLED)
    add_button.config(state=tk.DISABLED)
    delete_button.config(state=tk.DISABLED)
    update_button.config(state=tk.DISABLED)
    search_entry.config(state=tk.DISABLED)
    search_button.config(state=tk.DISABLED)

# Создание основного окна
window = tk.Tk()
window.title("Телефонный справочник")

# Фрейм для элементов ввода (начальное состояние - отключено)
input_frame = tk.Frame(window)
input_frame.pack(pady=20)

# Название контакта
name_label = tk.Label(input_frame, text="Имя:")
name_label.grid(row=0, column=0, padx=5, pady=5)
name_entry = tk.Entry(input_frame, width=30)
name_entry.grid(row=0, column=1, padx=5, pady=5)

# Телефон
phone_label = tk.Label(input_frame, text="Телефон:")
phone_label.grid(row=1, column=0, padx=5, pady=5)
phone_entry = tk.Entry(input_frame, width=30)
phone_entry.grid(row=1, column=1, padx=5, pady=5)

# Должность
position_label = tk.Label(input_frame, text="Должность:")
position_label.grid(row=2, column=0, padx=5, pady=5)
position_entry = tk.Entry(input_frame, width=30)
position_entry.grid(row=2, column=1, padx=5, pady=5)

# Место проживания
address_label = tk.Label(input_frame, text="Адрес:")
address_label.grid(row=3, column=0, padx=5, pady=5)
address_entry = tk.Entry(input_frame, width=30)
address_entry.grid(row=3, column=1, padx=5, pady=5)

# Родственники
relatives_label = tk.Label(input_frame, text="Родственники:")
relatives_label.grid(row=4, column=0, padx=5, pady=5)
relatives_entry = tk.Entry(input_frame, width=30)
relatives_entry.grid(row=4, column=1, padx=5, pady=5)

# Дополнительные сведения
notes_label = tk.Label(input_frame, text="Дополнительные сведения:")
notes_label.grid(row=5, column=0, padx=5, pady=5)
notes_entry = tk.Entry(input_frame, width=30)
notes_entry.grid(row=5, column=1, padx=5, pady=5)

# Кнопки
button_frame = tk.Frame(window)
button_frame.pack(pady=10)

add_button = tk.Button(button_frame, text="Добавить", width=10, command=add_contact)
add_button.grid(row=0, column=0, padx=10, pady=5)

delete_button = tk.Button(button_frame, text="Удалить", width=10, command=delete_contact)
delete_button.grid(row=0, column=1, padx=10, pady=5)

update_button = tk.Button(button_frame, text="Обновить", width=10, command=update_contact)
update_button.grid(row=0, column=2, padx=10, pady=5)

# Поле поиска
search_frame = tk.Frame(window)
search_frame.pack(pady=10)

search_label = tk.Label(search_frame, text="Поиск:")
search_label.pack(side=tk.LEFT)

search_entry = tk.Entry(search_frame, width=30)
search_entry.pack(side=tk.LEFT, padx=5)

search_button = tk.Button(search_frame, text="Искать", command=search_contact)
search_button.pack(side=tk.LEFT)

# Отключение элементов ввода по умолчанию
disable_app()

# Список контактов
contact_listbox = tk.Listbox(window, width=80, height=10)
contact_listbox.pack(pady=20)

# Сообщение
message_label = tk.Label(window, text="")
message_label.pack()


connect_to_db()
window.mainloop()
