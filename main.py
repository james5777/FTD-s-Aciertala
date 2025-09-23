# ----------------------------------------------------------------------
# Autor: James Palacio
#        Jacobo Chica
#
# Fecha: 22/09/2025
#
# Descripción: El objetivo de esta automatizacion es definir desde los exportables del sportbook,
# cuales de los usuarios registrados son primeros depositos, teniendo en cuenta las variables
# ----------------------------------------------------------------------

import pandas as pd
import sqlite3
from pathlib import Path

### ---------- Archivos a leer ---------- ###
archivo_registros_excel = Path("Archivos/Diario_Aciertala_Peru.xlsm")
archivo_transacciones_csv = Path("Archivos/transactions.csv")

### ---------- Nombres de tablas en SQLite ---------- ###
name_tabla_registros_excel = "tabla_registros"
name_tabla_transacciones_csv = "tabla_transacciones"

### ---------- Archivo base de datos ---------- ###
archivo_base_datos = Path("Archivos/Archivos_base_datos/DataBase_aciertala.db")

### ---------- Nombres de columnas archivo excel (Registros) ---------- ###
ID_usuario_excel = 'ID de usuario'
Usuario_excel = 'Usuario'
fecha_creacion_excel = 'Fecha de creación'

### ---------- Nombres de columnas archivo CSV (transacciones) ---------- ###
fecha_deposito_csv = 'Crear hora'
ID_usuario_csv = 'ID de usuario'
usuario_csv = 'Usuario'
tipo_transaccion_csv = 'Tipo de transacción'
ID_transaccion_csv = 'ID de transacción'

### ---------- Conexión a SQLite ---------- ###
conn = sqlite3.connect(archivo_base_datos)

def actualizar_tabla(df, nombre_tabla, conn, unique_cols):
    """
    Inserta solo filas nuevas en una tabla SQLite desde un DataFrame.
    - df: DataFrame con los datos nuevos
    - nombre_tabla: nombre de la tabla en SQLite
    - conn: conexión a la BD
    - unique_cols: lista de columnas que actúan como clave compuesta
    """

    # Crear tabla si no existe
    df.head(0).to_sql(nombre_tabla, conn, if_exists="append", index=False)

    # Leer datos ya existentes en la tabla (solo columnas clave)
    try:
        existentes = pd.read_sql(f"SELECT {', '.join(unique_cols)} FROM {nombre_tabla}", conn)
    except Exception:
        existentes = pd.DataFrame(columns=unique_cols)

    # Copias seguras para evitar SettingWithCopyWarning
    df = df.copy()
    existentes = existentes.copy()

    # Crear columna hash para comparar claves compuestas
    df["_hash"] = df[unique_cols].astype(str).agg("-".join, axis=1).astype(str)
    if not existentes.empty:
        existentes["_hash"] = existentes[unique_cols].astype(str).agg("-".join, axis=1).astype(str)
    else:
        existentes["_hash"] = []

    # Filtrar solo filas nuevas
    nuevos = df[~df["_hash"].isin(existentes["_hash"])].drop(columns=["_hash"])

    # Insertar filas nuevas
    if not nuevos.empty:
        nuevos.to_sql(nombre_tabla, conn, if_exists="append", index=False)
        print(f"✅ {len(nuevos)} filas nuevas insertadas en {nombre_tabla}")
    else:
        print(f"ℹ️ No hay filas nuevas en {nombre_tabla}")

    print(unique_cols)

### ---------- Leer Excel ---------- ###
df_registros_excel = pd.read_excel(archivo_registros_excel, sheet_name='Historico')



df_transacciones_csv = pd.read_csv(
    archivo_transacciones_csv,
    sep=",",
    quotechar='"',
    encoding="utf-8"
)

df_transacciones_csv.columns = (
    df_transacciones_csv.columns
    .str.strip()
    .str.replace('"', '', regex=False)
)

print("📌 Columnas del CSV limpio:")
print(df_transacciones_csv.columns.tolist())

print("📌 Columnas del Excel:")
print(df_registros_excel.columns.tolist())

### ---------- Filtrar columnas necesarias csv ---------- ###
col_necesarias_csv = [fecha_deposito_csv, ID_usuario_csv, usuario_csv, tipo_transaccion_csv, ID_transaccion_csv]
df_final_transacciones = df_transacciones_csv[col_necesarias_csv]

# Normalizar fechas a string YYYY-MM-DD en CSV
df_final_transacciones.loc[:, fecha_deposito_csv] = pd.to_datetime(
    df_final_transacciones[fecha_deposito_csv], errors="coerce"
).dt.strftime("%Y-%m-%d").astype(str)

### ---------- Filtrar columnas necesarias excel ---------- ###
col_necesarias_excel = [fecha_creacion_excel, ID_usuario_excel, Usuario_excel]
df_final_registros = df_registros_excel[col_necesarias_excel]

# Normalizar fechas a string YYYY-MM-DD en Excel
df_final_registros.loc[:, fecha_creacion_excel] = pd.to_datetime(
    df_final_registros[fecha_creacion_excel], errors="coerce"
).dt.strftime("%Y-%m-%d").astype(str)


print("📌 Vista previa columnas necesarias:")
print(df_final_transacciones.head())
print(df_final_registros.head())

### ---------- Actualizar tablas en SQLite ---------- ###
actualizar_tabla(df_final_registros, name_tabla_registros_excel, conn, unique_cols=[Usuario_excel])
actualizar_tabla(df_final_transacciones, name_tabla_transacciones_csv, conn, unique_cols=[usuario_csv, fecha_deposito_csv])

### ---------- Cerrar conexión con SQLite ---------- ###
conn.close()

print("\n📌 DEBUG FECHAS - Registros (Excel)")
print(df_final_registros[fecha_creacion_excel].head(10))
print("dtype:", df_final_registros[fecha_creacion_excel].dtype)

print("\n📌 DEBUG FECHAS - Transacciones (CSV)")
print(df_final_transacciones[fecha_deposito_csv].head(10))
print("dtype:", df_final_transacciones[fecha_deposito_csv].dtype)

print(df_final_transacciones[ID_transaccion_csv].head(10))

# --- Identificar primeros depósitos ---

# Filtrar depósitos
df_depositos = df_final_transacciones[
    df_final_transacciones[tipo_transaccion_csv].str.lower() == "deposit"
].copy()

# Asegurar que la fecha es datetime
df_depositos[fecha_deposito_csv] = pd.to_datetime(df_depositos[fecha_deposito_csv], errors="coerce")

# Ordenar por usuario y fecha
df_depositos = df_depositos.sort_values(by=[usuario_csv, fecha_deposito_csv])

# Obtener el primer depósito por usuario
df_primer_deposito = df_depositos.groupby(usuario_csv).first().reset_index()

# Normalizar nombres de usuario para que coincidan
df_final_registros[Usuario_excel] = (
    df_final_registros[Usuario_excel].astype(str).str.strip().str.lower()
)
df_final_transacciones[usuario_csv] = (
    df_final_transacciones[usuario_csv].astype(str).str.strip().str.lower()
)

# --- Primer depósito por usuario en transacciones ---
df_primer_deposito = (
    df_final_transacciones
    .sort_values(by=fecha_deposito_csv)
    .groupby([ID_usuario_csv, usuario_csv], as_index=False)
    .first()[[ID_usuario_csv, usuario_csv, fecha_deposito_csv, ID_transaccion_csv]]
)

# --- Cruce por ID de usuario ---
df_merge_id = pd.merge(
    df_final_registros.dropna(subset=[ID_usuario_excel]),
    df_primer_deposito,
    how="left",
    left_on=ID_usuario_excel,
    right_on=ID_usuario_csv
)

# --- Cruce por Usuario (para los que tienen ID NaN) ---
df_merge_user = pd.merge(
    df_final_registros[df_final_registros[ID_usuario_excel].isna()],
    df_primer_deposito,
    how="left",
    left_on=Usuario_excel,
    right_on=usuario_csv
)

# --- Unir ambos resultados ---
df_resultado = pd.concat([df_merge_id, df_merge_user], ignore_index=True)

# --- Renombrar columnas ---
df_resultado = df_resultado.rename(columns={
    fecha_creacion_excel: "Fecha de registro",
    fecha_deposito_csv: "Fecha primer depósito",
    ID_transaccion_csv: "ID primer depósito"
})[
    ["Fecha de registro", ID_usuario_excel, Usuario_excel, "Fecha primer depósito", "ID primer depósito"]
]

print("📊 Vista previa de primeros depósitos encontrados:")
print(df_resultado.head(20))
