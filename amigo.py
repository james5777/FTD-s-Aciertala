import pandas as pd
import sqlite3
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import warnings

# --- Configuración ---
warnings.filterwarnings("ignore")

# --- Rutas y nombres ---
archivo_base_datos = Path("Archivos/Archivos_base_datos/DataBase_aciertala.db")
nombre_tabla_resumen = "tabla_resumen_diario"

# --- Estilo de gráficos ---
sns.set_theme(style="whitegrid")
plt.rcParams["figure.figsize"] = (10, 6)

# --- 1. Cargar y preparar datos ---
def cargar_y_preparar_datos(db_path, table_name):
    """Carga y prepara los datos desde la base de datos SQLite."""
    print(f"Cargando datos desde '{table_name}'...")
    conn = sqlite3.connect(db_path)
    try:
        df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
        df["Fecha"] = pd.to_datetime(df["Fecha"])
        df = df.set_index("Fecha").sort_index()
        df = df.asfreq("D", fill_value=0)
        print("Datos cargados correctamente.")
        return df
    except Exception as e:
        print(f"Error al cargar datos: {e}")
        return None
    finally:
        conn.close()

# --- 2. Análisis y gráficos ---
def analisis_periodos(df):
    """Compara dos periodos definidos y genera gráficos de totales y promedios mensuales."""
    print("\nIniciando comparación entre periodos...")

    # Definir periodos
    periodo_1 = df["2024-01-01":"2025-02-28"]
    periodo_2 = df["2025-03-01":"2025-09-30"]

    # Calcular totales por periodo
    resumen = pd.DataFrame({
        "Periodo": ["Ene2024-Feb2025", "Mar2025-Sep2025"],
        "Meses": [14, 7],
        "Registros": [
            periodo_1["Registros"].sum(),
            periodo_2["Registros"].sum()
        ],
        "Primeros Depósitos": [
            periodo_1["Primeros Depósitos"].sum(),
            periodo_2["Primeros Depósitos"].sum()
        ]
    })

    # Calcular promedios mensuales
    resumen["Promedio Registros"] = resumen["Registros"] / resumen["Meses"]
    resumen["Promedio Depósitos"] = resumen["Primeros Depósitos"] / resumen["Meses"]

    print("\n--- Totales y Promedios por Periodo ---")
    print(resumen[["Periodo", "Registros", "Primeros Depósitos", "Promedio Registros", "Promedio Depósitos"]])

    # --- Gráfico 1: Registros Totales ---
    plt.figure()
    sns.barplot(
        x="Periodo",
        y="Registros",
        data=resumen,
        palette=["#1f77b4"],  # azul
        edgecolor="black"
    )
    plt.title("Comparación de Registros Totales por Periodo", fontsize=15, weight="bold")
    plt.ylabel("Total de Registros")
    plt.xlabel("Periodo")
    plt.tight_layout()
    plt.savefig("comparacion_registros_totales.png")
    print("Gráfico 'comparacion_registros_totales.png' guardado.")

    # --- Gráfico 2: Primeros Depósitos Totales ---
    plt.figure()
    sns.barplot(
        x="Periodo",
        y="Primeros Depósitos",
        data=resumen,
        palette=["#ff7f0e"],  # naranja
        edgecolor="black"
    )
    plt.title("Comparación de Primeros Depósitos Totales por Periodo", fontsize=15, weight="bold")
    plt.ylabel("Total de Primeros Depósitos")
    plt.xlabel("Periodo")
    plt.tight_layout()
    plt.savefig("comparacion_depositos_totales.png")
    print("Gráfico 'comparacion_depositos_totales.png' guardado.")

    # --- Gráfico 3: Promedio Mensual de Registros ---
    plt.figure()
    sns.barplot(
        x="Periodo",
        y="Promedio Registros",
        data=resumen,
        palette=["#4a90e2"],  # azul más claro
        edgecolor="black"
    )
    plt.title("Promedio Mensual de Registros por Periodo", fontsize=15, weight="bold")
    plt.ylabel("Registros Promedio por Mes")
    plt.xlabel("Periodo")
    plt.tight_layout()
    plt.savefig("promedio_mensual_registros.png")
    print("Gráfico 'promedio_mensual_registros.png' guardado.")

    # --- Gráfico 4: Promedio Mensual de Primeros Depósitos ---
    plt.figure()
    sns.barplot(
        x="Periodo",
        y="Promedio Depósitos",
        data=resumen,
        palette=["#ffa64d"],  # naranja más claro
        edgecolor="black"
    )
    plt.title("Promedio Mensual de Primeros Depósitos por Periodo", fontsize=15, weight="bold")
    plt.ylabel("Depósitos Promedio por Mes")
    plt.xlabel("Periodo")
    plt.tight_layout()
    plt.savefig("promedio_mensual_depositos.png")
    print("Gráfico 'promedio_mensual_depositos.png' guardado.")

# --- Ejecución del Script ---
if __name__ == "__main__":
    df_principal = cargar_y_preparar_datos(archivo_base_datos, nombre_tabla_resumen)

    if df_principal is not None:
        analisis_periodos(df_principal)
        print("\nAnálisis completado con éxito.")
