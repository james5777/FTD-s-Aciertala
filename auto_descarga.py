from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import time
import os

# === ⚙️ CONFIGURACIÓN GENERAL ===
USERNAME = "MarketingQM"
PASSWORD = "QuotaMedia2025*"
URL_LOGIN = "https://headoffice.technovus.app/backoffice/auth/login"
URL_TRANSACTIONS = "https://headoffice.technovus.app/backoffice/transactions-v2"

# === 📅 CONFIGURACIÓN DE FECHAS ===
# Puedes editar estas variables para ajustar el rango
FECHA_INICIO = "2025-03-01 00:00"
FECHA_FIN = "2025-09-21 23:59"

# Carpeta donde se descargará el CSV
DOWNLOAD_DIR = os.path.join(os.getcwd(), "Archivos")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# === 🚀 CONFIGURAR CHROME ===
options = webdriver.ChromeOptions()
prefs = {"download.default_directory": DOWNLOAD_DIR}
options.add_experimental_option("prefs", prefs)
options.add_argument("--start-maximized")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 40)

try:
    # === 1. LOGIN ===
    print("🌐 Iniciando sesión en el Sportbook...")
    driver.get(URL_LOGIN)
    wait.until(EC.presence_of_element_located((By.NAME, "username")))

    driver.find_element(By.NAME, "username").send_keys(USERNAME)
    driver.find_element(By.NAME, "password").send_keys(PASSWORD)
    driver.find_element(By.CSS_SELECTOR, "button.blue-btn").click()

    wait.until(EC.presence_of_element_located((By.LINK_TEXT, "Informes")))
    print("✅ Login exitoso.")

    # === 2. Ir a lista de transacciones ===
    print("📊 Navegando a 'Lista de transacciones'...")
    driver.get(URL_TRANSACTIONS)

    wait.until(EC.presence_of_element_located((By.XPATH, "//button[contains(., 'Exportar')]")))
    print("🧭 Formulario de transacciones detectado.")

    # === 3. Seleccionar “grupo causal” → Deposit - Withdraw ===
    print("🎯 Seleccionando 'grupo causal'...")

    boton_multiselect = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//label[contains(., 'grupo causal')]/following-sibling::div//button"))
    )
    boton_multiselect.click()
    time.sleep(1)

    opcion = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//label[contains(., 'Deposit - Withdraw')]/input"))
    )
    driver.execute_script("arguments[0].click();", opcion)
    time.sleep(1)

    boton_multiselect.click()
    print("✅ 'grupo causal' seleccionado correctamente.")

    # === 4. Seleccionar “Tipo” → Depositar ===
    print("🎯 Seleccionando 'Tipo'...")
    tipo_select = wait.until(EC.presence_of_element_located((By.NAME, "type")))
    Select(tipo_select).select_by_value("1")  # 1 = Depositar
    print("✅ 'Tipo' seleccionado correctamente.")

    # === 5. Configurar rango de fechas ===
    print("🕒 Configurando rango de fechas...")
    from_date = wait.until(EC.presence_of_element_located((By.ID, "from-date")))
    to_date = wait.until(EC.presence_of_element_located((By.ID, "to-date")))

    driver.execute_script("""
        arguments[0].value = arguments[2];
        arguments[1].value = arguments[3];
        arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
        arguments[1].dispatchEvent(new Event('change', { bubbles: true }));
    """, from_date, to_date, FECHA_INICIO, FECHA_FIN)

    try:
        boton_fecha = driver.find_element(By.CSS_SELECTOR, "button.daterange-ranges span")
        driver.execute_script(
            "arguments[0].textContent = arguments[1];",
            boton_fecha,
            f"{FECHA_INICIO} - {FECHA_FIN}"
        )
        print(f"✅ Fechas configuradas: {FECHA_INICIO} → {FECHA_FIN}")
    except Exception:
        print("⚠️ No se actualizó el texto visible (no es crítico).")

    # === 6. Aplicar filtro ===
    print("🔍 Aplicando filtro...")
    try:
        form = driver.find_element(By.XPATH, "//form[contains(@action, 'transactions-v2')]")
        driver.execute_script("arguments[0].submit();", form)
        print("✅ Filtro enviado (submit forzado).")
        time.sleep(6)
    except Exception as e:
        print(f"❌ Error al aplicar el filtro: {e}")
        driver.save_screenshot("error_filtro_submit.png")

    # === 7. Exportar CSV ===
    print("📁 Intentando exportar CSV...")
    try:
        boton_exportar = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Exportar')]"))
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", boton_exportar)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", boton_exportar)
        print("✅ Clic en 'Exportar' realizado.")

        # Esperar a que se descargue el CSV
        time.sleep(40)
        archivos = [f for f in os.listdir(DOWNLOAD_DIR) if f.endswith(".csv")]
        if archivos:
            print(f"✅ Archivo CSV detectado: {archivos[-1]}")
        else:
            print("⚠️ No se encontró ningún archivo CSV en la carpeta de descargas.")

    except Exception as e:
        print(f"❌ Error al exportar CSV: {e}")
        driver.save_screenshot("error_exportar.png")

except Exception as e:
    print("❌ Error general:", e)
    driver.save_screenshot("error_general.png")

finally:
    driver.quit()
    print("🌙 Navegador cerrado.")
