# A2A  Protocolo de agente a agente

> O MCP é agente-to-tool. A2A (Agent2Agent) é um protocolo aberto para permitir que agentes opacos construídos em diferentes estruturas colaborem. Lançado pelo Google em abril de 2025, doado à Linux Foundation em junho de 2025, alcançando v1.0 em abril de 2026 com mais de 150 apoiadores, incluindo AWS, Cisco, Microsoft, Salesforce, SAP e ServiceNow. Absorveu o ACP da IBM e acrescentou a extensão dos pagamentos AP2. Esta lição percorre o Cartão de Agente, Ciclo de Vida da Tarefa e as três ligações de protocolo, usando os nomes de fios A2A 1.0.1.

**Type:** Build
**Languages:** Python (stdlib, Agent Card + Task harness)
**Prerequisites:** Phase 13 · 06 (MCP fundamentals), Phase 13 · 08 (MCP client)
**Time:** ~75 minutes

## Objetivos de aprendizagem

- Distinguir casos de utilização de agente para ferramenta (MCP) de casos de utilização de agente para agente (A2A).
- Publica um cartão de agente em `/.well-known/agent-card.json`com competências e`supportedInterfaces`Metadados.
- Caminhar o ciclo de vida da tarefa: `TASK_STATE_SUBMITTED`- Não .`TASK_STATE_WORKING`- Não .`TASK_STATE_INPUT_REQUIRED`, e os estados terminais `TASK_STATE_COMPLETED`- Não .`TASK_STATE_FAILED`- Não .`TASK_STATE_CANCELED`- Não .`TASK_STATE_REJECTED`- Não .
- Use Mensagens cujas partes contenham cada uma de `text`- Não .`raw`- Não .`url`, ou `data`, e artefatos como saídas.

## O problema

Um agente de atendimento ao cliente precisa delegar a redação de relatórios a um agente de escritores especializado.

- Funciona, mas cada emparejamento é único.
- Base de código compartilhada, exige que os dois agentes executem o mesmo quadro.
- MCP: não se encaixa: MCP é para chamar ferramentas, não para dois agentes colaborando enquanto preservam o raciocínio interno opaco de cada agente.

A2A preenche a lacuna. Modela a interação como um agente enviando uma tarefa para outro, com um ciclo de vida, mensagens e artefatos. O estado interno do agente chamado permanece opaco.

A A2A é o protocolo "deixe os agentes através de frameworks falarem uns com os outros".

## O conceito

### Agente Card

Todos os agentes que cumprem os requisitos A2A publicam um cartão em `/.well-known/agent-card.json`- Não .

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

A descoberta é baseada em URL: traga o cartão, escolha o primeiro `supportedInterfaces`Entrada cujo `protocolBinding`Os modos de entrada e saída são tipos de mídia.

### Cartões de Agente assinados

Um cartão pode levar um`signatures`Cada entrada é um JWS (RFC 7515) calculado sobre o JSON canônico RFC 8785 do cartão, com o `signatures`O campo foi excluído. os consumidores canonizam o cartão da mesma forma e verificam.

### Ciclo de vida da tarefa

```text
TASK_STATE_SUBMITTED
  -> TASK_STATE_WORKING
  -> TASK_STATE_COMPLETED | TASK_STATE_FAILED | TASK_STATE_CANCELED | TASK_STATE_REJECTED

TASK_STATE_WORKING
  -> TASK_STATE_INPUT_REQUIRED
  -> TASK_STATE_WORKING (the client sends a message with the same taskId)
```

Os clientes iniciam com `SendMessage`O agente chamado passa por estados; os clientes pesquisam com `GetTask`ou fluir sobre o SSE com `SendStreamingMessage`E ...`SubscribeToTask`Um rio leva`statusUpdate`E ...`artifactUpdate`O processo de execução da tarefa é realizado em função do estado de execução da tarefa.`final`- Não.

### Mensagens e partes

Uma mensagem tem um`messageId`, a `role`(`ROLE_USER`ou `ROLE_AGENT`Cada Parte contém exatamente um campo de conteúdo, e esse nome de campo é o tipo.`kind`campo.

- `text`: conteúdo simples.
- `raw`: bytes de arquivo, base64 em JSON, geralmente com `filename`E ...`mediaType`- Não .
- `url`: um link para o conteúdo do ficheiro.
- `data`: carga útil JSON estruturada (entrada estruturada para o agente chamado).

Exemplo:

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

### Artifactos

As saídas são artefatos, não cordas brutas.

```json
{
  "artifactId": "art-001",
  "name": "summary",
  "parts": [{"text": "...", "mediaType": "text/markdown"}]
}
```

Os artefatos podem ser transmitidos como pedaços.`artifactUpdate`O evento carrega o artefato mais `append`E ...`lastChunk`O que chama acumula-se.

### Três compromissos de protocolo

1. **JSON-RPC 2.0 over HTTP**(`JSONRPC`O POST para as solicitações, o SSE para o streaming.`SendMessage`- Não .`SendStreamingMessage`- Não .`GetTask`- Não .`ListTasks`- Não .`CancelTask`- Não .`SubscribeToTask`- Não .`CreateTaskPushNotificationConfig`- Não .`GetTaskPushNotificationConfig`- Não .`ListTaskPushNotificationConfigs`- Não .`DeleteTaskPushNotificationConfig`, e `GetExtendedAgentCard`- Não .
2. **gRPC**(`GRPC`Para ambientes empresariais onde o gRPC é nativo.
3. **HTTP+JSON/REST**(`HTTP+JSON` ). URLs de recursos como `POST /message:send`E ...`GET /tasks/{id}`- Não .

As três ligações têm o mesmo modelo de dados.`supportedInterfaces`nome de entrada um vinculativo e o seu `protocolVersion`Os clientes enviam o cabeçalho .`A2A-Version: 1.0`em cada pedido, porque um servidor lê uma solicitação sem ele como versão 0.3.

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

### Preservação da opacidade

Um princípio de design chave: o estado interno do agente chamado é opaco. O chamador vê o estado da tarefa e artefatos. A cadeia de pensamento do agente chamado, suas chamadas de ferramenta, sua delegação de sub-agente  são todas invisíveis. Isso é diferente do MCP, onde as chamadas de ferramentas são transparentes.

A A2A pode ser "chamá-lo para o agente de atendimento ao cliente" sem que o chamador aprenda como esse agente implementa o serviço.

### Linha de tempo

- **2025-04-09.**O Google anuncia A2A.
- **2025-06-23.**Doado à Fundação Linux.
- **2025-08.**Absorve o ACP da IBM.
- **2025-09.**Naves de extensão AP2 (pagamentos por agentes).
- **2026-04.**V1.0 lançado com mais de 150 organizações de apoio.

### Relação com a MCP

| Dimension | MCP | A2A |
|-----------|-----|-----|
| Use case | Agent-to-tool | Agent-to-agent |
| Opacity | Transparent tool calls | Opaque inner reasoning |
| Typical caller | Agent runtime | Another agent |
| State | Tool-call result | Task with lifecycle |
| Authorization | OAuth 2.1 (Phase 13 · 16) | Agent Card `securitySchemes` + `securityRequirements` |
| Transport | Stdio / Streamable HTTP | JSON-RPC / gRPC / HTTP+JSON |

Use MCP quando quiser invocar uma ferramenta específica. Use A2A quando quiser delegar uma tarefa inteira a outro agente. Muitos sistemas de produção usam ambos: um agente usa MCP para sua camada de ferramentas e A2A para sua camada de colaboração.

```figure
a2a-task-lifecycle
```

## Usá-lo

`code/main.py`Implementa um arame A2A mínimo: o agente de redacção publica o seu cartão, o agente de investigação envia-o um `SendMessage`A tarefa é executada através de uma peça PDF e uma instrução de texto.`TASK_STATE_WORKING`→ `TASK_STATE_INPUT_REQUIRED`→ `TASK_STATE_WORKING`→ `TASK_STATE_COMPLETED`Antes de devolver um artefato de texto. Todos stdlib; usa um transporte na memória para se concentrar em formas de mensagem.

O que ver:

- Forma de cartão JSON.
- Assegnação de id de tarefa do lado do servidor e transições de estado.
- Partes digitadas por que o campo de conteúdo está presente.
- `TASK_STATE_INPUT_REQUIRED`Branco no meio da tarefa.
- O artefato retorna ao término.

## Envia-o

Esta lição produz`outputs/skill-a2a-agent-spec.md`. Dado um novo agente que deve ser chamado por outros agentes, a habilidade produz o JSON do Cartão do Agente, esquema de habilidades e plano de ponto final.

## Exercícios

1. Corra .`code/main.py`- Traçar todo o ciclo de vida da tarefa, incluindo o`TASK_STATE_INPUT_REQUIRED`Pausa quando o agente chamado pedir esclarecimentos.

2. Adicione um cartão de agente assinado.`signatures`com`alg`definido para `HS256`, assinando o JSON canônico da carta sem o `signatures`Escreva um verificador e confirma que falha num cartão mutado.

3. Implementar tarefas em streaming com `SendStreamingMessage`O agente do escritor emite o`task`, três .`artifactUpdate`- e um`statusUpdate`com`TASK_STATE_COMPLETED`O chamador acumula os pedaços.

4. Desenhar um agente A2A que envolva um servidor MCP. mapear cada ferramenta MCP para uma habilidade A2A. Observe as compensações  que opacidade é perdida?

5. Leia o anúncio A2A v1.0 e identifique a única característica que ainda não foi implementada por nenhuma estrutura a partir de abril de 2026.

## Termos-chave

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

## Mais leitura

- [a2a-protocol.org](https://a2a-protocol.org/latest/) especificação canónica A2A
- [a2aproject/A2A — GitHub](https://github.com/a2aproject/A2A) Implementações de referência e KDS
- [A2A v1.0.1 release](https://github.com/a2aproject/A2A/tree/v1.0.1): os marcados `docs/specification.md`e a normativa `specification/a2a.proto`Esta lição segue
- [Linux Foundation — A2A launch press release](https://www.linuxfoundation.org/press/linux-foundation-launches-the-agent2agent-protocol-project-to-enable-secure-intelligent-communication-between-ai-agents) Transferência de governança de Junho de 2025
- [Google Cloud — A2A protocol upgrade](https://cloud.google.com/blog/products/ai-machine-learning/agent2agent-protocol-is-getting-an-upgrade) Mapa de estrada e impulso dos parceiros
- [Google Dev — A2A 1.0 milestone](https://discuss.google.dev/t/the-a2a-1-0-milestone-ensuring-and-testing-backward-compatibility/352258) Nota de liberação e orientação compatível para trás
