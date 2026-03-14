import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.simpledialog import Dialog
import mysql.connector
from datetime import datetime

class DatabaseManager:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="qwerty1234",
            database="student_activity"
        )
        
    def get_cursor(self):
        return self.conn.cursor(dictionary=True, buffered=True)
    
    def get_primary_key(self, table_name):
        cursor = self.get_cursor()
        try:
            cursor.execute(f"SHOW KEYS FROM {table_name} WHERE Key_name = 'PRIMARY'")
            result = cursor.fetchone()
            return result['Column_name'] if result else None
        finally:
            cursor.close()

    def execute_query(self, query, params=None, fetch=False):
        cursor = self.get_cursor()
        try:
            cursor.execute(query, params or ())
            self.conn.commit()
            if fetch:
                result = cursor.fetchall()
                return result
            return None
        except Exception as e:
            messagebox.showerror("Ошибка базы данных", str(e))
            return None
        finally:
            cursor.close()

class CRUDDialog(Dialog):
    def __init__(self, parent, title, fields, initial_data=None, table_name=None):
        self.fields = fields
        self.initial_data = initial_data or {}
        self.table_name = table_name
        super().__init__(parent, title)

    def body(self, master):
        self.entries = {}
        for i, (field, config) in enumerate(self.fields.items()):
            tk.Label(master, text=config['label']).grid(row=i, column=0, sticky=tk.W)
            
            if config['type'] == 'combobox':
                entry = ttk.Combobox(master, values=config['values'])
                entry.set(config['values'][0])
            else:
                entry = ttk.Entry(master)
            
            entry.grid(row=i, column=1, padx=5, pady=5)
            if field in self.initial_data:
                entry.insert(0, str(self.initial_data[field]))
            self.entries[field] = entry
        return master

    def validate(self):
        for field, config in self.fields.items():
            if config.get('required', True) and not self.entries[field].get():
                messagebox.showwarning("Ошибка", f"Поле {config['label']} обязательно для заполнения")
                return False
            
            if config['type'] == 'number':
                try:
                    float(self.entries[field].get())
                except ValueError:
                    messagebox.showwarning("Ошибка", f"Некорректное значение в поле {config['label']}")
                    return False
            
            if config['type'] == 'date':
                try:
                    datetime.strptime(self.entries[field].get(), "%Y-%m-%d")
                except ValueError:
                    messagebox.showwarning("Ошибка", f"Некорректный формат даты в поле {config['label']} (требуется ГГГГ-ММ-ДД)")
                    return False
        return True

    def apply(self):
        self.result = {}
        for field, entry in self.entries.items():
            value = entry.get()
            if self.fields[field]['type'] == 'number':
                value = float(value)
            self.result[field] = value

class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Управление студенческой активностью")
        self.geometry("1200x600")
        self.db = DatabaseManager()
        
        self.create_widgets()
        self.load_data()
        
    def create_widgets(self):
        self.notebook = ttk.Notebook(self)
        
        self.tabs = {
            'students': ttk.Frame(self.notebook),
            'attendance': ttk.Frame(self.notebook),
            'test_results': ttk.Frame(self.notebook),
            'test_standards': ttk.Frame(self.notebook)
        }
        
        for name, frame in self.tabs.items():
            self.notebook.add(frame, text=name.capitalize())
            self.create_table_ui(frame, name)
            
        self.notebook.pack(expand=True, fill=tk.BOTH)
        
    def create_table_ui(self, parent, table_name):
        columns = self.get_columns(table_name)
        tree = ttk.Treeview(parent, columns=columns, show='headings')
        
        for col in columns:
            tree.heading(col, text=col.replace('_', ' ').title())
            tree.column(col, width=120, anchor=tk.CENTER)
            
        parent.tree = tree
        
        toolbar = ttk.Frame(parent)
        ttk.Button(toolbar, text="Обновить", command=self.load_data).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Добавить", command=lambda: self.open_add_dialog(table_name)).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Изменить", command=lambda: self.open_edit_dialog(table_name)).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Удалить", command=lambda: self.delete_record(table_name)).pack(side=tk.LEFT, padx=2)
        
        toolbar.pack(side=tk.TOP, fill=tk.X)
        tree.pack(expand=True, fill=tk.BOTH)
        
    def get_columns(self, table_name):
        result = self.db.execute_query(f"SHOW COLUMNS FROM {table_name}", fetch=True)
        return [col['Field'] for col in result] if result else []
    
    def load_data(self):
        current_tab = self.notebook.tab(self.notebook.select(), "text").lower()
        tree = self.tabs[current_tab].tree
        
        tree.delete(*tree.get_children())
        result = self.db.execute_query(f"SELECT * FROM {current_tab}", fetch=True)
        
        if result:
            for row in result:
                tree.insert('', tk.END, values=list(row.values()))
    
    def get_field_config(self, table_name):
        config = {
            'students': {
                'full_name': {'label': 'ФИО', 'type': 'text'},
                'birth_date': {'label': 'Дата рождения (ГГГГ-ММ-ДД)', 'type': 'date'},
                'group_name': {'label': 'Группа', 'type': 'text'}
            },
            'attendance': {
                'student_id': {'label': 'ID студента', 'type': 'number'},
                'date': {'label': 'Дата (ГГГГ-ММ-ДД)', 'type': 'date'},
                'status': {
                    'label': 'Статус',
                    'type': 'combobox',
                    'values': ['present', 'absent', 'late']
                }
            },
            'test_results': {
                'student_id': {'label': 'ID студента', 'type': 'number'},
                'test_type': {
                    'label': 'Тип теста',
                    'type': 'combobox',
                    'values': ['running', 'jumping', 'flexibility']
                },
                'result_value': {'label': 'Результат', 'type': 'number'},
                'test_date': {'label': 'Дата теста (ГГГГ-ММ-ДД)', 'type': 'date'}
            },
            'test_standards': {
                'test_type': {
                    'label': 'Тип теста',
                    'type': 'combobox',
                    'values': ['running', 'jumping', 'flexibility']
                },
                'age_group': {'label': 'Возрастная группа (например, 18-20)', 'type': 'text'},
                'min_value': {'label': 'Минимальное значение', 'type': 'number'},
                'max_value': {'label': 'Максимальное значение', 'type': 'number'}
            }
        }
        return config[table_name]
    
    def open_add_dialog(self, table_name):
        fields = self.get_field_config(table_name)
        dialog = CRUDDialog(self, f"Добавить запись в {table_name}", fields, table_name=table_name)
        if dialog.result:
            self.insert_record(table_name, dialog.result)
    
    def open_edit_dialog(self, table_name):
        tree = self.tabs[table_name].tree
        selected = tree.focus()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите запись для редактирования")
            return
        
        item = tree.item(selected)
        fields = self.get_field_config(table_name)
        initial_data = dict(zip(fields.keys(), item['values']))
        
        dialog = CRUDDialog(self, f"Редактировать запись в {table_name}", fields, initial_data, table_name)
        if dialog.result:
            pk_column = self.db.get_primary_key(table_name)
            record_id = item['values'][0]
            self.update_record(table_name, dialog.result, pk_column, record_id)
    
    def insert_record(self, table_name, data):
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        self.db.execute_query(query, tuple(data.values()))
        self.load_data()
    
    def update_record(self, table_name, data, pk_column, record_id):
        set_clause = ', '.join([f"{key} = %s" for key in data.keys()])
        query = f"UPDATE {table_name} SET {set_clause} WHERE {pk_column} = %s"
        params = tuple(data.values()) + (record_id,)
        self.db.execute_query(query, params)
        self.load_data()
    
    def delete_record(self, table_name):
        tree = self.tabs[table_name].tree
        selected = tree.focus()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите запись для удаления")
            return
        
        if messagebox.askyesno("Подтверждение", "Удалить выбранную запись?"):
            pk_column = self.db.get_primary_key(table_name)
            record_id = tree.item(selected)['values'][0]
            query = f"DELETE FROM {table_name} WHERE {pk_column} = %s"
            self.db.execute_query(query, (record_id,))
            self.load_data()

if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()