# Herramienta para la limpieza de datos CASA - Formularios PhD

## Contacto

- **Nombre del Proyecto**: Herramienta de Limpieza de Datos CASA - Formularios PhD
- **Autor**: Adrian Velasquez
- **Correo Electrónico**: a.velasquezs@uniandes.edu.co

# Descripción
Este proyecto es una herramienta de limpieza de datos diseñada para procesar formularios relacionados con el programa
de doctorado (PhD) en la institución CASA.
La herramienta se encarga de eliminar caracteres no deseados, corregir formatos y asegurar la 
consistencia de los datos para facilitar su análisis y uso posterior.

## Instrucciones de ejecución

1. Instala dependencias:

```bash
pip install -r requirements.txt
```

2. Ejecuta la aplicación:

```bash
python src/main.py
```

## Generar ejecutable (PyInstaller)

El ejecutable se genera directamente en la carpeta raíz del proyecto.

### Compilación local (nativa)

Ejecuta el script en el sistema operativo en el que quieras producir el binario:

```bash
# macOS → genera  ./casa_phd_form.app
# Windows → genera ./casa_phd_form.exe
python src/services/build.py
```

Opciones disponibles:

| Flag | Descripción |
|---|---|
| `--name <nombre>` | Nombre del ejecutable (por defecto `casa_phd_form`) |
| `--no-clean` | No borrar artefactos de compilaciones anteriores |
| `--dry-run` | Mostrar el comando sin ejecutarlo |

### Compilación cruzada (GitHub Actions)

PyInstaller no soporta cross-compilation nativa: un `.exe` debe compilarse en Windows y el binario de macOS debe compilarse en macOS.

El workflow `.github/workflows/build.yml` resuelve esto automáticamente:

- Se dispara en cada push a `main`/`master`, en pull requests y en tags `v*`.
- Lanza **dos jobs en paralelo**: uno en `macos-latest` y otro en `windows-latest`.
- Windows se publica como `casa_phd_form.exe`.
- macOS se publica como `casa_phd_form-macos.zip`, que contiene `casa_phd_form.app`.
- Los artefactos quedan disponibles como **descargas** en la pestaña *Actions* de GitHub.
- Al hacer push de un tag de versión (p. ej. `v1.0.0`), se crea automáticamente un **GitHub Release** con ambos artefactos adjuntos.

### Nota importante sobre macOS

Para una aplicación gráfica de macOS, distribuir un `.app` es mejor que distribuir un binario suelto.

- Un binario descargado desde internet suele quedar marcado por **Gatekeeper** y puede no abrirse correctamente.
- Un `.dmg` mejora la experiencia de instalación, pero **no soluciona por sí solo** el problema si la app no está **firmada y notarizada**.
- Por ahora, este proyecto genera y publica un **`.app` comprimido en `.zip`**, que es la opción más simple y correcta sin agregar el flujo completo de firma/notarización.

Si macOS bloquea la aplicación descargada, puede ser necesario abrirla con clic derecho → **Open/Abrir** la primera vez, o quitar la cuarentena manualmente:

```bash
xattr -dr com.apple.quarantine casa_phd_form.app
```

```bash
# Dispara una compilación para ambas plataformas desde cualquier OS:
git tag v1.0.0 && git push origin v1.0.0
```

