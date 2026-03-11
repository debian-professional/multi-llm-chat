# Multi-LLM Chat Client – OpenAI, DeepSeek, Google Gemini, Hugging Face & GroqCloud

**Multi-LLM Chat Client** es un cliente de chat completamente autónomo, alojado localmente, compatible con múltiples proveedores de IA: OpenAI, DeepSeek, Google Gemini, Hugging Face y GroqCloud. Desarrollado con foco en **seguridad, simplicidad y usabilidad profesional**, utilizando únicamente tecnologías probadas: Apache como servidor web, Python CGI para la lógica del servidor y HTML/JavaScript/CSS puro en el lado del cliente.

Características principales:
- **Soporte Multi-LLM** – Cambia entre OpenAI, DeepSeek, Google Gemini, Hugging Face y GroqCloud mediante un toggle de proveedor en el panel de configuración LLM.
- **Carga de múltiples archivos** – Selecciona y envía varios archivos a la vez. Los contenidos se combinan y se envían juntos como contexto.
- **Grabación de audio por micrófono** – Graba audio directamente en el navegador y envíalo a la IA. Compatible con Google Gemini (todos los modelos) y OpenAI (gpt-4o, gpt-4.1). El botón aparece automáticamente solo cuando hay un modelo con capacidad de audio activo.
- **Gestión de contexto única** – Elimina mensajes individuales junto con todos los posteriores. El chat permanece consistente y el uso de tokens se actualiza dinámicamente.
- **Máxima seguridad** – La clave API nunca es visible en el lado del cliente, las cargas están protegidas contra archivos ejecutables mediante inspección de magic bytes, y las sesiones se almacenan con permisos restrictivos.
- **Sin frameworks exóticos** – Todo se basa en Apache, Python, Bash y HTML/JS puro.
- **Funciones de exportación profesionales** – PDF, Markdown, TXT, RTF para el chat completo o mensajes individuales.
- **Soporte multilingüe** – Traducción completa de la interfaz mediante `language.xml` externo (inglés, alemán, español, ampliable con idiomas personalizados).
- **Grabación de audio** – Botón de micrófono integrado (API MediaRecorder) para entrada de voz directa. Visible automáticamente solo cuando hay un modelo con capacidad de audio activo (todos los modelos Gemini, OpenAI gpt-4o y gpt-4.1). El audio se transmite como base64 WebM/MP4 — sin transcripción, el modelo procesa el habla de forma nativa.
- **Integración del portapapeles** – Manejador Ctrl+V con diálogo para texto, imágenes y protección contra pegado accidental de rutas de archivo.
- **Respuestas en streaming** – Las respuestas de la IA aparecen token a token, igual que ChatGPT o Claude.
- **Gestión de límite de tasa 429** – Reintento automático con visualización de cuenta regresiva para los límites del nivel gratuito de Google Gemini.
- **Herramienta incluida** – El script `repo2text.sh` exporta todo el repositorio como archivo de texto, ideal para trabajar con asistentes de IA (como éste).

---

## Tabla de contenidos

- [Descripción general](#descripción-general)
- [Arquitectura](#arquitectura)
- [Gestión de contexto única](#gestión-de-contexto-única)
- [Características en detalle](#características-en-detalle)
  - [Interfaz de chat](#interfaz-de-chat)
  - [Respuestas en streaming](#respuestas-en-streaming)
  - [Manejador del portapapeles (Ctrl+V)](#manejador-del-portapapeles-ctrlv)
  - [Carga de archivos con verificación de seguridad](#carga-de-archivos-con-verificación-de-seguridad)
  - [Sistema de marcadores de posición para diéresis](#sistema-de-marcadores-de-posición-para-diéresis)
  - [Modo DeepThink](#modo-deepthink)
  - [Detección de modelos y capacidades](#detección-de-modelos-y-capacidades)
  - [Sistema multilingüe](#sistema-multilingüe)
  - [Configuración (toggles en lugar de botones de radio)](#configuración-toggles-en-lugar-de-botones-de-radio)
  - [Gestión de sesiones](#gestión-de-sesiones)
  - [Funciones de exportación](#funciones-de-exportación)
  - [Botones de feedback y registro](#botones-de-feedback-y-registro)
  - [Visualización dinámica del contexto](#visualización-dinámica-del-contexto)
  - [Visualización de tarjeta de archivo](#visualización-de-tarjeta-de-archivo)
  - [Grabación de audio](#grabación-de-audio)
- [El script auxiliar `repo2text.sh`](#el-script-auxiliar-repo2textsh)
- [Arquitectura de seguridad en detalle](#arquitectura-de-seguridad-en-detalle)
- [Despliegue y uso](#despliegue-y-uso)
  - [Requisitos previos](#requisitos-previos)
  - [Instalación](#instalación)
  - [Configuración](#configuración)
  - [Scripts de despliegue](#scripts-de-despliegue)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Configuración de modelos](#configuración-de-modelos)
- [Manifiesto de diseño](#manifiesto-de-diseño)
- [Limitaciones conocidas y notas técnicas](#limitaciones-conocidas-y-notas-técnicas)
- [Dependencias](#dependencias)
- [Conclusión / Por qué destaca este proyecto](#conclusión--por-qué-destaca-este-proyecto)

---

## Descripción general

Multi-LLM Chat Client es una **aplicación web local** que se comunica a través de diversas APIs. Desarrollada para un entorno de servidor privado (Debian), puede ejecutarse en cualquier sistema con Apache y Python 3. El objetivo fue crear un cliente de chat **seguro, extensible y fácil de usar** que funcione sin dependencias en la nube y ofrezca control total sobre los datos.

El proyecto ha crecido continuamente durante varias semanas de desarrollo activo, añadiendo funciones como streaming, gestión de sesiones, exportaciones, soporte multilingüe, integración del portapapeles y medidas de seguridad robustas — todo sin introducir frameworks JavaScript externos.

---

## Arquitectura

La arquitectura es intencionalmente simple pero bien pensada:

### 1. Cliente
- HTML/JavaScript/CSS puro, servido mediante Apache.
- Sin herramientas de compilación, sin Node.js, sin bibliotecas externas (excepto PDF.js para extracción de texto PDF en el navegador).
- Toda la lógica del cliente (procesamiento de mensajes, actualizaciones de UI, recepción de streaming, cambio de idioma, manejo del portapapeles) está encapsulada en un único `index.html`.
- Todos los textos de la interfaz se cargan desde un `language.xml` externo al inicio — sin cadenas codificadas en el HTML.

### 2. Servidor
- **Apache** con soporte CGI (`mod_cgi`).
- **Scripts Python CGI** bajo `/cgi-bin/` gestionan:
  - Comunicación con la API de OpenAI (`openai-api.py`) — endpoint nativo con streaming (Server-Sent Events)
  - Comunicación con la API de DeepSeek (`deepseek-api.py`) — con streaming (Server-Sent Events)
  - Comunicación con la API de Google Gemini (`google-api.py`) — convierte el formato OpenAI al formato Gemini
  - Comunicación con la API de Hugging Face Inference (`hugging-api.py`) — endpoint de router compatible con OpenAI
  - Comunicación con la API de GroqCloud (`groq-api.py`) — endpoint compatible con OpenAI, inferencia acelerada por LPU
  - Descubrimiento de modelos (`deepseek-models.py`) — consulta `/v1/models` al inicio
  - Almacenamiento y recuperación de sesiones (`save-session.py`, `load-session.py`, `delete-session.py`)
  - Exportaciones en varios formatos (`export-pdf.py`, `export-markdown.py`, `export-txt.py`, `export-rtf.py`)
  - Registro de feedback (`feedback-log.py`)
  - Visualización de registros (`get-log.py`)
- Las claves API se proporcionan exclusivamente mediante variables de entorno de Apache (`OPENAI_API_KEY`, `DEEPSEEK_API_KEY`, `GOOGLE_API_KEY`, `HF_API_KEY`, `GRQ_API_KEY` en `/etc/apache2/envvars`) — **nunca en el código del cliente**.
- Un único `ScriptAlias /cgi-bin/ /var/www/deepseek-chat/cgi-bin/` cubre todos los scripts — no se necesitan cambios en Apache al añadir nuevos scripts.

### 3. Almacenamiento de datos
- Las **sesiones** se almacenan como archivos JSON en `/var/www/deepseek-chat/sessions/` con `chmod 700`.
- Los **registros** se escriben en `/var/www/deepseek-chat/cgi-bin/deepseek-chat.log` (sin clave API ni contenido de sesiones).
- La **configuración** permanece localmente en el navegador (`localStorage`) con control de versiones.
- Los **datos de idioma** se cargan desde `language.xml` al cargar la página mediante `fetch()`.

### 4. Scripts auxiliares
- `deploy.sh`, `sync-back.sh`, `install.sh`, `tag-release.sh` facilitan el despliegue entre los directorios de desarrollo y producción.
- `repo2text.sh` exporta todo el repositorio como archivo de texto para asistentes de IA.

---

## Gestión de contexto única

Una de las características más destacadas es la capacidad de **eliminar mensajes individuales junto con todos los posteriores**. Esto va mucho más allá del típico "eliminar último mensaje" y permite la corrección flexible del historial de conversación.

**Implementación**:
- Cada mensaje (usuario e IA) recibe un `id` único (formato: `msg_N`) y se almacena en un array `contextHistory.messages`.
- La función `deleteMessage(msgId)` determina el índice del mensaje, trunca el array desde `index` en adelante y elimina todos los elementos siguientes del DOM (incluidos divisores).
- La estimación de tokens (`updateContextEstimation()`) se recalcula inmediatamente, al igual que el porcentaje de utilización del contexto en el encabezado.
- La sesión modificada se guarda automáticamente a continuación (`saveSession()`).

**¿Por qué es esto único?**
Muchos clientes de chat solo permiten eliminar el último mensaje o ninguna manipulación del historial. Aquí, el usuario puede **definir cualquier punto de la conversación como nuevo punto de inicio** — perfecto para pruebas, correcciones o limpieza del contexto sin perder todo el chat.

**Función de regeneración**: Además de la eliminación, cada respuesta de IA tiene un botón "Regenerar" que elimina la respuesta anterior y genera automáticamente una nueva basada en el mismo mensaje del usuario — usando el contexto completo de la conversación hasta ese punto.

---

## Características en detalle

### Interfaz de chat

- **Modo oscuro** (fijo, sin opción) — agradable para los ojos, apariencia profesional.
  - Fondo: `#121212`, texto: `#f0f0f0`, acento: `#0056b3`
- El **encabezado del servidor** muestra el nombre del servidor, la dirección IP interna, la utilización dinámica del contexto y los nombres de modelos detectados.
- **Contenedores de mensajes** con botones al pasar el cursor (feedback, exportar, eliminar).
- El **área de texto** se expande al enfocarse de 40px a 120px con animación CSS suave — Enter envía, Shift+Enter crea una nueva línea.
- Todos los botones siguen un diseño estricto de **estilo píldora** (border-radius: 20px, height: 36px) — ningún botón cuadrado en ningún lugar.
- Los mensajes del usuario aparecen en azul (`#4dabf7`), las respuestas de IA en blanco sobre fondo oscuro.
- Preservación automática de saltos de línea (`white-space: pre-wrap`) para todo el contenido de los mensajes.
- Desplazamiento automático al mensaje más reciente durante y después del streaming.

### Respuestas en streaming

Las respuestas de IA se reciben y muestran **token a token** mediante Server-Sent Events (SSE):

- `deepseek-api.py` envía solicitudes a DeepSeek con `stream: True` y reenvía el flujo de eventos directamente.
- `index.html` lee el flujo mediante la API `ReadableStream` y `TextDecoder`.
- Cada token recibido se añade al elemento de mensaje en tiempo real.
- El efecto psicológico es significativo: los primeros tokens aparecen en ~0,3 segundos en lugar de esperar 8+ segundos por una respuesta completa.
- Tanto `sendMessage()` como `handleRegenerate()` usan lógica de streaming idéntica.
- El desplazamiento automático permanece activo durante el streaming.

**Cabeceras técnicas** establecidas por `deepseek-api.py` para un streaming correcto:
```
Content-Type: text/event-stream
X-Accel-Buffering: no
Cache-Control: no-cache
```

### Integración con OpenAI

El cliente admite OpenAI como primer proveedor de IA (mostrado en la parte superior de la selección LLM) mediante `openai-api.py`:

- **Arquitectura**: Usa el endpoint nativo de OpenAI Chat Completions — no se requiere conversión de formato. El flujo SSE se reenvía directamente.
- **Endpoint**: `https://api.openai.com/v1/chat/completions`
- **Clave API**: `OPENAI_API_KEY` en `/etc/apache2/envvars` — nunca expuesta al cliente.
- **Nivel gratuito**: `gpt-4o-mini`, `gpt-5-mini`.
- **Nivel de pago**: `gpt-5.4`, `gpt-5.2-chat-latest`, `gpt-4o`, `gpt-4.1`, `gpt-4o-mini`.
- El menú desplegable de modelos en la configuración LLM se actualiza automáticamente según el nivel seleccionado.
- **Entrada de audio**: `gpt-4o` y `gpt-4.1` admiten grabaciones directas por micrófono. Cuando cualquiera de estos modelos está activo, el botón de grabación de audio se vuelve visible. El audio se envía como `input_audio` en formato OpenAI.
- El botón DeepThink y el indicador DeepThink se ocultan cuando OpenAI está activo.
- El prompt del sistema identifica el modelo activo: *"You are [model], an AI assistant made by OpenAI."*

### Integración con Google Gemini

El cliente admite Google Gemini como segundo proveedor de IA mediante `google-api.py`:

- **Arquitectura**: El script CGI convierte el formato de mensajes compatible con OpenAI que se usa internamente al formato específico `contents` de Gemini, envía la solicitud al endpoint `streamGenerateContent` de Gemini y convierte la respuesta de vuelta al formato SSE de OpenAI esperado por `index.html`.
- **Clave API**: `GOOGLE_API_KEY` en `/etc/apache2/envvars` — nunca expuesta al cliente.
- **Nivel gratuito** (predeterminado): `gemini-2.5-flash` — 5 solicitudes por minuto, 20 solicitudes por día.
- **Nivel de pago**: `gemini-2.5-flash`, `gemini-2.5-pro`, `gemini-1.5-pro`, `gemini-2.0-flash`.
- El menú desplegable de modelos en la configuración LLM se actualiza automáticamente según el nivel seleccionado.
- **Entrada de audio**: Todos los modelos Gemini admiten grabaciones directas por micrófono. El botón de grabación de audio siempre es visible cuando Google Gemini es el proveedor activo. El audio se envía como `inline_data` en el formato nativo de Gemini.
- El botón DeepThink y el indicador DeepThink se ocultan cuando Google Gemini está activo.

### Integración con Hugging Face

El cliente admite Hugging Face Inference Providers como tercer proveedor de IA mediante `hugging-api.py`:

- **Arquitectura**: Usa el endpoint de router de Hugging Face compatible con OpenAI — no se requiere conversión de formato. El flujo SSE se reenvía directamente.
- **Endpoint**: `https://router.huggingface.co/v1/chat/completions` — el router selecciona automáticamente el proveedor disponible más rápido.
- **Clave API**: `HF_API_KEY` en `/etc/apache2/envvars` — un token de escritura de huggingface.co/settings/tokens con el permiso "Make calls to Inference Providers".
- **Nivel gratuito**: `Qwen/Qwen2.5-72B-Instruct`, `mistralai/Mistral-7B-Instruct-v0.3`, `microsoft/Phi-3.5-mini-instruct`.
- **Nivel de pago**: `meta-llama/Meta-Llama-3.1-70B-Instruct`, `meta-llama/Meta-Llama-3.1-405B-Instruct`, `Qwen/Qwen2.5-72B-Instruct`, `mistralai/Mixtral-8x7B-Instruct-v0.1`.
- El menú desplegable de modelos se actualiza automáticamente según el nivel seleccionado.
- El botón DeepThink y el indicador DeepThink se ocultan cuando Hugging Face está activo.


### Integración con GroqCloud

El cliente admite GroqCloud como cuarto proveedor de IA mediante `groq-api.py`:

- **Arquitectura**: Usa el endpoint de GroqCloud compatible con OpenAI — no se requiere conversión de formato. El flujo SSE se reenvía directamente.
- **Endpoint**: `https://api.groq.com/openai/v1/chat/completions`
- **Clave API**: `GRQ_API_KEY` en `/etc/apache2/envvars`.
- **Nota**: Se requiere una cabecera `User-Agent` para eludir la protección de Cloudflare (sin ella: código de error 1010).
- **Nivel gratuito y de pago**: `llama-3.3-70b-versatile`, `llama-3.1-8b-instant`, `mixtral-8x7b-32768`, `gemma2-9b-it`.
- El menú desplegable de modelos se actualiza automáticamente según el nivel seleccionado.
- El botón DeepThink y el indicador DeepThink se ocultan cuando GroqCloud está activo.
- Todos los modelos se ejecutan en el hardware LPU (Language Processing Unit) de GroqCloud para una latencia muy baja.

### Panel de configuración LLM

Un panel dedicado de **Configuración LLM** (separado del panel de configuración principal) mantiene las opciones específicas del proveedor fuera de la interfaz principal:

- **Selección de proveedor**: Alterna entre OpenAI, DeepSeek, Google Gemini, Hugging Face y GroqCloud — solo uno activo a la vez.
- **Opciones de OpenAI**: Selección de plan Gratuito / De pago con actualización automática de la lista de modelos.
- **Opciones de DeepSeek**: Modo predeterminado (Chat Normal / DeepThink), toggle de privacidad (cabecera X-No-Training).
- **Opciones de Google**: Selección de plan Gratuito / De pago con actualización automática de la lista de modelos.
- **Opciones de Hugging Face**: Selección de plan Gratuito / De pago con actualización automática de la lista de modelos.
- **Opciones de GroqCloud**: Selección de plan Gratuito / De pago con actualización automática de la lista de modelos.
- **Menú desplegable de modelos**: Siempre visible, el contenido se actualiza automáticamente según el proveedor y plan activos.
- Todas las configuraciones se guardan en `localStorage` y persisten tras recargar la página.

### Gestión del límite de tasa 429

El nivel gratuito de Google Gemini impone límites de tasa estrictos (5 RPM, 20 RPD). El cliente los gestiona de forma elegante:

- Ante una respuesta 429, el cliente reintenta automáticamente hasta **3 veces** con intervalos de **15 segundos**.
- Durante la espera, se muestra una cuenta regresiva directamente en el chat: *"Límite de tasa alcanzado – esperando 15 segundos y reintentando... (Intento 1/3)"*
- Tras 3 intentos fallidos, se muestra un mensaje de error final.
- Los detalles detallados del error se escriben en el registro del servidor para diagnóstico.
- La lógica de reintento distingue entre límites RPM temporales (reintentable) y cuota diaria agotada (no reintentable).

### Manejador del portapapeles (Ctrl+V)

Un sofisticado manejador del portapapeles intercepta los eventos de pegado y responde de forma inteligente según el tipo de contenido:

**Contenido de texto** → Aparece el diálogo de pegado con dos opciones:
- "Insertar en la posición del cursor" — inserta el texto directamente en el campo de entrada en el cursor
- "Adjuntar como archivo" — trata el texto del portapapeles como `clipboard.txt` y lo adjunta como archivo al siguiente mensaje

**Contenido de imagen** → Aparece una vista previa en miniatura sobre el campo de entrada con la imagen, su tamaño en KB y un botón de eliminar. La imagen está lista para enviarse con el siguiente mensaje (si el modelo admite imágenes).

**Rutas de archivos del gestor de archivos (XFCE/Thunar, KDE/Dolphin)** → Estas se bloquean y se muestra una alerta:
> "Los archivos copiados en el gestor de archivos no pueden ser leídos por el navegador. Por favor, use el botón de carga en su lugar."

**Fondo técnico**: En Linux/X11/Firefox, `e.preventDefault()` no bloquea de forma fiable los eventos de pegado. La solución es permitir el pegado, luego verificar inmediatamente el contenido del campo de entrada mediante `setTimeout(0)` y limpiarlo si se detectan rutas de archivo. Lógica de detección: 2 o más líneas donde cada línea comienza con `/` o `file://`. Una llamada `requestAnimationFrame` garantiza que el campo de entrada se limpie visualmente antes de que aparezca el diálogo de alerta.

### Carga de archivos con verificación de seguridad

- Formatos aceptados: `.txt`, `.pdf`, `.doc`, `.docx`, `.jpg`, `.jpeg`, `.png`, `.csv`, `.xlsx`, `.pptx`
- Formatos procesables (extracción de contenido): `.txt`, `.pdf`
- Otros formatos aceptados: adjuntados como contexto binario (sin extracción de texto)
- Tamaño máximo de archivo: **10 MB**
- Contenido extraído máximo: **250.000 caracteres** (suficiente para archivos de texto grandes y exportaciones de repositorios)

**Inspección de magic bytes** (primeros 20 bytes) detecta y bloquea archivos ejecutables independientemente de su extensión:

| Platform | Format | Signature |
|----------|--------|-----------|
| Windows 32/64 bit | PE/MZ Executable | `4D 5A` |
| Linux 32 bit | ELF32 | `7F 45 4C 46 01` |
| Linux 64 bit | ELF64 | `7F 45 4C 46 02` |
| ARM 32 bit | ELF32 ARM | `7F 45 4C 46 01 01 01 00 ... 02 00 28 00` |
| ARM 64 bit | ELF64 AArch64 | `7F 45 4C 46 02 01 01 00 ... 02 00 B7 00` |
| macOS 32 bit | Mach-O | `CE FA ED FE` |
| macOS 64 bit | Mach-O | `CF FA ED FE` |
| macOS Universal | Fat Binary | `CA FE BA BE` |
| macOS/iOS ARM 32 | Big Endian | `FE ED FA CE` |
| macOS/iOS ARM 64 | Big Endian | `FE ED FA CF` |
| Linux/macOS | Shell Script | `23 21` (#!) |
| Python | Bytecode (.pyc) | `55 0D 0D 0A` |

**Extracción PDF**: Usa PDF.js 3.11.174 cargado desde CDN con fallback automático a un CDN secundario. El progreso se muestra página a página. Tiempo de espera de extracción: 30 segundos.

**Los archivos cargados se muestran como tarjetas de archivo** en el mensaje del usuario (ver [Visualización de tarjeta de archivo](#visualización-de-tarjeta-de-archivo)).

### Sistema de marcadores de posición para diéresis

Una solución única para un problema fundamental con la API de DeepSeek y el texto alemán:

**Problema**: DeepSeek reemplaza internamente las diéresis alemanas en el contenido de archivos con equivalentes ASCII (p.ej. `Ä → AeNDERUNG`, `Ü → MUeSSEN`). Este comportamiento no puede suprimirse mediante prompts del sistema o parámetros de la API.

**Solución**: Antes de enviar el contenido del archivo a DeepSeek, las diéresis se reemplazan con marcadores de posición únicos. DeepSeek devuelve estos marcadores sin cambios. JavaScript los reemplaza de vuelta a las diéresis reales tras recibir la respuesta.

| Original | Placeholder |
|----------|-------------|
| `ä` | `[[AE]]` |
| `ö` | `[[OE]]` |
| `ü` | `[[UE]]` |
| `ß` | `[[SS]]` |
| `Ä` | `[[CAE]]` |
| `Ö` | `[[COE]]` |
| `Ü` | `[[CUE]]` |

**Detalle de implementación importante**: Las funciones `encodeUmlautsForAI()` y `decodeUmlautsFromAI()` usan **exclusivamente secuencias de escape Unicode** (`\u00e4` en lugar de `ä`) y `split/join` en lugar de expresiones regulares — esto es crítico para evitar la corrupción cuando los archivos se transfieren mediante Git.

La decodificación se ejecuta **tanto durante el streaming** (token a token) como después de recibir la respuesta completa.

Este sistema se aplica **únicamente al contenido de archivos**, no a los mensajes regulares del usuario ni a los prompts del sistema.

### Modo DeepThink

- Conmutable mediante un botón dedicado (estilo píldora) en la segunda fila de botones.
- En el modo DeepThink, se usa el modelo `deepseek-reasoner` (razonamiento real de cadena de pensamiento).
- El botón cambia visualmente: oscuro/inactivo (`#2d2d2d`) → azul activo (fondo `#1e3a5f`, borde y texto `#4dabf7`).
- Aparece una barra indicadora debajo de los botones mostrando "Modo DeepThink activo: Análisis en profundidad en curso".
- Los límites de contexto y de tokens de salida se ajustan automáticamente (ver [Configuración de modelos](#configuración-de-modelos)).
- El modo se registra con cada mensaje y se muestra en las exportaciones.
- El modo predeterminado (Chat o DeepThink) se puede configurar en Ajustes y se persiste en `localStorage`.

### Detección de modelos y capacidades

Al inicio, el cliente consulta `/cgi-bin/deepseek-models.py` que a su vez llama al endpoint `/v1/models` de DeepSeek:

- Los IDs de modelos detectados se muestran en el encabezado del servidor: `Model: deepseek-chat, deepseek-reasoner`
- Un mapa `MODEL_CAPABILITIES` define qué modelos admiten imágenes:
  ```javascript
  const MODEL_CAPABILITIES = {
      'deepseek-chat':     { images: false, text: true },
      'deepseek-reasoner': { images: false, text: true },
      'deepseek-v4':       { images: true,  text: true },  // ready for future models
      'default':           { images: false, text: true },
  };
  ```
- Si se pega una imagen desde el portapapeles o se carga un archivo `.jpg`/`.png`, y el modelo actual no admite imágenes, una alerta bloquea la operación.
- Esta arquitectura es **compatible hacia adelante**: cuando se lance DeepSeek V4 con soporte de imágenes, funcionará automáticamente sin cambios de código.

### Sistema multilingüe

La interfaz admite múltiples idiomas cargados desde un archivo `language.xml` externo:

**Idiomas incluidos actualmente**:
- Inglés (`en`) — predeterminado
- Alemán (`de`) — con forma de tratamiento formal/informal (Sie/Du)
- Español (`es`) — con forma de tratamiento formal/informal (Usted/Tú)
- Ranura personalizada (`custom`) — se puede activar mediante `visible="true"` en `language.xml`

**Cómo funciona**:
- Todos los textos de la interfaz se referencian mediante IDs numéricos (p.ej. `t(205)` = etiqueta del botón Enviar).
- `loadLanguage()` obtiene y analiza `language.xml` al cargar la página.
- `t(id)` devuelve el texto para el idioma actual, con fallback al inglés si no se encuentra.
- `tf(id, ...args)` admite sustitución de marcadores de posición (`{0}`, `{1}`, ...).
- `tform(idFormal, idInformal)` devuelve el texto apropiado según la forma de tratamiento seleccionada.
- El cambio de idioma es inmediato sin recargar la página.
- El idioma seleccionado se persiste en `localStorage`.

**Sistema de forma de tratamiento (alemán/español)**:
- Los idiomas pueden declarar `has_address_form="true"` en `language.xml`.
- Para dichos idiomas, el panel de Ajustes muestra un grupo "Forma de tratamiento" (Formal/Informal).
- La forma seleccionada afecta: el prompt del sistema (fuerza respuestas coherentes de la IA), el marcador de posición de entrada, todas las descripciones de ajustes.
- El inglés no tiene distinción de forma de tratamiento.

**El prompt del sistema** se construye dinámicamente según el idioma, la forma de tratamiento y el modo:
- Prompt base (IDs de texto 29/30 para formal/informal)
- Adición DeepThink (IDs de texto 31/32)
- Siempre se añade una instrucción estricta para la visualización de archivos en inglés para garantizar un comportamiento coherente independientemente del idioma de la interfaz.

### Configuración (toggles en lugar de botones de radio)

Todas las configuraciones usan **interruptores de palanca** (deslizamiento de izquierda a derecha), nunca botones de radio ni casillas de verificación:

| Grupo | Ajuste | Color del toggle |
|-------|---------|-------------|
| Idioma | EN / DE / ES / Custom | Verde (preferencia personal) |
| Forma de tratamiento | Formal / Informal | Verde (preferencia personal) |
| Modo predeterminado | Chat Normal / DeepThink | Azul (modo técnico) |
| Privacidad | No usar datos para entrenamiento | Verde |

**Comportamiento del toggle**:
- Dentro de un grupo, los toggles se comportan como botones de radio: activar uno desactiva los demás.
- Hacer clic en cualquier lugar de la fila `setting-item` activa ese toggle (no solo el elemento toggle en sí).
- Retroalimentación visual: los elementos activos obtienen un fondo de color (`#1a2e1a` verde o `#1e3a5f` azul).

**Toggle de privacidad**: Establece la cabecera `X-No-Training: true` en las solicitudes de la API (soportado por el mecanismo de exclusión de DeepSeek).

**Persistencia de ajustes**: Todos los ajustes se almacenan en `localStorage` bajo la clave `deepseekSettings`. `SETTINGS_VERSION: 1.3` actual. La función `migrateSettings()` proporciona compatibilidad con versiones anteriores de los ajustes almacenados (p.ej. el modo "search" eliminado se migra automáticamente a "chat").

### Gestión de sesiones

Cada conversación se gestiona automáticamente como una sesión con nombre:

- **Formato del ID de sesión**: `YYYY-MM-DD_HHMMSS_random` (p.ej. `2026-02-16_143045_abc123`) — generado en el cliente, validado en el servidor.
- **Guardado automático**: Después de cada par de mensajes (usuario + IA), el array completo `contextHistory.messages` se guarda en el servidor como archivo JSON.
- **Formato del archivo de sesión**: `{sessionId}.json` en `/var/www/deepseek-chat/sessions/`, `chmod 600`.
- **Modal de carga del historial de chat**: Muestra todas las sesiones guardadas con ID, fecha, vista previa del mensaje y número de mensajes. Cada sesión tiene botones [Cargar] (verde) y [Eliminar] (rojo).
- **Comportamiento de carga**: Al cargar una sesión, el chat actual se guarda automáticamente primero, luego la sesión seleccionada se restaura con el historial completo de mensajes y reconstrucción de la interfaz.
- **Eliminación de sesión**: El archivo JSON se elimina del servidor inmediatamente.

**Scripts CGI**:
- `save-session.py` — POST: recibe `{sessionId, messages}`, valida el formato del ID, escribe JSON
- `load-session.py` — GET: devuelve lista con vistas previas; GET con `?id=`: devuelve datos completos de la sesión
- `delete-session.py` — DELETE: elimina el archivo de sesión

### Funciones de exportación

**Exportación global** (botón desplegable en la fila principal):

| Formato | Generación | Contiene |
|--------|-----------|---------|
| PDF | En el servidor (ReportLab) | Encabezado, estadísticas, índice, chat completo |
| Markdown | En el servidor | Estructura idéntica al PDF, con anclas Markdown |
| TXT | En el servidor | Texto plano con separadores |
| RTF | En el servidor | Formato RTF, diéresis como códigos RTF (sin biblioteca externa) |

**Exportación por mensaje** (botón al pasar el cursor sobre cada mensaje):

| Formato | Generación |
|--------|-----------|
| TXT | En el cliente (JavaScript Blob, sin ida al servidor) |
| Markdown | En el cliente |
| RTF | En el cliente |
| PDF | En el servidor (mensaje único enviado a `export-pdf.py`) |

**Contenido de exportación** (PDF/Markdown):
- Encabezado con nombre del servidor, IP, fecha de exportación, configuración de idioma/forma de tratamiento
- Sección de estadísticas: número de mensajes, modos usados, archivos adjuntos, tokens estimados, duración
- Índice con todos los mensajes
- Historial completo del chat con marcas de tiempo e indicadores de modo
- Codificación por colores según el rol del mensaje y el modo

**Nota técnica de PDF**: Los datos PDF binarios se escriben exclusivamente mediante `sys.stdout.buffer` con cabeceras HTTP codificadas como bytes — evitando el error "Bad header" que ocurre al mezclar `print()` (modo texto) con salida binaria.

### Botones de feedback y registro

Cuatro botones aparecen al pasar el cursor sobre cada respuesta de IA (lado izquierdo, abajo):

- **Copiar** — Copia el texto del mensaje al portapapeles; muestra "¡Copiado!" durante 2 segundos, luego se reinicia.
- **Me gusta** — Marca la respuesta positivamente (resaltado azul); envía una entrada LIKE al registro del servidor. Hacer clic de nuevo elimina el like.
- **No me gusta** — Marca la respuesta negativamente (resaltado rojo); envía una entrada DISLIKE. Me gusta y No me gusta son mutuamente excluyentes.
- **Regenerar** — Elimina la respuesta actual de la IA del contexto y el DOM, luego llama a la API de nuevo con el mismo mensaje del usuario y el historial completo anterior.

**Formato del registro en el servidor** (`deepseek-chat.log`):
```
2026-02-17 17:30:00 | 192.168.1.x | FEEDBACK | LIKE | msg_5 | "First 60 chars of message..."
2026-02-17 17:30:00 | 192.168.1.x | POST | /cgi-bin/deepseek-api.py | 200
```
**Nunca registrado**: Claves API, contenido de sesiones o texto de mensajes más allá de la vista previa de feedback de 60 caracteres.

### Visualización dinámica del contexto

El encabezado del servidor muestra cuatro líneas de información:
1. Nombre del servidor (en azul, `#4dabf7`)
2. `IP: xxx.xxx.xxx.xxx`
3. `Context: XX% (nombre-modelo)`
4. `Model: deepseek-chat, deepseek-reasoner`

**Cálculo de utilización del contexto**:
- Tokens estimados = total de caracteres en mensajes recientes × `TOKENS_PER_CHAR` (0,25)
- Solo se cuentan los últimos N mensajes (N = `maxContextMessages` de `MODEL_CONFIG`)
- Los tokens del prompt del sistema se añaden por separado
- Porcentaje = tokens estimados / `maxContextTokens` × 100

**Sistema de advertencia**: Por encima del 90%, la línea de contexto se vuelve roja y parpadea (animación CSS, opacidad 0 → 1, ciclo de 1 segundo) — una advertencia muy visible de que la ventana de contexto está casi llena.

La visualización se actualiza automáticamente con: cada mensaje enviado, cada mensaje eliminado, cada cambio de modelo.

### Visualización de tarjeta de archivo

Cuando se carga un archivo o se adjunta texto del portapapeles, el mensaje del usuario muestra una **tarjeta de archivo** — un elemento visual compacto similar a Claude o ChatGPT:

```
┌─────────────────────────────────────┐
│  [PDF]  │  filename.pdf             │
│  icon   │  PDF Document             │
└─────────────────────────────────────┘
```

- Muestra el badge del tipo de archivo (PDF, TXT, XLSX, etc.) derivado de la extensión del archivo
- Muestra el nombre de archivo truncado (máx. 30 caracteres con `...`)
- Se aplica a: cargas de archivos reales mediante el botón de carga, texto del portapapeles adjuntado como archivo (`clipboard.txt`), todos los demás formatos aceptados y grabaciones de audio
- Las grabaciones de audio muestran el badge `AUDIO` con la etiqueta localizada (p.ej. "Grabación de audio")

### Carga de múltiples archivos

El botón de carga permite seleccionar **varios archivos a la vez**:

- Todos los archivos seleccionados se validan individualmente (verificación de formato, inspección de magic bytes, verificación de capacidad de imagen).
- Los archivos de texto extraíble (`.txt`, `.pdf`) se procesan en secuencia; sus contenidos se combinan con separador `---` y una cabecera `[nombre_archivo]` por archivo.
- La barra de información de archivos muestra todos los archivos separados por ` | ` en una línea.
- Se genera una tarjeta de archivo por cada archivo en el mensaje del usuario.
- Formatos aceptados: `.txt`, `.pdf`, `.doc`, `.docx`, `.jpg`, `.jpeg`, `.png`, `.csv`, `.xlsx`, `.pptx`

### Grabación de audio

El cliente incluye un **botón de grabación por micrófono** integrado que permite la entrada de voz directa a modelos con capacidad de audio:

- **Botón**: `audioButton` — estilo píldora, posicionado en la fila de botones 2 junto al botón DeepThink.
- **Visibilidad**: El botón solo se muestra cuando el modelo actualmente seleccionado admite entrada de audio. Se oculta automáticamente cuando un modelo sin audio está activo. Esto lo controla `updateAudioButtonVisibility()` que se llama en cada cambio de modelo.
- **Modelos con capacidad de audio** (constante `AUDIO_CAPABLE_MODELS`):
  - **Google Gemini**: `gemini-2.5-flash`, `gemini-2.5-pro`, `gemini-1.5-pro`, `gemini-2.0-flash`
  - **OpenAI**: `gpt-4o`, `gpt-4.1`
- **Flujo de grabación**: `getUserMedia()` → API `MediaRecorder` → grabación en fragmentos → `Blob` ensamblado al detener → codificado en base64.
- **Tipo MIME**: `audio/webm` (Chrome/Firefox) o `audio/mp4` (Safari) — detectado automáticamente en tiempo de ejecución.
- **Después de grabar**: Los datos de audio se muestran en el cuadro `fileInfo` con una tarjeta badge AUDIO. La etiqueta proviene de `language.xml` (`t(250)` — "Grabación de audio" en los cuatro idiomas).
- **Envío**: `audio_data` (cadena base64) y `audio_mime_type` se incluyen en el cuerpo de la solicitud JSON junto al mensaje de texto. El indicador `hasFile` **no** se establece para audio — no se inyecta ningún prompt del sistema de procesamiento de archivos.
- **Exclusividad mutua**: La carga de archivos y la grabación de audio son mutuamente excluyentes. Iniciar una grabación limpia cualquier archivo adjunto pendiente y viceversa.
- **Backend — Google (`google-api.py`)**: El audio se adjunta al último mensaje del usuario como bloque `inline_data` en el formato nativo de Gemini. El modelo recibe y procesa el audio directamente.
- **Backend — OpenAI (`openai-api.py`)**: El audio se adjunta al último mensaje del usuario como bloque `input_audio` en el formato de OpenAI (`format: webm` o `mp4`).
- **Regla de mantenimiento** (documentada en el manifiesto): Cuando un proveedor LLM integrado añada o elimine soporte de audio para un modelo, `AUDIO_CAPABLE_MODELS` en `index.html` **debe** actualizarse inmediatamente.

**IDs de idioma añadidos** (los cuatro idiomas):

| ID | Contenido |
|----|---------|
| 247 | Grabar audio / Record Audio / Audio aufnehmen |
| 248 | Stop |
| 249 | Audio grabado / Audio recorded / Audio aufgenommen |
| 250 | Grabación de audio / Audio recording / Audioaufnahme |


---


### Bloque de información del proxy API (desde 08.03.2026)

Cada uno de los cinco scripts CGI proxy (`openai-api.py`, `deepseek-api.py`, `google-api.py`, `hugging-api.py`, `groq-api.py`) contiene una cabecera de documentación estructurada directamente después de la declaración de codificación:

- **Fecha de importación** — cuándo se actualizó el archivo por última vez
- **Versión del modelo** — versión de cada modelo/submodelo soportado
- **Ventana de contexto** — límites de tokens de entrada y salida por modelo
- **Capacidades** — Solo texto / Texto + Imágenes + Audio + Video
- **Asignación Gratuito/De pago** — para proveedores con distinción de nivel
- **Enlace fuente** — documentación oficial de la API

Esto garantiza que la información del modelo siempre sea rastreable directamente en el código fuente sin consultar documentación externa.

## El script auxiliar `repo2text.sh`

Este script Bash fue desarrollado específicamente para **exportar todo el código fuente de un repositorio GitHub como un único archivo de texto** — ideal para pasar el contexto completo del proyecto a un asistente de IA.

**Cómo funciona**:
- Clones the repository with `git clone --depth 1`.
- Analyzes all text files (MIME type + `grep -Iq .`) and writes them with separators into an output file.
- Explicitly respects `.gitignore` and `.gitattributes`.
- Supports TXT, JSON, and Markdown output formats.
- Creates a ZIP archive of the export file.
- Includes metadata: commit hash, branch, timestamp.

**Opciones especiales**:
- `--flat`: Usar solo nombres de archivo sin rutas.
- `-o, --only RUTA`: Exportar solo un subdirectorio específico.
- `-md5, --md5`: Calcular e incluir suma de verificación MD5 para cada archivo.
- Detección inteligente de la URL remota cuando se ejecuta dentro de un repositorio Git.
- Se admiten tanto `md5sum` (Linux) como `md5` (macOS).

**Ejemplos**:

```bash
# Simple export (interactive URL prompt)
./repo2text.sh

# Export with URL as Markdown
./repo2text.sh -f md https://github.com/debian-professional/multi-llm-chat.git

# Export only the 'shell-scripts' directory with flat structure
./repo2text.sh --flat -o shell-scripts https://github.com/debian-professional/multi-llm-chat.git

# Export with MD5 checksums
./repo2text.sh -md5 https://github.com/debian-professional/multi-llm-chat.git
```

**¿Por qué es útil esto?**
- Permite la documentación completa del proyecto en un único archivo.
- Perfecto para insertar bases de código completas en chats de IA.
- La opción MD5 ayuda a verificar la integridad de los archivos tras la exportación.

> `repo2text` is also available as a standalone project: [github.com/debian-professional/repo2text](https://github.com/debian-professional/repo2text)

---

## Arquitectura de seguridad en detalle

La seguridad fue la máxima prioridad durante todo el proyecto. Aquí todas las medidas clave:

### 1. Clave API — Nunca expuesta al cliente
- La clave se mantiene **exclusivamente** en la variable de entorno de Apache `DEEPSEEK_API_KEY` (establecida en `/etc/apache2/envvars`).
- `deepseek-api.py` la recupera mediante `os.environ.get('DEEPSEEK_API_KEY')`.
- El cliente se comunica solo con `/cgi-bin/deepseek-api.py` (proxy local) — nunca directamente con la API de DeepSeek.
- Incluso en caso de un ataque XSS, la clave no podría leerse de la página.

### 2. Inspección de magic bytes contra archivos ejecutables
- Antes de leer cualquier archivo cargado, los primeros 20 bytes se comparan contra una base de datos de firmas exhaustiva (ver [Carga de archivos con verificación de seguridad](#carga-de-archivos-con-verificación-de-seguridad)).
- Si una firma coincide, la carga se bloquea con un mensaje de error detallado que muestra la plataforma y el formato detectados.
- Esta protección funciona incluso si los archivos maliciosos se renombran (p.ej. `virus.exe` → `factura.pdf`).

### 3. Almacenamiento seguro de sesiones
- Directorio de sesiones: `/var/www/deepseek-chat/sessions/` — `chmod 700`
- Cada archivo de sesión: `chmod 600`
- El formato del ID de sesión se valida en el servidor — no es posible el recorrido de rutas.

### 4. Registro sin datos sensibles
- El registro contiene: marcas de tiempo, direcciones IP, métodos HTTP, rutas, códigos de estado, mensajes de error.
- **Nunca registrado**: Claves API, contenido de sesiones, texto de mensajes (más allá de las vistas previas de feedback de 60 caracteres).
- Las solicitudes OPTIONS se filtran para evitar el desbordamiento del registro.

### 5. Sin comunicación directa cliente-API
- Todas las operaciones críticas de seguridad ocurren en el servidor mediante Python CGI.
- El cliente no tiene conocimiento de las credenciales de la API, rutas del servidor o ubicaciones de almacenamiento de sesiones.

### 6. Validación de entrada
- Los formatos de archivo se validan tanto por extensión como por magic bytes.
- Los IDs de sesión se validan en el servidor contra la expresión regular del formato esperado.
- El pegado del portapapeles se filtra para bloquear rutas de archivos antes de que lleguen a la API.

### 7. Seguridad del transporte
- HTTPS se aplica mediante la configuración SSL de Apache (`deepseek-chat-ssl.conf`).
- La configuración HTTP (`deepseek-chat.conf`) se desactiva mediante `a2dissite`.

---

## Despliegue y uso

### Requisitos previos

- Sistema basado en Debian (o cualquier Linux con Apache, Python 3, Bash)
- Apache con módulo CGI (`a2enmod cgi`) y SSL (`a2enmod ssl`)
- Python 3 con paquetes: `reportlab`
- Para `repo2text.sh`: `jq`, `pv`, `zip`, `git`
- Una clave API de DeepSeek válida de [platform.deepseek.com](https://platform.deepseek.com)

### Instalación

**1. Clonar el repositorio** (como usuario `source`):
```bash
git clone https://github.com/debian-professional/multi-llm-chat.git /home/source/multi-llm-chat
```

**2. Configurar la clave API**:
```bash
# Añadir a /etc/apache2/envvars:
export DEEPSEEK_API_KEY="tu-clave-api-de-deepseek-aquí"
```

**3. Activar la configuración de Apache**:
```bash
a2ensite deepseek-chat-ssl.conf
a2dissite deepseek-chat.conf   # desactivar configuración HTTP sin cifrar
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

**Configuración de modelos** (`MODEL_CONFIG` en `index.html`):
```javascript
const MODEL_CONFIG = {
    'deepseek-chat':     { maxContextTokens: 100000,  maxOutputTokens: 8192,  maxContextMessages: 50  },
    'deepseek-reasoner': { maxContextTokens: 65000,   maxOutputTokens: 32768, maxContextMessages: 30  },
    'gemini-2.5-flash':  { maxContextTokens: 1048576, maxOutputTokens: 8192,  maxContextMessages: 100 },
    'gemini-2.5-pro':    { maxContextTokens: 1048576, maxOutputTokens: 65536, maxContextMessages: 100 },
    'gemini-1.5-pro':    { maxContextTokens: 2097152, maxOutputTokens: 8192,  maxContextMessages: 100 },
    'gemini-2.0-flash':  { maxContextTokens: 1048576, maxOutputTokens: 8192,  maxContextMessages: 100 },
    'Qwen/Qwen2.5-72B-Instruct':              { maxContextTokens: 128000, maxOutputTokens: 8192, maxContextMessages: 80 },
    'mistralai/Mistral-7B-Instruct-v0.3':     { maxContextTokens: 32768,  maxOutputTokens: 4096, maxContextMessages: 40 },
    'microsoft/Phi-3.5-mini-instruct':        { maxContextTokens: 128000, maxOutputTokens: 4096, maxContextMessages: 60 },
    'meta-llama/Meta-Llama-3.1-70B-Instruct': { maxContextTokens: 128000, maxOutputTokens: 8192, maxContextMessages: 80 },
    'meta-llama/Meta-Llama-3.1-405B-Instruct':{ maxContextTokens: 128000, maxOutputTokens: 8192, maxContextMessages: 80 },
    'mistralai/Mixtral-8x7B-Instruct-v0.1':   { maxContextTokens: 32768,  maxOutputTokens: 4096, maxContextMessages: 40 },
    // GroqCloud
    'llama-3.3-70b-versatile': { maxContextTokens: 128000, maxOutputTokens: 8192,  maxContextMessages: 80 },
    'llama-3.1-8b-instant':    { maxContextTokens: 131072, maxOutputTokens: 8192,  maxContextMessages: 80 },
    'mixtral-8x7b-32768':      { maxContextTokens: 32768,  maxOutputTokens: 32768, maxContextMessages: 40 },
    'gemma2-9b-it':            { maxContextTokens: 8192,   maxOutputTokens: 8192,  maxContextMessages: 50 }
};
const OPENAI_MODELS_FREE = ['gpt-4o-mini', 'gpt-5-mini'];
const OPENAI_MODELS_PAID = ['gpt-5.4', 'gpt-5.2-chat-latest', 'gpt-4o', 'gpt-4.1', 'gpt-4o-mini'];
const DEEPSEEK_MODELS    = ['deepseek-chat', 'deepseek-reasoner'];
const GOOGLE_MODELS_FREE = ['gemini-2.5-flash'];
const GOOGLE_MODELS_PAID = ['gemini-2.5-flash', 'gemini-2.5-pro', 'gemini-1.5-pro', 'gemini-2.0-flash'];
const HF_MODELS_FREE     = ['Qwen/Qwen2.5-72B-Instruct', 'mistralai/Mistral-7B-Instruct-v0.3', 'microsoft/Phi-3.5-mini-instruct'];
const HF_MODELS_PAID     = ['meta-llama/Meta-Llama-3.1-70B-Instruct', 'meta-llama/Meta-Llama-3.1-405B-Instruct', 'Qwen/Qwen2.5-72B-Instruct', 'mistralai/Mixtral-8x7B-Instruct-v0.1'];
const GROQ_MODELS_FREE   = ['llama-3.3-70b-versatile', 'llama-3.1-8b-instant', 'mixtral-8x7b-32768', 'gemma2-9b-it'];
const GROQ_MODELS_PAID   = ['llama-3.3-70b-versatile', 'llama-3.1-8b-instant', 'mixtral-8x7b-32768', 'gemma2-9b-it'];
// Models with native audio input support (microphone recording button)
const AUDIO_CAPABLE_MODELS = ['gemini-2.5-flash','gemini-2.5-pro','gemini-1.5-pro','gemini-2.0-flash','gpt-4o','gpt-4.1'];
```

**Configuración de claves API** (`/etc/apache2/envvars`):
```bash
export OPENAI_API_KEY="sk-proj-..."
export DEEPSEEK_API_KEY="sk-..."
export GOOGLE_API_KEY="AIza..."
export HF_API_KEY="hf_..."
export GRQ_API_KEY="gsk_..."
```

**Configuración de idioma** (`language.xml`):
- Añadir un nuevo bloque `<language id="custom" name="..." visible="true">` para activar el espacio de idioma personalizado.
- Establecer `has_address_form="true"` para idiomas con distinción formal/informal.

### Scripts de despliegue

| Script | Función |
|--------|----------|
| `deploy.sh <user>` | Copia archivos de `/home/<user>/multi-llm-chat/var/www/deepseek-chat/` a `/var/www/deepseek-chat/`, establece permisos, recarga Apache |
| `sync-back.sh <user>` | Copia los archivos modificados de producción de vuelta al repositorio fuente |
| `install.sh` | Instala `deploy.sh` y `sync-back.sh` en el directorio de producción |
| `tag-release.sh` | Crea una nueva etiqueta Git con número de versión autoincremental (p.ej. v0.80 → v0.81) y la sube |

---

## Estructura del proyecto

```
/
├── etc/apache2/sites-available/
│   ├── deepseek-chat.conf              (desactivado — solo HTTP, redirige a HTTPS)
│   └── deepseek-chat-ssl.conf          (activo — SSL, CGI, clave API mediante envvars)
├── shell-scripts/
│   ├── repo2text.sh                    Exportar todo el repositorio como un único archivo de texto
│   ├── deploy.sh                       Copia el repositorio fuente → producción
│   ├── sync-back.sh                    Copia la producción → repositorio fuente
│   ├── install.sh                      Instala los scripts deploy/sync-back
│   └── tag-release.sh                  Crea y sube etiquetas de versión Git
├── var/www/deepseek-chat/
│   ├── index.html                      Aplicación principal (todo JS/CSS/HTML)
│   ├── language.xml                    Todos los textos de la interfaz en todos los idiomas (EN, DE, ES, Custom)
│   ├── manifest                        Manifiesto de diseño (todas las convenciones, ~20KB)
│   ├── changelog                       Historial completo de desarrollo (78+ entradas, ~44KB)
│   ├── files-directorys                Resumen de archivos / listado de directorios
│   ├── cgi-bin/
│   │   ├── openai-api.py              Proxy de streaming hacia la API de OpenAI
│   │   ├── deepseek-api.py            Proxy de streaming hacia la API de DeepSeek
│   │   ├── google-api.py              Proxy de streaming hacia la API de Google Gemini
│   │   ├── hugging-api.py             Proxy de streaming hacia la API de Hugging Face Inference
│   │   ├── groq-api.py                Proxy de streaming hacia la API de GroqCloud (acelerado por LPU)
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

## Configuración de modelos

El objeto `MODEL_CONFIG` en `index.html` es la única fuente de verdad para todos los límites específicos de cada modelo. Cubre los cinco proveedores:

```javascript
const MODEL_CONFIG = {
    // OpenAI
    'gpt-5.4':              { maxContextTokens: 1050000, maxOutputTokens: 16384, maxContextMessages: 100 },
    'gpt-5.2-chat-latest':  { maxContextTokens: 128000,  maxOutputTokens: 16384, maxContextMessages: 80  },
    'gpt-4o':               { maxContextTokens: 128000,  maxOutputTokens: 16384, maxContextMessages: 80  },
    'gpt-4.1':              { maxContextTokens: 1048576, maxOutputTokens: 32768, maxContextMessages: 100 },
    'gpt-4o-mini':          { maxContextTokens: 128000,  maxOutputTokens: 16384, maxContextMessages: 80  },
    'gpt-5-mini':           { maxContextTokens: 128000,  maxOutputTokens: 16384, maxContextMessages: 80  },
    // DeepSeek
    'deepseek-chat':     { maxContextTokens: 100000,  maxOutputTokens: 8192,  maxContextMessages: 50  },
    'deepseek-reasoner': { maxContextTokens: 65000,   maxOutputTokens: 32768, maxContextMessages: 30  },
    // Google Gemini
    'gemini-2.5-flash':  { maxContextTokens: 1048576, maxOutputTokens: 8192,  maxContextMessages: 100 },
    'gemini-2.5-pro':    { maxContextTokens: 1048576, maxOutputTokens: 65536, maxContextMessages: 100 },
    'gemini-1.5-pro':    { maxContextTokens: 2097152, maxOutputTokens: 8192,  maxContextMessages: 100 },
    'gemini-2.0-flash':  { maxContextTokens: 1048576, maxOutputTokens: 8192,  maxContextMessages: 100 },
    // Hugging Face
    'Qwen/Qwen2.5-72B-Instruct':               { maxContextTokens: 128000, maxOutputTokens: 8192, maxContextMessages: 80 },
    'mistralai/Mistral-7B-Instruct-v0.3':      { maxContextTokens: 32768,  maxOutputTokens: 4096, maxContextMessages: 40 },
    'microsoft/Phi-3.5-mini-instruct':         { maxContextTokens: 128000, maxOutputTokens: 4096, maxContextMessages: 60 },
    'meta-llama/Meta-Llama-3.1-70B-Instruct':  { maxContextTokens: 128000, maxOutputTokens: 8192, maxContextMessages: 80 },
    'meta-llama/Meta-Llama-3.1-405B-Instruct': { maxContextTokens: 128000, maxOutputTokens: 8192, maxContextMessages: 80 },
    'mistralai/Mixtral-8x7B-Instruct-v0.1':    { maxContextTokens: 32768,  maxOutputTokens: 4096, maxContextMessages: 40 },
    // GroqCloud
    'llama-3.3-70b-versatile': { maxContextTokens: 128000, maxOutputTokens: 8192,  maxContextMessages: 80 },
    'llama-3.1-8b-instant':    { maxContextTokens: 131072, maxOutputTokens: 8192,  maxContextMessages: 80 },
    'mixtral-8x7b-32768':      { maxContextTokens: 32768,  maxOutputTokens: 32768, maxContextMessages: 40 },
    'gemma2-9b-it':            { maxContextTokens: 8192,   maxOutputTokens: 8192,  maxContextMessages: 50 }
};
```

Fuentes: [OpenAI API Docs](https://platform.openai.com/docs), [DeepSeek API Docs](https://api-docs.deepseek.com), [Google Gemini Docs](https://ai.google.dev/gemini-api/docs), [Hugging Face Inference Providers](https://huggingface.co/docs/inference-providers), [GroqCloud Docs](https://console.groq.com/docs/models) (a fecha de 11.03.2026).

---

## Manifiesto de diseño

El proyecto incluye un **archivo `manifest`** que documenta todas las decisiones de diseño y convenciones. Cada cambio en el proyecto se documenta allí. Reglas clave:

- **Todos los botones**: Solo estilo píldora (border-radius: 20px, height: 36px) — los botones cuadrados están prohibidos.
- **Colores de botones**: Azul (`#0056b3`) para acciones, toggle oscuro/azul para modos, rojo (`#dc3545`) para destructivo, verde (`#28a745`) para constructivo.
- **Ajustes**: Solo interruptores de palanca — sin botones de radio, sin casillas de verificación.
- **Sin emojis** en botones ni etiquetas (excepción: el icono DeepThink ✦).
- **Sin PHP** — exclusivamente JavaScript y Python.
- **Sin frameworks JS externos** — sin Node, sin React, sin Vue.
- **Preservación del formato**: La sangría y el formato existentes en `index.html` nunca deben cambiarse.
- **`AUDIO_CAPABLE_MODELS` debe actualizarse**: Cuando un modelo gane o pierda soporte de audio, la constante debe actualizarse inmediatamente (Regla del Manifiesto E.1).
- El manifiesto es un **archivo separado** y nunca debe incrustarse en `index.html`.

---

## Limitaciones conocidas y notas técnicas

### "Lost in the Middle" — Una limitación conocida de la IA
Todos los modelos de lenguaje actuales (incluido DeepSeek) tienden a recordar de forma fiable el contenido al **principio y al final** de un contexto largo, pero el contenido **en el medio** a veces se pasa por alto o se alucina. (Liu et al., 2023: "Lost in the Middle: How Language Models Use Long Contexts")

**Impacto práctico en este proyecto**:
- Una exportación del repositorio de ~270.000 caracteres ≈ ~67.500 tokens.
- Ventana de contexto de DeepSeek: 100.000 tokens → ~67% de utilización → el contenido en el medio puede ser poco fiable.
- **Recomendación**: Para tareas específicas, cargar solo los archivos relevantes individualmente en lugar de la exportación completa del repositorio.

### Caché de URL sin procesar de GitHub
Después de un `git push`, la nueva versión **no está disponible de inmediato** a través de las URLs de `raw.githubusercontent.com` — GitHub las almacena en caché hasta 10 minutos. Esto es normal y no puede evitarse. Los archivos se almacenan correctamente en GitHub tan pronto como `git push` tiene éxito.

### Nano y Unicode — Advertencia crítica
**Nunca** editar archivos que contengan secuencias de escape Unicode (como las funciones de diéresis) usando `nano` o copiando y pegando en un terminal. Nano corrompe `\u00e4` a `M-CM-$`, que es basura binaria para JavaScript.

**El único flujo de trabajo seguro**:
1. Editar archivos localmente (VS Code, gedit, kate o cualquier editor adecuado).
2. `git add` / `git commit` / `git push` desde la máquina local.
3. En el servidor: `git pull` (en el repositorio fuente como usuario `source`).
4. Como root: `./deploy.sh source`.

### Comportamiento de pegado en Linux/X11/Firefox
En Linux con X11 y Firefox, `e.preventDefault()` en los manejadores de eventos de pegado no bloquea de forma fiable el comportamiento nativo del navegador para contenido proveniente de gestores de archivos. La solución implementada aquí (permitir el pegado, verificar el contenido en `setTimeout(0)`, limpiar si se detectan rutas de archivo) es la solución alternativa fiable para esta limitación específica de la plataforma.

---

## Dependencias

| Componente | Propósito | Instalación |
|-----------|---------|-------------|
| Apache2 | Servidor web, soporte CGI | `apt install apache2` |
| Python 3 | Scripts CGI del servidor | `apt install python3` |
| reportlab | Exportación PDF | `pip3 install reportlab` |
| pdf.js 3.11.174 | Extracción PDF en el cliente | Cargado vía CDN (fallback automático) |
| jq | Procesamiento JSON en `repo2text.sh` | `apt install jq` |
| pv | Visualización del progreso en `repo2text.sh` | `apt install pv` |
| git | Gestión de versiones | `apt install git` |
| zip | Creación de archivos zip en `repo2text.sh` | `apt install zip` |

**Sin frameworks exóticos** — todas las dependencias son paquetes estándar en un entorno Debian o se cargan desde CDNs reconocidos.

---

## Conclusión / Por qué destaca este proyecto

Este proyecto demuestra desarrollo web de nivel profesional con un enfoque minimalista y orientado a la seguridad:

**Arquitectura**:
- Separación clara entre cliente (HTML/JS puro) y servidor (Python CGI) sin mezcla de responsabilidades.
- La clave API nunca se expone — incluso un compromiso XSS completo no puede filtrarla.
- Cliente de un único archivo (`index.html`) completamente autónomo pero altamente modular internamente.

**Experiencia de usuario**:
- Respuestas en streaming con latencia del primer token inferior a un segundo.
- Gestión de contexto flexible y única (eliminar cualquier mensaje + todos los posteriores).
- Manejo inteligente del portapapeles para texto, imágenes y protección de rutas de archivos.
- **Grabación de audio** directamente en el navegador — entrada de micrófono para Google Gemini (todos los modelos) y OpenAI gpt-4o / gpt-4.1.
- Soporte multilingüe con distinción de forma de tratamiento, cargado desde XML externo.

**Ingeniería**:
- Inspección de magic bytes que detecta malware independientemente de la extensión del archivo.
- Sistema de marcadores de posición para diéresis que resuelve una limitación fundamental de la API de DeepSeek.
- Mapa de capacidades de modelos compatible hacia adelante, listo para modelos con soporte de imágenes.
- Rastro de auditoría completo mediante Git y registro de cambios detallado.

**Herramientas**:
- `repo2text.sh` como herramienta práctica para el desarrollo asistido por IA.
- Scripts de despliegue que garantizan despliegues consistentes y con permisos correctos.
- Etiquetado de versiones para una gestión limpia de lanzamientos.

**Para un desarrollador profesional**, este proyecto demuestra:
- **Conciencia de seguridad** — protección de claves API, detección de malware, almacenamiento seguro de sesiones.
- **Disciplina estructurada** — manifiesto, etiquetas de versión, convenciones de diseño estrictas, registro de cambios documentado.
- **Profundidad en la resolución de problemas** — comportamiento de pegado en X11, corrupción de diéresis, salida binaria PDF, "Lost in the Middle".
- **Documentación completa** — tanto en línea como en archivos dedicados.

Multi-LLM Chat Client es un **ejemplo de desarrollo web profesional** — sin sobrecargas innecesarias, pero con los más altos estándares en seguridad, corrección y facilidad de uso.

---

*Última actualización: 11.03.2026*





