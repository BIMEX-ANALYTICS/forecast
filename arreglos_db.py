import sqlite3

# Connect to (or create) the database
conn = sqlite3.connect("forecast.db")
cursor = conn.cursor()

# Drop existing tables if they exist to start fresh
cursor.execute("DROP TABLE IF EXISTS proyectos")
# cursor.execute("DROP TABLE IF EXISTS clientes")

# Create `proyectos` table with all required columns
cursor.execute("""
    CREATE TABLE proyectos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        probabilidad REAL,
        tarifa REAL,
        jornadas INTEGER,
        forecast REAL,
        estado TEXT,
        tecnologia TEXT,
        cliente TEXT,
        comentarios TEXT,
        fecha_ini DATS,
        fecha_fin DATS
    )
""")

# # Create `clientes` table to store unique client names
# cursor.execute("""
#     CREATE TABLE clientes (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         nombre TEXT UNIQUE
#     )
# """)

# Commit changes and close the connection
conn.commit()
conn.close()
print("Database and tables created successfully.")
