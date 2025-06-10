# 🧴 Proyecto Integrador – Sistema de Recomendaciones de Rutinas de Cuidado de la Piel

## 📝 Descripción

Este proyecto es una aplicación web desarrollada como trabajo final del curso de **Desarrollo de Software**. Su objetivo es ayudar a los usuarios a identificar sus hábitos actuales de cuidado de la piel y recibir una **rutina personalizada de productos recomendados**, basándose en sus respuestas.

Está dirigido a personas interesadas en mejorar su rutina de cuidado facial de forma guiada, especialmente quienes no tienen conocimientos dermatológicos y desean recomendaciones sencillas, efectivas y accesibles.

## 🚀 Funcionalidades principales

- 🧪 **Test de hábitos de cuidado de la piel** interactivo con imágenes y opciones simples.
- 🧠 **Análisis automático** de hábitos para generar una rutina personalizada.
- 📦 **Recomendación de productos** según el perfil del usuario y sus hábitos actuales.
- 👤 **Registro de usuarios** con almacenamiento de datos en la nube.
- 🌐 Interfaz amigable y responsive, pensada para usuarios móviles y de escritorio.
- 🖼️ Carga de imagen de perfil.
- 💾 Almacenamiento de hábitos y preferencias del usuario en base de datos.

## 🛠️ Tecnologías usadas

### 🌐 Frontend

- HTML5 + CSS3
- JavaScript (vanilla)
- [Jinja2](https://jinja.palletsprojects.com/) para renderizar plantillas dinámicas
- Estilo visual personalizado (colores pastel, imágenes ilustrativas)

### ⚙️ Backend

- Python 3.12
- FastAPI (framework web asincrónico)
- SQLAlchemy (ORM)
- Pydantic (validación de datos)

### 🗄️ Base de datos

- PostgreSQL (hospedada en [Clever Cloud](https://www.clever-cloud.com/))

### ☁️ Almacenamiento de imágenes

- Supabase (para guardar fotos de perfil de los usuarios)

### Despliegue en render

Link para ver el proyecto completo: https://proyecto-integrador-6gns.onrender.com

## 📂 Estructura del proyecto
Proyecto_Integrador/
│
├── app_/ # Lógica del backend (FastAPI)
│ ├── models.py
│ ├── routes.py
│ ├── database.py
│ └── ...
│
├── static/ # Archivos estáticos (CSS, imágenes, JS)
│
├── templates/ # Plantillas HTML (renderizadas por Jinja2)
│ ├── index.html
│ ├── test.html
│ └── rutina.html
│
├── main.py # Archivo principal que lanza el servidor FastAPI
└── README.md # Este archivo

## 🚧 Estado actual

✅ Registro de usuarios  
✅ Test de hábitos funcional  
✅ Recomendaciones personalizadas  
✅ Conexión a base de datos funcionando  
⏳ En desarrollo: vista de historial o evolución de hábitos


## 🤝 Autora

**Luna Herrera**
Estudiante de Sexto semestre de Ingeniería de Sistemas y Computación  
📧 lherrera95@ucatolica.edu.co


