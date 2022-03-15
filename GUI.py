import tkinter, Mysqlfuncs, MysqlNewUser
from tkinter import *
from tkinter import ttk, messagebox
from connectDB import mydbfunc
# Defining flags for main.append and main.delete functions
flag_append = False
flag_delete = False
# Defining the root window
root = Tk()

# main function that will contain all GUI besides the login screen
def main():
    # cur_mode is a StringVar used in main.append and main.delete
    global cur_mode
    # Function to retrieve user inputs and store them in Mysql database
    def new_password():
        # Function that takes the inputs and sends them to Mysqlfuncs.storeMysql function when enter_button is pressed
        def enter():
            description = description_entry.get()
            username = username_entry.get()
            password = password_entry.get()
            # if else statement to ensure users can not give empty inputs
            if not description or not username or not password:
                messagebox.showerror("ERROR", "Missing input")
                return
            else:
                Mysqlfuncs.storeMysql(userid, masterpassword, description, username, password)
                search()
                store_window.destroy()

        # New window dedicated to the new_password function
        store_window = Toplevel(root)
        store_window.geometry("150x200")
        store_window.title("Register new password")
        description_label = ttk.Label(store_window, text="description")
        description_entry = ttk.Entry(store_window)
        username_label = ttk.Label(store_window, text="username")
        username_entry = ttk.Entry(store_window)
        password_label = ttk.Label(store_window, text="password")
        password_entry = ttk.Entry(store_window, show="*")
        description_label.grid()
        description_entry.grid()
        username_label.grid()
        username_entry.grid()
        password_label.grid()
        password_entry.grid()
        enter_button = ttk.Button(store_window, text="Enter", command=enter)
        enter_button.grid()

    # append and delete functions are used to change what happens when tree_view entries gets selected by user
    def append():
        # flag_append and flag_delete used to track which mode is in use
        global flag_append, flag_delete
        flag_delete = False
        if not flag_append:
            # Sets the mode to edit mode
            cur_mode.set(value="Current mode: Edit mode")
            tree_view.bind('<<TreeviewSelect>>', item_selected_append)
            flag_append = True
        elif flag_append:
            # Sets the mode to show password mode
            cur_mode.set(value="Current mode: Show password")
            tree_view.bind('<<TreeviewSelect>>', item_selected)
            flag_append = False
    def delete():
        global flag_delete, flag_append
        flag_append = False
        if not flag_delete:
            # Sets the mode to delete mode
            cur_mode.set(value="Current mode: Delete mode")
            tree_view.bind('<<TreeviewSelect>>', item_selected_delete)
            flag_delete = True
        elif flag_delete:
            # Sets the mode to Show password mode
            cur_mode.set(value="Current mode: Show password")
            tree_view.bind('<<TreeviewSelect>>', item_selected)
            flag_delete = False
        return

    # search function is used to filter the shown entries in tree_view and refresh them
    def search(var="", index="", mode=""):
        search_input = search_entry.get()
        search_results = Mysqlfuncs.searchMysql(userid, search_input)
        for row in tree_view.get_children():
            tree_view.delete(row)
        # Error handling for when there are no search results
        try:
            for each in search_results:
                tree_view.insert('', tkinter.END, values=each)
        except TypeError:
            pass

    # Function that creates a new window for user to input new information to replace old ones
    def append_window(userid, masterpassword, description_username, root):
        mydb = mydbfunc(userid)
        mycursor = mydb.cursor(buffered=True)
        append_window = Toplevel(root)
        append_window.title("Edit entries")
        append_window.geometry("200x400")
        description, username = description_username
        description, username = str(description), str(username)
        mycursor.execute("SELECT logindetailsID FROM logindetailst WHERE usernames = %s AND "
                         "descriptionID = (SELECT descriptionID FROM descriptionst"
                         " WHERE descriptions = %s)", (username, description))
        logindetailsID = str(mycursor.fetchone()[0])
        selected_password = Mysqlfuncs.fetchMysql(userid, masterpassword, description_username=description_username)

        def description_func():
            description = description_entry.get()
            if description:
                Mysqlfuncs.appendMysql(userid, masterpassword, logindetailsID, sub_func=1, new_description=description)
                search()
                description_var.set(value="Current description: " + description)
            else:
                messagebox.showerror(title="Error", message="Text box cannot be empty")
        description_var = StringVar()
        description_label = ttk.Label(append_window, textvariable=description_var)
        description_label.grid()
        description_var.set(value="Current description: " + description)
        description_entry = ttk.Entry(append_window)
        description_entry.grid()
        description_button = ttk.Button(append_window, text="Enter", command=description_func)
        description_button.grid()

        def username_func():
            username = username_entry.get()
            if username:
                Mysqlfuncs.appendMysql(userid, masterpassword, logindetailsID, sub_func=2, new_username=username)
                search()
                username_var.set(value="Current username: " + username)
            else:
                messagebox.showerror(title="Error", message="Text box cannot be empty")
        username_var = StringVar()
        username_label = ttk.Label(append_window, textvariable=username_var)
        username_label.grid()
        username_var.set(value="Current username: " + username)
        username_entry = ttk.Entry(append_window)
        username_entry.grid()
        username_button = ttk.Button(append_window, text="Enter", command=username_func)
        username_button.grid()

        def password_func():
            selected_password = password_entry.get()
            if selected_password:
                Mysqlfuncs.appendMysql(userid, masterpassword, logindetailsID, sub_func=3, new_password=selected_password)
                search()
                password_var.set(value="Current password: " + selected_password)
            else:
                messagebox.showerror(title="Error", message="Text box cannot be empty")
        password_var = StringVar()
        password_label = ttk.Label(append_window, textvariable=password_var)
        password_label.grid()
        password_var.set(value="Current password: " + selected_password)
        password_entry = ttk.Entry(append_window)
        password_entry.grid()
        password_button = ttk.Button(append_window, text="Enter", command=password_func)
        password_button.grid()

        append_window.mainloop()

    def item_selected(event):
        for selected_item in tree_view.selection():
            item = tree_view.item(selected_item)
            record = item['values']
            # Shows the retrieved password
            retrieved_password = Mysqlfuncs.fetchMysql(userid, masterpassword, description_username=record)
            messagebox.showinfo(title='Information', message="Password is: " + retrieved_password)

    def item_selected_append(event):
        for selected_item in tree_view.selection():
            item = tree_view.item(selected_item)
            record = item['values']
            # Opens a new window where user can edit entry
            append_window(userid, masterpassword, record, root)

    def item_selected_delete(event):
        for selected_item in tree_view.selection():
            item = tree_view.item(selected_item)
            record = item['values']
            # Opens a messagebox to confirm if user wants to delete entry
            if tkinter.messagebox.askyesno("Confirmation", "Selected record: "
                                           + str(record) +
                                           " Are you sure you want to delete this record?"):
                Mysqlfuncs.deleteMysql(userid, record)
            search()

    root.title("Password manager")
    root.geometry("600x240")
    tree_view = ttk.Treeview(root, columns=("Description", "Username"), show="headings")
    tree_view.heading("Description", text="Description")
    tree_view.heading("Username", text="Username")
    # Retrieves all descriptions and usernames to place in tree_view
    tree_list = Mysqlfuncs.get_descriptions_and_usernames(userid)
    for each in tree_list:
        tree_view.insert('', tkinter.END, values=each)
    tree_view.bind('<<TreeviewSelect>>', item_selected)
    tree_view.grid(column=0, columnspan=3, row=0, rowspan=8)

    # Creates scrollbar for tree_view
    scrollbar = ttk.Scrollbar(root, orient=tkinter.VERTICAL, command=tree_view.yview)
    tree_view.configure(yscroll=scrollbar.set)
    scrollbar.grid(row=0, rowspan=8, column=3, sticky="ns")

    new_password_button = ttk.Button(root, text="+", command=new_password)
    new_password_button.place(x=420, y=40, width=30)
    append_mode_button = ttk.Button(root, text="&", command=append)
    append_mode_button.place(x=455, y=40, width=30)
    delete_mode_button = ttk.Button(root, text="X", command=delete)
    delete_mode_button.place(x=490, y=40, width=30)
    cur_mode = StringVar()
    cur_mode.set(value="Current mode: Show pasword")
    cur_mode_label = ttk.Label(root, textvariable=cur_mode)
    cur_mode_label.place(x=420, y=65)
    textvar = StringVar()
    search_label = ttk.Label(root,text="Search:")
    search_label.place(x=420,y=10)
    # Automatically updates list when entry field is typed into
    textvar.trace_add("write", search)
    search_entry = ttk.Entry(root, textvariable=textvar)
    search_entry.place(x=470, y=10)
    root.mainloop()

# Function to login or register
def login_window():

    root.title("Login")
    root.geometry("460x50")
    email_label = ttk.Label(root, text="Email:")
    email_label.grid(column=0, row=0)
    password_label = ttk.Label(root, text="Password:")
    password_label.grid(column=1, row=0)
    email_input = ttk.Entry(root)
    email_input.grid(column=0, row=1)
    password_input = ttk.Entry(root, show="*")
    password_input.grid(column=1, row=1)

    # Function to retrieve inputs and put run Mysqlfuncs.validatemasterpassword with them,
    # and then run the main function if the login details are valid
    def retrieve_inputs():
        global userid, masterpassword
        email = email_input.get()
        masterpassword = password_input.get()
        # if statement to stop users from entering empty inputs
        if not email or not masterpassword:
            error_message.set(value="Entry fields cannot be empty")
        else:
            if Mysqlfuncs.validatemasterpassword(email, masterpassword):
                userid = Mysqlfuncs.validatemasterpassword(email, masterpassword)
                for widget in root.winfo_children():
                    widget.destroy()
                main()
            else:
                # Error message if password validation fails
                error_message.set(value="Incorrect input")

    # Function to retrieve inputs and attempt to register with them
    def register():
        global userid, masterpassword
        email = email_input.get()
        masterpassword = password_input.get()
        if not email or not masterpassword:
            error_message.set(value="Entry fields cannot be empty")
        else:
            try:
                userid = MysqlNewUser.newuser(masterpassword, email)
                for widget in root.winfo_children():
                    widget.destroy()
                main()
            except:
                error_message.set(value="User already exists")
    error_message = StringVar()
    error_label = ttk.Label(root, textvariable=error_message, foreground="red")
    error_label.grid(column=2, row=0)
    confirm_input_button = ttk.Button(root, text="Enter", command=retrieve_inputs)
    confirm_input_button.grid(column=2, row=1)
    register_button = ttk.Button(root, text="Register", command=register)
    register_button.grid(column=3, row=1)
    root.mainloop()


login_window()
