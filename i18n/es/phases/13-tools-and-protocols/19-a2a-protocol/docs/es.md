# A2A  Protocolo entre agentes

> MCP es agente a herramienta. A2A (Agent2Agent) es un protocolo abierto para permitir que los agentes opacos construidos en diferentes marcos colaboren. Lanzado por Google en abril de 2025, donado a la Fundación Linux en junio de 2025, alcanzando la versión 1.0 en abril de 2026 con más de 150 partidarios, incluidos AWS, Cisco, Microsoft, Salesforce, SAP y ServiceNow. Absorbió el ACP de IBM y añadió la extensión de pagos AP2. Esta lección recorre la tarjeta de agente, el ciclo de vida de tareas y las tres obligaciones de protocolo, utilizando los nombres de alambre A2A 1.0.1.

**Type:** Build
**Languages:** Python (stdlib, Agent Card + Task harness)
**Prerequisites:** Phase 13 · 06 (MCP fundamentals), Phase 13 · 08 (MCP client)
**Time:** ~75 minutes

## Objetivos de aprendizaje

- Distinguir entre el agente a la herramienta (MCP) y los casos de uso entre agentes (A2A).
- Publica una tarjeta de agente en `/.well-known/agent-card.json`con habilidades y`supportedInterfaces`Metadatos.
- Caminar el ciclo de vida de la tarea: `TASK_STATE_SUBMITTED`¿ Qué ?`TASK_STATE_WORKING`¿ Qué ?`TASK_STATE_INPUT_REQUIRED`, y los estados terminales `TASK_STATE_COMPLETED`¿ Qué ?`TASK_STATE_FAILED`¿ Qué ?`TASK_STATE_CANCELED`¿ Qué ?`TASK_STATE_REJECTED`¿ Qué ?
- Utilice mensajes cuyas partes contienen una de cada `text`¿ Qué ?`raw`¿ Qué ?`url`, o`data`, y los artefactos como salidas.

## El problema

Un agente de servicio al cliente debe delegar la redacción de informes a un agente de redacción especializado.

- Funciona pero cada emparejamiento es una sola vez.
- Base de código compartida requiere que los dos agentes ejecuten el mismo marco.
- MCP: no encaja: MCP es para llamar a herramientas, no para dos agentes colaborando mientras se conserva el razonamiento interno opaco de cada agente.

A2A llena la brecha. Modela la interacción como un agente envía una tarea a otro, con un ciclo de vida, mensajes y artefactos. El estado interno del agente llamado se mantiene opaco.

A2A es el protocolo "dejen que los agentes de los marcos hablen entre sí".

## El concepto

### Agente Carte

Cada agente de A2A publica una tarjeta en `/.well-known/agent-card.json`¿Qué es esto ?

```json
{
  "name": "research-agent",
  "description": "Summarizes academic papers and drafts citations.",
  "version": "1.2.0",
  "supportedInterfaces": [
    {
      "url": "https://research.example.com/a2a",
      "protocolBinding": "JSONRPC",
      "protocolVersion": "1.0"
    }
  ],
  "capabilities": {"streaming": true, "pushNotifications": true},
  "securitySchemes": {
    "bearer": {"httpAuthSecurityScheme": {"scheme": "Bearer"}}
  },
  "securityRequirements": [{"schemes": {"bearer": {"list": []}}}],
  "defaultInputModes": ["text/plain"],
  "defaultOutputModes": ["text/markdown"],
  "skills": [
    {
      "id": "summarize_paper",
      "name": "Summarize a paper",
      "description": "Read a paper PDF and produce a 3-paragraph summary.",
      "tags": ["research", "summarization"],
      "inputModes": ["text/plain", "application/pdf"],
      "outputModes": ["text/markdown"]
    }
  ]
}
```

El descubrimiento se basa en URL: trae la tarjeta, elige la primera `supportedInterfaces`Entrada cuyo `protocolBinding`el cliente habla, y enumera habilidades. los modos de entrada y salida son tipos de medios.

### Carteles de agente firmados

Una tarjeta puede llevar un`signatures`Cada entrada es un JWS (RFC 7515) calculado sobre el RFC 8785 canónico JSON de la tarjeta, con el `signatures`El campo de identidad de la tarjeta se deja fuera.

### Ciclo de vida de las tareas

```text
TASK_STATE_SUBMITTED
  -> TASK_STATE_WORKING
  -> TASK_STATE_COMPLETED | TASK_STATE_FAILED | TASK_STATE_CANCELED | TASK_STATE_REJECTED

TASK_STATE_WORKING
  -> TASK_STATE_INPUT_REQUIRED
  -> TASK_STATE_WORKING (the client sends a message with the same taskId)
```

Los clientes comienzan con `SendMessage`El agente llamado pasa por estados; los clientes encuestan con`GetTask`o fluir por SSE con `SendStreamingMessage`y `SubscribeToTask`Un arroyo lleva`statusUpdate`y `artifactUpdate`Los eventos y cierra cuando la tarea alcanza un estado terminal.`final`bandera.

### Mensajes y partes

Un mensaje tiene un`messageId`, una `role`(El artículo`ROLE_USER`o `ROLE_AGENT`), y una o más partes. Cada parte contiene exactamente un campo de contenido, y ese nombre de campo es el tipo.`kind`campo.

- `text`: contenido simple.
- `raw`: bytes de archivo, base64 en JSON, generalmente con `filename`y `mediaType`¿ Qué ?
- `url`: un enlace al contenido del archivo.
- `data`: carga útil estructurada JSON (entrada estructurada para el agente llamado).

Ejemplo:

```json
{
  "messageId": "msg-001",
  "role": "ROLE_USER",
  "parts": [
    {"text": "Summarize this paper."},
    {"raw": "...", "filename": "paper.pdf", "mediaType": "application/pdf"},
    {"data": {"targetLength": "3 paragraphs"}, "mediaType": "application/json"}
  ]
}
```

### Artículos

Las salidas son artefactos, no cadenas crudas. Un artefacto es una salida nombrada y tipada:

```json
{
  "artifactId": "art-001",
  "name": "summary",
  "parts": [{"text": "...", "mediaType": "text/markdown"}]
}
```

Los artefactos pueden ser transmitidos como trozos.`artifactUpdate`El evento lleva el artefacto más `append`y `lastChunk`- El que llama se acumula.

### Tres vínculos de protocolo

1. **JSON-RPC 2.0 over HTTP**(El artículo`JSONRPC`POST para las solicitudes, SSE para la transmisión.`SendMessage`¿ Qué ?`SendStreamingMessage`¿ Qué ?`GetTask`¿ Qué ?`ListTasks`¿ Qué ?`CancelTask`¿ Qué ?`SubscribeToTask`¿ Qué ?`CreateTaskPushNotificationConfig`¿ Qué ?`GetTaskPushNotificationConfig`¿ Qué ?`ListTaskPushNotificationConfigs`¿ Qué ?`DeleteTaskPushNotificationConfig`, y `GetExtendedAgentCard`¿ Qué ?
2. **gRPC**(El artículo`GRPC`Para entornos empresariales donde el gRPC es nativo.
3. **HTTP+JSON/REST**(El artículo`HTTP+JSON` ). URL de recursos como `POST /message:send`y `GET /tasks/{id}`¿ Qué ?

Las tres obligaciones tienen el mismo modelo de datos.`supportedInterfaces`Nombres de entrada un vinculante y su `protocolVersion`Los clientes envían el encabezado .`A2A-Version: 1.0`en cada solicitud, porque un servidor lee una solicitud sin ella como versión 0.3.

```http
POST /a2a HTTP/1.1
Host: research.example.com
Content-Type: application/json
A2A-Version: 1.0

{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "SendMessage",
  "params": {
    "message": {
      "messageId": "msg-001",
      "role": "ROLE_USER",
      "parts": [{"text": "Summarize this paper."}]
    }
  }
}
```

### Preservación de la apertura

Un principio clave de diseño: el estado interno del agente llamado es opaco. El llamador ve el estado de tarea y los artefactos. La cadena de pensamiento del agente llamado, sus llamadas de herramienta, su delegación de subagentes  son todas invisibles. Esto es diferente de MCP, donde las llamadas de herramientas son transparentes.

Racionalización: A2A permite a los competidores colaborar sin revelar los datos internos. A2A puede ser "llamar a este agente de servicio al cliente" sin que el que llama aprenda cómo ese agente implementa el servicio.

### Línea de tiempo

- **2025-04-09.**Google anuncia A2A.
- **2025-06-23.**Donado a la Fundación Linux.
- **2025-08.**Absorbe el ACP de IBM.
- **2025-09.**Naves de extensión AP2 (pagos por agentes).
- **2026-04.**v1.0 lanzado con más de 150 organizaciones de apoyo.

### Relación con la MCP

| Dimension | MCP | A2A |
|-----------|-----|-----|
| Use case | Agent-to-tool | Agent-to-agent |
| Opacity | Transparent tool calls | Opaque inner reasoning |
| Typical caller | Agent runtime | Another agent |
| State | Tool-call result | Task with lifecycle |
| Authorization | OAuth 2.1 (Phase 13 · 16) | Agent Card `securitySchemes` + `securityRequirements` |
| Transport | Stdio / Streamable HTTP | JSON-RPC / gRPC / HTTP+JSON |

Utilice MCP cuando desea invocar una herramienta específica. Utilice A2A cuando desea delegar una tarea completa a otro agente. Muchos sistemas de producción utilizan ambos: un agente utiliza MCP para su capa de herramientas y A2A para su capa de colaboración.

```figure
a2a-task-lifecycle
```

## Usalo

`code/main.py`Implementa un mínimo de A2A: el agente de redacción publica su tarjeta, el agente de investigación la envía a un `SendMessage`La solicitud con una parte PDF y una instrucción de texto, y la tarea se mueve a través de `TASK_STATE_WORKING`¿ Qué es esto ?`TASK_STATE_INPUT_REQUIRED`¿ Qué es esto ?`TASK_STATE_WORKING`¿ Qué es esto ?`TASK_STATE_COMPLETED`Antes de devolver un artefacto de texto. todo stdlib; utiliza un transporte en memoria para centrarse en las formas de mensaje.

Qué ver:

- Forma de tarjeta de agente JSON.
- Asesoramiento de ID de tarea del lado del servidor y transiciones de estado.
- Partes que se escriben por el cual el campo de contenido está presente.
- `TASK_STATE_INPUT_REQUIRED`rama en medio de la tarea.
- El artefacto regresa al final.

## Envío

Esta lección produce`outputs/skill-a2a-agent-spec.md`. Dado que un nuevo agente que debe ser llamado por otros agentes, la habilidad produce el JSON de la tarjeta de agente, esquema de habilidades y plan de punto final.

## Los ejercicios

1. - ¿ Qué ?`code/main.py`.Rastrear todo el ciclo de vida de la tarea, incluida la `TASK_STATE_INPUT_REQUIRED`Ponga una pausa cuando el agente llamado pida una aclaración.

2. Añade una tarjeta de agente firmada.`signatures`con`alg`se fija en `HS256`, firmar el JSON canónico de la tarjeta sin el `signatures`Escriba un verificador y confirma que falla en una tarjeta mutada.

3. Implementar la tarea en streaming con `SendStreamingMessage`: el agente de redacción emite el `task`, tres `artifactUpdate`los trozos, y un `statusUpdate`con`TASK_STATE_COMPLETED`, luego cierra la corriente.

4. Diseñar un agente A2A que envuelva un servidor MCP. Mapa cada herramienta MCP a una habilidad A2A. Observe los compromisos  ¿qué opacidad se pierde?

5. Lea el anuncio de A2A v1.0 e identifique la única característica que aún no está implementada por ningún marco a partir de abril de 2026. (Intenta: se refiere a la delegación de tareas multi-hop).

## Términos clave

| Term | What people say | What it actually means |
|------|----------------|------------------------|
| A2A | "Agent-to-Agent protocol" | Open protocol for opaque agent collaboration |
| Agent Card | "`/.well-known/agent-card.json`" | Published metadata describing an agent's skills and `supportedInterfaces` |
| Skill | "A callable unit" | A named operation the agent supports (analog to MCP tool) |
| Task | "Unit of delegation" | A work item with a lifecycle and final artifact |
| Message | "Task input" | Carries Parts (`text`, `raw`, `url`, `data`) |
| Part | "Typed chunk" | Exactly one of `text` / `raw` / `url` / `data`, plus optional `mediaType`; no `kind` field |
| Artifact | "Task output" | Named, typed output returned on completion |
| AP2 | "Agent Payments Protocol" | Payments extension built on A2A; card signing is core A2A (`signatures`) |
| Opacity | "Black-box collaboration" | Called agent's internals are hidden from caller |
| `TASK_STATE_INPUT_REQUIRED` | "Task pause" | Interrupted state when the agent needs more info |

## Leer más

- [a2a-protocol.org](https://a2a-protocol.org/latest/) especificación canónica A2A
- [a2aproject/A2A — GitHub](https://github.com/a2aproject/A2A) Implementaciones de referencia y KDD
- [A2A v1.0.1 release](https://github.com/a2aproject/A2A/tree/v1.0.1): el etiquetado `docs/specification.md`y la normativa `specification/a2a.proto`Esta lección sigue
- [Linux Foundation — A2A launch press release](https://www.linuxfoundation.org/press/linux-foundation-launches-the-agent2agent-protocol-project-to-enable-secure-intelligent-communication-between-ai-agents) Transferencia de gobernanza de junio de 2025
- [Google Cloud — A2A protocol upgrade](https://cloud.google.com/blog/products/ai-machine-learning/agent2agent-protocol-is-getting-an-upgrade) hoja de ruta y impulso de los socios
- [Google Dev — A2A 1.0 milestone](https://discuss.google.dev/t/the-a2a-1-0-milestone-ensuring-and-testing-backward-compatibility/352258) Nota de liberación de la versión 1.0 y orientación retrocompatible
