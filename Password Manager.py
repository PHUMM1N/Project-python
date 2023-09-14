from tkinter import *
import sqlite3
from tkinter import messagebox
from tkinter import simpledialog

root = Tk()
root.title("Password Manager")
root.configure(bg="#E8f1fd")  
background_image = Label(root, bg="#E8F1FD")
background_image.grid(row=0, column=0, columnspan=2)  

# Database file path
db_file_path = r"D:\python work\security.db"
logged_in_user_id = None  
collected_data = []
websites_listbox = None  


def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width / 2) - (width / 2)
    y = (screen_height / 2) - (height / 2)
    window.geometry(f'{width}x{height}+{int(x)}+{int(y)}')


def create_user():
    conn = sqlite3.connect(db_file_path)
    cursor = conn.cursor()
    regisusername = regis_username_entry.get()
    regispassword = regis_password_entry.get()
    cursor.execute('INSERT INTO users VALUES (?, ?)', (regisusername, regispassword))
    conn.commit()
    conn.close()
    regis_username_entry.delete(0, END)
    regis_password_entry.delete(0, END)
    messagebox.showinfo("Create User", "User created successfully!")


def create_table():
    conn = sqlite3.connect(db_file_path)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS passwords
                      (website TEXT, username TEXT, password TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS users
                      (id INTEGER PRIMARY KEY, username TEXT, password TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS collected_data
                      (user_id INTEGER, website TEXT, username TEXT, password TEXT)''')
    conn.commit()
    conn.close()


def load_collected_data():
    global collected_data
    collected_data.clear()
    conn = sqlite3.connect(db_file_path)
    cursor = conn.cursor()
    cursor.execute('SELECT website, username, password FROM collected_data WHERE user_id=?', (logged_in_user_id,))
    rows = cursor.fetchall()
    conn.close()
    for row in rows:
        collected_data.append(row)


def login():
    global logged_in_user_id
    conn = sqlite3.connect(db_file_path)
    cursor = conn.cursor()
    username = username_entry.get()
    password = password_entry.get()
    cursor.execute('SELECT rowid FROM users WHERE username=? AND password=?',( username, password))
    user_id = cursor.fetchone()
   
    conn.close()
    if user_id:
        logged_in_user_id = user_id[0]
        messagebox.showinfo("Login Successful", "Login successful!")
        root.withdraw()
        load_collected_data()  
        show_main_window1()
    else:
        messagebox.showerror("Error", "Login failed. Please check your username and password.")


def delete_password_window():
    global collected_data  

    delete_window = Toplevel()
    delete_window.title("Delete Password")
    delete_window.configure(bg="#E8f1fd") 

    def delete_selected_password():
        selected_index = passwords_listbox.curselection()
        if not selected_index:
            messagebox.showwarning("No Selection", "Please select a password entry to delete.")
            return

        selected_details = passwords_listbox.get(selected_index[0])  
        selected_website = selected_details.split(',')[0].split(': ')[1].strip()  

        conn = sqlite3.connect(db_file_path)
        cursor = conn.cursor()

        
        cursor.execute('SELECT rowid FROM users WHERE username=?', (username_entry.get(),))
        user_id = cursor.fetchone()[0]

        cursor.execute('DELETE FROM collected_data WHERE user_id=? AND website=?', (user_id, selected_website))
        conn.commit()
        conn.close()

       
        collected_data_copy = collected_data.copy()
        for item in collected_data_copy:
            if item[0] == selected_website:
                collected_data.remove(item)

        passwords_listbox.delete(selected_index)
        messagebox.showinfo("Delete Password", f"Password for '{selected_website}' deleted successfully!")

    
    passwords_listbox = Listbox(delete_window, height=20, width=60, bg="#FFFFFF") 
    passwords_listbox.pack(fill=BOTH, expand=True)

   
    for item in collected_data:
        passwords_listbox.insert(END, f"Website: {item[0]}, Username: {item[1]}, Password: {item[2]}")

    delete_button = Button(delete_window, text="Delete Password", command=delete_selected_password, bg="#FF6347", fg="white")  
    delete_button.pack()


def change_selected_password_window():
    global collected_data

    change_window = Toplevel()
    change_window.title("Change Password")
    change_window.configure(bg="white")  

    def change_selected_password():
        selected_index = passwords_listbox.curselection()
        if not selected_index:
            messagebox.showwarning("No Selection", "Please select a password entry to change.")
            return

        selected_details = passwords_listbox.get(selected_index[0])
        selected_website = selected_details.split(',')[0].split(': ')[1].strip()

        new_website = simpledialog.askstring("Change Password", "Enter new website 🌍:", parent=change_window)
        new_username = simpledialog.askstring("Change Password", "Enter new username 👤:", parent=change_window)
        new_password = simpledialog.askstring("Change Password", "Enter new password 🗝:", parent=change_window)

        if new_website and new_username and new_password:
            conn = sqlite3.connect(db_file_path)
            cursor = conn.cursor()

            cursor.execute('SELECT rowid FROM users WHERE username=?', (username_entry.get(),))
            user_id = cursor.fetchone()[0]

            item_index = None
            for i, item in enumerate(collected_data):
                if item[0] == selected_website:
                    item_index = i
                    break

            if item_index is not None:
                updated_item = (new_website, new_username, new_password)
                collected_data[item_index] = updated_item

                cursor.execute('UPDATE collected_data SET website=?, username=?, password=? WHERE user_id=? AND website=?',
                               (new_website, new_username, new_password, user_id, selected_website))
                conn.commit()
                conn.close()

                load_collected_data()
                passwords_listbox.delete(0, END)
                for item in collected_data:
                    passwords_listbox.insert(END, f"Website: {item[0]}, Username: {item[1]}, Password : {item[2]}")

                messagebox.showinfo("Change Password", "Password updated successfully!")

    passwords_listbox = Listbox(change_window, height=20, width=60, bg="#FFFFFF") 
    passwords_listbox.pack(fill=BOTH, expand=True)

    for item in collected_data:
        passwords_listbox.insert(END, f"Website🌍: {item[0]}  Username 👤: {item[1]} Password🗝: {item[2]}",)


    change_button = Button(change_window, text="Change Password", command=change_selected_password, bg="#4CAF50", fg="white")  
    change_button.pack()

def show_main_window1():
    main_window = Toplevel()
    main_window.title("Password Manager")
    main_window.configure(bg="#E8f1fd")  

  
    main_window.geometry("400x300")
    center_window(main_window, 400, 300)
    menu= Label(main_window, text="MENU",width=50).pack()

    import_button = Button(main_window, text="Add Password ➕", command=show_import, width=20, bg="#FFFAFA", fg="Black")  
    import_button.pack(pady=10)

    search_button = Button(main_window, text="Search Passwords 🔍", command=search_data, width=20, bg="#FFFAFA", fg="Black")  
    search_button.pack()

    change_password_button = Button(main_window, text="Change Password 🔧", command=change_selected_password_window, width=20, bg="#FFFAFA", fg="Black")  
    change_password_button.pack(pady=10)

    delete_password_button = Button(main_window, text="Delete Password 🗑", command=delete_password_window, width=20, bg="#FFFAFA", fg="Black")  
    delete_password_button.pack()

    

   
def import_data(lead_window, import_website_entry, import_username_entry, import_password_entry):
    conn = sqlite3.connect(db_file_path)
    cursor = conn.cursor()
    website_add = import_website_entry.get()
    username_add = import_username_entry.get()
    password_add = import_password_entry.get()
    cursor.execute('INSERT INTO passwords VALUES (?, ?, ?)', (website_add, username_add, password_add))
    cursor.execute('INSERT INTO collected_data VALUES (?, ?, ?, ?)', (logged_in_user_id, website_add, username_add, password_add))
    conn.commit()
    conn.close()
    import_website_entry.delete(0, END)
    import_username_entry.delete(0, END)
    import_password_entry.delete(0, END)
    collected_data.append((website_add, username_add, password_add))
    messagebox.showinfo("Import Data", "Data imported successfully!")
    lead_window.destroy()  


def search_data():
    search_window = Toplevel()
    search_window.title("Search Passwords")
    search_window.configure(bg="#E8f1fd")  

   
    search_window.geometry("400x300")
    center_window(search_window, 400, 300)

    data_listbox = Listbox(search_window, height=15, width=60, bg="#FFFFFF")  
    data_listbox.pack(fill=BOTH, expand=True, padx=10, pady=10)

    for item in collected_data:
        data_listbox.insert(END, f"Website 🌍: {item[0]},Username 👤: {item[1]}, Password 🗝: {item[2]}")

    search_window.mainloop()



def show_import():
    lead_window = Toplevel()
    lead_window.title("Add Password")

    
    lead_window.geometry("400x200")
    center_window(lead_window, 400, 200)

    import_website_label = Label(lead_window, text="Website 🌎:", font=("Arial", 12), bg="#E6E6E6")  
    import_website_label.grid(row=0, column=0, padx=10, pady=5)
    import_website_entry = Entry(lead_window, width=30, font=("Arial", 12))
    import_website_entry.grid(row=0, column=1, padx=10, pady=5)

    import_username_label = Label(lead_window, text="Username 👤:", font=("Arial", 12), bg="#E6E6E6")  
    import_username_label.grid(row=1, column=0, padx=10, pady=5)
    import_username_entry = Entry(lead_window, width=30, font=("Arial", 12))
    import_username_entry.grid(row=1, column=1, padx=10, pady=5)

    import_password_label = Label(lead_window, text="Password 🗝:", font=("Arial", 12), bg="#E6E6E6")  
    import_password_label.grid(row=2, column=0, padx=10, pady=5)
    import_password_entry = Entry(lead_window, width=30, font=("Arial", 12))
    import_password_entry.grid(row=2, column=1, padx=10, pady=5)

    save_button = Button(lead_window, text="Save", command=lambda: import_data(lead_window, import_website_entry, import_username_entry, import_password_entry), width=20, font=("Arial", 12), bg="#4CAF50", fg="white")  # Set button color
    save_button.grid(row=3, column=1, padx=10, pady=10)

create_table()

username_label = Label(root, text="Username 👤:", font=("Arial", 12))  
username_label.grid(row=0, column=0, padx=10, pady=5)
username_entry = Entry(root, font=("Arial", 12))
username_entry.grid(row=0, column=1, padx=10, pady=5)
password_label = Label(root, text="Password 🗝:", font=("Arial", 12) )  
password_label.grid(row=1, column=0, padx=10, pady=5)
password_entry = Entry(root, show="*", font=("Arial", 12))
password_entry.grid(row=1, column=1, padx=10, pady=5)
login_button = Button(root, text="Login", command=login, width=20, font=("Arial", 12), bg="#99CCFF", fg="#000000") 
login_button.grid(row=2, column=1, padx=10, pady=10)

regis_username = Label(root, text="New username 👤:", font=("Arial", 12), )  
regis_username.grid(row=3, column=0, padx=10, pady=5)
regis_username_entry = Entry(root, font=("Arial", 12))
regis_username_entry.grid(row=3, column=1, padx=10, pady=5)
regis_password = Label(root, text="Password 🗝:", font=("Arial", 12), )  
regis_password.grid(row=4, column=0, padx=10, pady=5)
regis_password_entry = Entry(root, font=("Arial", 12))
regis_password_entry.grid(row=4, column=1, padx=10, pady=5)
regis_button = Button(root, text="Register", command=create_user, width=20, font=("Arial", 12), bg="#FFE4B5", fg="#000000")  
regis_button.grid(row=5, column=1, padx=10, pady=10)

root.geometry("400x300")
center_window(root, 400, 300)
root.mainloop()
