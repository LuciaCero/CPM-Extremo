import os

def crear_carpeta_ejecucion(nombre_input=None, base_dir="output"):
    """
    Crea la carpeta de salida para una ejecución del proyecto.

    Genera una subcarpeta dentro del directorio base usando el nombre del archivo de entrada, asegurando que tanto la carpeta base como la carpeta específica existan. Devuelve la ruta completa creada.

    Parámetros
    ----------
    nombre_input : str, opcional
        Nombre del archivo de entrada usado para nombrar la carpeta.
    base_dir : str, opcional
        Carpeta raíz donde se almacenarán los resultados (por defecto 'output').

    Devuelve
    --------
    str
        Ruta completa de la carpeta creada para esta ejecución.
    """

    nombre = os.path.splitext(os.path.basename(nombre_input))[0]

    # Asegurar que la carpeta base "output" exista
    os.makedirs(base_dir, exist_ok=True)

    # Crear subcarpeta para el input
    ruta = os.path.join(base_dir, nombre)
    os.makedirs(ruta, exist_ok=True)

    return ruta

def obtener_path_completo(dir: str, filename: str) -> str: 
    """
    Construye la ruta completa a un archivo dentro de un directorio dado.

    Parámetros
    ----------
    dir : str
        Directorio base.
    filename : str
        Nombre del archivo.

    Devuelve
    --------
    str
        Ruta absoluta combinando directorio y nombre de archivo.
    """

    return os.path.join(dir, filename)
