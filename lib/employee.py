
from __init__ import CURSOR, CONN
from department import Department

class Employee:
    # Identity map to track all Employee instances by ID
    all = {}

    def __init__(self, name, job_title, department_id, id=None):
        self.id = id
        self.name = name
        self.job_title = job_title
        self.department_id = department_id
        if self.id:  # Add to identity map if ID exists
            self.__class__.all[self.id] = self

    def __repr__(self):
        return f"<Employee {self.id}: {self.name}, {self.job_title}, Dept ID: {self.department_id}>"

    # === Property Validators (Keep Existing Code) ===
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not isinstance(value, str) or len(value.strip()) == 0:
            raise ValueError("Name must be a non-empty string")
        self._name = value

    @property
    def job_title(self):
        return self._job_title

    @job_title.setter
    def job_title(self, value):
        if not isinstance(value, str) or len(value.strip()) == 0:
            raise ValueError("Job title must be a non-empty string")
        self._job_title = value

    @property
    def department_id(self):
        return self._department_id

    @department_id.setter
    def department_id(self, value):
        if not isinstance(value, int) or not Department.find_by_id(value):
            raise ValueError("department_id must reference a valid department")
        self._department_id = value

    # === ORM Methods ===
    @classmethod
    def create_table(cls):
        sql = """
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY,
                name TEXT,
                job_title TEXT,
                department_id INTEGER,
                FOREIGN KEY (department_id) REFERENCES departments(id)
            )
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        sql = "DROP TABLE IF EXISTS employees"
        CURSOR.execute(sql)
        CONN.commit()
        cls.all.clear()  # Clear identity map

    def save(self):
        if self.id:  # Update existing record
            sql = """
                UPDATE employees
                SET name = ?, job_title = ?, department_id = ?
                WHERE id = ?
            """
            CURSOR.execute(sql, (self.name, self.job_title, self.department_id, self.id))
        else:  # Insert new record
            sql = """
                INSERT INTO employees (name, job_title, department_id)
                VALUES (?, ?, ?)
            """
            CURSOR.execute(sql, (self.name, self.job_title, self.department_id))
            self.id = CURSOR.lastrowid
            self.__class__.all[self.id] = self  # Add to identity map
        CONN.commit()

    @classmethod
    def create(cls, name, job_title, department_id):
        employee = cls(name, job_title, department_id)
        employee.save()
        return employee

    def update(self):
        sql = """
            UPDATE employees
            SET name = ?, job_title = ?, department_id = ?
            WHERE id = ?
        """
        CURSOR.execute(sql, (self.name, self.job_title, self.department_id, self.id))
        CONN.commit()

    def delete(self):
        if self.id is None:
            raise ValueError("Employee not persisted in the database")
        sql = "DELETE FROM employees WHERE id = ?"
        CURSOR.execute(sql, (self.id,))
        CONN.commit()
        del self.__class__.all[self.id]  # Remove from identity map
        self.id = None  # Reset ID

    @classmethod
    def instance_from_db(cls, row):
        """Return existing instance or update/create a new one"""
        employee = cls.all.get(row[0])
        if employee:  # Update existing instance
            employee.name = row[1]
            employee.job_title = row[2]
            employee.department_id = row[3]
        else:  # Create new instance
            employee = cls(row[1], row[2], row[3], row[0])
        return employee

    @classmethod
    def get_all(cls):
        sql = "SELECT * FROM employees"
        return [cls.instance_from_db(row) for row in CURSOR.execute(sql).fetchall()]

    @classmethod
    def find_by_id(cls, id):
        sql = "SELECT * FROM employees WHERE id = ?"
        row = CURSOR.execute(sql, (id,)).fetchone()
        return cls.instance_from_db(row) if row else None

    @classmethod
    def find_by_name(cls, name):
        sql = "SELECT * FROM employees WHERE name = ?"
        row = CURSOR.execute(sql, (name,)).fetchone()
        return cls.instance_from_db(row) if row else None