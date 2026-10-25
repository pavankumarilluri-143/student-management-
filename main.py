
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

# ---------------- DATABASE ----------------

conn = sqlite3.connect("students.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    age INTEGER NOT NULL,
    course TEXT NOT NULL,
    phone TEXT,
    email TEXT
)
""")
conn.commit()


# ---------------- MAIN WINDOW ----------------

root = tk.Tk()
root.title("Student Management System")
root.geometry("1100x650")
root.minsize(900, 550)
root.configure(bg="#f1f5f9")

# Colors
BLUE = "#2563eb"
DARK = "#1e293b"
BG = "#f1f5f9"

style = ttk.Style()
style.theme_use("clam")
style.configure(
    "Treeview",
    rowheight=30,
    font=("Arial", 10),
    background="white",
    fieldbackground="white"
)
style.configure(
    "Treeview.Heading",
    font=("Arial", 10, "bold"),
    background="#dbeafe"
)
style.map(
    "Treeview",
    background=[("selected", "#bfdbfe")],
    foreground=[("selected", DARK)]
)

# ---------------- HEADER ----------------

header = tk.Frame(root, bg=DARK, height=80)
header.pack(fill="x")
header.pack_propagate(False)

tk.Label(
    header,
    text="🎓 Student Management System",
    font=("Arial", 22, "bold"),
    bg=DARK,
    fg="white"
).pack(side="left", padx=25, pady=20)

# ---------------- FORM ----------------

form = tk.LabelFrame(
    root,
    text=" Student Details ",
    font=("Arial", 12, "bold"),
    bg="white",
    fg=DARK,
    padx=15,
    pady=12
)
form.pack(fill="x", padx=20, pady=15)

fields = ["Name", "Age", "Course", "Phone", "Email"]
entries = {}

for i, field in enumerate(fields):
    row = i // 3
    col = (i % 3) * 2

    tk.Label(
        form,
        text=field,
        font=("Arial", 10, "bold"),
        bg="white"
    ).grid(row=row, column=col, padx=8, pady=8, sticky="w")

    entry = tk.Entry(form, font=("Arial", 11), width=23)
    entry.grid(row=row, column=col + 1, padx=8, pady=8)
    entries[field] = entry


# ---------------- TABLE ----------------

table_frame = tk.Frame(root, bg=BG)
table_frame.pack(fill="both", expand=True, padx=20, pady=5)

columns = ("ID", "Name", "Age", "Course", "Phone", "Email")

tree = ttk.Treeview(
    table_frame,
    columns=columns,
    show="headings",
    selectmode="browse"
)

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=140, anchor="center")

tree.column("ID", width=55)
tree.column("Name", width=170)

scrollbar = ttk.Scrollbar(
    table_frame, orient="vertical", command=tree.yview
)
tree.configure(yscrollcommand=scrollbar.set)

tree.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")


# ---------------- FUNCTIONS ----------------

def clear_fields():
    for entry in entries.values():
        entry.delete(0, tk.END)
    tree.selection_remove(tree.selection())


def load_students(search=""):
    for item in tree.get_children():
        tree.delete(item)

    cursor.execute("""
        SELECT * FROM students
        WHERE name LIKE ? OR course LIKE ? OR email LIKE ?
        ORDER BY id DESC
    """, (f"%{search}%", f"%{search}%", f"%{search}%"))

    for student in cursor.fetchall():
        tree.insert("", tk.END, values=student)


def add_student():
    name = entries["Name"].get().strip()
    age = entries["Age"].get().strip()
    course = entries["Course"].get().strip()
    phone = entries["Phone"].get().strip()
    email = entries["Email"].get().strip()

    if not name or not age or not course:
        messagebox.showwarning(
            "Missing Details",
            "Name, Age and Course are required."
        )
        return

    try:
        age = int(age)
        if age <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror(
            "Invalid Age", "Please enter a valid positive age."
        )
        return

    try:
        cursor.execute("""
            INSERT INTO students (name, age, course, phone, email)
            VALUES (?, ?, ?, ?, ?)
        """, (name, age, course, phone, email))
        conn.commit()

        load_students()
        clear_fields()
        messagebox.showinfo("Success", "Student added successfully!")

    except sqlite3.Error as error:
        messagebox.showerror("Database Error", str(error))


def get_selected_id():
    selected = tree.selection()

    if not selected:
        messagebox.showwarning(
            "Select Student",
            "Please select a student from the table."
        )
        return None

    return tree.item(selected[0], "values")[0]


def select_student(event=None):
    selected = tree.selection()
    if not selected:
        return

    values = tree.item(selected[0], "values")

    for i, field in enumerate(fields):
        entries[field].delete(0, tk.END)
        entries[field].insert(0, values[i + 1])


def update_student():
    student_id = get_selected_id()
    if student_id is None:
        return

    name = entries["Name"].get().strip()
    age = entries["Age"].get().strip()
    course = entries["Course"].get().strip()
    phone = entries["Phone"].get().strip()
    email = entries["Email"].get().strip()

    if not name or not age or not course:
        messagebox.showwarning(
            "Missing Details",
            "Name, Age and Course are required."
        )
        return

    try:
        age = int(age)
        if age <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Invalid Age", "Enter a positive age.")
        return

    cursor.execute("""
        UPDATE students
        SET name=?, age=?, course=?, phone=?, email=?
        WHERE id=?
    """, (name, age, course, phone, email, student_id))

    conn.commit()
    load_students()
    clear_fields()
    messagebox.showinfo("Success", "Student updated successfully!")


def delete_student():
    student_id = get_selected_id()
    if student_id is None:
        return

    confirm = messagebox.askyesno(
        "Confirm Delete",
        "Are you sure you want to delete this student?"
    )

    if confirm:
        cursor.execute(
            "DELETE FROM students WHERE id=?", (student_id,)
        )
        conn.commit()
        load_students()
        clear_fields()
        messagebox.showinfo("Deleted", "Student deleted successfully!")


def search_students():
    load_students(search_entry.get().strip())


# Select a row to load its details into the form
tree.bind("<<TreeviewSelect>>", select_student)

# ---------------- BUTTONS ----------------

buttons = tk.Frame(root, bg=BG)
buttons.pack(fill="x", padx=20, pady=10)

def make_button(parent, text, color, command):
    return tk.Button(
        parent,
        text=text,
        bg=color,
        fg="white",
        font=("Arial", 10, "bold"),
        padx=14,
        pady=8,
        relief="flat",
        cursor="hand2",
        command=command
    )

make_button(buttons, "➕ Add Student", "#16a34a",
            add_student).pack(side="left", padx=5)

make_button(buttons, "✏ Update", BLUE,
            update_student).pack(side="left", padx=5)

make_button(buttons, "🗑 Delete", "#dc2626",
            delete_student).pack(side="left", padx=5)

make_button(buttons, "Clear", "#64748b",
            clear_fields).pack(side="left", padx=5)

# Search area
tk.Label(
    buttons,
    text="Search:",
    font=("Arial", 10, "bold"),
    bg=BG
).pack(side="left", padx=(20, 5))

search_entry = tk.Entry(buttons, font=("Arial", 11), width=20)
search_entry.pack(side="left", padx=5)
search_entry.bind("<Return>", lambda event: search_students())

make_button(buttons, "🔍 Search", DARK,
            search_students).pack(side="left", padx=5)

make_button(buttons, "Show All", "#475569",
            lambda: [search_entry.delete(0, tk.END),
                     load_students()]).pack(side="left", padx=5)

# ---------------- START APPLICATION ----------------

load_students()

def close_app():
    conn.close()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", close_app)
root.mainloop()
