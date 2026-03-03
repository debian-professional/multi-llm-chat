# DeepSeek Chat – Un cliente de chat privado y seguro para la API de DeepSeek

**DeepSeek Chat** es un cliente de chat completamente autónomo y alojado localmente para la API de DeepSeek. Fue desarrollado con enfoque en **seguridad, simplicidad y usabilidad profesional**. La arquitectura no requiere frameworks exóticos y utiliza únicamente tecnologías probadas: Apache como servidor web, Python CGI para la lógica del lado del servidor, y HTML/JavaScript/CSS puro en el lado del cliente.

Características principales:
- **Gestión de contexto única** – Elimina mensajes individuales junto con todos los posteriores. El chat permanece consistente y el uso de tokens se actualiza dinámicamente.
- **Máxima seguridad** – La clave API nunca es visible en el lado del cliente, las cargas están protegidas contra archivos ejecutables mediante inspección de magic bytes, y las sesiones se almacenan con permisos de archivo restrictivos.
- **Sin frameworks exóticos** – Todo se basa en Apache, Python, Bash y HTML/JS puro.
- **Funciones de exportación profesionales** – PDF, Markdown, TXT, RTF para todo el chat o mensajes individuales.
- **Soporte multiidioma** – Traducción completa de la UI mediante `language.xml` externo (inglés, alemán, español, extensible con idiomas personalizados).
- **Integración con portapapeles** – Manejador Ctrl+V con diálogo para texto, imágenes y protección contra el pegado accidental de rutas de archivos.
- **Respuestas en streaming** – Las respuestas de la IA aparecen token a token, igual que ChatGPT o Claude.
- **Herramienta incluida** – El script `repo2text.sh` exporta todo el repositorio como archivo de texto, ideal para trabajar con asistentes de IA (como este).

---

## Tabla de Contenidos

- [Descripción General](#descripción-general)
- [Arquitectura](#arquitectura)
- [Gestión de Contexto Única](#gestión-de-contexto-única)
- [Características en Detalle](#características-en-detalle)
  - [Interfaz de Chat](#interfaz-de-chat)
  - [Respuestas en Streaming](#respuestas-en-streaming)
  - [Manejador de Portapapeles (Ctrl+V)](#manejador-de-portapapeles-ctrlv)
  - [Carga de Archivos con Verificación de Seguridad](#carga-de-archivos-con-verificación-de-seguridad)
  - [Sistema de Marcadores de Posición para Umlauts](#sistema-de-marcadores-de-posición-para-umlauts)
  - [Modo DeepThink](#modo-deepthink)
  - [Detección de Modelos y Capacidades](#detección-de-modelos-y-capacidades)
  - [Sistema Multiidioma](#sistema-multiidioma)
  - [Configuración (Toggles en lugar de Botones de Radio)](#configuración-toggles-en-lugar-de-botones-de-radio)
  - [Gestión de Sesiones](#gestión-de-sesiones)
  - [Funciones de Exportación](#funciones-de-exportación)
  - [Botones de Feedback y Registro](#botones-de-feedback-y-registro)
  - [Visualización Dinámica del Contexto](#visualización-dinámica-del-contexto)
  - [Visualización de Tarjetas de Archivo](#visualización-de-tarjetas-de-archivo)
- [El Script Auxiliar `repo2text.sh`](#el-script-auxiliar-repo2textsh)
- [Arquitectura de Seguridad en Detalle](#arquitectura-de-seguridad-en-detalle)
- [Despliegue y Uso](#despliegue-y-uso)
  - [Requisitos Previos](#requisitos-previos)
  - [Instalación](#instalación)
  - [Configuración](#configuración)
  - [Scripts de Despliegue](#scripts-de-despliegue)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Configuración del Modelo](#configuración-del-modelo)
- [Manifiesto de Diseño](#manifiesto-de-diseño)
- [Limitaciones Conocidas y Notas Técnicas](#limitaciones-conocidas-y-notas-técnicas)
- [Dependencias](#dependencias)
- [Conclusión / Por Qué Destaca Este Proyecto](#conclusión--por-qué-destaca-este-proyecto)

---

## Descripción General

DeepSeek Chat es una **aplicación web local** que se comunica a través de la API de DeepSeek (modelos `deepseek-chat` y `deepseek-reasoner`). Desarrollada para un entorno de servidor privado (Debian), puede ejecutarse en cualquier sistema con Apache y Python 3. El objetivo fue crear un cliente de chat **seguro, extensible y fácil de usar** que funcione sin dependencias de nube y ofrezca control total sobre los datos.

El proyecto ha crecido continuamente durante varias semanas de desarrollo activo, añadiendo características como streaming, gestión de sesiones, funciones de exportación, soporte multiidioma, integración con portapapeles y medidas de seguridad robustas — todo sin introducir nunca frameworks JavaScript externos.

---

## Arquitectura

La arquitectura es intencionalmente simple pero bien pensada:

### 1. Cliente
- HTML/JavaScript/CSS puro, servido a través de Apache.
- Sin herramientas de compilación, sin Node.js, sin bibliotecas externas (excepto PDF.js para la extracción de texto PDF en el navegador).
- Toda la lógica del cliente (procesamiento de mensajes, actualizaciones de UI, recepción de streaming, cambio de idioma, manejo del portapapeles) está encapsulada en un único `index.html`.
- Todos los textos de la UI se cargan desde un `language.xml` externo al inicio — sin cadenas codificadas en el HTML.

### 2. Servidor
- **Apache** con soporte CGI (`mod_cgi`).
- **Scripts CGI de Python** bajo `/cgi-bin/` gestionan:
  - Comunicación con la API de DeepSeek (`deepseek-api.py`) — con streaming (Server-Sent Events)
  - Descubrimiento de modelos (`deepseek-models.py`) — consulta `/v1/models` al inicio
  - Almacenamiento y recuperación de sesiones (`save-session.py`, `load-session.py`, `delete-session.py`)
  - Exportaciones en varios formatos (`export-pdf.py`, `export-markdown.py`, `export-txt.py`, `export-rtf.py`)
  - Registro de feedback (`feedback-log.py`)
  - Visualización de registros (`get-log.py`)
- La **clave API** se proporciona exclusivamente a través de una variable de entorno de Apache (`DEEPSEEK_API_KEY` en `/etc/apache2/envvars`) — **nunca en el código del cliente**.
- Un único `ScriptAlias /cgi-bin/ /var/www/deepseek-chat/cgi-bin/` cubre todos los scripts — no se necesitan cambios en Apache al añadir nuevos scripts.

### 3. Almacenamiento de Datos
- Las **sesiones** se almacenan como archivos JSON en `/var/www/deepseek-chat/sessions/` con `chmod 700`.
- Los **registros** se escriben en `/var/www/deepseek-chat/cgi-bin/deepseek-chat.log` (sin clave API ni contenidos de sesión).
- La **configuración** permanece localmente en el navegador (`localStorage`) con control de versiones.
- Los **datos de idioma** se cargan desde `language.xml` al cargar la página mediante `fetch()`.

### 4. Scripts Auxiliares
- `deploy.sh`, `sync-back.sh`, `install.sh`, `tag-release.sh` facilitan el despliegue entre directorios de desarrollo y producción.
- `repo2text.sh` exporta todo el repositorio como archivo de texto para asistentes de IA.

---

## Gestión de Contexto Única

Una de las características más destacadas es la capacidad de **eliminar mensajes individuales junto con todos los posteriores**. Esto va mucho más allá del típico "eliminar último mensaje" y permite la corrección flexible del historial de conversación.

**Implementación**:
- Cada mensaje (usuario e IA) recibe un `id` único (formato: `msg_N`) y se almacena en un array `contextHistory.messages`.
- La función `deleteMessage(msgId)` determina el índice del mensaje, trunca el array desde `index` en adelante y elimina todos los elementos siguientes del DOM (incluidos los separadores).
- La estimación de tokens (`updateContextEstimation()`) se recalcula inmediatamente, al igual que el porcentaje de utilización del contexto en el encabezado.
- La sesión modificada se guarda automáticamente a continuación (`saveSession()`).

**¿Por qué es único?**
Muchos clientes de chat solo permiten eliminar el último mensaje o ninguna manipulación del historial. Aquí, el usuario puede **definir cualquier punto de la conversación como nuevo punto de partida** — perfecto para pruebas, correcciones o limpieza de la ventana de contexto sin perder todo el chat.

**Función de regeneración**: Además de la eliminación, cada respuesta de IA tiene un botón "Regenerar" que elimina la respuesta anterior y genera automáticamente una nueva basada en el mismo mensaje del usuario — usando el contexto completo de la conversación hasta ese punto.

---

## Características en Detalle

### Interfaz de Chat

- **Modo oscuro** (fijo, sin opción) — agradable a la vista, apariencia profesional.
  - Fondo: `#121212`, texto: `#f0f0f0`, acento: `#0056b3`
- **Encabezado del servidor** muestra el nombre del servidor, la dirección IP interna, la utilización dinámica del contexto y los nombres de modelos detectados.
- **Contenedores de mensajes** con botones al pasar el cursor (feedback, exportar, eliminar).
- **Textarea** se expande al enfocarse de 40px a 120px con suave animación CSS — Enter envía, Shift+Enter crea una nueva línea.
- Todos los botones siguen un diseño estricto de **estilo píldora** (border-radius: 20px, height: 36px) — sin botones cuadrados en ningún lugar.
- Los mensajes del usuario aparecen en azul (`#4dabf7`), las respuestas de IA en blanco sobre fondo oscuro.
- Preservación automática de saltos de línea (`white-space: pre-wrap`) para todo el contenido de los mensajes.
- Desplazamiento automático al último mensaje durante y después del streaming.

### Respuestas en Streaming

Las respuestas de IA se reciben y muestran **token a token** usando Server-Sent Events (SSE):

- `deepseek-api.py` envía solicitudes a DeepSeek con `stream: True` y reenvía el flujo de eventos directamente.
- `index.html` lee el flujo a través de la API `ReadableStream` y `TextDecoder`.
- Cada token recibido se añade al elemento de mensaje en tiempo real.
- El efecto psicológico es significativo: los primeros tokens aparecen en ~0,3 segundos en lugar de esperar 8+ segundos por una respuesta completa.
- Tanto `sendMessage()` como `handleRegenerate()` usan lógica de streaming idéntica.
- El desplazamiento automático permanece activo durante el streaming.

**Cabeceras técnicas** establecidas por `deepseek-api.py` para el streaming correcto:
```
Content-Type: text/event-stream
X-Accel-Buffering: no
Cache-Control: no-cache
```

### Integración con Google Gemini

Además de DeepSeek, la aplicación soporta **Google Gemini** como segundo proveedor de LLM:

- El cambio entre proveedores se realiza mediante el **toggle de Selección de LLM** en el panel de configuración principal (toggle verde, coherente con los toggles de preferencias personales).
- Un script Python dedicado `google-api.py` gestiona toda la comunicación con la API de Google Generative Language (`https://generativelanguage.googleapis.com/v1beta/models/{model}:streamGenerateContent`).
- La **GOOGLE_API_KEY** se almacena de forma segura en `/etc/apache2/envvars` — nunca en el código del cliente.
- Cuando Google está activo: el botón DeepThink se oculta (no aplicable), el toggle de Privacidad no es visible para usuarios del Free Tier.
- **Disponibilidad de modelos por nivel**:
  - **Free Tier**: `gemini-2.5-flash` (5 RPM, 20 RPD)
  - **Paid Tier**: `gemini-2.5-flash`, `gemini-2.5-pro`, `gemini-1.5-pro`, `gemini-2.0-flash`
- El desplegable de modelos se actualiza automáticamente al cambiar entre Free y Paid — los modelos no disponibles desaparecen al instante.

### Panel de Configuración LLM

Un nuevo botón **Configuración LLM** abre un segundo overlay de configuración con opciones específicas del proveedor:

- **Para DeepSeek**: Modo de Chat (Chat / DeepThink), toggle de Privacidad (no usar datos para entrenamiento), desplegable de selección de modelo.
- **Para Google**: Plan Google (Free / Paid), desplegable de selección de modelo.
- El panel de configuración principal permanece compacto: solo Selección de LLM, Idioma y Forma de tratamiento.
- Este enfoque de dos paneles mantiene la UI ordenada y hace que todas las opciones sean fácilmente accesibles.

### Manejo de Límite de Tasa 429

Cuando la API de Google Gemini devuelve un error `429 Too Many Requests`, la aplicación lo gestiona de forma elegante:

- **3 intentos de reintento automático** con **15 segundos de espera** entre cada uno.
- Se muestra un **mensaje de cuenta regresiva** en el chat durante cada período de espera (p. ej. "Límite de tasa alcanzado – esperando 15 segundos y reintentando... (Intento 1/3)").
- Tras agotar todos los reintentos, se muestra un mensaje de error amigable.
- Los detalles de error detallados de la respuesta de la API de Google se escriben en el registro del servidor para diagnóstico.
- Nota: Un `429` puede significar que se ha superado el RPM (solicitudes por minuto) o que se ha agotado la cuota diaria. El registro contiene el mensaje de error completo de Google para distinguir entre ambos casos.

### Manejador de Portapapeles (Ctrl+V)

Un sofisticado manejador de portapapeles intercepta los eventos de pegado y responde de forma inteligente según el tipo de contenido:

**Contenido de texto** → Aparece un diálogo de pegado con dos opciones:
- "Insertar en la posición del cursor" — inserta el texto directamente en el campo de entrada en la posición del cursor
- "Adjuntar como archivo" — trata el texto del portapapeles como `clipboard.txt` y lo adjunta como archivo al siguiente mensaje

**Contenido de imagen** → Aparece un cuadro de vista previa en miniatura encima del campo de entrada con la imagen, su tamaño en KB y un botón de eliminar. La imagen está lista para enviarse con el siguiente mensaje (si el modelo admite imágenes).

**Rutas de archivo del gestor de archivos (XFCE/Thunar, KDE/Dolphin)** → Estas se bloquean y se muestra una alerta:
> "Los archivos copiados en el gestor de archivos no pueden ser leídos por el navegador. Por favor, utilice el botón 'Subir archivo' en su lugar."

**Contexto técnico**: En Linux/X11/Firefox, `e.preventDefault()` no bloquea de forma fiable el comportamiento nativo de pegado del navegador para contenido proveniente de gestores de archivos. La solución implementada aquí (permitir el pegado, luego comprobar el contenido del campo de entrada mediante `setTimeout(0)`, y borrarlo si se detectan rutas de archivo) es la solución confiable para esta limitación específica de la plataforma.

### Carga de Archivos con Verificación de Seguridad

- Formatos aceptados: `.txt`, `.pdf`, `.doc`, `.docx`, `.jpg`, `.jpeg`, `.png`, `.csv`, `.xlsx`, `.pptx`
- Formatos procesables (extracción de contenido): `.txt`, `.pdf`
- Otros formatos aceptados: adjuntados como contexto binario (sin extracción de texto)
- Tamaño máximo de archivo: **10 MB**
- Contenido extraído máximo: **250.000 caracteres** (suficiente para archivos de texto grandes y exportaciones de repositorios)

**Inspección de magic bytes** (primeros 20 bytes) detecta y bloquea archivos ejecutables independientemente de su extensión de nombre de archivo:

| Plataforma | Formato | Firma |
|----------|--------|-----------|
| Windows 32/64 bits | PE/MZ Executable | `4D 5A` |
| Linux 32 bits | ELF32 | `7F 45 4C 46 01` |
| Linux 64 bits | ELF64 | `7F 45 4C 46 02` |
| ARM 32 bits | ELF32 ARM | `7F 45 4C 46 01 01 01 00 ... 02 00 28 00` |
| ARM 64 bits | ELF64 AArch64 | `7F 45 4C 46 02 01 01 00 ... 02 00 B7 00` |
| macOS 32 bits | Mach-O | `CE FA ED FE` |
| macOS 64 bits | Mach-O | `CF FA ED FE` |
| macOS Universal | Fat Binary | `CA FE BA BE` |
| macOS/iOS ARM 32 | Big Endian | `FE ED FA CE` |
| macOS/iOS ARM 64 | Big Endian | `FE ED FA CF` |
| Linux/macOS | Script Shell | `23 21` (#!) |
| Python | Bytecode (.pyc) | `55 0D 0D 0A` |

**Extracción de PDF**: Usa PDF.js 3.11.174 cargado desde CDN con respaldo automático a un CDN secundario. El progreso se muestra página a página. Tiempo de espera de extracción: 30 segundos.

**Los archivos cargados se muestran como tarjetas de archivo** en el mensaje del usuario (ver [Visualización de Tarjetas de Archivo](#visualización-de-tarjetas-de-archivo)).

### Sistema de Marcadores de Posición para Umlauts

Una solución única para un problema fundamental con la API de DeepSeek y el texto alemán:

**Problema**: DeepSeek reemplaza internamente los umlauts alemanes en el contenido de los archivos con equivalentes ASCII (por ejemplo, `Ä → AeNDERUNG`, `Ü → MUeSSEN`). Este comportamiento no puede suprimirse mediante prompts del sistema o parámetros de la API.

**Solución**: Antes de enviar el contenido del archivo a DeepSeek, los umlauts se reemplazan con marcadores de posición únicos. DeepSeek devuelve estos marcadores sin cambios. JavaScript los reemplaza de vuelta por umlauts reales tras recibir la respuesta.

| Original | Marcador |
|----------|----------|
| `ä` | `[[AE]]` |
| `ö` | `[[OE]]` |
| `ü` | `[[UE]]` |
| `ß` | `[[SS]]` |
| `Ä` | `[[CAE]]` |
| `Ö` | `[[COE]]` |
| `Ü` | `[[CUE]]` |

**Detalle importante de implementación**: Las funciones `encodeUmlautsForAI()` y `decodeUmlautsFromAI()` usan **exclusivamente secuencias de escape Unicode** (`\u00e4` en lugar de `ä`) y `split/join` en lugar de regex — esto es crítico para evitar corrupción al transferir archivos mediante Git.

La decodificación se ejecuta **tanto durante el streaming** (token a token) como después de recibir la respuesta completa.

Este sistema se aplica **solo al contenido de archivos**, no a los mensajes de usuario regulares ni a los prompts del sistema.

### Modo DeepThink

- Conmutable mediante un botón dedicado (estilo píldora-modo) en la segunda fila de botones.
- En modo DeepThink, se usa el modelo `deepseek-reasoner` (razonamiento real de cadena de pensamiento).
- El botón cambia visualmente: oscuro/inactivo (`#2d2d2d`) → azul activo (`#1e3a5f` fondo, `#4dabf7` borde y texto).
- Aparece una barra indicadora debajo de los botones mostrando "Modo DeepThink activo: Análisis en profundidad en curso".
- Los límites de contexto y de tokens de salida se ajustan automáticamente (ver [Configuración del Modelo](#configuración-del-modelo)).
- El modo se registra con cada mensaje y se muestra en las exportaciones.
- El modo predeterminado (Chat o DeepThink) se puede configurar en Ajustes y se persiste en `localStorage`.

### Detección de Modelos y Capacidades

Al inicio, el cliente consulta `/cgi-bin/deepseek-models.py` que a su vez llama al endpoint `/v1/models` de DeepSeek:

- Los IDs de modelos detectados se muestran en el encabezado del servidor: `Modelo: deepseek-chat, deepseek-reasoner`
- Un mapa `MODEL_CAPABILITIES` define qué modelos admiten imágenes:
  ```javascript
  const MODEL_CAPABILITIES = {
      'deepseek-chat':     { images: false, text: true },
      'deepseek-reasoner': { images: false, text: true },
      'deepseek-v4':       { images: true,  text: true },  // listo para modelos futuros
      'default':           { images: false, text: true },
  };
  ```
- Si se pega una imagen mediante el portapapeles o se carga un archivo `.jpg`/`.png`, y el modelo actual no admite imágenes, una alerta bloquea la operación.
- Esta arquitectura es **compatible con el futuro**: cuando DeepSeek V4 con soporte de imágenes sea lanzado, funcionará automáticamente sin cambios en el código.

### Sistema Multiidioma

La UI admite múltiples idiomas cargados desde un archivo `language.xml` externo:

**Idiomas actualmente incluidos**:
- Inglés (`en`) — predeterminado
- Alemán (`de`) — con forma de tratamiento formal/informal (Sie/Du)
- Español (`es`) — con forma de tratamiento formal/informal (Usted/Tú)
- Ranura personalizada (`custom`) — se puede activar mediante `visible="true"` en `language.xml`

**Cómo funciona**:
- Todos los textos de la UI se referencian mediante IDs numéricos (por ejemplo, `t(205)` = etiqueta del botón Enviar).
- `loadLanguage()` obtiene y analiza `language.xml` al cargar la página.
- `t(id)` devuelve el texto para el idioma actual, con respaldo al inglés si no se encuentra.
- `tf(id, ...args)` admite sustitución de marcadores de posición (`{0}`, `{1}`, ...).
- `tform(idFormal, idInformal)` devuelve el texto apropiado según la forma de tratamiento seleccionada.
- El cambio de idioma es inmediato sin recargar la página.
- El idioma seleccionado se persiste en `localStorage`.

**Sistema de forma de tratamiento (alemán/español)**:
- Los idiomas pueden declarar `has_address_form="true"` en `language.xml`.
- Para tales idiomas, el panel de Ajustes muestra un grupo "Forma de Tratamiento" (Formal/Informal).
- La forma seleccionada afecta a: el prompt del sistema (fuerza respuestas consistentes de la IA), el marcador de posición del campo de entrada, todas las descripciones de ajustes.
- El inglés no tiene distinción de forma de tratamiento.

**El prompt del sistema** se construye dinámicamente según el idioma, la forma de tratamiento y el modo:
- Prompt base (IDs de texto 29/30 para formal/informal)
- Adición de DeepThink (IDs de texto 31/32)
- Una instrucción estricta para la visualización de archivos siempre se añade en inglés para garantizar un comportamiento consistente independientemente del idioma de la UI.

### Configuración (Toggles en lugar de Botones de Radio)

Todos los ajustes usan **interruptores toggle** (deslizando de izquierda a derecha), nunca botones de radio ni casillas de verificación:

| Grupo | Ajuste | Color del Toggle |
|-------|---------|-------------|
| Idioma | EN / DE / ES / Custom | Verde (preferencia personal) |
| Forma de Tratamiento | Formal / Informal | Verde (preferencia personal) |
| Modo Predeterminado | Chat Normal / DeepThink | Azul (modo técnico) |
| Privacidad | No usar datos para entrenamiento | Verde |

**Comportamiento del toggle**:
- Dentro de un grupo, los toggles se comportan como botones de radio: activar uno desactiva los otros.
- Hacer clic en cualquier parte de la fila `setting-item` activa el toggle correspondiente.
- Retroalimentación visual: los elementos activos obtienen un fondo de color (`#1a2e1a` verde o `#1e3a5f` azul).

**Toggle de privacidad**: Establece la cabecera `X-No-Training: true` en las solicitudes a la API (compatible con el mecanismo de exclusión voluntaria de DeepSeek).

**Persistencia de ajustes**: Todos los ajustes se almacenan en `localStorage` bajo la clave `deepseekSettings`. `SETTINGS_VERSION` actual: `1.3`. La función `migrateSettings()` proporciona compatibilidad hacia atrás con ajustes almacenados más antiguos.

### Gestión de Sesiones

Cada conversación se gestiona automáticamente como una sesión con nombre:

- **Formato del ID de sesión**: `YYYY-MM-DD_HHMMSS_random` (por ejemplo, `2026-02-16_143045_abc123`) — generado en el cliente, validado en el servidor.
- **Guardado automático**: Después de cada par de mensajes (usuario + IA), el array completo `contextHistory.messages` se guarda como archivo JSON en el servidor.
- **Formato del archivo de sesión**: `{sessionId}.json` en `/var/www/deepseek-chat/sessions/`, `chmod 600`.
- **Modal de carga del historial de chat**: Muestra todas las sesiones guardadas con ID, fecha, vista previa del mensaje y número de mensajes. Cada sesión tiene botones [Cargar] (verde) y [Eliminar] (rojo).
- **Comportamiento al cargar**: Al cargar una sesión, el chat actual se guarda automáticamente primero, luego la sesión seleccionada se restaura con el historial completo de mensajes y la reconstrucción de la UI.
- **Eliminación de sesión**: El archivo JSON se elimina del servidor inmediatamente.

**Scripts CGI**:
- `save-session.py` — POST: recibe `{sessionId, messages}`, valida el formato del ID, escribe JSON
- `load-session.py` — GET: devuelve lista con vistas previas; GET con `?id=`: devuelve datos completos de la sesión
- `delete-session.py` — DELETE: elimina el archivo de sesión

### Funciones de Exportación

**Exportación global** (botón desplegable en la fila principal):

| Formato | Generación | Contiene |
|--------|-----------|---------|
| PDF | En el servidor (ReportLab) | Encabezado, estadísticas, tabla de contenidos, chat completo |
| Markdown | En el servidor | Estructura idéntica al PDF, con anclas Markdown |
| TXT | En el servidor | Texto plano con separadores |
| RTF | En el servidor | Formato RTF, umlauts como códigos RTF (sin biblioteca externa) |

**Exportación por mensaje** (botón al pasar el cursor sobre cada mensaje):

| Formato | Generación |
|--------|-----------|
| TXT | En el cliente (JavaScript Blob, sin petición al servidor) |
| Markdown | En el cliente |
| RTF | En el cliente |
| PDF | En el servidor (mensaje único enviado a `export-pdf.py`) |

**Contenido de exportación** (PDF/Markdown):
- Encabezado con nombre del servidor, IP, fecha de exportación, ajustes de idioma/forma de tratamiento
- Sección de estadísticas: número de mensajes, modos usados, archivos adjuntos, tokens estimados, duración
- Tabla de contenidos con todos los mensajes
- Historial completo del chat con marcas de tiempo e indicadores de modo
- Codificación de colores por rol del mensaje y modo

**Nota técnica sobre PDF**: Los datos PDF binarios se escriben exclusivamente a través de `sys.stdout.buffer` con encabezados HTTP codificados como bytes — evitando el error "Bad header" que ocurre al mezclar `print()` (modo texto) con salida binaria.

### Botones de Feedback y Registro

Cuatro botones aparecen al pasar el cursor sobre cada respuesta de IA (lado izquierdo, inferior):

- **Copiar** — Copia el texto del mensaje al portapapeles; muestra "¡Copiado!" durante 2 segundos, luego se restablece.
- **Me gusta** — Marca la respuesta positivamente (resaltado azul); envía una entrada ME GUSTA al registro del servidor. Hacer clic de nuevo elimina el like.
- **No me gusta** — Marca la respuesta negativamente (resaltado rojo); envía una entrada NO ME GUSTA. Me gusta y No me gusta se excluyen mutuamente.
- **Regenerar** — Elimina la respuesta de IA actual del contexto y DOM, luego llama a la API de nuevo con el mismo mensaje del usuario y el historial previo completo.

**Formato del registro en el servidor** (`deepseek-chat.log`):
```
2026-02-17 17:30:00 | 192.168.1.x | FEEDBACK | LIKE | msg_5 | "Primeros 60 caracteres del mensaje..."
2026-02-17 17:30:00 | 192.168.1.x | POST | /cgi-bin/deepseek-api.py | 200
```
**Nunca se registra**: Claves API, contenidos de sesión o texto de mensajes más allá de la vista previa de 60 caracteres del feedback.

### Visualización Dinámica del Contexto

El encabezado del servidor muestra cuatro líneas de información:
1. Nombre del servidor (en azul, `#4dabf7`)
2. `IP: xxx.xxx.xxx.xxx`
3. `Contexto: XX% (nombre-modelo)`
4. `Modelo: deepseek-chat, deepseek-reasoner`

**Cálculo de la utilización del contexto**:
- Tokens estimados = total de caracteres en mensajes recientes × `TOKENS_PER_CHAR` (0,25)
- Solo se cuentan los últimos N mensajes (N = `maxContextMessages` de `MODEL_CONFIG`)
- Los tokens del prompt del sistema se añaden por separado
- Porcentaje = tokens estimados / `maxContextTokens` × 100

**Sistema de advertencia**: Por encima del 90%, la línea de contexto se vuelve roja y parpadea (animación CSS, opacidad 0 → 1, ciclo de 1 segundo) — una advertencia muy visible de que la ventana de contexto está casi llena.

La visualización se actualiza automáticamente con: cada mensaje enviado, cada mensaje eliminado, cada cambio de modelo.

### Visualización de Tarjetas de Archivo

Cuando se carga un archivo o se adjunta texto del portapapeles, el mensaje del usuario muestra una **tarjeta de archivo** — un elemento visual compacto similar a Claude o ChatGPT:

```
┌─────────────────────────────────────┐
│  [PDF]  │  nombre_archivo.pdf       │
│  Icono  │  Documento PDF            │
└─────────────────────────────────────┘
```

- Muestra la insignia del tipo de archivo (PDF, TXT, XLSX, etc.) derivada de la extensión del archivo
- Muestra el nombre de archivo truncado (máximo 30 caracteres con `...`)
- Se aplica a: cargas de archivos reales mediante el botón de carga, texto del portapapeles adjuntado como archivo (`clipboard.txt`), y todos los demás formatos aceptados

---

## El Script Auxiliar `repo2text.sh`

Este script de Bash fue desarrollado específicamente para **exportar todo el código fuente de un repositorio de GitHub como un único archivo de texto** — ideal para pasar el contexto completo del proyecto a un asistente de IA.

**Cómo funciona**:
- Clona el repositorio con `git clone --depth 1`.
- Analiza todos los archivos de texto (tipo MIME + `grep -Iq .`) y los escribe con separadores en un archivo de salida.
- Respeta explícitamente `.gitignore` y `.gitattributes`.
- Admite formatos de salida TXT, JSON y Markdown.
- Crea un archivo ZIP del archivo de exportación.
- Incluye metadatos: hash de commit, rama, marca de tiempo.

**Opciones especiales**:
- `--flat`: Usar solo nombres de archivo sin rutas.
- `-o, --only PATH`: Exportar solo un subdirectorio específico.
- `-md5, --md5`: Calcular e incluir la suma de comprobación MD5 para cada archivo.
- Detección inteligente de la URL remota cuando el script se ejecuta dentro de un repositorio Git.
- Se admiten tanto `md5sum` (Linux) como `md5` (macOS).

**Ejemplos**:

```bash
# Exportación simple (solicitud interactiva de URL)
./repo2text.sh

# Exportación con URL como Markdown
./repo2text.sh -f md https://github.com/debian-professional/private-chatboot.git

# Exportar solo el directorio 'shell-scipts' con estructura plana
./repo2text.sh --flat -o shell-scipts https://github.com/debian-professional/private-chatboot.git

# Exportación con sumas de comprobación MD5
./repo2text.sh -md5 https://github.com/debian-professional/private-chatboot.git
```

**¿Por qué es útil?**
- Permite la documentación completa del proyecto en un único archivo.
- Perfecto para insertar bases de código completas en chats de IA.
- La opción MD5 ayuda a verificar la integridad de los archivos después de la exportación.

> `repo2text` también está disponible como proyecto independiente: [github.com/debian-professional/repo2text](https://github.com/debian-professional/repo2text)

---

## Arquitectura de Seguridad en Detalle

La seguridad fue la máxima prioridad en todo este proyecto. Aquí están todas las medidas clave:

### 1. Clave API — Nunca Expuesta al Cliente
- La clave se mantiene **exclusivamente** en la variable de entorno de Apache `DEEPSEEK_API_KEY` (configurada en `/etc/apache2/envvars`).
- `deepseek-api.py` la recupera mediante `os.environ.get('DEEPSEEK_API_KEY')`.
- El cliente solo se comunica con `/cgi-bin/deepseek-api.py` (proxy local) — nunca directamente con la API de DeepSeek.
- Incluso en caso de un ataque XSS, la clave no podría leerse desde la página.

### 2. Inspección de Magic Bytes Contra Archivos Ejecutables
- Antes de leer cualquier archivo cargado, se comprueban los primeros 20 bytes contra una base de datos de firmas completa (ver [Carga de Archivos con Verificación de Seguridad](#carga-de-archivos-con-verificación-de-seguridad)).
- Si hay una coincidencia, la carga se bloquea con un mensaje de error detallado que muestra la plataforma y el formato detectados.
- Esta protección funciona incluso si los archivos maliciosos son renombrados (por ejemplo, `virus.exe` → `factura.pdf`).

### 3. Almacenamiento Seguro de Sesiones
- Directorio de sesiones: `/var/www/deepseek-chat/sessions/` — `chmod 700`
- Cada archivo de sesión: `chmod 600`
- El formato del ID de sesión se valida en el servidor — no es posible el recorrido de rutas.

### 4. Registro Sin Datos Sensibles
- El registro contiene: marcas de tiempo, direcciones IP, métodos HTTP, rutas, códigos de estado, mensajes de error.
- **Nunca registrado**: Claves API, contenidos de sesión, texto de mensajes (más allá de las vistas previas de 60 caracteres del feedback).
- Las solicitudes OPTIONS se filtran para evitar la saturación del registro.

### 5. Sin Comunicación Directa Cliente-API
- Todas las operaciones críticas de seguridad ocurren en el lado del servidor a través de CGI de Python.
- El cliente no tiene conocimiento de credenciales de API, rutas del servidor o ubicaciones de almacenamiento de sesiones.

### 6. Validación de Entrada
- Los formatos de archivo se validan tanto por extensión como por magic bytes.
- Los IDs de sesión se validan en el servidor contra el regex del formato esperado.
- El pegado del portapapeles se filtra para bloquear rutas de archivo antes de que lleguen a la API.

### 7. Seguridad en el Transporte
- HTTPS forzado mediante la configuración SSL de Apache (`deepseek-chat-ssl.conf`).
- La configuración HTTP (`deepseek-chat.conf`) está desactivada mediante `a2dissite`.

---

## Despliegue y Uso

### Requisitos Previos

- Sistema basado en Debian (o cualquier Linux con Apache, Python 3, Bash)
- Apache con módulo CGI (`a2enmod cgi`) y SSL (`a2enmod ssl`)
- Python 3 con paquetes: `reportlab`
- Para `repo2text.sh`: `jq`, `pv`, `zip`, `git`
- Una clave API de DeepSeek válida de [platform.deepseek.com](https://platform.deepseek.com)

### Instalación

**1. Clonar el repositorio** (como usuario `source`):
```bash
git clone https://github.com/debian-professional/private-chatboot.git /home/source/private-chatboot
```

**2. Configurar la clave API**:
```bash
# Añadir a /etc/apache2/envvars:
export DEEPSEEK_API_KEY="su-clave-api-de-deepseek-aqui"
```

**3. Activar la configuración de Apache**:
```bash
a2ensite deepseek-chat-ssl.conf
a2dissite deepseek-chat.conf   # desactivar configuración HTTP simple
systemctl restart apache2
```

**4. Crear los directorios necesarios**:
```bash
mkdir -p /var/www/deepseek-chat/sessions
chown www-data:www-data /var/www/deepseek-chat/sessions
chmod 700 /var/www/deepseek-chat/sessions
```

**5. Ejecutar el script de despliegue** (como root):
```bash
./deploy.sh source
```

**6. Instalar scripts auxiliares**:
```bash
./install.sh   # como root — copia deploy.sh y sync-back.sh al directorio de producción
```

### Configuración

**Clave API de DeepSeek** (en `/etc/apache2/envvars`):
```bash
export DEEPSEEK_API_KEY="tu-clave-deepseek-aquí"
```

**Clave API de Google Gemini** (mismo archivo):
```bash
export GOOGLE_API_KEY="tu-clave-google-aquí"
```

Ambas claves se cargan en el entorno de Apache y se pasan a los scripts CGI correspondientes — no aparecen en ningún archivo accesible desde el cliente.

**Configuración del modelo** (`MODEL_CONFIG` en `index.html`):
```javascript
const MODEL_CONFIG = {
    'deepseek-chat':    { maxContextTokens: 100000,  maxOutputTokens: 8192,  maxContextMessages: 50  },
    'deepseek-reasoner':{ maxContextTokens: 65000,   maxOutputTokens: 32768, maxContextMessages: 30  },
    'gemini-2.5-flash': { maxContextTokens: 1048576, maxOutputTokens: 8192,  maxContextMessages: 100 },
    'gemini-2.5-pro':   { maxContextTokens: 1048576, maxOutputTokens: 65536, maxContextMessages: 100 },
    'gemini-1.5-pro':   { maxContextTokens: 2097152, maxOutputTokens: 8192,  maxContextMessages: 100 },
    'gemini-2.0-flash': { maxContextTokens: 1048576, maxOutputTokens: 8192,  maxContextMessages: 100 }
};
```
Para añadir un nuevo modelo, basta con ampliar este bloque y la lista `GOOGLE_MODELS_FREE` / `GOOGLE_MODELS_PAID` correspondiente.

**Configuración de idioma** (`language.xml`):
- Añadir un nuevo bloque `<language id="custom" name="..." visible="true">` para activar el slot de idioma personalizado.
- Establecer `has_address_form="true"` para idiomas con distinción formal/informal.

### Scripts de Despliegue

| Script | Función |
|--------|----------|
| `deploy.sh <user>` | Copia archivos desde `/home/<user>/private-chatboot/var/www/deepseek-chat/` a `/var/www/deepseek-chat/`, establece propiedad/permisos, recarga Apache |
| `sync-back.sh <user>` | Copia archivos modificados de producción de vuelta al repositorio fuente |
| `install.sh` | Instala `deploy.sh` y `sync-back.sh` en el directorio de producción |
| `tag-release.sh` | Crea una nueva etiqueta Git con número de versión auto-incrementado (por ejemplo, v0.80 → v0.81) y la empuja |

---

## Estructura del Proyecto

```
/
├── etc/apache2/sites-available/
│   ├── deepseek-chat.conf              (desactivado — solo HTTP, redirige a HTTPS)
│   └── deepseek-chat-ssl.conf          (activo — SSL, CGI, clave API via envvars)
├── shell-scipts/
│   ├── repo2text.sh                    Exportar todo el repo como archivo de texto único
│   ├── deploy.sh                       Copia repositorio fuente → producción
│   ├── sync-back.sh                    Copia producción → repositorio fuente
│   ├── install.sh                      Instala scripts deploy/sync-back
│   └── tag-release.sh                  Crea y empuja etiquetas de versión Git
├── var/www/deepseek-chat/
│   ├── index.html                      Aplicación principal (todo JS/CSS/HTML)
│   ├── language.xml                    Todos los textos de la UI en todos los idiomas (EN, DE, ES, Custom)
│   ├── manifest                        Manifiesto de diseño (todas las convenciones, ~20KB)
│   ├── changelog                       Historial completo de desarrollo (68+ entradas, ~44KB)
│   ├── files-directorys                Resumen de archivos / listado de directorios
│   ├── cgi-bin/
│   │   ├── deepseek-api.py            Proxy de streaming a la API de DeepSeek
│   │   ├── google-api.py              Proxy de streaming a la API de Google Gemini (con reintento 429)
│   │   ├── deepseek-models.py         Consulta el endpoint /v1/models
│   │   ├── save-session.py            Guarda sesiones de chat (POST)
│   │   ├── load-session.py            Carga lista de sesiones (GET) o sesión (GET ?id=)
│   │   ├── delete-session.py          Elimina sesión (DELETE)
│   │   ├── export-pdf.py              Exportación PDF con ReportLab
│   │   ├── export-markdown.py         Exportación Markdown
│   │   ├── export-txt.py              Exportación TXT
│   │   ├── export-rtf.py              Exportación RTF (sin biblioteca externa)
│   │   ├── feedback-log.py            Registro de Me gusta/No me gusta
│   │   ├── get-log.py                 Lee y devuelve el archivo de registro
│   │   └── deepseek-chat.log          Archivo de registro del servidor (creado automáticamente)
│   └── sessions/                      Archivos JSON de sesiones de chat (creados automáticamente)
```

---

## Configuración del Modelo

El objeto `MODEL_CONFIG` en `index.html` es la única fuente de verdad para todos los límites específicos de cada modelo:

```javascript
const MODEL_CONFIG = {
    'deepseek-chat': {
        maxContextTokens:   100000,   // Ventana de contexto de DeepSeek V3
        maxOutputTokens:    8192,     // Tokens máximos por respuesta
        maxContextMessages: 50        // Mensajes máximos enviados como contexto
    },
    'deepseek-reasoner': {
        maxContextTokens:   65000,    // Ventana de contexto de DeepSeek R1
        maxOutputTokens:    32768,    // R1 admite cadenas de razonamiento más largas
        maxContextMessages: 30        // Menos mensajes debido al overhead de razonamiento
    },
    'gemini-2.5-flash': {
        maxContextTokens:   1048576,  // Ventana de contexto de 1M tokens
        maxOutputTokens:    8192,
        maxContextMessages: 100
    },
    'gemini-2.5-pro': {
        maxContextTokens:   1048576,
        maxOutputTokens:    65536,
        maxContextMessages: 100
    },
    'gemini-1.5-pro': {
        maxContextTokens:   2097152,  // Ventana de contexto de 2M tokens
        maxOutputTokens:    8192,
        maxContextMessages: 100
    },
    'gemini-2.0-flash': {
        maxContextTokens:   1048576,
        maxOutputTokens:    8192,
        maxContextMessages: 100
    }
};
```

Listas de modelos por nivel de Google:
```javascript
const GOOGLE_MODELS_FREE = ['gemini-2.5-flash'];
const GOOGLE_MODELS_PAID = ['gemini-2.5-flash', 'gemini-2.5-pro', 'gemini-1.5-pro', 'gemini-2.0-flash'];
```

Fuentes: [Documentación de la API de DeepSeek](https://api-docs.deepseek.com) (19.02.2026), [Google AI Rate Limits](https://ai.dev/rate-limit) (03.03.2026).

**Estimación de tokens**: `TOKENS_PER_CHAR = 0,25` (4 caracteres ≈ 1 token — estimación conservadora para texto mixto inglés/alemán).

Al añadir un nuevo modelo, **solo es necesario actualizar `MODEL_CONFIG` y la lista de modelos correspondiente**. Todas las funciones dependientes (`updateContextDisplay()`, `sendMessage()`, `handleRegenerate()`) usarán automáticamente los nuevos valores.

---

## Manifiesto de Diseño

El proyecto incluye un archivo **`manifest`** que documenta todas las decisiones y convenciones de diseño. Cada cambio en el proyecto se documenta allí. Reglas clave:

- **Todos los botones**: Solo estilo píldora (border-radius: 20px, height: 36px) — los botones cuadrados están prohibidos.
- **Colores de botones**: Azul (`#0056b3`) para acciones, toggle oscuro/azul para modos, rojo (`#dc3545`) para destructivos, verde (`#28a745`) para constructivos.
- **Ajustes**: Solo interruptores toggle — sin botones de radio, sin casillas de verificación.
- **Sin emojis** en botones o etiquetas (excepción: el icono DeepThink ✦).
- **Sin PHP** — exclusivamente JavaScript y Python.
- **Sin frameworks JS externos** — sin Node, sin React, sin Vue.
- **Preservación del formato**: La indentación y el formato existentes en `index.html` nunca deben cambiarse.
- El manifiesto es un **archivo separado** y nunca debe incrustarse en `index.html`.

---

## Limitaciones Conocidas y Notas Técnicas

### "Lost in the Middle" — Una Limitación Conocida de la IA
Todos los modelos de lenguaje actuales (incluido DeepSeek) tienden a recordar el contenido al **principio y al final** de un contexto largo de forma fiable, pero el contenido **en el medio** a veces se pasa por alto o se alucina. (Liu et al., 2023: "Lost in the Middle: How Language Models Use Long Contexts")

**Impacto práctico en este proyecto**:
- Una exportación de repositorio de ~270.000 caracteres ≈ ~67.500 tokens.
- Ventana de contexto de DeepSeek: 100.000 tokens → ~67% de utilización → el contenido en el medio puede ser poco fiable.
- **Recomendación**: Para tareas específicas, cargar solo los archivos relevantes individualmente en lugar de toda la exportación del repositorio.

### Caché de URLs Raw de GitHub
Después de un `git push`, la nueva versión **no está disponible inmediatamente** a través de las URLs de `raw.githubusercontent.com` — GitHub las almacena en caché hasta 10 minutos. Esto es normal y no puede evitarse. Los archivos se almacenan correctamente en GitHub tan pronto como `git push` tiene éxito.

### Nano y Unicode — Advertencia Crítica
**Nunca** editar archivos que contengan secuencias de escape Unicode (como las funciones de umlaut) usando `nano` o copiando y pegando en un terminal. Nano corrompe `\u00e4` a `M-CM-$`, que es basura binaria para JavaScript.

**El único flujo de trabajo seguro**:
1. Editar archivos localmente (VS Code, gedit, kate o cualquier editor apropiado).
2. `git add` / `git commit` / `git push` desde la máquina local.
3. En el servidor: `git pull` (en el repositorio fuente como usuario `source`).
4. Como root: `./deploy.sh source`.

### Comportamiento de Pegado en Linux/X11/Firefox
En Linux con X11 y Firefox, `e.preventDefault()` en los manejadores de eventos de pegado no bloquea de forma fiable el comportamiento nativo de pegado del navegador para contenido proveniente de gestores de archivos. La solución implementada aquí (permitir el pegado, comprobar el contenido en `setTimeout(0)`, borrar si se detectan rutas de archivo) es la solución confiable para esta limitación específica de la plataforma.

---

## Dependencias

| Componente | Propósito | Instalación |
|-----------|---------|-------------|
| Apache2 | Servidor web, soporte CGI | `apt install apache2` |
| Python 3 | Scripts CGI del lado del servidor | `apt install python3` |
| reportlab | Exportación PDF | `pip3 install reportlab` |
| pdf.js 3.11.174 | Extracción PDF en el cliente | Cargado via CDN (respaldo automático) |
| jq | Procesamiento JSON en `repo2text.sh` | `apt install jq` |
| pv | Visualización de progreso en `repo2text.sh` | `apt install pv` |
| git | Gestión de versiones | `apt install git` |
| zip | Creación de archivos en `repo2text.sh` | `apt install zip` |

**Sin frameworks exóticos** — todas las dependencias son paquetes estándar en un entorno Debian o se cargan desde CDNs bien establecidos.

---

## Conclusión / Por Qué Destaca Este Proyecto

Este proyecto demuestra desarrollo web de nivel profesional con un enfoque minimalista y centrado en la seguridad:

**Arquitectura**:
- Separación limpia entre cliente (HTML/JS puro) y servidor (Python CGI) sin confusión de responsabilidades.
- Clave API nunca expuesta — incluso un compromiso XSS completo no puede filtrarla.
- Cliente de archivo único (`index.html`) que es completamente autónomo pero altamente modular internamente.

**Experiencia de usuario**:
- Respuestas en streaming con latencia de primer token inferior a un segundo.
- Gestión de contexto flexible única (eliminar cualquier mensaje + todos los posteriores).
- Manejo inteligente del portapapeles para texto, imágenes y protección de rutas de archivo.
- Soporte multiidioma con distinción de forma de tratamiento, cargado desde XML externo.

**Ingeniería**:
- Inspección de magic bytes que detecta malware independientemente de la extensión del nombre de archivo.
- Sistema de marcadores de posición de umlauts que resuelve una limitación fundamental de la API de DeepSeek.
- Mapa de capacidades de modelo compatible con el futuro, listo para modelos con soporte de imágenes.
- Rastro de auditoría completo mediante Git y changelog detallado.

**Herramientas**:
- `repo2text.sh` como herramienta práctica para el desarrollo asistido por IA.
- Scripts de despliegue que garantizan despliegues consistentes y con permisos correctos.
- Etiquetado de versiones para una gestión limpia de lanzamientos.

**Para un desarrollador profesional**, este proyecto demuestra:
- **Conciencia de seguridad** — protección de clave API, detección de malware, almacenamiento seguro de sesiones.
- **Disciplina estructurada** — manifiesto, etiquetas de versión, convenciones de diseño estrictas, changelog documentado.
- **Profundidad en resolución de problemas** — comportamiento de pegado X11, corrupción de umlauts, salida binaria PDF, "Lost in the Middle".
- **Documentación completa** — tanto en línea como en archivos dedicados.

DeepSeek Chat es un **escaparate del desarrollo web profesional** — sin sobrecarga innecesaria, pero con los más altos estándares de seguridad, corrección y facilidad de uso.

---

*Última actualización: 03.03.2026*
