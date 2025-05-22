
from __init__ import CURSOR, CONN

class Department:

    def __init__(self, name, location, id=None):
        self.id = id
        self.name = name
        self.location = location
    def __repr__(self):
        return f"<Department(id={self.id}, name='{self.name}', location='{self.location}>"

    # === Property Validators ===
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not isinstance(value, str) or len(value.strip()) == 0:
            raise ValueError("Name must be a non-empty string")
        self._name = value

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, value):
        if not isinstance(value, str) or len(value.strip()) == 0:
            raise ValueError("Location must be a non-empty string")
        self._location = value

    # === ORM Methods ===
    @classmethod
    def create_table(cls):
        """Create departments table"""
        sql = """
            CREATE TABLE IF NOT EXISTS departments (
                id INTEGER PRIMARY KEY,
                name TEXT,
                location TEXT
            )
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        """Drop departments table"""
        sql = "DROP TABLE IF EXISTS departments"
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        """Save instance to database"""
        sql = """
            INSERT INTO departments (name, location)
            VALUES (?, ?)
        """
        CURSOR.execute(sql, (self.name, self.location))
        CONN.commit()
        self.id = CURSOR.lastrowid

    @classmethod
    def create(cls, name, location):
        """Create and save new instance"""
        department = cls(name, location)
        department.save()
        return department

    def update(self):
        """Update database row"""
        sql = """
            UPDATE departments
            SET name = ?, location = ?
            WHERE id = ?
        """
        CURSOR.execute(sql, (self.name, self.location, self.id))
        CONN.commit()

    def delete(self):
        """Delete database row"""
        sql = "DELETE FROM departments WHERE id = ?"
        CURSOR.execute(sql, (self.id,))
        CONN.commit()
        self.id = None

    @classmethod
    def instance_from_db(cls, row):
        """Create instance from database row"""
        return cls(row[1], row[2], row[0])

    @classmethod
    def get_all(cls):
        """Get all departments"""
        sql = "SELECT * FROM departments"
        return [cls.instance_from_db(row) for row in CURSOR.execute(sql).fetchall()]

    @classmethod
    def find_by_id(cls, id):
        """Find department by ID"""
        sql = "SELECT * FROM departments WHERE id = ?"
        row = CURSOR.execute(sql, (id,)).fetchone()
        return cls.instance_from_db(row) if row else None

    @classmethod
    def find_by_name(cls, name):
        """Find department by name"""
        sql = "SELECT * FROM departments WHERE name = ?"
        row = CURSOR.execute(sql, (name,)).fetchone()
        return cls.instance_from_db(row) if row else None

    def employees(self):
        """Get related employees"""
        from employee import Employee
        sql = "SELECT * FROM employees WHERE department_id = ?"
        return [Employee.instance_from_db(row) for row in CURSOR.execute(sql, (self.id,)).fetchall()]