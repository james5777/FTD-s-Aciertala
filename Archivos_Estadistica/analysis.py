
'''
Análisis de Datos y Proyección de Comportamiento de Usuarios

Este script realiza un análisis comparativo y una proyección de los datos de registros
y primeros depósitos de la empresa, con el objetivo de medir el impacto de una campaña
de publicidad iniciada en marzo de 2025.

El script realiza las siguientes acciones:
1.  Carga los datos desde la tabla de resumen diario de la base de datos SQLite.
2.  Prepara y limpia los datos para el análisis.
3.  Realiza un análisis comparativo entre los períodos marzo-septiembre de 2024 y 2025.
4.  Calcula y visualiza métricas clave como totales, promedios y tasa de conversión.
5.  Entrena modelos de series temporales (SARIMA) para registros y primeros depósitos.
6.  Genera y visualiza proyecciones para los próximos meses.
7.  Guarda todos los gráficos generados como archivos .png.
'''

import pandas as pd
import sqlite3
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.tsa.statespace.sarimax import SARIMAX
import warnings

# --- Configuración ---
warnings.filterwarnings("ignore")  # Ignorar warnings de los modelos para una salida más limpia

# --- Rutas y Nombres ---
archivo_base_datos = Path("Archivos/Archivos_base_datos/DataBase_aciertala.db")
nombre_tabla_resumen = 'tabla_resumen_diario'

# --- Estilo de los Gráficos ---
sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = (12, 7)

# --- 1. Carga y Preparación de Datos ---
def cargar_y_preparar_datos(db_path, table_name):
    '''Carga y prepara el DataFrame desde la base de datos.'''
    print(f"Cargando datos desde '{table_name}'...")
    conn = sqlite3.connect(db_path)
    try:
        df = pd.read_sql(f'SELECT * FROM {table_name}', conn)
        df['Fecha'] = pd.to_datetime(df['Fecha'])
        df = df.set_index('Fecha').sort_index()
        # Asegurar que el DataFrame tiene frecuencia diaria y rellenar huecos
        df = df.asfreq('D', fill_value=0)
        print("Datos cargados y preparados con éxito.")
        return df
    except Exception as e:
        print(f"Error al cargar los datos: {e}")
        return None
    finally:
        conn.close()

# --- 2. Análisis Comparativo ---
def analisis_comparativo(df):
    '''Realiza y visualiza la comparación entre 2024 y 2025.'''
    print("\nIniciando análisis comparativo...")
    # Segmentar datos
    periodo_2024 = df['2024-03-01':'2024-09-30']
    periodo_2025 = df['2025-03-01':'2025-09-30']

    # Calcular KPIs
    kpis = {}
    for year, data in [('2024', periodo_2024), ('2025', periodo_2025)]:
        total_registros = data['Registros'].sum()
        total_depositos = data['Primeros Depósitos'].sum()
        conversion_rate = (total_depositos / total_registros * 100) if total_registros > 0 else 0
        kpis[year] = {
            'Total Registros': total_registros,
            'Total Primeros Depósitos': total_depositos,
            'Tasa de Conversión (%)': conversion_rate
        }
    
    df_kpis = pd.DataFrame(kpis).T
    print("\n--- KPIs Comparativos (Mar-Sep) ---")
    print(df_kpis)

    # Visualización 1: Gráfico de Barras de Totales
    df_kpis[['Total Registros', 'Total Primeros Depósitos']].plot(kind='bar', rot=0)
    plt.title('Comparación de Totales (Marzo-Septiembre): 2024 vs 2025', fontsize=16, weight='bold')
    plt.ylabel('Cantidad Total')
    plt.xlabel('Año')
    plt.tight_layout()
    plt.savefig("comparacion_totales.png")
    print("\nGráfico 'comparacion_totales.png' guardado.")

    # Visualización 2: Gráficos de Líneas de Tendencia Mensual
    resumen_mensual_2024 = periodo_2024.resample('M').sum()
    resumen_mensual_2025 = periodo_2025.resample('M').sum()

    # Gráfico para Registros
    plt.figure()
    plt.plot(resumen_mensual_2024.index.month, resumen_mensual_2024['Registros'], marker='o', linestyle='--', label='Registros 2024')
    plt.plot(resumen_mensual_2025.index.month, resumen_mensual_2025['Registros'], marker='o', label='Registros 2025')
    plt.title('Tendencia Mensual de Registros: 2024 vs 2025', fontsize=16, weight='bold')
    plt.ylabel('Cantidad de Registros')
    plt.xlabel('Mes del Año')
    plt.xticks(ticks=range(3, 10), labels=['Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep'])
    plt.legend()
    plt.tight_layout()
    plt.savefig("comparacion_tendencia_mensual_registros.png")
    print("Gráfico 'comparacion_tendencia_mensual_registros.png' guardado.")

    # Gráfico para Primeros Depósitos
    plt.figure()
    plt.plot(resumen_mensual_2024.index.month, resumen_mensual_2024['Primeros Depósitos'], marker='x', linestyle='--', label='FTDs 2024')
    plt.plot(resumen_mensual_2025.index.month, resumen_mensual_2025['Primeros Depósitos'], marker='x', label='FTDs 2025')
    plt.title('Tendencia Mensual de Primeros Depósitos: 2024 vs 2025', fontsize=16, weight='bold')
    plt.ylabel('Cantidad de Primeros Depósitos')
    plt.xlabel('Mes del Año')
    plt.xticks(ticks=range(3, 10), labels=['Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep'])
    plt.legend()
    plt.tight_layout()
    plt.savefig("comparacion_tendencia_mensual_depositos.png")
    print("Gráfico 'comparacion_tendencia_mensual_depositos.png' guardado.")

# --- 3. Proyección con Series Temporales ---
def realizar_proyeccion(df, columna, n_meses):
    '''Entrena un modelo SARIMA y proyecta futuros valores.'''
    print(f"\nIniciando proyección para '{columna}'...")
    # Usar datos hasta el final del periodo conocido
    datos_serie = df[columna]
    
    # Definir y entrenar el modelo SARIMA
    # (p,d,q) son los parámetros de tendencia, (P,D,Q,m) los de estacionalidad.
    # m=7 para estacionalidad semanal.
    modelo = SARIMAX(datos_serie, order=(1, 1, 1), seasonal_order=(1, 1, 1, 7))
    resultado = modelo.fit(disp=False)
    
    # Realizar la predicción
    prediccion = resultado.get_prediction(start=len(datos_serie), end=len(datos_serie) + (n_meses * 30) - 1)
    prediccion_ci = prediccion.conf_int()

    # Visualización
    plt.figure()
    ax = datos_serie['2025':].plot(label='Observado (2025)')
    prediccion.predicted_mean.plot(ax=ax, label='Proyección', linestyle='--')
    ax.fill_between(prediccion_ci.index, prediccion_ci.iloc[:, 0], prediccion_ci.iloc[:, 1], color='k', alpha=.15)
    ax.set_xlabel('Fecha')
    ax.set_ylabel(columna)
    plt.title(f'Proyección de {columna} para los Próximos {n_meses} Meses', fontsize=16, weight='bold')
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"proyeccion_{columna.lower().replace(' ', '_')}.png")
    print(f"Gráfico 'proyeccion_{columna.lower().replace(' ', '_')}.png' guardado.")

# --- Ejecución del Script ---
if __name__ == "__main__":
    df_principal = cargar_y_preparar_datos(archivo_base_datos, nombre_tabla_resumen)
    
    if df_principal is not None:
        # Realizar el análisis comparativo
        analisis_comparativo(df_principal)
        
        # Realizar las proyecciones para los próximos 3 meses
        realizar_proyeccion(df_principal, 'Registros', n_meses=3)
        realizar_proyeccion(df_principal, 'Primeros Depósitos', n_meses=3)
        
        print("\nAnálisis y proyección finalizados con éxito.")
