import pandas as pd
import sqlite3
from pathlib import Path
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.utils import get_column_letter

### ---------- Nombres de tablas en SQLite ---------- ###
name_tabla_registros_excel = "tabla_registros"
name_tabla_transacciones_csv = "tabla_transacciones"
name_tabla_resultados = 'cruce_registros_transacciones'
name_tabla_resumen = 'tabla_resumen_diario'

### ---------- Archivo base de datos ---------- ###
archivo_base_datos = Path("Archivos/Archivos_base_datos/copy_jaco.db")


# --- Función general para convertir columnas de fecha ---
def convertir_fechas_en_tabla(conn, nombre_tabla, columnas_fecha):
    """Convierte las columnas especificadas a formato fecha (YYYY-MM-DD)
    y actualiza la tabla en la base de datos SQLite.
    """
    print(f"\nProcesando tabla '{nombre_tabla}'...")

    # Leer la tabla completa desde SQLite
    df = pd.read_sql(f"SELECT * FROM {nombre_tabla}", conn)

    # Convertir columnas especificadas a tipo datetime
    for col in columnas_fecha:
        if col in df.columns:
            print(f" → Convirtiendo columna '{col}' a datetime...")
            df[col] = pd.to_datetime(df[col], format="%Y-%m-%d", errors="coerce").dt.date
        else:
            print(f" ⚠️  La columna '{col}' no se encontró en la tabla '{nombre_tabla}'.")

    # Confirmar el tipo de datos después de la conversión
    print(df.dtypes[df.dtypes == 'datetime64[ns]'])

    # Sobrescribir la tabla en SQLite (reemplaza la versión anterior)
    df.to_sql(nombre_tabla, conn, if_exists="replace", index=False)
    print(f"✅ Tabla '{nombre_tabla}' actualizada correctamente con formato fecha.")


# --- Ejecución principal ---
if __name__ == "__main__":
   
############################################################################################################

    """Agregar columna de mes y año en la tabla de resumen y cruce de registros"""
    try:
        conn = sqlite3.connect(archivo_base_datos)
        # Leemos las tablas para crear las columnas de mes y año
        df_resultados = pd.read_sql(f"SELECT * FROM {name_tabla_resultados}", conn)
        df_resumen = pd.read_sql(f"SELECT * FROM {name_tabla_resumen}", conn)

        df_resultados['mes_año_registro'] = pd.to_datetime(df_resultados['Fecha de registro']).dt.strftime('%m %B %Y')
        df_resultados['mes_año_depósito'] = pd.to_datetime(df_resultados['Fecha primer depósito']).dt.strftime('%m %B %Y')

        df_resumen['mes_año'] = pd.to_datetime(df_resumen['Fecha']).dt.strftime('%m %B %Y')

        df_resultados.to_sql(name_tabla_resultados, conn, if_exists='replace', index=False)
        df_resumen.to_sql(name_tabla_resumen, conn, if_exists='replace', index=False)
        print("✅ Columnas de mes y año agregadas correctamente.")


    finally:
        conn.close()
        print("Se crearon las columnas de mes y año.\nConexión cerrada.")
############################################################################################################



    """Cambio de formato en las columnas de la base de datos"""
    try:
        conn = sqlite3.connect(archivo_base_datos)
        # Convertir columnas de fecha en las dos tablas
        convertir_fechas_en_tabla(conn, name_tabla_resultados, ['Fecha de registro', 'Fecha primer depósito'])
        convertir_fechas_en_tabla(conn, name_tabla_resumen, ['Fecha'])
    finally:
        conn.close()
        print("\nConexión cerrada.")
############################################################################################################


    """"""










