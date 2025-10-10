# ============================================================
# ANALISIS ESTADÍSTICO DE CAMPAÑA DE MARKETING (2024 vs 2025)
# ============================================================

import pandas as pd
import sqlite3
from scipy.stats import ttest_ind
from statsmodels.stats.proportion import proportions_ztest
import numpy as np
from pathlib import Path
import warnings
import matplotlib.pyplot as plt
import seaborn as sns

warnings.filterwarnings("ignore")

# -------------------------------
# CONFIGURACIÓN
# -------------------------------
db_path = Path("Archivos/Archivos_base_datos/DataBase_aciertala.db")
tabla_resumen = "tabla_resumen_diario"

sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

# -------------------------------
# 1. CARGA Y PREPARACIÓN DE DATOS
# -------------------------------
def cargar_datos(db_path, tabla):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql(f"SELECT * FROM {tabla}", conn)
    conn.close()
    df["Fecha"] = pd.to_datetime(df["Fecha"])
    df = df.set_index("Fecha").sort_index()
    df = df.asfreq("D", fill_value=0)
    return df

df = cargar_datos(db_path, tabla_resumen)

# -------------------------------
# 2. SEGMENTACIÓN DE PERÍODOS
# -------------------------------
periodo_2024 = df["2024-03-01":"2024-09-30"]
periodo_2025 = df["2025-01-01":"2025-09-30"]

# -------------------------------
# 3. CÁLCULO DE KPIs
# -------------------------------
def calcular_kpis(data):
    total_reg = data["Registros"].sum()
    total_dep = data["Primeros Depósitos"].sum()
    tasa_conv = (total_dep / total_reg * 100) if total_reg > 0 else 0
    promedio_mensual = data.resample("M").sum().mean()
    return {
        "Registros totales": total_reg,
        "Depósitos totales": total_dep,
        "Tasa conversión (%)": tasa_conv,
        "Promedio mensual registros": promedio_mensual["Registros"],
        "Promedio mensual depósitos": promedio_mensual["Primeros Depósitos"]
    }

kpi_2024 = calcular_kpis(periodo_2024)
kpi_2025 = calcular_kpis(periodo_2025)

# -------------------------------
# 4. RESUMEN COMPARATIVO
# -------------------------------
def resumen_comparativo(kpi_2024, kpi_2025):
    def cambio_abs(y1, y2): return y2 - y1
    def cambio_pct(y1, y2): return (y2 - y1) / y1 * 100 if y1 > 0 else np.nan

    comparativo = pd.DataFrame({
        "Métrica": ["Registros totales", "Depósitos totales", "Tasa conversión (%)"],
        "2024": [kpi_2024["Registros totales"], kpi_2024["Depósitos totales"], kpi_2024["Tasa conversión (%)"]],
        "2025": [kpi_2025["Registros totales"], kpi_2025["Depósitos totales"], kpi_2025["Tasa conversión (%)"]],
        "Cambio absoluto": [
            cambio_abs(kpi_2024["Registros totales"], kpi_2025["Registros totales"]),
            cambio_abs(kpi_2024["Depósitos totales"], kpi_2025["Depósitos totales"]),
            cambio_abs(kpi_2024["Tasa conversión (%)"], kpi_2025["Tasa conversión (%)"])
        ],
        "Cambio %": [
            cambio_pct(kpi_2024["Registros totales"], kpi_2025["Registros totales"]),
            cambio_pct(kpi_2024["Depósitos totales"], kpi_2025["Depósitos totales"]),
            cambio_abs(kpi_2024["Tasa conversión (%)"], kpi_2025["Tasa conversión (%)"])
        ]
    })
    return comparativo

resumen = resumen_comparativo(kpi_2024, kpi_2025)

# -------------------------------
# 5. PRUEBAS DE SIGNIFICANCIA
# -------------------------------
def pruebas_significancia(p24, p25):
    print("\n--- PRUEBAS DE SIGNIFICANCIA ---")
    # t-test para comparar medias mensuales de registros
    reg24 = p24.resample("M").sum()["Registros"]
    reg25 = p25.resample("M").sum()["Registros"]
    t_reg, p_reg = ttest_ind(reg24, reg25, equal_var=False)

    dep24 = p24.resample("M").sum()["Primeros Depósitos"]
    dep25 = p25.resample("M").sum()["Primeros Depósitos"]
    t_dep, p_dep = ttest_ind(dep24, dep25, equal_var=False)

    # Test de proporciones para tasa de conversión
    count = np.array([p24["Primeros Depósitos"].sum(), p25["Primeros Depósitos"].sum()])
    nobs = np.array([p24["Registros"].sum(), p25["Registros"].sum()])
    z_stat, p_z = proportions_ztest(count, nobs)

    print(f"T-test Registros: p-value = {p_reg:.4f}")
    print(f"T-test Depósitos: p-value = {p_dep:.4f}")
    print(f"Z-test Tasa Conversión: p-value = {p_z:.4f}")

    return {"p_reg": p_reg, "p_dep": p_dep, "p_z": p_z}

p_vals = pruebas_significancia(periodo_2024, periodo_2025)

# -------------------------------
# 6. VISUALIZACIÓN RÁPIDA
# -------------------------------
def graficos_basicos(p24, p25):
    resumen_mensual_24 = p24.resample("M").sum()
    resumen_mensual_25 = p25.resample("M").sum()
    
    plt.figure()
    # plt.plot(resumen_mensual_24.index.month, resumen_mensual_24["Registros"], label="Registros 2024", linestyle="--", marker="o")
    # plt.plot(resumen_mensual_25.index.month, resumen_mensual_25["Registros"], label="Registros 2025", marker="o")
    plt.plot(resumen_mensual_24.index.month, resumen_mensual_24["Primeros Depósitos"], label="Depósitos 2024", linestyle="--", marker="x")
    plt.plot(resumen_mensual_25.index.month, resumen_mensual_25["Primeros Depósitos"], label="Depósitos 2025", marker="x")
    plt.xticks(range(3,10), ["Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep"])
    plt.title("Comparación mensual 2024 vs 2025")
    plt.xlabel("Mes")
    plt.ylabel("Cantidad")
    plt.legend()
    plt.tight_layout()
    plt.savefig("comparacion_mensual_registros.png")

# graficos_basicos(periodo_2024, periodo_2025)  # <- Descomenta si quieres el gráfico

# -------------------------------
# 7. IMPRESIÓN DE RESULTADOS
# -------------------------------
print("\n================ RESULTADOS CLAVE ================\n")
print(resumen.to_string(index=False))

# Interpretaciones automáticas
print("\n--- INTERPRETACIÓN ---")
if resumen.loc[0, "Cambio %"] > 0:
    print(f"• Los registros crecieron {resumen.loc[0, 'Cambio %']:.1f}% respecto al 2024.")
if resumen.loc[1, "Cambio %"] > 0:
    print(f"• Los primeros depósitos crecieron {resumen.loc[1, 'Cambio %']:.1f}% respecto al 2024.")
if resumen.loc[2, 'Cambio absoluto'] < 0:
    print(f"• La tasa de conversión disminuyó {abs(resumen.loc[2, 'Cambio absoluto']):.2f} puntos porcentuales.")

# Significancia
if p_vals["p_reg"] < 0.05:
    print("• Diferencia significativa en registros (p < 0.05).")
if p_vals["p_dep"] < 0.05:
    print("• Diferencia significativa en depósitos (p < 0.05).")
if p_vals["p_z"] < 0.05:
    print("• Diferencia significativa en tasa de conversión (p < 0.05).")

print("\n==================================================\n")
print("Análisis completado. Puedes usar estos resultados en tu presentación.")

graficos_basicos(periodo_2024, periodo_2025)
