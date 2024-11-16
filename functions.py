import pandas as pd
import sqlite3

# Función para calcular el forecast
def calcular_forecast(probabilidad, tarifa, jornadas):
    return probabilidad * tarifa * jornadas

# Función para insertar datos en la base de datos
def insertar_proyecto(nombre, probabilidad, tarifa, jornadas, forecast, estado, tecnologia, cliente, comentarios,fecha_ini, fecha_fin):
    conn = sqlite3.connect("forecast.db")  # Crear nueva conexión
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO proyectos (nombre, probabilidad, tarifa, jornadas, forecast, estado, tecnologia, cliente, comentarios,fecha_ini,fecha_fin)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?,?,?)
    """, (nombre, probabilidad, tarifa, jornadas, forecast, estado, tecnologia, cliente, comentarios,fecha_ini,fecha_fin))
    conn.commit()
    conn.close()  # Cerrar la conexión

# Función para leer todos los proyectos de la base de datos
def leer_proyectos():
    conn = sqlite3.connect("forecast.db")  # Crear nueva conexión
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM proyectos")
    rows = cursor.fetchall()
    conn.close()  # Cerrar la conexión
    return pd.DataFrame(rows, columns=["ID", "Nombre", "Probabilidad", "Tarifa", "Jornadas", 
                                       "Forecast", "Estado", "Tecnología", "Cliente", "Comentarios","Fecha_Ini","Fecha_Fin"])

# Función para leer todos los clientes de la base de datos
def leer_clientes():
    conn = sqlite3.connect("forecast.db")  # Crear nueva conexión
    cursor = conn.cursor()
    cursor.execute("SELECT nombre FROM clientes")
    clientes = cursor.fetchall()
    conn.close()  # Cerrar la conexión
    return [cliente[0] for cliente in clientes]

# Función para aplicar ajuste de escenario
def aplicar_escenario(data, ajuste_prob):
    data_copy = data.copy()
    data_copy["Probabilidad Ajustada"] = data_copy["Probabilidad"] * (1 + ajuste_prob / 100)
    data_copy["Forecast Ajustado (€)"] = data_copy["Probabilidad Ajustada"] * data_copy["Tarifa"] * data_copy["Jornadas"]
    return data_copy

# Función para actualizar un proyecto en la base de datos
def actualizar_proyecto(proyecto_id, columna, valor):
    conn = sqlite3.connect("forecast.db")  # Crear nueva conexión
    cursor = conn.cursor()
    cursor.execute(f"UPDATE proyectos SET {columna} = ? WHERE id = ?", (valor, proyecto_id))
    conn.commit()
    conn.close()  # Cerrar la conexión

# Función para insertar un nuevo cliente
def insertar_cliente(nombre_cliente):
    conn = sqlite3.connect("forecast.db")  # Crear nueva conexión
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO clientes (nombre) VALUES (?)", (nombre_cliente,))
        conn.commit()
        conn.close()  # Cerrar la conexión
        return True
    except sqlite3.IntegrityError:
        conn.close()  # Cerrar la conexión en caso de error
        return False


# Función para eliminar un proyecto de la base de datos
def eliminar_proyectos(proyectos_ids):
    conn = sqlite3.connect("forecast.db")
    cursor = conn.cursor()
    cursor.executemany("DELETE FROM proyectos WHERE id = ?", [(proyecto_id,) for proyecto_id in proyectos_ids])
    conn.commit()
    conn.close()