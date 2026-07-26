# Multi-LLM Chat Client – OpenAI, DeepSeek, Google Gemini, Hugging Face & GroqCloud

**Multi-LLM Chat Client** es un cliente de chat completamente autónomo y alojado localmente con soporte para cinco proveedores de IA: OpenAI, DeepSeek, Google Gemini, Hugging Face y GroqCloud. Desarrollado con foco en **seguridad, simplicidad y usabilidad profesional**, la arquitectura no requiere frameworks exóticos y se basa exclusivamente en tecnologías probadas: Apache como servidor web, Python CGI para la lógica del servidor y HTML/JavaScript/CSS puro en el lado del cliente.

Aspectos destacados:
- **Soporte Multi-LLM** – Cambio entre OpenAI, DeepSeek, Google Gemini, Hugging Face y GroqCloud mediante un toggle de proveedor en el panel de configuración LLM. Cada proveedor tiene su propia lista de modelos, selección de tier y opciones de configuración.
- **DeepSeek V4** – Migración completa a `deepseek-v4-flash` y `deepseek-v4-pro` con ventanas de contexto de 1M tokens. Los nombres de modelo heredados `deepseek-chat` y `deepseek-reasoner` están programados para retiro el 24 de julio de 2026.
- **Listo para GPT-5.6** – Lineup de modelos de OpenAI actualizado a la familia GPT-5.6 (Sol, Terra, Luna) más GPT-5.5, junto a GPT-4o y GPT-4.1. Las solicitudes ahora usan `max_completion_tokens`, el parámetro requerido por todos los modelos actuales de OpenAI.
- **Pipeline de visión funcional** – La subida de imágenes y el pegado desde el portapapeles están completamente conectados de extremo a extremo para Google Gemini y OpenAI: las imágenes se codifican en base64 en el cliente y se entregan como bloques nativos `inline_data` (Gemini) o `image_url` (OpenAI). La detección de capacidades del modelo (`MODEL_CAPABILITIES`) ahora está correctamente poblada por proveedor, en lugar de asumir por defecto "sin soporte de imágenes" para todo lo que no sea DeepSeek.
- **Subida de múltiples archivos** – Seleccionar y enviar varios archivos simultáneamente. Los contenidos se combinan y envían como contexto con cabeceras y separadores por archivo.
- **Grabación de audio mediante micrófono** – Grabar audio directamente en el navegador y enviarlo a la IA. Soporte nativo de Google Gemini (`gemini-2.5-flash`, `gemini-2.5-pro`) y OpenAI (`gpt-4o`, `gpt-4.1`). El botón de grabación aparece automáticamente solo con modelos compatibles con audio.
- **Gestión de contexto única** – Eliminar mensajes individuales junto con todos los posteriores. El chat permanece consistente y el uso de tokens se recalcula dinámicamente.
- **Máxima seguridad** – Las claves API nunca son visibles en el cliente, las subidas están protegidas contra archivos ejecutables mediante inspección de bytes mágicos, y las sesiones se almacenan con permisos de archivo restrictivos.
- **Sin frameworks exóticos** – Todo se basa en Apache, Python 3, Bash y HTML/JavaScript/CSS puro. Sin Node.js, sin React, sin pipeline de compilación.
- **Funciones de exportación profesionales** – PDF, Markdown, TXT y RTF para todo el chat o mensajes individuales, más copia directa al portapapeles (lado del cliente, sin roundtrip al servidor).
- **Soporte multilingüe** – Traducción completa de la UI mediante `language.xml` externo (inglés, alemán, español, extensible con un slot de idioma personalizado).
- **Kompressor (compresión de contexto)** – Compresión inteligente y automática del historial del chat cuando la ventana de contexto se llena. Una segunda llamada LLM resume el 50% más antiguo de los mensajes e inyecta el resumen en el prompt del sistema — conversaciones indefinidamente largas sin perder el contexto.
- **Banners de cuota y límite** – Banners visuales persistentes por crédito agotado (rojo, proveedores de pago) y límites diarios (azul, proveedores de tier gratuito), cada uno con botón de cierre.
- **Manejo de ventana de contexto superada** – Cuando se alcanza el tamaño máximo de contexto, aparece un cuadro interactivo directamente en el chat con dos opciones: continuar con el contexto comprimido transferido o iniciar un chat nuevo y limpio. La sesión actual se guarda automáticamente en ambos casos.
- **Integración con portapapeles** – Manejador Ctrl+V con diálogo para texto, imágenes y protección contra el pegado accidental de rutas de archivos.
- **Respuestas en streaming** – Las respuestas de la IA aparecen token por token, igual que ChatGPT o Claude.
- **Manejo de límite de tasa 429** – Reintento automático con visualización de cuenta regresiva para los límites del tier gratuito de Google Gemini.
- **Diagnóstico de errores transparente** – Las respuestas de error de la API ahora muestran el mensaje de error real del proveedor (en lugar de una cadena vacía) siempre que el error no coincida con un patrón conocido de cuota/contexto.
- **Verificación de despliegue** – `deploy.sh` imprime sumas de verificación MD5 de cada archivo copiado a producción, permitiendo la comparación inmediata con el repositorio fuente sin un paso manual adicional.
- **Herramienta incluida** – El script `repo2text.sh` exporta todo el repositorio como un único archivo de texto, ideal para trabajar con asistentes de IA.

---

## Tabla de Contenidos

- [Descripción General](#descripción-general)
- [Arquitectura](#arquitectura)
- [Gestión de Contexto Única](#gestión-de-contexto-única)
- [Características en Detalle](#características-en-detalle)
  - [Interfaz de Chat](#interfaz-de-chat)
  - [Respuestas en Streaming](#respuestas-en-streaming)
  - [Manejador de Portapapeles (Ctrl+V)](#manejador-de-portapapeles-ctrlv)
  - [Subida de Archivos con Comprobación de Seguridad](#subida-de-archivos-con-comprobación-de-seguridad)
  - [Sistema de Marcadores de Posición para Umlauts](#sistema-de-marcadores-de-posición-para-umlauts)
  - [Modo DeepThink](#modo-deepthink)
  - [Detección de Modelos y Capacidades](#detección-de-modelos-y-capacidades)
  - [Soporte de Imágenes (Visión)](#soporte-de-imágenes-visión)
  - [Sistema Multilingüe](#sistema-multilingüe)
  - [Configuración (Toggles en lugar de Botones de Radio)](#configuración-toggles-en-lugar-de-botones-de-radio)
  - [Gestión de Sesiones](#gestión-de-sesiones)
  - [Funciones de Exportación](#funciones-de-exportación)
  - [Botones de Feedback y Registro](#botones-de-feedback-y-registro)
  - [Visualización Dinámica del Contexto](#visualización-dinámica-del-contexto)
  - [Visualización de Tarjetas de Archivo](#visualización-de-tarjetas-de-archivo)
  - [Grabación de Audio](#grabación-de-audio)
  - [Kompressor — Compresión Inteligente de Contexto](#kompressor--compresión-inteligente-de-contexto)
  - [Banners de Cuota y Límite](#banners-de-cuota-y-límite)
  - [Manejo de Ventana de Contexto Superada](#manejo-de-ventana-de-contexto-superada)
- [Migración a DeepSeek V4](#migración-a-deepseek-v4)
- [Actualización de Mantenimiento y Funciones del 19 de Julio de 2026](#actualización-de-mantenimiento-y-funciones-del-19-de-julio-de-2026)
- [El Script Auxiliar `repo2text.sh`](#el-script-auxiliar-repo2textsh)
- [Arquitectura de Seguridad en Detalle](#arquitectura-de-seguridad-en-detalle)
- [Despliegue y Uso](#despliegue-y-uso)
  - [Requisitos Previos](#requisitos-previos)
  - [Instalación](#instalación)
  - [Configuración](#configuración)
  - [Scripts de Despliegue](#scripts-de-despliegue)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Configuración de Modelos](#configuración-de-modelos)
- [Manifiesto de Diseño](#manifiesto-de-diseño)
- [Limitaciones Conocidas y Notas Técnicas](#limitaciones-conocidas-y-notas-técnicas)
- [Dependencias](#dependencias)
- [Conclusión / Por Qué Este Proyecto Destaca](#conclusión--por-qué-este-proyecto-destaca)

---

## Descripción General

Multi-LLM Chat Client es una **aplicación web local** que se comunica con APIs de IA externas exclusivamente a través de scripts proxy CGI de Python del lado del servidor. Desarrollado para un entorno de servidor Debian privado, puede ejecutarse en cualquier sistema Linux con Apache 2.4 y Python 3. El objetivo era un cliente de chat **seguro, extensible y fácil de usar** sin dependencias en la nube y con control total sobre los datos y credenciales de API.

El proyecto ha crecido continuamente durante varias semanas de desarrollo activo, acumulando características como respuestas en streaming, gestión de sesiones, funciones de exportación, soporte multilingüe, integración con portapapeles, compresión inteligente de contexto, grabación de audio y medidas de seguridad robustas — sin introducir nunca frameworks JavaScript externos ni una cadena de compilación.

Toda la lógica del cliente reside en un único archivo `index.html` (~5.000 líneas). Todos los textos de la UI están externalizados en `language.xml`. Todas las operaciones del servidor son manejadas por 15 scripts CGI de Python en `/cgi-bin/`.

---

## Arquitectura

La arquitectura es intencionalmente simple pero bien pensada:

### 1. Capa del Cliente

- HTML5/JavaScript/CSS3 puro, servido mediante Apache.
- Sin herramientas de compilación, sin Node.js, sin bibliotecas JavaScript externas (excepción: PDF.js 3.11.174, cargado vía CDN, para extracción de texto PDF en el navegador).
- Toda la lógica del cliente — procesamiento de mensajes, actualizaciones de UI, recepción de streaming, cambio de idioma, manejo del portapapeles, gestión de sesiones, estimación de contexto — está encapsulada en un único `index.html`.
- Todos los textos de la UI se cargan desde un `language.xml` externo al inicio mediante `fetch()`. No existen cadenas de UI codificadas en el HTML.
- La configuración se persiste en `localStorage` con migración de esquema versionada.

### 2. Capa del Servidor

- **Apache 2.4** con `mod_cgi` habilitado. HTTPS forzado mediante configuración SSL.
- **Scripts CGI de Python 3** bajo `/cgi-bin/` gestionan todas las operaciones del servidor:

| Script | Función |
|--------|---------|
| `openai-api.py` | Proxy de streaming al endpoint OpenAI Chat Completions (formato nativo) |
| `deepseek-api.py` | Proxy de streaming al endpoint DeepSeek Chat Completions (compatible con OpenAI) |
| `google-api.py` | Proxy a la API de Google Gemini con conversión de formato (OpenAI ↔ Gemini) |
| `hugging-api.py` | Proxy de streaming al router de inferencia de Hugging Face (compatible con OpenAI) |
| `groq-api.py` | Proxy de streaming a la API de GroqCloud (compatible con OpenAI, hardware LPU) |
| `compress-context.py` | Compresión de contexto — resume el 50% más antiguo de los mensajes mediante segunda llamada LLM |
| `deepseek-models.py` | Consulta el endpoint DeepSeek `/v1/models` en tiempo real al inicio |
| `save-session.py` | POST: recibe `{sessionId, messages}`, valida ID, escribe JSON en disco |
| `load-session.py` | GET: devuelve lista de sesiones con vistas previas; POST `{sessionId}`: devuelve sesión completa |
| `delete-session.py` | POST `{sessionId}`: elimina el archivo JSON de sesión |
| `export-pdf.py` | Exportación PDF del lado del servidor mediante ReportLab |
| `export-markdown.py` | Exportación Markdown del lado del servidor |
| `export-txt.py` | Exportación TXT del lado del servidor |
| `export-rtf.py` | Exportación RTF del lado del servidor (sin biblioteca externa, codificación RTF manual) |
| `feedback-log.py` | Escribe entradas de feedback Like/Dislike en el log del servidor |
| `get-log.py` | Lee y devuelve el contenido del archivo de log del servidor |

- Las **claves API** se proporcionan exclusivamente mediante variables de entorno de Apache en `/etc/apache2/envvars` — `OPENAI_API_KEY`, `DEEPSEEK_API_KEY`, `GOOGLE_API_KEY`, `HF_API_KEY`, `GRQ_API_KEY`. **Nunca** están presentes en el código del cliente ni en las respuestas HTTP.
- Un único `ScriptAlias /cgi-bin/ /var/www/deepseek-chat/cgi-bin/` cubre todos los scripts — no se necesitan cambios en la configuración de Apache al añadir nuevos scripts.

### 3. Almacenamiento de Datos

| Ubicación | Contenido | Permisos |
|-----------|-----------|---------|
| `/var/www/deepseek-chat/sessions/` | Archivos JSON de sesiones de chat | `chmod 700` (dir), `chmod 600` (archivos) |
| `/var/www/deepseek-chat/logs/multi-llm-chat.log` | Log de actividad del servidor (sin claves API, sin contenido de sesión) | Propietario `www-data` |
| `/var/www/deepseek-chat/kompressor/` | Archivos de resultados de compresión (uno por ronda de compresión) | Propietario `www-data` |
| `localStorage` del navegador | Configuración del usuario (con migración de versión), idioma, preferencias de modelo | Solo del lado del cliente |
| `language.xml` | Todos los textos de UI en todos los idiomas | Cargado mediante `fetch()` al inicio de página |

### 4. Scripts Auxiliares

- `deploy.sh` — copia el repositorio fuente al directorio de producción, establece propietario/permisos correctos, recarga Apache.
- `sync-back.sh` — copia archivos modificados desde producción de vuelta al repositorio fuente.
- `install.sh` — instala `deploy.sh` y `sync-back.sh` en el directorio de producción.
- `tag-release.sh` — crea un tag Git con número de versión auto-incrementado (p.ej. `v0.94 → v0.95`) y lo envía. Ejecuta `git fetch --tags` automáticamente para evitar conflictos con tags remotos existentes.
- `repo2text.sh` — exporta todo el repositorio como un único archivo de texto delimitado para asistentes de IA.

---

## Gestión de Contexto Única

Una de las características más destacadas es la capacidad de **eliminar cualquier mensaje individual junto con todos los posteriores**. Esto va mucho más allá del típico "eliminar el último mensaje" y permite la corrección flexible del historial de conversación en cualquier punto.

**Implementación**:
- Cada mensaje (usuario y IA) recibe un ID único (formato: `msg_N`) y se almacena en el array `contextHistory.messages[]`.
- `deleteMessage(msgId)` determina el índice del mensaje objetivo, trunca el array desde ese índice y elimina todos los elementos DOM siguientes (mensajes + separadores).
- `updateContextEstimation()` recalcula inmediatamente el conteo estimado de tokens y el porcentaje de utilización del contexto mostrado en la cabecera.
- Si el contexto cae por debajo del último umbral del compresor activado después de la eliminación, el resumen de compresión se descarta automáticamente y el seguimiento de umbrales se reinicia — asegurando que el estado de compresión siempre refleje el contenido real de la conversación.
- La sesión modificada se guarda automáticamente de inmediato mediante `saveSession()`.

**Por qué es única**: La mayoría de los clientes de chat solo permiten eliminar el último mensaje o ninguna manipulación del historial. Aquí, el usuario puede **definir cualquier punto de la conversación como nuevo punto de partida** — ideal para probar variaciones de prompts, corregir errores a mitad de conversación o limpiar la ventana de contexto sin descartar todo el chat.

**Función de regeneración**: Cada respuesta de IA incluye un botón "Regenerar" que elimina la respuesta actual del contexto y el DOM, luego emite una nueva llamada a la API basada en el mismo mensaje del usuario y el historial previo completo.

---

## Características en Detalle

### Interfaz de Chat

- **Dark Mode fijo** — Fondo `#121212`, texto `#f0f0f0`, acento `#0056b3`. Sin opción de modo claro por diseño.
- **Cabecera del servidor** (4 líneas): nombre del servidor (azul `#4dabf7`), dirección IP interna, utilización dinámica del contexto con nombre del modelo activo, IDs de modelos detectados de la API de DeepSeek.
- **Contenedores de mensajes**: botones de acción activados por hover (feedback, exportación por mensaje, eliminar). Los mensajes del usuario aparecen en azul (`#4dabf7`), las respuestas de IA en blanco sobre fondo oscuro.
- **Textarea**: se expande al enfocarse de 40px a 120px mediante transición CSS. Enter envía el mensaje; Shift+Enter inserta un salto de línea.
- **Diseño pill-style estricto**: border-radius 20px, altura 36px para todos los botones — sin botones cuadrados en ningún lugar de la UI.
- `white-space: pre-wrap` en todo el contenido de mensajes preserva el formato de las respuestas de IA.
- Auto-scroll al mensaje más reciente activo durante y después del streaming.

### Respuestas en Streaming

Todas las respuestas de IA se reciben y muestran **token por token** usando Server-Sent Events (SSE):

- Los cinco scripts proxy CGI envían sus respectivas solicitudes a la API con `stream: True` (o equivalente) y reenvían el flujo SSE sin buffer directamente al cliente.
- `index.html` lee el flujo mediante la API `ReadableStream` con `TextDecoder`.
- Cada fragmento recibido se añade al elemento DOM del mensaje activo en tiempo real.
- **Cabeceras SSE técnicas** establecidas por todos los scripts proxy CGI:
  ```
  Content-Type: text/event-stream
  X-Accel-Buffering: no
  Cache-Control: no-cache
  ```
- El efecto psicológico es significativo: los primeros tokens aparecen en ~300ms en lugar de esperar 5–10 segundos por una respuesta completa.
- Tanto `sendMessage()` como `handleRegenerate()` usan lógica de streaming idéntica.

### Integración con OpenAI

- **Endpoint**: `https://api.openai.com/v1/chat/completions`
- **Arquitectura**: Formato nativo OpenAI Chat Completions — sin conversión de formato requerida. Flujo SSE reenviado directamente por `openai-api.py`.
- **Clave API**: `OPENAI_API_KEY` mediante variables de entorno de Apache.
- **Modelos Tier Gratuito**: `gpt-4o-mini`, `gpt-5.6-luna`
- **Modelos Tier de Pago**: `gpt-5.6-sol`, `gpt-5.6-terra`, `gpt-5.6-luna`, `gpt-5.5`, `gpt-5.4`, `gpt-4o`, `gpt-4.1`, `gpt-4o-mini`
- **Parámetro de tokens de salida**: `max_completion_tokens` — requerido por todos los modelos actuales de OpenAI (GPT-4o/4.1 también lo aceptan, por lo que un único parámetro funciona en todo el lineup). El parámetro más antiguo `max_tokens` es rechazado por los modelos GPT-5.x con HTTP 400 (`Unsupported parameter: 'max_tokens' is not supported with this model. Use 'max_completion_tokens' instead.`).
- **Entrada de imágenes**: `gpt-4o-mini`, `gpt-4o`, `gpt-4.1`, `gpt-5.4`, `gpt-5.5` y toda la familia GPT-5.6 aceptan entrada de imágenes. Las imágenes se envían como bloques de contenido `image_url` con una URL de datos base64 (`data:{mime};base64,{data}`).
- **Entrada de audio**: `gpt-4o` y `gpt-4.1` soportan grabaciones de micrófono. El audio se envía como bloques `input_audio` en el formato nativo de OpenAI. El botón de grabación se muestra/oculta automáticamente según el modelo activo.
- **Sin tier gratuito de API para GPT-5.x**: OpenAI no ofrece un tier realmente gratuito para GPT-5.4/5.5/5.6 en la API — la agrupación "Free" en este cliente denota los modelos más económicos disponibles (`gpt-4o-mini`, `gpt-5.6-luna`), no una cuota de $0.
- **Retiro programado**: `gpt-4o` y `gpt-4o-mini` (junto con GPT-4, GPT-4 Turbo, GPT-3.5 Turbo y la serie o) están programados para su cierre en toda la API el **23 de octubre de 2026**.
- El botón DeepThink y el indicador se ocultan cuando OpenAI es el proveedor activo.
- El prompt del sistema identifica el modelo activo: *"You are [model], an AI assistant made by OpenAI."*

### Integración con Google Gemini

- **Endpoint**: `https://generativelanguage.googleapis.com/v1beta/models/{model}:streamGenerateContent`
- **Arquitectura**: `google-api.py` convierte el formato interno compatible con OpenAI al formato `contents` de Gemini, envía la solicitud y convierte la respuesta SSE de Gemini de vuelta al formato SSE de OpenAI esperado por el cliente.
- **Clave API**: `GOOGLE_API_KEY` mediante variables de entorno de Apache.
- **Modelos Tier Gratuito**: `gemini-2.5-flash` (5 RPM, 20 RPD)
- **Modelos Tier de Pago**: `gemini-2.5-flash`, `gemini-2.5-pro`
- **Entrada de imágenes**: Ambos modelos aceptan entrada de imágenes, enviadas como bloques `inline_data` en el formato nativo de Gemini (el mismo mecanismo usado para audio).
- **Entrada de audio**: Ambos modelos Gemini soportan audio nativamente. El audio se envía como bloques `inline_data` en formato Gemini. El botón de grabación siempre es visible cuando Google Gemini está activo.
- **Modelos retirados**: `gemini-2.0-flash` (cerrado el 1 de junio de 2026) y `gemini-1.5-pro` (retirado anteriormente) fueron eliminados de todas las listas de modelos, `MODEL_CONFIG` y `AUDIO_CAPABLE_MODELS`. El modelo de respaldo por defecto se actualizó de `gemini-2.0-flash` a `gemini-2.5-flash`.
- **Retiro próximo**: `gemini-2.5-flash` mismo está programado para cierre el **16 de octubre de 2026** (sucesor: `gemini-3.5-flash`, aún no integrado).
- El botón DeepThink y el indicador se ocultan cuando Google Gemini es el proveedor activo.

### Integración con Hugging Face

- **Endpoint**: `https://router.huggingface.co/v1/chat/completions` — el router de inferencia de Hugging Face selecciona automáticamente el proveedor disponible más rápido.
- **Arquitectura**: Formato compatible con OpenAI — sin conversión requerida. SSE reenviado directamente por `hugging-api.py`.
- **Clave API**: `HF_API_KEY` — un token de escritura de `huggingface.co/settings/tokens` con permiso "Make calls to Inference Providers".
- **Modelos Tier Gratuito**: `Qwen/Qwen2.5-72B-Instruct`, `mistralai/Mistral-7B-Instruct-v0.3`, `microsoft/Phi-3.5-mini-instruct`
- **Modelos Tier de Pago**: `meta-llama/Meta-Llama-3.1-70B-Instruct`, `meta-llama/Meta-Llama-3.1-405B-Instruct`, `Qwen/Qwen2.5-72B-Instruct`
- **Eliminado**: `mistralai/Mixtral-8x7B-Instruct-v0.1` — desde el 19 de julio de 2026 ya no está desplegado por ningún Inference Provider en el router de Hugging Face.
- El botón DeepThink y el indicador se ocultan cuando Hugging Face está activo.

### Integración con GroqCloud

- **Endpoint**: `https://api.groq.com/openai/v1/chat/completions`
- **Arquitectura**: Formato compatible con OpenAI — sin conversión requerida. SSE reenviado directamente por `groq-api.py`.
- **Clave API**: `GRQ_API_KEY` mediante variables de entorno de Apache.
- **Importante**: Se requiere una cabecera `User-Agent` en todas las solicitudes — sin ella, Cloudflare devuelve el código de error 1010 y bloquea la solicitud.
- **Modelos Tier Gratuito y de Pago**: `llama-3.3-70b-versatile`, `llama-3.1-8b-instant`, `meta-llama/llama-4-scout-17b-16e-instruct`, `qwen/qwen3-32b`. Solo de pago: `moonshotai/kimi-k2-instruct-0905`.
- Todos los modelos corren en hardware LPU (Language Processing Unit) de GroqCloud, ofreciendo latencia de inferencia muy baja.
- **Limpieza de documentación**: La cabecera de `groq-api.py` documentaba anteriormente `mixtral-8x7b-32768` (deprecado por Groq desde el 20 de marzo de 2025) y `gemma2-9b-it` (deprecado desde el 8 de octubre de 2025) como modelos soportados — ambos ya eran inalcanzables y se eliminaron de la cabecera. Los arrays de modelos reales en `index.html` ya eran correctos; solo la documentación estaba desactualizada.
- El botón DeepThink y el indicador se ocultan cuando GroqCloud es el proveedor activo.

### Panel de Configuración LLM

Un panel de **Configuración LLM** dedicado (separado del panel de Configuración principal) mantiene toda la configuración específica del proveedor fuera de la interfaz principal:

- **Selección de proveedor**: Toggle entre OpenAI, DeepSeek, Google Gemini, Hugging Face y GroqCloud — exactamente un proveedor activo a la vez.
- **Opciones de OpenAI**: Toggle de plan Gratuito/De pago con actualización automática de la lista de modelos.
- **Opciones de DeepSeek**: Modo predeterminado (Chat Normal / DeepThink), toggle de privacidad (cabecera `X-No-Training`).
- **Opciones de Google**: Toggle de plan Gratuito/De pago con actualización automática de la lista de modelos.
- **Opciones de Hugging Face**: Toggle de plan Gratuito/De pago con actualización automática de la lista de modelos.
- **Opciones de GroqCloud**: Toggle de plan Gratuito/De pago con actualización automática de la lista de modelos.
- **Opciones del Kompressor**: Toggle de activación, selección de proveedor de compresión (solo proveedores de pago), selección de modelo de compresión. Predeterminado: activado, DeepSeek / `deepseek-v4-flash`.
- **Dropdown de modelos**: Siempre visible, el contenido se actualiza automáticamente según el proveedor activo y el plan seleccionado.
- Toda la configuración LLM se persiste en `localStorage` y sobrevive a recargas de página.

### Manejo de Límite de Tasa 429

El tier gratuito de Google Gemini aplica límites de tasa estrictos (5 RPM, 20 RPD). El cliente los maneja con elegancia sin mostrar un error en bruto:

- En HTTP 429, el cliente reintenta automáticamente hasta **3 veces** con intervalos de **15 segundos**.
- Durante la espera, se muestra una cuenta regresiva directamente en el chat: *"Rate limit reached – waiting 15 seconds and retrying... (Attempt 1/3)"*.
- Después de 3 intentos fallidos, la comprobación del límite diario activa el banner azul de límite si es aplicable.
- La lógica de reintento distingue entre límites RPM temporales (reintentables) y cuota diaria agotada (no reintentable).
- Los detalles de error detallados se escriben en el log del servidor para diagnóstico.

### Manejador de Portapapeles (Ctrl+V)

Un sofisticado manejador de portapapeles intercepta todos los eventos de pegado y responde de forma inteligente según el tipo de contenido:

**Contenido de texto** → Aparece un diálogo de pegado con dos opciones:
- *"Insertar en la posición del cursor"* — inserta el texto directamente en el campo de entrada en la posición actual del cursor.
- *"Adjuntar como archivo"* — trata el texto del portapapeles como `clipboard.txt` y lo adjunta como tarjeta de archivo al siguiente mensaje.

**Contenido de imagen** → Aparece un cuadro de vista previa en miniatura sobre el campo de entrada mostrando la imagen, sus dimensiones en KB y un botón de eliminación. La imagen está lista para enviarse con el siguiente mensaje si el modelo activo soporta imágenes.

**Rutas de archivos de gestores de archivos (XFCE/Thunar, KDE/Dolphin, etc.)** → Bloqueado con una alerta:
> *"Los archivos copiados en el gestor de archivos no pueden ser leídos por el navegador. Por favor usa el botón de subida."*

**Contexto técnico**: En Linux/X11/Firefox, `e.preventDefault()` no bloquea de forma fiable los eventos de pegado para contenido proveniente de gestores de archivos. La solución implementada permite el pegado, luego verifica inmediatamente el contenido del campo de entrada mediante `setTimeout(0)` y lo limpia si se detectan rutas de archivo. Lógica de detección: 2 o más líneas donde cada línea no vacía comienza con `/` o `file://`. Una llamada `requestAnimationFrame` asegura que el campo de entrada se limpie visualmente antes de que aparezca el diálogo de alerta.

### Subida de Archivos con Comprobación de Seguridad

- **Formatos aceptados**: `.txt`, `.pdf`, `.doc`, `.docx`, `.jpg`, `.jpeg`, `.png`, `.csv`, `.xlsx`, `.pptx`
- **Formatos con extracción de contenido** (texto enviado a la IA): `.txt`, `.pdf`
- **Otros formatos aceptados**: adjuntados como contexto binario (sin extracción de texto)
- **Tamaño máximo de archivo**: 10 MB por archivo
- **Contenido extraído máximo**: dinámico — calculado como el 75% de la ventana de contexto del modelo activo en caracteres: `getDynamicMaxFileChars() = Math.floor(config.maxContextTokens × 4 × 0.75)`

**Ejemplos de límite de subida dinámico**:

| Modelo | maxContextTokens | Máx. contenido de archivo |
|--------|-----------------|--------------------------|
| `deepseek-v4-flash` | 1.048.576 | ~3.145.000 caracteres |
| `deepseek-v4-pro` | 1.048.576 | ~3.145.000 caracteres |
| `gemini-2.5-flash` | 1.048.576 | ~3.145.000 caracteres |
| `gpt-5.6-sol` / `-terra` / `-luna` | 1.048.576 | ~3.145.000 caracteres |
| `gpt-4o` / `gpt-4o-mini` | 128.000 | ~384.000 caracteres |

**Inspección de bytes mágicos** (primeros 20 bytes) detecta y bloquea archivos ejecutables independientemente de la extensión del nombre de archivo:

| Plataforma | Formato | Firma Hex |
|-----------|---------|-----------|
| Windows 32/64 bit | PE/MZ Ejecutable | `4D 5A` |
| Linux 32 bit | ELF32 | `7F 45 4C 46 01` |
| Linux 64 bit | ELF64 | `7F 45 4C 46 02` |
| ARM 32 bit | ELF32 ARM | `7F 45 4C 46 01 01 01 00 ... 02 00 28 00` |
| ARM 64 bit | ELF64 AArch64 | `7F 45 4C 46 02 01 01 00 ... 02 00 B7 00` |
| macOS 32 bit | Mach-O | `CE FA ED FE` |
| macOS 64 bit | Mach-O | `CF FA ED FE` |
| macOS Universal | Fat Binary | `CA FE BA BE` |
| macOS/iOS ARM 32 | Big Endian | `FE ED FA CE` |
| macOS/iOS ARM 64 | Big Endian | `FE ED FA CF` |
| Linux/macOS | Script de shell | `23 21` (`#!`) |
| Python | Bytecode (.pyc) | `55 0D 0D 0A` |

**Extracción PDF**: Usa PDF.js 3.11.174 cargado desde CDN con fallback automático a un CDN secundario. El progreso de extracción se muestra página por página. Timeout de extracción: 30 segundos.

**Comprobación de contexto previa a la subida**: Antes de extraer el contenido del archivo, el cliente estima si añadir el archivo superaría el límite de subida dinámico. Si es así, la subida se bloquea con un mensaje de error claro antes de que se extraiga cualquier contenido.

### Sistema de Marcadores de Posición para Umlauts

Una solución única para un problema fundamental con la API de DeepSeek y el texto alemán:

**Problema**: DeepSeek reemplaza internamente los umlauts alemanes en el contenido de archivos con equivalentes ASCII (p.ej. `Ä → AeNDERUNG`, `Ü → MUeSSEN`). Este comportamiento no puede suprimirse mediante prompts del sistema o parámetros de API.

**Solución**: Antes de enviar contenido de archivos a DeepSeek, los umlauts se reemplazan con marcadores de posición únicos entre corchetes. DeepSeek los devuelve sin cambios. JavaScript los reemplaza de vuelta a umlauts reales después de recibir la respuesta.

| Original | Marcador de posición |
|----------|---------------------|
| `ä` | `[[AE]]` |
| `ö` | `[[OE]]` |
| `ü` | `[[UE]]` |
| `ß` | `[[SS]]` |
| `Ä` | `[[CAE]]` |
| `Ö` | `[[COE]]` |
| `Ü` | `[[CUE]]` |

**Detalle crítico de implementación**: Tanto `encodeUmlautsForAI()` como `decodeUmlautsFromAI()` usan exclusivamente **secuencias de escape Unicode** (`\u00e4` en lugar de `ä`) y `split()/join()` en lugar de regex — esencial para prevenir la corrupción cuando los archivos se transfieren mediante Git o se editan en editores de texto.

La decodificación se ejecuta **tanto durante el streaming** (token por token) como nuevamente después de que se recibe la respuesta completa, asegurando que no queden marcadores visibles incluso con entrega parcial de fragmentos.

Este sistema se aplica **solo al contenido de archivos**, nunca a mensajes regulares del usuario ni a prompts del sistema.

### Modo DeepThink

DeepThink es un modo dedicado para el razonamiento analítico profundo, disponible exclusivamente cuando DeepSeek es el proveedor activo:

- Activado mediante un botón pill-style dedicado en la segunda fila de botones debajo del campo de entrada.
- Cuando está activo, se usa `deepseek-v4-flash` (o `deepseek-v4-pro`, si se selecciona en el dropdown de modelos) — el modo solo cambia el prompt del sistema, no el modelo. El más capaz `deepseek-v4-pro` se selecciona manualmente mediante el dropdown de modelos para máxima profundidad de razonamiento en cualquier modo. **Nota**: antes del 19 de julio de 2026, un error de copiar-pegar en la lógica de selección de modelo causaba que `deepseek-v4-pro` nunca se solicitara realmente sin importar la selección del dropdown — esto se corrigió; ver [Actualización de Mantenimiento y Funciones del 19 de Julio de 2026](#actualización-de-mantenimiento-y-funciones-del-19-de-julio-de-2026).
- El botón cambia visualmente: inactivo (oscuro `#2d2d2d`) → activo azul (`#1e3a5f` fondo, `#4dabf7` borde y texto).
- Aparece una barra indicadora debajo de la fila de botones: *"Modo DeepThink activo: Análisis en profundidad en progreso"*.
- Los límites de contexto y de tokens de salida se ajustan automáticamente según la entrada `MODEL_CONFIG` del modelo activo.
- El modo se registra con cada mensaje (campo `mode: 'deepthink'`) y se muestra en todos los formatos de exportación.
- El modo predeterminado (Chat o DeepThink) puede configurarse en Ajustes y persiste en `localStorage`.
- El botón DeepThink y el indicador se ocultan automáticamente cuando cualquier proveedor que no sea DeepSeek está activo.

### Detección de Modelos y Capacidades

Al inicio, `index.html` consulta `/cgi-bin/deepseek-models.py`, que llama al endpoint DeepSeek `/v1/models` en tiempo real:

- Los IDs de modelos devueltos se almacenan en `detectedModels[]` y se usan internamente para las verificaciones de capacidad (ver abajo). **No** se usan para renderizar la cabecera — la cabecera del servidor (`Modelo: ...`) siempre muestra el modelo actualmente **seleccionado** (`settings.selectedModel`), coincidiendo con el comportamiento en los cinco proveedores. Versiones anteriores mostraban incorrectamente la lista completa de `detectedModels` para DeepSeek independientemente de la selección activa; esto se corrigió el 19 de julio de 2026.
- Un mapa `MODEL_CAPABILITIES` define qué modelos soportan qué tipos de entrada, poblado por proveedor según las capacidades documentadas de cada backend:
  ```javascript
  const MODEL_CAPABILITIES = {
      // DeepSeek: solo texto
      'deepseek-v4-flash': { images: false, text: true },
      'deepseek-v4-pro':   { images: false, text: true },
      // Google Gemini: multimodal
      'gemini-2.5-flash':  { images: true,  text: true },
      'gemini-2.5-pro':    { images: true,  text: true },
      // OpenAI: multimodal en todo el lineup actual
      'gpt-4o-mini': { images: true, text: true },
      'gpt-4o':      { images: true, text: true },
      'gpt-4.1':     { images: true, text: true },
      'gpt-5.4':     { images: true, text: true },
      'gpt-5.5':     { images: true, text: true },
      'gpt-5.6-sol':   { images: true, text: true },
      'gpt-5.6-terra': { images: true, text: true },
      'gpt-5.6-luna':  { images: true, text: true },
      // GroqCloud / Hugging Face: solo texto (lineup de modelos actual)
      // ... (ver index.html para la lista completa)
      'default': { images: false, text: true },
  };
  ```
- `currentModelSupportsImages()` verifica `settings.selectedModel` (con respaldo al valor actual del dropdown `modelSelect`) contra `MODEL_CAPABILITIES`. Versiones anteriores verificaban `detectedModels` en su lugar — un array relevante solo para DeepSeek que nunca se poblaba para otros proveedores — lo que significaba que la subida y el pegado de imágenes se bloqueaban silenciosamente para **todos** los proveedores y modelos, incluidos los genuinamente compatibles con imágenes. Esto se corrigió el 19 de julio de 2026.
- Si se pega una imagen mediante el portapapeles o se sube un archivo `.jpg`/`.png`, y el modelo actual no soporta imágenes, la operación se bloquea con una alerta antes de que ocurra cualquier subida.
- Esta arquitectura es **compatible con el futuro**: añadir soporte de imágenes para un modelo solo requiere añadir o actualizar su entrada en `MODEL_CAPABILITIES` — pero hay que notar que `MODEL_CONFIG` (ver [Configuración de Modelos](#configuración-de-modelos)) también necesita una entrada correspondiente para que el modelo obtenga límites correctos de contexto/salida, en lugar de recurrir silenciosamente a los valores por defecto de DeepSeek.

### Soporte de Imágenes (Visión)

La subida de imágenes y el pegado desde el portapapeles están completamente conectados de extremo a extremo para Google Gemini y OpenAI. Esta era una brecha significativa cerrada el 19 de julio de 2026 — anteriormente, las imágenes eran aceptadas por la UI pero nunca llegaban realmente a ningún modelo.

**Lado del cliente (`index.html`)**:
- **Subida de archivos**: Cuando se selecciona un archivo de imagen (`.jpg`, `.jpeg`, `.png`, etc.) y el modelo activo soporta imágenes (según `currentModelSupportsImages()`), el archivo se lee mediante `FileReader.readAsDataURL()`, y la carga base64 (sin el prefijo `data:...;base64,`) se almacena en `imageData`, con el tipo MIME en `imageMimeType`.
- **Pegado desde portapapeles**: Pegar una imagen (Ctrl+V) realiza la misma lectura base64, usada tanto para la vista previa en miniatura mostrada sobre el campo de entrada como para el `imageData` real enviado con el siguiente mensaje.
- **Payload de solicitud**: `sendMessage()` incluye `image_data` e `image_mime_type` en el cuerpo JSON siempre que `imageData` esté definido — junto al mecanismo existente `audio_data`/`audio_mime_type`. Ambos pueden estar presentes simultáneamente.
- **Reinicio de estado**: `imageData`/`imageMimeType` se limpian después de enviar un mensaje, al eliminar un archivo mediante el botón "X", y al comenzar una nueva selección de archivo — seis puntos de reinicio en total, siguiendo la lógica de reinicio de audio existente.
- **Limitación cosmética conocida**: Un adjunto de imagen enviado *sin* un archivo de texto acompañante no genera actualmente su propia tarjeta de archivo en la burbuja del chat (idéntico al comportamiento preexistente para mensajes de solo audio). La transmisión al modelo funciona correctamente independientemente de esto; solo falta la tarjeta visual en ese caso específico.

**Lado del servidor**:
- **`google-api.py`**: `convert_messages_to_gemini()` acepta `image_data`/`image_mime_type` y añade la imagen como una parte `inline_data` al último mensaje del usuario — el mismo mecanismo ya usado para audio.
- **`openai-api.py`**: El `content` del último mensaje del usuario se construye como una lista combinando la parte de texto con un bloque opcional `input_audio` y un bloque opcional `image_url` (`{'type': 'image_url', 'image_url': {'url': 'data:{mime};base64,{data}'}}`). El código anterior sobrescribía `content` incondicionalmente al manejar audio, lo que habría descartado silenciosamente una imagen enviada simultáneamente (o viceversa) — la lógica reescrita construye la lista de contenido de forma incremental para que ambos puedan coexistir.
- **GroqCloud y Hugging Face** actualmente no reciben datos de imagen — sus lineups de modelos son solo texto según la documentación propia de cada proveedor, y `MODEL_CAPABILITIES` refleja esto (`images: false`), por lo que el cliente bloquea los adjuntos de imagen para esos proveedores antes de que se envíe cualquier solicitud.

**Verificado**: Probado en vivo con `gemini-2.5-flash` y `gpt-4o-mini` — ambos describieron correctamente el contenido de una captura de pantalla subida en detalle.

### Sistema Multilingüe

La UI soporta múltiples idiomas cargados desde un archivo `language.xml` externo. No existen cadenas de UI codificadas en `index.html`.

**Idiomas actualmente incluidos**:
- Inglés (`en`) — predeterminado, sin distinción de forma de tratamiento
- Alemán (`de`) — con forma de tratamiento formal/informal (Sie/Du)
- Español (`es`) — con forma de tratamiento formal/informal (Usted/Tú)
- Slot personalizado (`custom`) — activado estableciendo `visible="true"` en `language.xml`

**Implementación técnica**:
- Todos los textos de la UI se referencian por IDs numéricos: `t(205)` devuelve la etiqueta del botón Enviar en el idioma actual.
- `loadLanguage()` carga y analiza `language.xml` mediante `fetch()` al inicio de página.
- `t(id)` — devuelve texto para el idioma actual, recurre al inglés si no se encuentra el ID.
- `tf(id, ...args)` — soporta sustitución de marcadores `{0}`, `{1}`, ...
- `tform(idFormal, idInformal)` — devuelve el texto apropiado según la forma de tratamiento seleccionada.
- El cambio de idioma es instantáneo, sin recarga de página requerida.
- El idioma seleccionado persiste en `localStorage`.

**Sistema de forma de tratamiento** (alemán/español):
- Los idiomas declaran `has_address_form="true"` en `language.xml`.
- Para dichos idiomas, el panel de Ajustes muestra un grupo "Forma de Tratamiento" (Formal/Informal).
- La forma seleccionada afecta: el prompt del sistema (impone un estilo de respuesta de IA consistente), el texto del placeholder del campo de entrada, todos los textos de descripción de ajustes.

**El prompt del sistema** se construye dinámicamente por solicitud desde:
1. Prompt base (IDs de texto 29/30 para formal/informal)
2. Adición DeepThink (IDs de texto 31/32)
3. Una instrucción estricta de manejo de archivos siempre añadida en inglés independientemente del idioma de la UI — asegurando comportamiento de IA consistente al procesar contenido de archivos.

### Configuración (Toggles en lugar de Botones de Radio)

Todos los ajustes usan **interruptores toggle** (deslizando de izquierda a derecha), nunca botones de radio ni casillas de verificación:

| Grupo | Ajuste | Color del Toggle |
|-------|--------|----------------|
| Idioma | EN / DE / ES / Personalizado | Verde |
| Forma de Tratamiento | Formal / Informal | Verde |
| Modo Predeterminado | Chat Normal / DeepThink | Azul |
| Privacidad | No usar datos para entrenamiento | Verde |

**Comportamiento del toggle**:
- Dentro de un grupo, los toggles se comportan como botones de radio: activar uno desactiva todos los demás del grupo.
- Hacer clic en cualquier parte de la fila `setting-item` activa ese toggle — no solo el elemento toggle en sí.
- Los elementos activos reciben un fondo de color: `#1a2e1a` (grupos verdes) o `#1e3a5f` (grupos azules).

**Toggle de privacidad**: Establece la cabecera HTTP `X-No-Training: true` en todas las solicitudes de API a DeepSeek, utilizando el mecanismo de exclusión voluntaria de DeepSeek para datos de entrenamiento.

**Persistencia de ajustes**: Todos los ajustes se almacenan en `localStorage` bajo la clave `deepseekSettings`. Versión de esquema actual: `SETTINGS_VERSION: 1.7`. La función `migrateSettings()` asegura la compatibilidad hacia atrás — los campos faltantes se rellenan con valores predeterminados, los modos desconocidos se normalizan.

### Gestión de Sesiones

Cada conversación se gestiona automáticamente como una sesión del lado del servidor:

- **Formato de ID de sesión**: `YYYY-MM-DD_HHMMSS_random6chars` (p.ej. `2026-05-11_143045_abc123`) — generado en el cliente, validado en el servidor mediante regex antes de cualquier E/S de archivo.
- **Guardado automático**: Después de cada par de mensajes enviados (usuario + IA), el array completo `contextHistory.messages[]` se serializa y guarda en el servidor como archivo JSON.
- **Archivo de sesión**: `{sessionId}.json` en `/var/www/deepseek-chat/sessions/`, `chmod 600`, propietario `www-data`.
- **Modal de carga del historial de chat**: Lista todas las sesiones guardadas con ID, fecha, vista previa del mensaje (primeros 80 caracteres) y conteo de mensajes. Cada sesión tiene botones [Cargar] (verde) y [Eliminar] (rojo).
- **Comportamiento de carga**: El chat actual se guarda automáticamente primero, luego se restaura la sesión seleccionada — historial de mensajes completo, reconstrucción de UI, recálculo de estimación de contexto.
- **Eliminar**: El archivo JSON se elimina del servidor inmediatamente sin diálogo de confirmación.

**Detalles del endpoint CGI**:
- `save-session.py` — `POST`: recibe `{sessionId, messages}`, valida formato de ID (regex), escribe `sessions/{sessionId}.json`
- `load-session.py` — `GET`: devuelve `[{id, preview, count, date}]`; `POST {sessionId}`: devuelve `{messages: [...]}` completo
- `delete-session.py` — `POST {sessionId}`: elimina `sessions/{sessionId}.json`

### Funciones de Exportación

**Exportación global** (botón dropdown en la fila de botones principal):

| Formato | Generación | Notas |
|---------|-----------|-------|
| PDF | Lado del servidor (`export-pdf.py`, ReportLab) | Cabecera, estadísticas, tabla de contenidos, chat completo |
| Markdown | Lado del servidor (`export-markdown.py`) | Estructura idéntica al PDF, con anchors |
| TXT | Lado del servidor (`export-txt.py`) | Texto plano con separadores |
| RTF | Lado del servidor (`export-rtf.py`) | Codificación RTF manual, umlauts como códigos de escape RTF |
| **Copiar al portapapeles** | **Solo del lado del cliente (sin roundtrip al servidor)** | Texto plano ensamblado en JavaScript, escrito mediante `navigator.clipboard.writeText()` |

**Exportación por mensaje** (botón hover en cada mensaje):

| Formato | Generación |
|---------|-----------|
| TXT | Lado del cliente (JavaScript Blob, `URL.createObjectURL()`) |
| Markdown | Lado del cliente |
| RTF | Lado del cliente |
| PDF | Lado del servidor (mensaje individual enviado a `export-pdf.py`) |

**Contenido de exportación** (exportación global PDF/Markdown):
- Cabecera: nombre del servidor, IP, fecha de exportación, idioma activo, forma de tratamiento
- Estadísticas: conteo total de mensajes, modos usados (chat/deepthink), archivos adjuntos, conteo estimado de tokens, duración de sesión
- Tabla de contenidos con todas las marcas de tiempo de los mensajes
- Historial completo del chat con marcas de tiempo por mensaje e indicadores de modo

**Copiar al portapapeles**: Ensamblado en el cliente en formato TXT y escrito mediante `navigator.clipboard.writeText()`. Una confirmación de *"¡Copiado!"* de 2 segundos reemplaza la etiqueta del botón Exportar, luego se restablece automáticamente.

**Nota técnica PDF**: Los datos binarios de PDF se escriben exclusivamente mediante `sys.stdout.buffer` con cabeceras HTTP codificadas como bytes — evitando el error `"Bad header"` que ocurre al mezclar `print()` (stdout en modo texto) con contenido binario.

### Botones de Feedback y Registro

Cuatro botones aparecen al hover para cada respuesta de IA (lado izquierdo, fila inferior):

- **Copiar** — Copia el texto del mensaje al portapapeles; muestra *"¡Copiado!"* por 2 segundos, luego se restablece.
- **Like** — Marca la respuesta positivamente (resaltado azul); envía una entrada `LIKE` al log del servidor. Hacer clic nuevamente elimina el like.
- **Dislike** — Marca la respuesta negativamente (resaltado rojo); envía una entrada `DISLIKE`. Like y Dislike son mutuamente excluyentes.
- **Regenerar** — Elimina la respuesta de IA actual del array de contexto y del DOM, luego llama a la API nuevamente con el mismo mensaje del usuario y el historial previo completo.

**Formato del log del servidor** (`/var/www/deepseek-chat/logs/multi-llm-chat.log`):
```
2026-05-11T12:30:00.000 | IP: 194.182.64.122 | POST /cgi-bin/deepseek-api.py | Status: 200
2026-05-11T12:30:00.000 | IP: 194.182.64.122 | FEEDBACK | LIKE | msg_5 | "Primeros 60 caracteres de la respuesta..."
```

**Nunca registrado**: claves API, contenido completo de sesiones, o texto de mensajes más allá de la vista previa de feedback de 60 caracteres.

### Visualización Dinámica del Contexto

La cabecera del servidor muestra cuatro líneas de información en tiempo real:
1. Nombre del servidor (azul `#4dabf7`)
2. `IP: xxx.xxx.xxx.xxx`
3. `Contexto: XX% (nombre-modelo-activo)`
4. `Modelo: deepseek-v4-flash, deepseek-v4-pro` (en tiempo real desde `/v1/models`)

**Cálculo de utilización del contexto**:
- Tokens estimados = suma de conteos de caracteres en los últimos `maxContextMessages` mensajes × `TOKENS_PER_CHAR` (0,25)
- Los tokens del prompt del sistema se añaden como overhead fijo
- Porcentaje = tokens estimados / `maxContextTokens` × 100

**Sistema de advertencia**: Por encima del 90% de utilización del contexto, la línea de contexto se vuelve roja y parpadea (animación CSS keyframe, opacidad 0 → 1, ciclo de 1 segundo). Esto proporciona una advertencia temprana muy visible.

La visualización se actualiza automáticamente después de cada mensaje enviado, cada mensaje eliminado y cada cambio de modelo.

### Visualización de Tarjetas de Archivo

Cuando se sube un archivo o se adjunta texto del portapapeles, el mensaje del usuario muestra una **tarjeta de archivo** compacta:

```
┌──────────────────────────────────────┐
│  [PDF]  │  nombre-archivo.pdf        │
│  icono  │  Documento PDF             │
└──────────────────────────────────────┘
```

- Insignia de tipo de archivo derivada de la extensión del archivo (PDF, TXT, XLSX, DOCX, etc.)
- Nombre de archivo truncado a 30 caracteres con `...` si es más largo
- Las grabaciones de audio muestran una insignia `AUDIO` con la etiqueta localizada
- Las subidas de múltiples archivos generan una tarjeta por archivo; todos los nombres de archivo aparecen en la barra de información separados por ` | `

### Grabación de Audio

El cliente incluye un **botón de grabación de micrófono** incorporado que permite la entrada de voz directa a modelos compatibles con audio:

- **Visibilidad**: Controlada por `updateAudioButtonVisibility()`, llamada en cada cambio de modelo. Visible solo cuando el modelo activo está listado en `AUDIO_CAPABLE_MODELS`.
- **Modelos compatibles con audio** (constante `AUDIO_CAPABLE_MODELS`):
  - Google Gemini: `gemini-2.5-flash`, `gemini-2.5-pro`
  - OpenAI: `gpt-4o`, `gpt-4.1`
- **Flujo de grabación**: `getUserMedia()` → API `MediaRecorder` → grabación por fragmentos (intervalos de 10ms) → `Blob` ensamblado al detener → codificado en base64.
- **Auto-detección de tipo MIME**: `audio/webm` (Chrome/Firefox) o `audio/mp4` (Safari) — detectado en tiempo de ejecución mediante `MediaRecorder.isTypeSupported()`.
- **Después de la grabación**: Los datos de audio se muestran en el cuadro `fileInfo` como tarjeta de insignia AUDIO.
- **Payload de solicitud**: `audio_data` (cadena base64) y `audio_mime_type` se añaden al cuerpo JSON junto con el mensaje de texto. El flag `hasFile` **no** se establece — no se inyecta prompt del sistema de procesamiento de archivos para audio.
- **Exclusión mutua**: La subida de archivos y la grabación de audio son mutuamente excluyentes. Iniciar una grabación borra cualquier archivo adjunto pendiente y viceversa.
- **Backend — Google (`google-api.py`)**: El audio se añade al último mensaje del usuario como bloque `inline_data` en el formato nativo de Gemini.
- **Backend — OpenAI (`openai-api.py`)**: El audio se añade como bloque `input_audio` con `format: webm` o `mp4`.
- **Regla de mantenimiento** (Regla de Manifiesto E.1): Siempre que un proveedor integrado añada o elimine soporte de audio para un modelo, `AUDIO_CAPABLE_MODELS` en `index.html` **debe** actualizarse inmediatamente.

### Kompressor — Compresión Inteligente de Contexto

Cada modelo de lenguaje tiene una ventana de contexto finita. En sesiones largas — particularmente con subidas de archivos grandes, conversaciones de varias horas o flujos de trabajo de análisis extensos — la ventana de contexto finalmente se llena, causando errores de API (HTTP 400/413) que obligan al usuario a empezar de nuevo y perder todo el hilo de la conversación.

El **Kompressor** resuelve este problema de forma automática y transparente, sin ninguna acción del usuario requerida.

#### Concepto Central

En lugar de truncar mensajes antiguos o forzar un reinicio manual, el Kompressor **resume** la mitad más antigua de la conversación mediante una segunda llamada LLM dedicada. Este resumen se inyecta en el prompt del sistema de todas las solicitudes posteriores. El modelo activo efectivamente "recuerda" el pasado resumido — la conversación puede continuar indefinidamente.

#### Umbrales de Activación

| Umbral | Acción |
|--------|--------|
| **70%** de utilización del contexto | Primera ronda de compresión |
| **85%** de utilización del contexto | Segunda ronda de compresión |
| **95%** de utilización del contexto | Tercera ronda de compresión |

Cada umbral se activa como máximo una vez por ciclo de sesión. Después de la eliminación manual de mensajes, si el porcentaje de contexto cae por debajo del último umbral activado, todo el seguimiento de umbrales se reinicia.

#### Proceso de Compresión (Paso a Paso)

1. Después de cada mensaje enviado, `updateContextEstimation()` recalcula la utilización del contexto.
2. Si se supera un umbral, se llama a `compress-context.py` **antes** de la llamada principal a la API.
3. Se extraen el 50% más antiguo de los mensajes. El corte avanza al siguiente mensaje del usuario — asegurando compatibilidad de API (el contexto siempre debe comenzar con un turno del usuario).
4. Los datos base64, imágenes y contenido multimedia se filtran — solo se envía texto plano al LLM de compresión.
5. El LLM de compresión (proveedor y modelo configurables) devuelve un resumen estructurado.
6. Los mensajes antiguos se reemplazan por una única entrada comprimida (flag `compressed: true`).
7. El texto del resumen se antepone al prompt del sistema para todas las llamadas de API posteriores — nunca se envía como mensaje `assistant` independiente (lo que causaría errores 400).
8. El contexto comprimido se guarda en disco. La llamada principal a la API procede con el contexto reducido.

#### Descarte Inteligente del Resumen

Cuando el usuario elimina mensajes manualmente y el porcentaje de contexto cae por debajo del **último umbral activado** (no simplemente por debajo del 70%), el resumen de compresión se elimina automáticamente del prompt del sistema y todos los contadores de umbrales se reinician. Esto asegura que el estado de compresión siempre coincida con el contenido real de la conversación.

#### Restricción de Proveedor (Solo de Pago)

El Kompressor hace una llamada LLM separada que puede involucrar grandes cantidades de tokens. Los límites de tasa del tier gratuito (Groq: 6.000–12.000 TPM; Hugging Face: variable) son insuficientes para la compresión fiable de conversaciones del mundo real. Solo se ofrecen proveedores de pago:

| Proveedor | Modelos de Compresión Disponibles |
|-----------|----------------------------------|
| DeepSeek | `deepseek-v4-flash`, `deepseek-v4-pro` |
| OpenAI | `gpt-4o-mini`, `gpt-5.6-luna`, `gpt-4o`, `gpt-4.1` |
| Google | `gemini-2.5-flash`, `gemini-2.5-pro` |

**Predeterminado recomendado**: DeepSeek + `deepseek-v4-flash` — sin límites de tasa, menor costo por token, resultados más fiables.

#### Archivos de Resultados

Cada ronda de compresión se guarda en disco para revisión:
```
/var/www/deepseek-chat/kompressor/kompressor_YYYYMMDD_HHMMSS.txt
```

### Banners de Cuota y Límite

**Banner Rojo — "¡El crédito debe renovarse!"** (proveedores de pago):
- Activado por crédito agotado en una API de pago.
- **DeepSeek**: Respuesta HTTP 402.
- **OpenAI**: HTTP 429 + `insufficient_quota` en el cuerpo de respuesta JSON.
- Se muestra como un elemento de posición fija en la parte superior del viewport hasta que se cierra manualmente (botón ×).

**Banner Azul — "¡Límite diario alcanzado!"** (proveedores de tier gratuito):
- Activado por cuota diaria agotada en una API gratuita.
- **Google Gemini**: HTTP 429 + palabras clave de cuota diaria en el cuerpo de respuesta.
- **GroqCloud**: HTTP 429.
- **Hugging Face**: HTTP 429.
- Misma visualización de posición fija con botón de cierre ×.

### Manejo de Ventana de Contexto Superada

Cuando la API devuelve HTTP 400 con palabras clave relacionadas con el contexto en el cuerpo de respuesta, aparece un **cuadro interactivo** directamente en el chat en lugar de un mensaje de error genérico:

- **Cuadro con borde azul**: *"Se ha alcanzado el tamaño máximo del chat del LLM actual."*
- **Botón verde — "Iniciar nuevo chat con el contexto actual"** (Opción C):
  1. La sesión actual se guarda automáticamente.
  2. El último resumen de compresión (si está disponible) se combina con todos los mensajes no comprimidos posteriores como texto plano.
  3. Una nueva sesión comienza con este contexto combinado precargado como archivo adjunto — la conversación continúa sin problemas con transferencia completa del contexto.
- **Botón azul — "Iniciar nuevo chat sin contexto"** (reinicio limpio):
  1. La sesión actual se guarda automáticamente.
  2. La nueva sesión comienza con un contexto vacío.

Esto permite **conversaciones encadenadas** a través de múltiples sesiones — teóricamente ilimitadas en longitud total.

Los cinco scripts proxy CGI detectan el desbordamiento de contexto verificando el código de estado HTTP y haciendo coincidencia de palabras clave en el cuerpo de error de la API, devolviendo `error_type: 'context_exceeded'` al cliente.

### Cabeceras de Documentación de Proxy API

Cada uno de los cinco scripts proxy CGI (`openai-api.py`, `deepseek-api.py`, `google-api.py`, `hugging-api.py`, `groq-api.py`) contiene un bloque de documentación estructurado directamente después de la declaración de codificación:

- **Fecha de importación/actualización** — cuándo se actualizó el archivo por última vez
- **Modelos soportados** — versión, límites de tokens de contexto/salida, capacidades (texto/imágenes/audio/video), asignación gratuito/de pago
- **Enlace de fuente** — URL de documentación oficial de la API con fecha

Esto asegura que todas las especificaciones de modelos sean trazables directamente en el código fuente sin consultar documentación externa.

---

## Migración a DeepSeek V4

### Contexto

El **24 de abril de 2026**, DeepSeek lanzó el **DeepSeek V4 Preview** — una nueva generación de modelos de lenguaje MoE (Mixture-of-Experts) con capacidades dramáticamente expandidas. Los dos nuevos modelos reemplazan a `deepseek-chat` (V3) y `deepseek-reasoner` (R1).

### Nuevos Modelos

| Modelo | Parámetros | Activos | Contexto | Máx. Salida | Modo Thinking |
|--------|-----------|---------|---------|------------|--------------|
| `deepseek-v4-flash` | 284B total | 13B | 1.048.576 tokens | 8.192 tokens | Sí (Thinking + Non-Thinking) |
| `deepseek-v4-pro` | 1,6T total | 49B | 1.048.576 tokens | 32.768 tokens | Sí (Thinking + Non-Thinking) |

### Mejoras de Arquitectura (V4 vs. V3)

- **Atención Híbrida**: V4 combina Compressed Sparse Attention (CSA) y Heavily Compressed Attention (HCA) — habilitando contexto de 1M tokens con solo el 27% de los FLOPs de inferencia de token único de V3.2 y solo el 10% del caché KV.
- **Hyper-Connections con Restricción de Variedad (mHC)**: Fortalece las conexiones residuales para una propagación de señal más estable a través de las capas.
- **Tres modos de esfuerzo de razonamiento**: Non-think (rápido), Think High (análisis lógico), Think Max (alcance de razonamiento completo) — accesibles mediante parámetros de API.

### Cronograma de Obsolescencia

| Fecha | Evento |
|-------|--------|
| 24 de abril de 2026 | Lanzamiento de V4 Preview. `deepseek-chat` y `deepseek-reasoner` comienzan a enrutar a `deepseek-v4-flash`. |
| **24 de julio de 2026** | **`deepseek-chat` y `deepseek-reasoner` completamente retirados e inaccesibles.** |

### Cambios Realizados en Este Proyecto (11 de mayo de 2026)

**`index.html`**:
- `MODEL_CONFIG`: `deepseek-chat` (100k tokens) → `deepseek-v4-flash` (1.048.576 tokens); `deepseek-reasoner` (65k tokens) → `deepseek-v4-pro` (1.048.576 tokens)
- `MODEL_CAPABILITIES`: actualizado a `deepseek-v4-flash` y `deepseek-v4-pro`
- `DEEPSEEK_MODELS`, `COMPRESSOR_MODELS.deepseek`: actualizados a nombres V4
- Dropdowns de modelos (selección de modelo + selección de modelo del compresor): opciones V4
- Lógica DeepThink (8 ocurrencias): ambos modos leen `settings.selectedModel` (con respaldo a `deepseek-v4-flash`) — ver la actualización del 19 de julio de 2026 más abajo sobre un error en esta lógica que ya se corrigió
- Configuración predeterminada: `selectedModel` y `compressorModel` por defecto a `deepseek-v4-flash`
- Manejador de errores del frontend corregido: el consumo del cuerpo de `response.json()` ya no causa mensajes de error vacíos

**`deepseek-api.py`**:
- Comentario de cabecera actualizado a modelos V4 con tamaños correctos de contexto/salida
- Fallback predeterminado de modelo: `'deepseek-chat'` → `'deepseek-v4-flash'`
- Aviso de obsolescencia añadido a la cabecera

**`deepseek-models.py`**: Sin cambios necesarios — obtiene la lista de modelos en tiempo real de la API de DeepSeek. Ya devuelve correctamente `deepseek-v4-flash` y `deepseek-v4-pro`.

### Compatibilidad de API

La API de DeepSeek V4 usa la misma URL base y el mismo formato compatible con OpenAI que V3. No se requirieron cambios estructurales en `deepseek-api.py` — solo los nombres de modelo necesitaban actualizarse.

---

## Actualización de Mantenimiento y Funciones del 19 de Julio de 2026

Una sesión de mantenimiento y funciones de día completo que cubrió un error crítico de selección de modelo, varias inconsistencias acumuladas en documentación/listas de modelos en los cinco proveedores, y la finalización de una pipeline de visión (imágenes) previamente no funcional. Documentado en las entradas 87–89 del changelog.

### 1. Error Crítico: `deepseek-v4-pro` Nunca Era Alcanzable

**Síntoma**: Seleccionar `deepseek-v4-pro` en el dropdown de modelos no tenía efecto — cada solicitud, sin importar la selección del dropdown o el modo DeepThink, se enviaba usando `deepseek-v4-flash`.

**Causa raíz**: Ocho ocurrencias del mismo error de copiar-pegar distribuidas en `index.html`, cada una resolviendo a:
```javascript
(currentMode === 'deepthink') ? 'deepseek-v4-flash' : 'deepseek-v4-flash'
```
Ambas ramas del operador ternario devolvían la misma cadena, lo que significaba que `settings.selectedModel` nunca se consultaba para el proveedor DeepSeek — a diferencia de cualquier otro proveedor (Google, OpenAI, Groq, Hugging Face), que correctamente usaban `settings.selectedModel || <respaldo>`.

**Corrección**: Las ocho ocurrencias (distribuidas en `sendMessage()`, `handleRegenerate()`, las funciones de estimación de contexto/tokens, y las actualizaciones de indicadores de la UI) ahora leen `settings.selectedModel || 'deepseek-v4-flash'`, consistente con el patrón usado en el resto del código.

**Corrección relacionada — cabecera de contexto desactualizada**: `llmSaveHandler` (el botón "Apply Settings" en el panel de Configuración LLM) ahora llama explícitamente a `updateContextDisplay()` como acción final, garantizando que la cabecera `Context: X% (modelo)` refleje inmediatamente la selección de modelo recién guardada en lugar de solo en el siguiente recálculo de contexto.

**Corrección relacionada — cabecera de modelo engañosa**: La cabecera `Modelo: ...` mostraba anteriormente, solo para DeepSeek, la lista *completa* de modelos reportados por `deepseek-models.py` (p. ej. `Modelo: deepseek-v4-flash, deepseek-v4-pro`) sin importar cuál modelo estuviera realmente seleccionado — inconsistente con cualquier otro proveedor, que correctamente mostraba solo el modelo activo. `updateApiServiceUI()`, la rutina general de actualización de UI, y `fetchDeepSeekModels()` se corrigieron para mostrar `settings.selectedModel` de forma uniforme en todos los proveedores.

### 2. Registro de Diagnóstico: Nombre del Modelo en el Log del Servidor

Las funciones `log_to_file()` y `send_error()` de `deepseek-api.py` ganaron un parámetro opcional `model`. Cada línea de log ahora incluye `| Model: <nombre>` desde el punto en que se ha analizado el cuerpo de la solicitud en adelante — tanto para solicitudes exitosas como para respuestas de error — permitiendo la verificación en el servidor de qué modelo realmente recibió una solicitud dada, independientemente de (y más fiable que) el estado de la UI del cliente o la autodeclaración de identidad del propio modelo (ver [Auto-Informe del Modelo DeepSeek](#auto-informe-del-modelo-deepseek)).

### 3. Limpieza de Modelos Obsoletos

Varios modelos referenciados en comentarios de código y listas de selección ya no eran alcanzables:

| Proveedor | Modelo eliminado | Motivo |
|-----------|-------------------|--------|
| Google | `gemini-2.0-flash` | Cerrado el 1 de junio de 2026; también era el modelo de respaldo por defecto del script CGI |
| Google | `gemini-1.5-pro` | Retirado antes de esta limpieza |
| Hugging Face | `mistralai/Mixtral-8x7B-Instruct-v0.1` | Ya no está desplegado por ningún Inference Provider en el router de HF |
| GroqCloud (solo doc.) | `mixtral-8x7b-32768` | Deprecado por Groq desde el 20 de marzo de 2025 (la documentación estaba desactualizada; los arrays de modelos en vivo ya eran correctos) |
| GroqCloud (solo doc.) | `gemma2-9b-it` | Deprecado por Groq desde el 8 de octubre de 2025 (solo documentación) |
| OpenAI | `gpt-5-mini`, `gpt-5.2-chat-latest` | Ya no están en la lista actual de modelos/precios de OpenAI (reemplazados por la familia GPT-5.4/5.5/5.6) |

Eliminados de `GOOGLE_MODELS_PAID`, `HF_MODELS_PAID`, `OPENAI_MODELS_FREE`/`PAID`, `MODEL_CONFIG`, `MODEL_CAPABILITIES`, `AUDIO_CAPABLE_MODELS` y `COMPRESSOR_MODELS`, según corresponda. El modelo de respaldo por defecto de `google-api.py` se cambió de `gemini-2.0-flash` a `gemini-2.5-flash`. También se limpió una entrada huérfana en `MODEL_CONFIG` para el modelo Mixtral eliminado (presente aunque ya había sido eliminado de todas las listas de selección).

Adicionalmente, a `MODEL_CONFIG` le faltaba por completo una entrada para `moonshotai/kimi-k2-instruct-0905` a pesar de estar listado en `GROQ_MODELS_PAID` — recurría silenciosamente al límite de tokens de salida de DeepSeek. Se añadió una entrada correcta (131.072 de contexto / 8.192 de salida).

### 4. Lineup de OpenAI Actualizado a GPT-5.5 / GPT-5.6

OpenAI lanzó **GPT-5.5** (23 de abril de 2026) y la **familia GPT-5.6 — Sol, Terra, Luna** (9 de julio de 2026, la generación insignia actual) desde que la configuración de modelos de este proyecto se actualizó por última vez (10 de marzo de 2026). Ver [Integración con OpenAI](#integración-con-openai) para las listas de modelos actualizadas.

Un segundo problema, descubierto de forma independiente: `MODEL_CONFIG` no tenía **ninguna entrada para ningún modelo de OpenAI** antes de esta actualización. Cada solicitud a OpenAI — sin importar qué modelo estuviera seleccionado — usaba silenciosamente los límites de DeepSeek Flash (8.192 tokens de salida máximos), perjudicando a modelos como `gpt-4.1` (32.768 de salida máxima real) o la familia GPT-5.6 (128.000 de salida máxima real). Se añadieron ocho entradas correctas, con valores de contexto/salida obtenidos de la documentación actual de la API de OpenAI.

### 5. Mensajes de Error de API Transparentes

**Síntoma**: Los errores de API de DeepSeek, OpenAI, Groq y Hugging Face se mostraban como un escueto `Error: API error (400):` sin más detalles, haciendo imposible el diagnóstico solo desde la UI.

**Causa raíz**: En tres ramas separadas de manejo de errores dentro de `sendMessage()`, la respuesta de error del backend ya analizada (`errData`) se descartaba una vez verificada contra los dos tipos de error conocidos específicos (`insufficient_quota`, `context_exceeded`). Si el error real no era ninguno de esos — p. ej. un parámetro no reconocido, como se encontró en el punto 6 más abajo —, el mensaje de error lanzado estaba fijado a una cadena vacía.

**Corrección**: Las tres ramas ahora extraen `errData.details || errData.error || errData.message` y lo pasan al mensaje de error mostrado, revelando el texto de diagnóstico real proporcionado por el proveedor.

### 6. `max_tokens` → `max_completion_tokens` para OpenAI

Descubierto como consecuencia directa de la corrección 5 anterior: una vez que el texto de error real se volvió visible, la primera prueba en vivo con `gpt-5.6-luna` devolvió:
```
Unsupported parameter: 'max_tokens' is not supported with this model. Use 'max_completion_tokens' instead.
```
Los modelos de generación actual de OpenAI (la serie GPT-5.x y los modelos con capacidad de razonamiento en general) rechazan el parámetro `max_tokens` en la API de Chat Completions. `openai-api.py` ahora envía `max_completion_tokens` en su lugar — un parámetro aceptado tanto por los modelos heredados (GPT-4o, GPT-4.1) como por el lineup GPT-5.x actual, lo que permite usarlo incondicionalmente en lugar de bifurcar por modelo. Verificado en vivo tanto con `gpt-5.6-luna` como con `gpt-4o-mini`.

### 7. Pipeline de Visión Completada

Ver la sección dedicada [Soporte de Imágenes (Visión)](#soporte-de-imágenes-visión) arriba para la descripción completa. En resumen: `MODEL_CAPABILITIES` se pobló correctamente por proveedor (anteriormente solo DeepSeek tenía entradas, todas `images: false`), `currentModelSupportsImages()` se corrigió para verificar el modelo realmente seleccionado en lugar de un array independiente relevante solo para DeepSeek, y la conexión cliente/servidor para transmitir realmente bytes de imagen a Google Gemini y OpenAI se implementó por primera vez — las imágenes eran anteriormente aceptadas por la UI pero nunca llegaban a ningún modelo.

### 8. `deploy.sh`: Verificación de Suma de Comprobación MD5

`deploy.sh` ahora imprime la suma de comprobación MD5 de cada archivo que copia al directorio de producción, inmediatamente después de los pasos de copia/chown/chmod y antes del reinicio de Apache:
```
=== MD5-Summen der kopierten Dateien (Produktion) ===
4a08bef03d8543cc3e1cbacf1a10bc96  /var/www/deepseek-chat/index.html
42abf2af226184edf979b3721aff0e1c  /var/www/deepseek-chat/cgi-bin/openai-api.py
...
```
Esto elimina la necesidad de un paso manual separado de `md5sum` después de cada despliegue para confirmar que el archivo de producción coincide con el commit deseado — un paso que ya había detectado un problema de despliegue obsoleto durante esta misma sesión (una invocación de `deploy.sh` en producción estaba ejecutando una copia en caché desactualizada de sí misma, ya que el script no se despliega a sí mismo; ver la nota en [Scripts de Despliegue](#scripts-de-despliegue)).

### Archivos Modificados

`index.html`, `deepseek-api.py`, `google-api.py`, `groq-api.py`, `hugging-api.py`, `openai-api.py`, `shell-scripts/deploy.sh`

---

## El Script Auxiliar `repo2text.sh`

Este script Bash fue desarrollado específicamente para **exportar todo el código fuente de un repositorio de GitHub como un único archivo de texto** — ideal para pasar el contexto completo del proyecto a un asistente de IA en una única subida.

**Cómo funciona**:
- Clona el repositorio con `git clone --depth 1`.
- Analiza todos los archivos de texto (verificación de tipo MIME + `grep -Iq .`) y los escribe secuencialmente con delimitadores únicos en un archivo de salida.
- Usa `sort -z -u` para deduplicar rutas de archivo antes del procesamiento — previene entradas de archivo duplicadas en la salida.
- Usa un formato de delimitador único (`############ FILE: ruta/al/archivo ############`) que no puede aparecer en el código fuente.
- Respeta explícitamente `.gitignore` y `.gitattributes`.
- Soporta formatos de salida TXT, JSON y Markdown.
- Crea un archivo ZIP del archivo de exportación.
- Incluye metadatos: hash de commit, rama, marca de tiempo de exportación.

**Opciones especiales**:
- `--flat`: Usar solo nombres de archivo sin rutas de directorio.
- `-o, --only RUTA`: Exportar solo un subdirectorio específico.
- `-md5, --md5`: Calcular e incluir suma de comprobación MD5 para cada archivo.
- Detección inteligente de URL remota cuando se ejecuta dentro de un repositorio Git existente.
- Tanto `md5sum` (Linux) como `md5` (macOS) son soportados.

**Ejemplos de uso**:

```bash
# Exportación simple (prompt interactivo de URL)
./repo2text.sh

# Exportación con URL en formato Markdown
./repo2text.sh -f md https://github.com/debian-professional/multi-llm-chat.git

# Exportar solo el directorio 'shell-scripts' con estructura plana
./repo2text.sh --flat -o shell-scripts https://github.com/debian-professional/multi-llm-chat.git

# Exportación con sumas de comprobación MD5
./repo2text.sh -md5 https://github.com/debian-professional/multi-llm-chat.git
```

> `repo2text` también está disponible como proyecto independiente: [github.com/debian-professional/repo2text](https://github.com/debian-professional/repo2text)

---

## Arquitectura de Seguridad en Detalle

La seguridad fue una prioridad principal durante todo el desarrollo. Todas las medidas clave:

### 1. Claves API — Nunca Expuestas al Cliente

- Todas las claves API se mantienen exclusivamente en variables de entorno de Apache (`/etc/apache2/envvars`).
- Cada script CGI recupera su clave mediante `os.environ.get('..._API_KEY')`.
- El cliente se comunica solo con proxies CGI locales — nunca directamente con APIs externas.
- Incluso un compromiso XSS completo de la página no puede filtrar las claves API.

### 2. Inspección de Bytes Mágicos

- Los primeros 20 bytes de cada archivo subido se comprueban contra una base de datos de firmas completa que cubre 12 formatos ejecutables en 4 plataformas.
- Si hay coincidencia de firma, la subida se bloquea antes de que se lea cualquier contenido — con un mensaje de error detallado que muestra la plataforma y el formato detectados.
- La protección funciona incluso si los archivos maliciosos son renombrados (p.ej. `malware.exe` → `documento.pdf`).

### 3. Almacenamiento Seguro de Sesiones

- Directorio de sesiones: `/var/www/deepseek-chat/sessions/` — `chmod 700`, propietario `www-data`.
- Cada archivo de sesión: `chmod 600`.
- Los IDs de sesión se validan en el servidor mediante regex antes de cualquier E/S de archivo — sin posibilidad de path traversal.

### 4. Log sin Datos Sensibles

- Registrado: marcas de tiempo, direcciones IP, métodos HTTP, rutas de endpoints, códigos de estado, mensajes de error.
- **Nunca registrado**: claves API, contenido completo de sesiones, texto de mensajes (solo vistas previas de feedback de 60 caracteres).
- Las solicitudes de preflight OPTIONS se filtran para prevenir inundación del log.

### 5. Sin Comunicación Directa Cliente-API

- Todas las operaciones de seguridad crítica son CGI de Python del lado del servidor.
- El cliente tiene cero conocimiento de credenciales de API, rutas del servidor o ubicaciones de almacenamiento de sesiones.

### 6. Validación de Entrada

- Archivos validados por lista de extensiones permitidas E inspección de bytes mágicos.
- IDs de sesión validados contra regex de formato esperado en el servidor.
- El pegado del portapapeles se filtra para bloquear rutas de archivo antes de que lleguen a la API.
- `Content-Length` validado antes de leer cuerpos POST en scripts CGI.

### 7. Seguridad de Transporte

- HTTPS forzado mediante `deepseek-chat-ssl.conf` con Apache mod_ssl.
- La configuración HTTP simple (`deepseek-chat.conf`) desactivada mediante `a2dissite`.

---

## Despliegue y Uso

### Requisitos Previos

- Linux basado en Debian (o cualquier Linux con Apache 2.4, Python 3.9+, Bash)
- Módulos Apache: `mod_cgi`, `mod_ssl`
- Paquetes Python: `reportlab` (para exportación PDF)
- Para `repo2text.sh`: `jq`, `pv`, `zip`, `git`
- Clave API válida para al menos un proveedor soportado

### Instalación

**1. Clonar el repositorio** (como usuario `source`):
```bash
git clone https://github.com/debian-professional/multi-llm-chat.git /home/source/multi-llm-chat
```

**2. Configurar claves API** en `/etc/apache2/envvars`:
```bash
export DEEPSEEK_API_KEY="sk-..."
export OPENAI_API_KEY="sk-proj-..."
export GOOGLE_API_KEY="AIza..."
export HF_API_KEY="hf_..."
export GRQ_API_KEY="gsk_..."
```

**3. Habilitar configuración de Apache**:
```bash
a2ensite deepseek-chat-ssl.conf
a2dissite deepseek-chat.conf
systemctl restart apache2
```

**4. Crear directorios requeridos**:
```bash
mkdir -p /var/www/deepseek-chat/sessions
chown www-data:www-data /var/www/deepseek-chat/sessions
chmod 700 /var/www/deepseek-chat/sessions
```

**5. Desplegar** (como root):
```bash
./deploy.sh source
```

**6. Instalar scripts auxiliares**:
```bash
./install.sh   # copia deploy.sh y sync-back.sh al directorio de producción
```

### Configuración

**Configuración de modelos** (`MODEL_CONFIG` en `index.html`) — única fuente de verdad para todos los límites de modelos, a partir del 19.07.2026:
```javascript
const MODEL_CONFIG = {
    // DeepSeek V4
    'deepseek-v4-flash':    { maxContextTokens: 1048576, maxOutputTokens: 8192,   maxContextMessages: 50  },
    'deepseek-v4-pro':      { maxContextTokens: 1048576, maxOutputTokens: 32768,  maxContextMessages: 50  },
    // Google Gemini
    'gemini-2.5-flash':     { maxContextTokens: 1048576, maxOutputTokens: 8192,   maxContextMessages: 100 },
    'gemini-2.5-pro':       { maxContextTokens: 1048576, maxOutputTokens: 65536,  maxContextMessages: 100 },
    // Hugging Face
    'Qwen/Qwen2.5-72B-Instruct':               { maxContextTokens: 128000, maxOutputTokens: 8192, maxContextMessages: 80 },
    'mistralai/Mistral-7B-Instruct-v0.3':      { maxContextTokens: 32768,  maxOutputTokens: 4096, maxContextMessages: 40 },
    'microsoft/Phi-3.5-mini-instruct':         { maxContextTokens: 128000, maxOutputTokens: 4096, maxContextMessages: 60 },
    'meta-llama/Meta-Llama-3.1-70B-Instruct':  { maxContextTokens: 128000, maxOutputTokens: 8192, maxContextMessages: 80 },
    'meta-llama/Meta-Llama-3.1-405B-Instruct': { maxContextTokens: 128000, maxOutputTokens: 8192, maxContextMessages: 80 },
    // GroqCloud
    'llama-3.3-70b-versatile':                   { maxContextTokens: 128000, maxOutputTokens: 8192,  maxContextMessages: 80 },
    'llama-3.1-8b-instant':                      { maxContextTokens: 131072, maxOutputTokens: 8192,  maxContextMessages: 80 },
    'meta-llama/llama-4-scout-17b-16e-instruct': { maxContextTokens: 131072, maxOutputTokens: 8192,  maxContextMessages: 80 },
    'qwen/qwen3-32b':                            { maxContextTokens: 131072, maxOutputTokens: 40960, maxContextMessages: 80 },
    'moonshotai/kimi-k2-instruct-0905':          { maxContextTokens: 131072, maxOutputTokens: 8192,  maxContextMessages: 80 },
    // OpenAI (añadido el 19.07.2026 — antes ausente por completo, recurría silenciosamente a los límites de DeepSeek Flash)
    'gpt-4o-mini':    { maxContextTokens: 128000,  maxOutputTokens: 16384,  maxContextMessages: 80  },
    'gpt-4o':         { maxContextTokens: 128000,  maxOutputTokens: 16384,  maxContextMessages: 80  },
    'gpt-4.1':        { maxContextTokens: 1048576, maxOutputTokens: 32768,  maxContextMessages: 100 },
    'gpt-5.4':        { maxContextTokens: 1048576, maxOutputTokens: 16384,  maxContextMessages: 100 },
    'gpt-5.5':        { maxContextTokens: 1048576, maxOutputTokens: 128000, maxContextMessages: 100 },
    'gpt-5.6-sol':    { maxContextTokens: 1048576, maxOutputTokens: 128000, maxContextMessages: 100 },
    'gpt-5.6-terra':  { maxContextTokens: 1048576, maxOutputTokens: 128000, maxContextMessages: 100 },
    'gpt-5.6-luna':   { maxContextTokens: 1048576, maxOutputTokens: 128000, maxContextMessages: 100 },
};
const DEEPSEEK_MODELS    = ['deepseek-v4-flash', 'deepseek-v4-pro'];
const OPENAI_MODELS_FREE = ['gpt-4o-mini', 'gpt-5.6-luna'];
const OPENAI_MODELS_PAID = ['gpt-5.6-sol', 'gpt-5.6-terra', 'gpt-5.6-luna', 'gpt-5.5', 'gpt-5.4', 'gpt-4o', 'gpt-4.1', 'gpt-4o-mini'];
const GOOGLE_MODELS_FREE = ['gemini-2.5-flash'];
const GOOGLE_MODELS_PAID = ['gemini-2.5-flash', 'gemini-2.5-pro'];
const HF_MODELS_FREE     = ['Qwen/Qwen2.5-72B-Instruct', 'mistralai/Mistral-7B-Instruct-v0.3', 'microsoft/Phi-3.5-mini-instruct'];
const HF_MODELS_PAID     = ['meta-llama/Meta-Llama-3.1-70B-Instruct', 'meta-llama/Meta-Llama-3.1-405B-Instruct', 'Qwen/Qwen2.5-72B-Instruct'];
const GROQ_MODELS_FREE   = ['llama-3.3-70b-versatile', 'llama-3.1-8b-instant', 'meta-llama/llama-4-scout-17b-16e-instruct', 'qwen/qwen3-32b'];
const GROQ_MODELS_PAID   = ['llama-3.3-70b-versatile', 'llama-3.1-8b-instant', 'meta-llama/llama-4-scout-17b-16e-instruct', 'qwen/qwen3-32b', 'moonshotai/kimi-k2-instruct-0905'];
const AUDIO_CAPABLE_MODELS = ['gemini-2.5-flash', 'gemini-2.5-pro', 'gpt-4o', 'gpt-4.1'];
```

**Configuración de idioma** (`language.xml`): Añadir un bloque `<language id="custom" name="..." visible="true">` para activar el slot de idioma personalizado. Establecer `has_address_form="true"` para idiomas con distinción formal/informal.

### Scripts de Despliegue

| Script | Función |
|--------|---------|
| `deploy.sh <user>` | Copia archivos desde `/home/<user>/multi-llm-chat/var/www/deepseek-chat/` a `/var/www/deepseek-chat/`, establece propietario y permisos, imprime sumas de comprobación MD5 de cada archivo copiado, recarga Apache |
| `sync-back.sh <user>` | Copia archivos modificados desde producción de vuelta al repositorio fuente |
| `install.sh` | Instala `deploy.sh` y `sync-back.sh` en el directorio de producción |
| `tag-release.sh` | Crea un tag Git con número de versión auto-incrementado y lo envía. Ejecuta primero `git fetch --tags` para evitar conflictos con tags remotos existentes. |

**Importante — `deploy.sh` no se despliega a sí mismo.** La propia lista `cp` del script cubre `index.html`, `manifest`, `files-directorys`, `cgi-bin/*.py` y `language.xml` — nunca se copia a sí mismo. Tras modificar `deploy.sh` en el repositorio fuente y ejecutar `git pull` en el servidor, la copia de producción en `/var/www/deepseek-chat/deploy.sh` sigue siendo la versión **antigua** hasta que se copia manualmente:
```bash
cp ~/multi-llm-chat/shell-scripts/deploy.sh /var/www/deepseek-chat/deploy.sh
chmod +x /var/www/deepseek-chat/deploy.sh
```
Esto causó un tropiezo real durante la sesión del 19 de julio de 2026 — `sudo deploy.sh` seguía produciendo la salida anterior a la extensión de suma MD5 incluso después de un `git pull` exitoso, porque el script invocado seguía siendo la copia de producción desactualizada.

---

## Estructura del Proyecto

```
/
├── etc/apache2/sites-available/
│   ├── deepseek-chat.conf              (desactivado — solo HTTP, redirige a HTTPS)
│   └── deepseek-chat-ssl.conf          (activo — SSL, CGI, claves API vía envvars)
├── shell-scripts/
│   ├── repo2text.sh                    Exportar repositorio completo como archivo de texto
│   ├── deploy.sh                       Copia repositorio fuente → producción
│   ├── sync-back.sh                    Copia producción → repositorio fuente
│   ├── install.sh                      Instala scripts deploy/sync-back
│   └── tag-release.sh                  Crea y envía tags de versión Git
├── var/www/deepseek-chat/
│   ├── index.html                      Aplicación principal (~5.000 líneas, todo JS/CSS/HTML)
│   ├── language.xml                    Todos los textos UI en todos los idiomas (EN, DE, ES, Personalizado)
│   ├── manifest                        Manifiesto de diseño (todas las convenciones y reglas)
│   ├── changelog                       Historial completo de desarrollo (89 entradas)
│   ├── files-directorys                Vista general de archivos / listado de directorio
│   ├── cgi-bin/
│   │   ├── openai-api.py              Proxy de streaming a OpenAI Chat Completions API
│   │   ├── deepseek-api.py            Proxy de streaming a DeepSeek Chat Completions API
│   │   ├── google-api.py              Proxy de streaming a Google Gemini API (con conversión de formato)
│   │   ├── hugging-api.py             Proxy de streaming al Router de Inferencia de Hugging Face
│   │   ├── groq-api.py                Proxy de streaming a GroqCloud API (acelerado por LPU)
│   │   ├── compress-context.py        Compresión de contexto mediante segunda llamada LLM
│   │   ├── deepseek-models.py         Lista de modelos en tiempo real desde DeepSeek /v1/models
│   │   ├── save-session.py            Endpoint de guardado de sesión (POST)
│   │   ├── load-session.py            Endpoint de lista (GET) / carga de sesión (POST)
│   │   ├── delete-session.py          Endpoint de eliminación de sesión (POST)
│   │   ├── export-pdf.py              Exportación PDF vía ReportLab
│   │   ├── export-markdown.py         Exportación Markdown
│   │   ├── export-txt.py              Exportación de texto plano
│   │   ├── export-rtf.py              Exportación RTF (codificación manual, sin biblioteca externa)
│   │   ├── feedback-log.py            Registro de feedback Like/Dislike
│   │   └── get-log.py                 Lector del log del servidor
│   ├── logs/                          Archivos de log del servidor (creados automáticamente por Apache/www-data)
│   ├── kompressor/                    Archivos de resultados de compresión (creados automáticamente)
│   └── sessions/                      Archivos JSON de sesiones de chat (creados automáticamente, chmod 700)
```

---

## Configuración de Modelos

El objeto `MODEL_CONFIG` en `index.html` es la **única fuente de verdad** para todos los límites específicos de modelos en los cinco proveedores. Todas las características que dependen de los límites de modelos — visualización de utilización del contexto, límites de subida dinámicos, detección de desbordamiento de contexto, umbrales del Kompressor — leen de este único objeto. Un modelo ausente en `MODEL_CONFIG` recurre silenciosamente a los límites de DeepSeek Flash en lugar de fallar de forma visible — esto afectó a todos los modelos de OpenAI hasta que se corrigió el 19 de julio de 2026 (ver [Actualización de Mantenimiento y Funciones del 19 de Julio de 2026](#actualización-de-mantenimiento-y-funciones-del-19-de-julio-de-2026)), por lo que cualquier modelo recién añadido debería verificarse explícitamente contra esta tabla en lugar de asumir que funciona.

**Actualizar la configuración de modelos**: Cuando un proveedor actualiza sus modelos (nuevo modelo, límites de contexto modificados, modelo obsoleto), solo se necesita actualizar el bloque `MODEL_CONFIG` en `index.html`. Ningún otro archivo requiere cambios a menos que el nombre del modelo también se use en las listas de modelos del proveedor (`DEEPSEEK_MODELS`, `GOOGLE_MODELS_*`, etc.), en `MODEL_CAPABILITIES` o en `AUDIO_CAPABLE_MODELS`.

Fuentes: [OpenAI API Docs](https://platform.openai.com/docs), [DeepSeek API Docs](https://api-docs.deepseek.com), [Google Gemini Docs](https://ai.google.dev/gemini-api/docs), [Hugging Face Inference Providers](https://huggingface.co/docs/inference-providers), [GroqCloud Docs](https://console.groq.com/docs/models) *(a partir del 19.07.2026)*.

---

## Manifiesto de Diseño

El proyecto incluye un archivo `manifest` que documenta todas las decisiones de diseño, convenciones de nomenclatura y reglas de desarrollo. Reglas clave:

- **Todos los botones**: Exclusivamente pill-style (border-radius: 20px, altura: 36px). Los botones cuadrados están prohibidos.
- **Colores de botones**: Azul (`#0056b3`) para acciones, toggle oscuro-a-azul para modos, rojo (`#dc3545`) para operaciones destructivas, verde (`#28a745`) para constructivas.
- **Configuración**: Solo interruptores toggle — sin botones de radio, sin casillas de verificación en ningún lugar.
- **Sin emojis** en botones o etiquetas (excepción: el icono DeepThink ✦).
- **Sin PHP** — exclusivamente JavaScript (cliente) y Python 3 (servidor).
- **Sin frameworks JavaScript externos** — sin Node.js, sin React, sin Vue, sin jQuery.
- **Preservación de formato**: La indentación y el formato existentes en `index.html` nunca deben cambiarse mediante herramientas automatizadas.
- **`AUDIO_CAPABLE_MODELS` debe mantenerse actualizado** (Regla de Manifiesto E.1): Siempre que un modelo gane o pierda soporte de audio, la constante debe actualizarse inmediatamente.
- **Banners de proveedor requeridos** (Regla de Manifiesto E.1): Al añadir un nuevo proveedor LLM, el banner apropiado de cuota/límite debe implementarse tanto en el script CGI como en el cliente.
- El manifiesto es un **archivo separado** y nunca debe incrustarse en `index.html`.

---

## Limitaciones Conocidas y Notas Técnicas

### "Lost in the Middle" — Una Limitación Conocida de IA

Todos los modelos de lenguaje actuales tienden a recordar de forma fiable el contenido al **principio y al final** de un contexto largo, mientras que el contenido **en el medio** a veces se pasa por alto o se alucina. (Liu et al., 2023: *"Lost in the Middle: How Language Models Use Long Contexts"*)

**Impacto práctico**:
- Un export del repositorio de este proyecto es aproximadamente 700.000 caracteres ≈ ~175.000 tokens.
- Los modelos DeepSeek V4 (`deepseek-v4-flash`, `deepseek-v4-pro`) tienen una ventana de contexto de 1M tokens — el export completo del repositorio cabe cómodamente.
- Google Gemini con contexto de 1–2M tokens maneja el export sin problemas.
- Los modelos OpenAI con contexto de 128k (p.ej. `gpt-4o`) **no pueden** cargar el export completo — el cliente bloqueará la subida con un mensaje de error claro.
- **Recomendación**: Incluso con modelos que técnicamente caben en el export, subir solo los archivos relevantes para la tarea actual para maximizar la atención efectiva del modelo.

### Caché de URL Raw de GitHub

Después de `git push`, la nueva versión **no está disponible inmediatamente** mediante URLs `raw.githubusercontent.com` — GitHub las almacena en caché hasta 10 minutos. Este es el comportamiento esperado y no puede evitarse. Los archivos se almacenan correctamente en GitHub tan pronto como `git push` reporta éxito.

### Nano y Unicode — Advertencia Crítica

**Nunca** editar archivos que contengan secuencias de escape Unicode (como las funciones de marcadores de umlauts) usando `nano` o copiando y pegando en un emulador de terminal.

Nano corrompe secuencias `\u00e4` a basura de múltiples bytes (`M-CM-$`), lo que rompe el análisis de JavaScript silenciosamente.

**El único flujo de trabajo seguro**:
1. Editar archivos localmente en un editor adecuado (VS Code, gedit, kate).
2. `git add` / `git commit` / `git push` desde la máquina local.
3. En el servidor: `git pull` (en el repositorio fuente como usuario `source`).
4. Como root: `./deploy.sh source`.

### Comportamiento de Pegado en Linux/X11/Firefox

En Linux con X11 y Firefox, `e.preventDefault()` en manejadores de eventos de pegado no bloquea de forma fiable el comportamiento de pegado nativo del navegador para contenido proveniente de gestores de archivos. El workaround implementado (permitir el pegado, verificar el contenido de entrada en `setTimeout(0)`, limpiar y alertar si se detectan rutas de archivo) es la única solución fiable para esta limitación específica de plataforma.

### Casos Límite en Detección de Desbordamiento de Contexto

La detección de desbordamiento de contexto en los cinco scripts CGI usa análisis de código de estado HTTP combinado con coincidencia de palabras clave en el cuerpo de respuesta de error de la API. El conjunto de palabras clave es suficientemente amplio para cubrir los mensajes de error estándar de la API. Sin embargo, los casos límite con mensajes de error inusuales de cambios en la infraestructura del proveedor pueden no detectarse y caerían en una visualización de error genérica.

### Auto-Informe del Modelo DeepSeek

Los modelos DeepSeek V4 pueden reportar conocimiento propio impreciso cuando se les pregunta sobre el tamaño de su ventana de contexto o versión — responden basándose en sus datos de entrenamiento, no en su configuración real de API. El modelo actualmente desplegado (`deepseek-v4-flash` o `deepseek-v4-pro`) puede verificarse mediante:
```bash
source /etc/apache2/envvars && curl -s https://api.deepseek.com/v1/models \
  -H "Authorization: Bearer $DEEPSEEK_API_KEY"
```

---

## Dependencias

| Componente | Propósito | Instalación |
|-----------|-----------|------------|
| Apache 2.4 | Servidor web, CGI, SSL | `apt install apache2` |
| Python 3.9+ | Todos los scripts CGI del lado del servidor | `apt install python3` |
| reportlab | Exportación PDF del lado del servidor | `pip3 install reportlab --break-system-packages` |
| PDF.js 3.11.174 | Extracción de texto PDF del lado del cliente | CDN (fallback automático a CDN secundario) |
| jq | Procesamiento JSON en `repo2text.sh` | `apt install jq` |
| pv | Visualización de progreso en `repo2text.sh` | `apt install pv` |
| git | Gestión de versiones | `apt install git` |
| zip | Creación de archivos en `repo2text.sh` | `apt install zip` |

Sin frameworks exóticos — todas las dependencias son paquetes estándar en un entorno Debian o bibliotecas CDN bien establecidas.

---

## Conclusión / Por Qué Este Proyecto Destaca

Este proyecto demuestra desarrollo web de nivel profesional en un enfoque minimalista y centrado en la seguridad — sin overhead innecesario, pero con los más altos estándares de seguridad, corrección y facilidad de uso.

**Arquitectura**:
- Separación limpia de cliente (HTML/JS puro) y servidor (CGI de Python) sin mezcla de responsabilidades.
- Claves API nunca expuestas — incluso un compromiso XSS completo no puede filtrarlas.
- Cliente de archivo único (`index.html`) que es completamente autónomo pero altamente modular internamente.
- Sin pipeline de compilación — el entorno de desarrollo es idéntico a producción.

**Experiencia de usuario**:
- Respuestas en streaming con latencia de primer token sub-segundo.
- Gestión de contexto flexible única — eliminar cualquier mensaje y todos los siguientes.
- Manejo inteligente del portapapeles para texto, imágenes y protección de rutas de archivo.
- Grabación de audio directamente en el navegador para Gemini (todos los modelos) y OpenAI (`gpt-4o`, `gpt-4.1`).
- Kompressor — compresión automática de contexto habilitando conversaciones indefinidamente largas.
- Manejo de contexto superado — cuadro interactivo en el chat con transferencia inteligente de contexto (Opción C).
- Banners de cuota — feedback visual claro y persistente por crédito agotado o límites diarios.
- Copiar al portapapeles — todo el chat exportado del lado del cliente con un solo clic.
- Soporte multilingüe con distinción de forma de tratamiento, cargado desde XML externo.

**Ingeniería**:
- Inspección de bytes mágicos detectando ejecutables independientemente de la extensión del archivo — 12 firmas en 4 plataformas.
- Sistema de marcadores de umlauts resolviendo una limitación fundamental de la API de DeepSeek para texto alemán.
- Mapa de capacidades de modelos compatible con el futuro — añadir un nuevo modelo requiere una única entrada de configuración (con `MODEL_CONFIG` y `MODEL_CAPABILITIES` mantenidos explícitamente sincronizados — una brecha que permitió que todo el lineup de modelos de OpenAI operara silenciosamente con el límite incorrecto de tokens de salida hasta el 19 de julio de 2026).
- Pipeline de visión de extremo a extremo para Google Gemini y OpenAI — los datos de imagen en base64 fluyen desde la subida/pegado en el navegador hasta payloads nativos `inline_data`/`image_url` de la API, controlados por un mapa de capacidades por modelo en lugar de una suposición hardcodeada.
- Descarte preciso del resumen del compresor: el resumen se invalida cuando el contexto cae por debajo del último umbral activado después de la eliminación manual.
- Límite de subida dinámico: 75% de la ventana de contexto del modelo activo en caracteres — escala automáticamente de 384k caracteres (`gpt-4o`) a ~3,1M caracteres (`deepseek-v4-flash`, `gemini-2.5-flash`, la familia GPT-5.6).
- Verificación de despliegue integrada en la pipeline de deployment — `deploy.sh` imprime sumas de comprobación MD5 de cada archivo copiado, detectando despliegues obsoletos/desajustados de inmediato en lugar de descubrirlos por comportamiento inexplicable en tiempo de ejecución.
- Rastro de auditoría completo mediante Git, changelog detallado de 89 entradas y manifiesto de diseño.

**Listo para DeepSeek V4** — migrado a `deepseek-v4-flash` y `deepseek-v4-pro` con ventanas de contexto de 1M tokens, antes del plazo de retiro de modelos heredados del 24 de julio de 2026.

**Listo para GPT-5.6** — lineup de OpenAI actualizado hasta la generación Sol/Terra/Luna (9 de julio de 2026), usando `max_completion_tokens` de forma consistente para compatibilidad en todo el rango de modelos.

**Para un desarrollador profesional**, este proyecto demuestra:
- **Conciencia de seguridad** — protección de claves API, detección de ejecutables, almacenamiento seguro de sesiones, sin path traversal.
- **Disciplina estructurada** — manifiesto de diseño, tags de versión, convenciones estrictas de UI, changelog de 89 entradas.
- **Profundidad en resolución de problemas** — comportamiento de pegado X11, corrupción de umlauts, problemas de salida binaria PDF, "Lost in the Middle", encadenamiento de desbordamiento de contexto, y una cadena de causa raíz en un mismo día desde un mensaje de error vacío hasta un parámetro de solicitud de OpenAI faltante.
- **Documentación completa** — comentarios de código inline, manifiesto dedicado, cabeceras de documentación por script, README trilingüe.

---

*Última actualización: 19.07.2026*






