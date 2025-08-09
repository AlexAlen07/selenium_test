import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    StaleElementReferenceException,
    TimeoutException,
)

# Inicializar Chrome
def initialize_driver():
    driver = webdriver.Chrome()
    driver.maximize_window()
    return driver

# Crear carpeta para guardar capturas
def create_screenshot_folder():
    folder_path = os.path.join(os.getcwd(), "screenshots")
    os.makedirs(folder_path, exist_ok=True)
    return folder_path

# Helper: click robusto sobre un elemento ya localizado
def safe_click_element(driver, element):
    try:
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'auto', block: 'center'});", element)
        time.sleep(0.2)
        element.click()
        return True
    except (ElementClickInterceptedException, StaleElementReferenceException) as e:
        try:
            # Fallback a click por JavaScript
            driver.execute_script("arguments[0].click();", element)
            return True
        except Exception as e2:
            print(f"⚠ safe_click_element: no se pudo clicar ni por .click() ni por JS: {e2}")
            return False
    except Exception as e:
        print(f"⚠ safe_click_element: error inesperado al clicar: {e}")
        return False

# Helper: wait + click por locator con fallback
def safe_click_by_locator(driver, wait, by, locator, folder_path=None, shot_name=None):
    try:
        element = wait.until(EC.element_to_be_clickable((by, locator)))
    except TimeoutException:
        print(f"⚠ safe_click_by_locator: timeout esperando {locator}")
        return False

    # intentar click normal y fallback a JS
    success = safe_click_element(driver, element)
    if folder_path and shot_name:
        try:
            driver.save_screenshot(os.path.join(folder_path, shot_name))
        except Exception:
            pass
    return success

# Registro con capturas
def register(driver, folder_path, nombre, usuario, clave):
    input_name = driver.find_element(By.NAME, "nombre")
    input_name.send_keys(nombre)
    driver.save_screenshot(os.path.join(folder_path, "01_nombre.png"))

    input_username = driver.find_element(By.NAME, "usuario")
    input_username.send_keys(usuario)
    driver.save_screenshot(os.path.join(folder_path, "02_usuario.png"))

    input_password = driver.find_element(By.NAME, "clave")
    input_password.send_keys(clave)
    driver.save_screenshot(os.path.join(folder_path, "03_clave.png"))

    register_button = driver.find_element(By.NAME, "registrarse")
    driver.save_screenshot(os.path.join(folder_path, "04_listo_para_registrar.png"))
    register_button.click()

    time.sleep(1)
    try:
        success_button = driver.find_element(By.NAME, "exito")
        driver.save_screenshot(os.path.join(folder_path, "05_boton_exito.png"))
        success_button.click()
        print("✅ Registro completado y regreso a login.php")
    except Exception:
        print("⚠ No se encontró el botón 'exito'")

# Login con los mismos datos del registro
def login(driver, folder_path, usuario, clave):
    time.sleep(1)
    input_username = driver.find_element(By.NAME, "usuario")
    input_username.send_keys(usuario)
    driver.save_screenshot(os.path.join(folder_path, "06_login_usuario.png"))

    input_password = driver.find_element(By.NAME, "clave")
    input_password.send_keys(clave)
    driver.save_screenshot(os.path.join(folder_path, "07_login_clave.png"))

    login_button = driver.find_element(By.NAME, "ingresar")
    driver.save_screenshot(os.path.join(folder_path, "08_listo_para_ingresar.png"))
    login_button.click()

    print("✅ Login realizado con el usuario recién registrado")

# Función para hacer scroll hasta el botón add_libro
def scroll_to_add_libro(driver):
    try:
        add_libro_button = driver.find_element(By.NAME, "add_libro")
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", add_libro_button)
        print("✅ Hice scroll hasta el botón 'add_libro'")
    except Exception:
        print("⚠ No se encontró el botón 'add_libro' para hacer scroll")

# Función para hacer scroll hasta el botón add_autor (no clickea)
def scroll_to_add_autor(driver):
    try:
        add_autor_button = driver.find_element(By.NAME, "add_autor")
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", add_autor_button)
        print("✅ Hice scroll hasta el botón 'add_autor'")
    except Exception:
        print("⚠ No se encontró el botón 'add_autor' para hacer scroll")

# Función para hacer click en add_libro y llenar campos
def add_libro(driver, folder_path, datos_libro):
    try:
        wait = WebDriverWait(driver, 10)
        add_libro_button = wait.until(EC.element_to_be_clickable((By.NAME, "add_libro")))
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'auto', block: 'center'});", add_libro_button)
        time.sleep(0.4)

        if not safe_click_element(driver, add_libro_button):
            print("⚠ No se pudo clicar add_libro")
            return

        time.sleep(1)
        driver.save_screenshot(os.path.join(folder_path, "09_click_add_libro.png"))
        print("✅ Click en botón 'add_libro'")

        for i, (campo, valor) in enumerate(datos_libro.items(), start=10):
            input_field = wait.until(EC.presence_of_element_located((By.NAME, campo)))
            input_field.clear()
            input_field.send_keys(str(valor))
            driver.save_screenshot(os.path.join(folder_path, f"{i:02d}_llenado_{campo}.png"))
            time.sleep(0.4)

        # Guardar libro
        btn_insertar = wait.until(EC.element_to_be_clickable((By.NAME, "btninsertar")))
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'auto', block: 'center'});", btn_insertar)
        time.sleep(0.3)
        if not safe_click_element(driver, btn_insertar):
            print("⚠ No se pudo clicar btninsertar")
        else:
            driver.save_screenshot(os.path.join(folder_path, "20_click_btninsertar.png"))
            print("✅ Click en botón 'btninsertar' para agregar el libro")

        time.sleep(1.5)

    except Exception as e:
        print(f"⚠ Error en add_libro: {e}")

# Función para hacer click en add_autor y llenar campos con click robusto en btnagregar
def add_autor(driver, folder_path, datos_autor):
    try:
        wait = WebDriverWait(driver, 12)

        # 1) localizar y clickear el botón que abre el formulario de autor
        add_autor_button = wait.until(EC.element_to_be_clickable((By.NAME, "add_autor")))
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'auto', block: 'center'});", add_autor_button)
        time.sleep(0.3)
        if not safe_click_element(driver, add_autor_button):
            print("⚠ No se pudo clicar add_autor")
            return
        time.sleep(0.8)
        driver.save_screenshot(os.path.join(folder_path, "21_click_add_autor.png"))
        print("✅ Click en botón 'add_autor'")

        # 2) esperar a que aparezca un campo referente al formulario del autor (usamos id_autor como ancla)
        try:
            anchor = wait.until(EC.presence_of_element_located((By.NAME, "id_autor")))
        except TimeoutException:
            # si no existe id_autor, tratamos de esperar cualquiera de los campos del autor
            possible = ["apellido", "nombre", "telefono"]
            anchor = None
            for p in possible:
                try:
                    anchor = wait.until(EC.presence_of_element_located((By.NAME, p)))
                    break
                except TimeoutException:
                    anchor = None
            if anchor is None:
                print("⚠ No se encontró ningún campo ancla del formulario de autor")
                return

        # 3) intentar obtener el formulario padre para buscar los inputs dentro de él (reduce colisiones por nombres repetidos)
        parent_scope = driver  # fallback global
        try:
            parent_scope = anchor.find_element(By.XPATH, "ancestor::form")
        except Exception:
            # si no hay <form>, se usará driver global (busca por name en todo el DOM)
            parent_scope = driver

        # 4) llenar los campos dentro del scope
        idx = 22
        for campo, valor in datos_autor.items():
            try:
                if parent_scope is driver:
                    input_field = wait.until(EC.presence_of_element_located((By.NAME, campo)))
                else:
                    # Buscar dentro del form
                    input_field = parent_scope.find_element(By.NAME, campo)
                input_field.clear()
                input_field.send_keys(str(valor))
                driver.save_screenshot(os.path.join(folder_path, f"{idx:02d}_llenado_{campo}.png"))
                idx += 1
                time.sleep(0.35)
            except Exception as e:
                print(f"⚠ No pude llenar campo '{campo}': {e}")

        # 5) localizar el botón btnagregar preferiblemente dentro del mismo scope y clicar con fallback
        try:
            if parent_scope is driver:
                btn_agregar = wait.until(EC.element_to_be_clickable((By.NAME, "btnagregar")))
            else:
                # intentar dentro del form primero
                try:
                    btn_agregar = parent_scope.find_element(By.NAME, "btnagregar")
                    # wrap with expected_conditions-like check: ensure it's displayed & enabled
                    if not btn_agregar.is_displayed() or not btn_agregar.is_enabled():
                        # fallback: wait for global clickable
                        btn_agregar = wait.until(EC.element_to_be_clickable((By.NAME, "btnagregar")))
                except Exception:
                    btn_agregar = wait.until(EC.element_to_be_clickable((By.NAME, "btnagregar")))
        except TimeoutException:
            print("⚠ Timeout buscando 'btnagregar'")
            return

        # Scroll + click robusto (intento normal y por JS como fallback)
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'auto', block: 'center'});", btn_agregar)
        time.sleep(0.3)
        clicked = safe_click_element(driver, btn_agregar)
        # Si no pudo con safe_click_element, intentar click via JS buscando de nuevo
        if not clicked:
            try:
                driver.execute_script("arguments[0].click();", btn_agregar)
                clicked = True
            except Exception as e:
                print(f"⚠ No se pudo forzar el click en btnagregar: {e}")
                clicked = False

        if clicked:
            driver.save_screenshot(os.path.join(folder_path, "31_click_btnagregar.png"))
            print("✅ Click en botón 'btnagregar' para agregar el autor")
        else:
            print("⚠ Falló el click en 'btnagregar'")

        time.sleep(1.5)

    except Exception as e:
        print(f"⚠ Error en add_autor: {e}")

# Función para ir a contacto y llenar el formulario
def contacto(driver, folder_path, datos_contacto):
    try:
        wait = WebDriverWait(driver, 10)
        contacto_button = wait.until(EC.element_to_be_clickable((By.NAME, "contacto")))
        if not safe_click_element(driver, contacto_button):
            print("⚠ No se pudo clicar contacto")
            return
        driver.save_screenshot(os.path.join(folder_path, "40_click_contacto.png"))
        time.sleep(0.6)

        # esperar a que el formulario de contacto esté presente (ancla: campo 'nombre' del contacto)
        anchor = wait.until(EC.presence_of_element_located((By.NAME, "nombre")))

        # intentar buscar inputs dentro del form padre (para evitar confusión con otros 'nombre')
        parent_scope = driver
        try:
            parent_scope = anchor.find_element(By.XPATH, "ancestor::form")
        except Exception:
            parent_scope = driver

        idx = 41
        for campo, valor in datos_contacto.items():
            try:
                if parent_scope is driver:
                    input_field = wait.until(EC.presence_of_element_located((By.NAME, campo)))
                else:
                    input_field = parent_scope.find_element(By.NAME, campo)
                input_field.clear()
                input_field.send_keys(str(valor))
                driver.save_screenshot(os.path.join(folder_path, f"{idx}_llenado_{campo}.png"))
                idx += 1
                time.sleep(0.35)
            except Exception as e:
                print(f"⚠ No pude llenar campo contacto '{campo}': {e}")

        btn_enviar = wait.until(EC.element_to_be_clickable((By.NAME, "btnenviar")))
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'auto', block: 'center'});", btn_enviar)
        time.sleep(0.3)
        if safe_click_element(driver, btn_enviar):
            driver.save_screenshot(os.path.join(folder_path, "50_click_btnenviar.png"))
            print("✅ Click en botón 'btnenviar' para enviar el formulario de contacto")
        else:
            print("⚠ No se pudo clicar btnenviar")

        time.sleep(1.5)

    except Exception as e:
        print(f"⚠ Error en contacto: {e}")

def main():
    driver = initialize_driver()
    folder_path = create_screenshot_folder()

    # Datos para registro/login
    nombre = "Emilio Ramon"
    usuario = "emilio"
    clave = "1234522"

    datos_libro = {
        "id_titulo": 839191,
        "titulo": "La Mona Lisa",
        "tipo": "Romance",
        "id_pub": 2829829,
        "precio": 8392,
        "avance": 3048,
        "total_ventas": 88201,
        "notas": "Prueba 66",
        "fecha_pub": "08/08/2025",
        "contrato": 1
    }

    datos_autor = {
        "id_autor": 2829292,
        "apellido": "Peralta",
        "nombre": "Luis",
        "telefono": "8098383933",
        "direccion": "calle Almanzar 4",
        "ciudad": "Distrito Nacional",
        "estado": "Santo Domingo",
        "pais": "Republica Dominicana",
        "cod_postal": "11733"
    }

    datos_contacto = {
        "nombre": "Feliz Jose",
        "correo": "felizjose828@gmail.com",
        "asunto": "Agregandome como cliente de la libreria",
        "fecha": "08/08/2025",
        "comentario": "Comentario de prueba"
    }

    driver.get("http://localhost/libreria-crud/login.php")

    register_button = driver.find_element(By.NAME, "registro")
    register_button.click()

    time.sleep(1)

    if driver.current_url == "http://localhost/libreria-crud/registro/registro.php":
        print("Accediendo al registro...")
        register(driver, folder_path, nombre, usuario, clave)
        login(driver, folder_path, usuario, clave)

        scroll_to_add_libro(driver)
        add_libro(driver, folder_path, datos_libro)

        # Intentar agregar autor con click robusto en btnagregar
        add_autor(driver, folder_path, datos_autor)

        # Luego ir a contacto y enviar formulario
        contacto(driver, folder_path, datos_contacto)

        print(f"✅ Capturas guardadas en: {folder_path}")
    else:
        print("❌ No se pudo acceder a la página de registro")

    time.sleep(2)
    driver.quit()

if __name__ == "__main__":
    main()