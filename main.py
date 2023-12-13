import sqlite3

class DatabaseManager:
    def __init__(self, db_name="school_database.db"):
        self.conn = sqlite3.connect(db_name)
        self.update_tables()

    def update_tables(self):
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                password TEXT NOT NULL,
                user_type TEXT NOT NULL
            )
        ''')

        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY,
                student_id INTEGER UNIQUE NOT NULL,
                FOREIGN KEY (id) REFERENCES users(id)
            )
        ''')

        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS teachers (
                id INTEGER PRIMARY KEY,
                teacher_id INTEGER UNIQUE NOT NULL,
                FOREIGN KEY (id) REFERENCES users(id)
            )
        ''')

        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS administrators (
                id INTEGER PRIMARY KEY,
                admin_id INTEGER UNIQUE NOT NULL,
                FOREIGN KEY (id) REFERENCES users(id)
            )
        ''')

        self.conn.commit()

    def insert_user(self, name, password, user_type):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO users (name, password, user_type) 
            VALUES (?, ?, ?)
        ''', (name, password, user_type))
        user_id = cursor.lastrowid
        self.conn.commit()
        return user_id

    def insert_student(self, user_id, student_id):
        self.conn.execute('''
            INSERT INTO students (id, student_id) 
            VALUES (?, ?)
        ''', (user_id, student_id))
        self.conn.commit()

    def insert_teacher(self, user_id, teacher_id):
        self.conn.execute('''
            INSERT INTO teachers (id, teacher_id) 
            VALUES (?, ?)
        ''', (user_id, teacher_id))
        self.conn.commit()

    def insert_administrator(self, user_id, admin_id):
        self.conn.execute('''
            INSERT INTO administrators (id, admin_id) 
            VALUES (?, ?)
        ''', (user_id, admin_id))
        self.conn.commit()

    def update_user_password(self, user_id, new_password):
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE users SET password=? WHERE id=?
        ''', (new_password, user_id))
        self.conn.commit()

    def delete_user(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            DELETE FROM users WHERE id=?
        ''', (user_id,))
        self.conn.commit()

    def filter_users_by_type(self, user_type):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM users WHERE user_type=?
        ''', (user_type,))
        return cursor.fetchall()

    def find_user_by_name(self, name):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE name=?", (name,))
        user = cursor.fetchone()
        if user:
            return {'id': user[0], 'name': user[1], 'password': user[2], 'user_type': user[3]}
        return None

    def close_connection(self):
        self.conn.close()

class UserManager:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.logged_user = None

    def show_menu(self):
        print("Выберите действие:")
        print("1. Авторизация")
        print("2. Регистрация")
        print("3. Изменить пароль")
        print("4. Удалить аккаунт")
        print("5. Фильтрация пользователей")

    def register_user(self):
        print("Регистрация нового пользователя:")
        name = input("Введите ваше имя: ")
        password = input("Введите пароль: ")

        user_type = input("Выберите тип пользователя (student/teacher/administrator): ").lower()

        if user_type == "student":
            student_id = input("Введите номер студенческого билета: ")
            user_id = self.db_manager.insert_user(name, password, user_type)
            self.db_manager.insert_student(user_id, student_id)
        elif user_type == "teacher":
            teacher_id = input("Введите идентификатор учителя: ")
            user_id = self.db_manager.insert_user(name, password, user_type)
            self.db_manager.insert_teacher(user_id, teacher_id)
        elif user_type == "administrator":
            admin_id = input("Введите идентификатор администратора: ")
            user_id = self.db_manager.insert_user(name, password, user_type)
            self.db_manager.insert_administrator(user_id, admin_id)
        else:
            print("Некорректный тип пользователя.")

    def login_user(self):
        print("Вход:")
        name = input("Введите ваше имя: ")
        password = input("Введите пароль: ")

        user = self.db_manager.find_user_by_name(name)

        if not user:
            print("Пользователь с таким именем не найден.")
            return

        if user["password"] != password:
            print("Неверный пароль.")
            return

        print("Вход выполнен успешно.")
        return user

    def update_password(self):
        if not self.logged_user:
            print("Вы не авторизованы.")
            return

        new_password = input("Введите новый пароль: ")
        self.db_manager.update_user_password(self.logged_user["id"], new_password)
        print("Пароль успешно обновлен.")

    def delete_account(self):
        if not self.logged_user:
            print("Вы не авторизованы.")
            return

        confirm = input("Вы уверены, что хотите удалить ваш аккаунт? (yes/no): ").lower()
        if confirm == "yes":
            self.db_manager.delete_user(self.logged_user["id"])
            self.logged_user = None
            print("Аккаунт успешно удален.")
        else:
            print("Операция отменена.")

    def filter_users(self):
        if not self.logged_user:
            print("Вы не авторизованы.")
            return

        user_type = input("Введите тип пользователя для фильтрации (student/teacher/administrator): ").lower()
        filtered_users = self.db_manager.filter_users_by_type(user_type)
        print("Список пользователей:")
        for user in filtered_users:
            print(f"ID: {user['id']}, Имя: {user['name']}, Тип: {user['user_type']}")

user_manager = UserManager()

while True:
    user_manager.show_menu()
    choice = input("Введите номер выбранного действия: ")

    if choice == "1":
        logged_user = user_manager.login_user()
        if logged_user:
            print("Добро пожаловать, ", logged_user["name"])
            user_manager.logged_user = logged_user
    elif choice == "2":
        user_manager.register_user()
    elif choice == "3":
        user_manager.update_password()
    elif choice == "4":
        user_manager.delete_account()
    elif choice == "5":
        user_manager.filter_users()
    else:
        print("Некорректный ввод. Пожалуйста, выберите от 1 до 5.")
