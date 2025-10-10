
'''
Script de corrección para la base de datos DataBase_aciertala.db

Este script se conecta a la base de datos, lee la tabla 'cruce_registros_transacciones',
reemplaza los valores de texto "nan" en la columna "Fecha primer depósito" por valores nulos (NULL),
y actualiza la tabla en la base de datos con los datos corregidos.
'''

import pandas as pd
import sqlite3
from pathlib import Path

# --- Configuración ---
archivo_base_datos = Path("Archivos/Archivos_base_datos/DataBase_aciertala.db")
nombre_tabla = "cruce_registros_transacciones"
columna_a_corregir = "Fecha primer depósito"

# --- Conexión a la base de datos ---
conn = sqlite3.connect(archivo_base_datos)

# --- Lectura de la tabla en un DataFrame de pandas ---
try:
    df = pd.read_sql(f"SELECT * FROM {nombre_tabla}", conn)
    print(f"Tabla '{nombre_tabla}' leída correctamente.")
except Exception as e:
    print(f"Error al leer la tabla: {e}")
    conn.close()
    exit()

# --- Corrección de la columna ---
if columna_a_corregir in df.columns:
    # Reemplazar 'nan' (como texto) por None, que se traducirá a NULL en SQLite
    df[columna_a_corregir] = df[columna_a_corregir].replace('nan', None)
    print(f"Valores 'nan' reemplazados por NULL en la columna '{columna_a_corregir}'.")
else:
    print(f"La columna '{columna_a_corregir}' no existe en la tabla.")
    conn.close()
    exit()

# --- Guardado de los datos corregidos en la base de datos ---
try:
    # Sobrescribir la tabla con el DataFrame corregido
    df.to_sql(nombre_tabla, conn, if_exists="replace", index=False)
    print(f"Tabla '{nombre_tabla}' actualizada con éxito en la base de datos.")
except Exception as e:
    print(f"Error al guardar la tabla: {e}")
finally:
    # --- Cierre de la conexión ---
    conn.close()

print("\nProceso de corrección finalizado.")
