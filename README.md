# 🩺 CuidaVida

CuidaVida es una aplicación web desarrollada para apoyar la gestión clínica y administrativa dentro del sector salud, permitiendo administrar pacientes y optimizar procesos médicos mediante herramientas digitales.

El proyecto fue desarrollado utilizando tecnologías web modernas y una arquitectura orientada a organización, escalabilidad y facilidad de mantenimiento.

---

## 📌 Objetivo

Desarrollar una solución tecnológica que facilite la administración de información médica y contribuya a mejorar la organización de procesos clínicos.

---

## ✨ Funcionalidades

✔️ Gestión de pacientes  
✔️ Administración clínica  
✔️ Autenticación de usuarios  
✔️ Gestión de registros médicos  
✔️ Generación de documentos PDF  
✔️ Manejo de base de datos  
✔️ Interfaz web para administración del sistema  

---

## 🛠️ Tecnologías utilizadas

### Backend
- Python
- Django

### Base de datos
- PostgreSQL
- SQL

### Frontend
- HTML
- CSS

### Herramientas
- Git
- GitHub

---

## 📂 Estructura del proyecto

```bash
cuidavida/
│
├── app/
├── templates/
├── static/
├── media/
├── database/
├── manage.py
├── requirements.txt
└── README.md
```

---

## ⚙️ Instalación

Clona el repositorio:

```bash
git clone https://github.com/annetjmtze/cuidavida1.git
```

Accede al proyecto:

```bash
cd cuidavida1
```

Crea un entorno virtual:

```bash
python -m venv venv
```

Activa el entorno:

Windows:

```bash
venv\Scripts\activate
```

Linux / Mac:

```bash
source venv/bin/activate
```

Instala dependencias:

```bash
pip install -r requirements.txt
```

---

## ▶️ Ejecución

Realiza migraciones:

```bash
python manage.py migrate
```

Inicia el servidor:

```bash
python manage.py runserver
```

Abre:

```txt
http://127.0.0.1:8000
```

---

## 🗄️ Base de datos

Configura las credenciales correspondientes dentro del archivo:

```txt
settings.py
```

Ejemplo:

```python
DATABASES = {
    'default': {
        'ENGINE': '',
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': ''
    }
}
```

---

## 📸 Capturas del sistema

Aquí puedes agregar imágenes del proyecto:

- Inicio de sesión
- Panel principal
- Gestión de pacientes
- Reportes generados

---

## 📚 Conceptos aplicados

- Arquitectura web
- CRUD
- Autenticación
- Gestión de bases de datos
- Generación de documentos
- Desarrollo backend

---

## 🎓 Contexto académico

Proyecto desarrollado como parte de la formación en **Ingeniería en Tecnologías de la Información y Comunicaciones (TICS)**.

---

## 👩‍💻 Autora

**Annet Martínez**  
Estudiante de Ingeniería en TICS  
Instituto Tecnológico de Morelia

GitHub: **@annetjmtze**
