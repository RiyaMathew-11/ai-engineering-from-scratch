# A2A  Ajan-Ajan Protokolü

> MCP, ajan-a-alıt. A2A (Agent2Agent) farklı çerçevelerde inşa edilmiş açık olmayan ajanların işbirliği yapmasına izin veren açık bir protokol. Google tarafından Nisan 2025'te yayınlanan, Haziran 2025'te Linux Vakfına bağışlanan, Nisan 2026'da AWS, Cisco, Microsoft, Salesforce, SAP ve ServiceNow dahil 150+ destekleyici ile v1.0'ya ulaştı. IBM'in ACP'ini absorbe etti ve AP2 ödeme uzatmalarını ekledi. Bu ders, A2A 1.0.1 tel isimlerini kullanarak ajan kartı, görev yaşam döngüsü ve üç protokol bağlamasını yürütüyor.

**Type:** Build
**Languages:** Python (stdlib, Agent Card + Task harness)
**Prerequisites:** Phase 13 · 06 (MCP fundamentals), Phase 13 · 08 (MCP client)
**Time:** ~75 minutes

## Öğrenme Hedefleri

- Ajan-a-ağent (A2A) kullanım durumlarından ajan-a-ağent (MCP) kullanımı ayırt edin.
- Bir ajan kartı yayınlayın .`/.well-known/agent-card.json`yetenekleri ve `supportedInterfaces`Metadata.
- Görev yaşam döngüsünü izleyin: `TASK_STATE_SUBMITTED`- Evet .`TASK_STATE_WORKING`- Evet .`TASK_STATE_INPUT_REQUIRED`, ve terminal durumları `TASK_STATE_COMPLETED`- Evet .`TASK_STATE_FAILED`- Evet .`TASK_STATE_CANCELED`- Evet .`TASK_STATE_REJECTED`- Evet .
- Her bir kısmının bir tane olduğu Mesajları kullan `text`- Evet .`raw`- Evet .`url`veya`data`, ve çıkış olarak eserler.

## Sorun

Müşteri hizmetleri ajanı rapor yazmayı uzman bir yazar ajanına devretmelidir.

- Yapısal REST API'si çalışır ama her çiftleme bir kerelik.
- Ortak kod tabanı. İki ajanın aynı çerçeveyi çalıştırmasını gerektirir.
- MCP, iki ajanın birbirleriyle işbirliği yaparak her bir ajanın iç mantığını koruduğu halde, çağrı araçları için değil.

A2A boşluğu dolduruyor. Bir ajanın bir görevi diğerine gönderdiği etkileşimi, bir yaşam döngüsü, mesajlar ve eserlerle modellediyor. Çağrılan ajanın iç durumu netsiz kalır.

A2A, "cadre arası ajanların birbirleriyle konuşmasına izin verin" protokolüdür.

## Anlaşım

### Ajan Kartı

A2A ' ya uygun her ajan bir kart yayınlar .`/.well-known/agent-card.json`- ...

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

Bulma URL tabanlı: kartı getir, ilkini seç `supportedInterfaces`Kayıtı`protocolBinding`Bu, bir iletişim ortamı olarak kullanılır.

### İmzalanmış Ajan Kartları

Bir kart bir kart taşıyabilir .`signatures`Array. Her giriş bir JWS (RFC 7515) kartın RFC 8785 kanonik JSON üzerinden hesaplanmıştır, `signatures`Kullanıcılar aynı şekilde kartı kanonikalize eder ve doğrulayır.

### Görev yaşam döngüsü

```text
TASK_STATE_SUBMITTED
  -> TASK_STATE_WORKING
  -> TASK_STATE_COMPLETED | TASK_STATE_FAILED | TASK_STATE_CANCELED | TASK_STATE_REJECTED

TASK_STATE_WORKING
  -> TASK_STATE_INPUT_REQUIRED
  -> TASK_STATE_WORKING (the client sends a message with the same taskId)
```

Müşteriler başlıyor `SendMessage`Adı ajanları devletler arasında geçiyor, müşteriler ile sorgu yapıyor.`GetTask`veya SSE üzerinden akış `SendStreamingMessage`ve `SubscribeToTask`Akıntı taşıyor .`statusUpdate`ve `artifactUpdate`Bu durum, görevlerin son durumuna ulaştığında gerçekleşir ve kapanır.`final`Bayrak.

### Mesajlar ve Bölümler

Bir mesajın bir `messageId`, a `role`(`ROLE_USER`veya `ROLE_AGENT`), ve bir veya daha fazla Bölüm. Her Bölüm tam olarak bir içerik alanı içerir ve bu alan adı türdür.`kind`- Alan.

- `text`: basit içerik.
- `raw`: dosya baytları, JSON'da base64, genellikle  ile`filename`ve `mediaType`- Evet .
- `url`Dosya içeriğine bir bağlantı.
- `data`: yapılandırılmış JSON payload (sırhlanan ajan için yapılandırılmış giriş).

Örnek:

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

### Sanat eserleri

Çıktıkları çiğ ip değil, eserler.

```json
{
  "artifactId": "art-001",
  "name": "summary",
  "parts": [{"text": "...", "mediaType": "text/markdown"}]
}
```

Sanat eserleri parça olarak akışabilir.`artifactUpdate`Olay , eser ve artfaktı taşıyor .`append`ve `lastChunk`- Arayan toplanıyor.

### Üç protokol bağlaması

1. **JSON-RPC 2.0 over HTTP**(`JSONRPC`) POST istekler için, SSE akış için.`SendMessage`- Evet .`SendStreamingMessage`- Evet .`GetTask`- Evet .`ListTasks`- Evet .`CancelTask`- Evet .`SubscribeToTask`- Evet .`CreateTaskPushNotificationConfig`- Evet .`GetTaskPushNotificationConfig`- Evet .`ListTaskPushNotificationConfigs`- Evet .`DeleteTaskPushNotificationConfig`ve`GetExtendedAgentCard`- Evet .
2. **gRPC**(`GRPC`) GRPC'nin yerli olduğu işletme ortamları için.
3. **HTTP+JSON/REST**(`HTTP+JSON`).  gibi kaynak URL'leri`POST /message:send`ve `GET /tasks/{id}`- Evet .

Üç bağlama da aynı veri modelini taşır.`supportedInterfaces`Giriş isimleri bir bağlayıcı ve onun `protocolVersion`Müşteriler başlığı gönderir .`A2A-Version: 1.0`Her istek için, çünkü bir sunucu, istek olmadan bir istekleri 0.3 sürümü olarak okuyor.

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

### Açıklık koruma

Ana tasarım prensibi: çağrılan ajanın iç durumu açık değildir. Çağrılan görev durumunu ve eserleri görür. çağrılan ajanın düşünce zinciri, araç çağrıları, alt ajan delegasyonu  hepsi görünmez. Bu, araç çağrılarının şeffaf olduğu MCP'den farklıdır.

A2A, rekabetçilerin içsel bilgileri açığa çıkarmadan işbirliği yapmasını sağlar. A2A, arama yapanın hizmeti nasıl uyguladığını öğrenmeden "bu müşteri hizmetleri ajanını arayın" olabilir.

### Zaman çizgisi

- **2025-04-09.**Google A2A'yı duyurdu.
- **2025-06-23.**Linux Vakfına bağışlanmış.
- **2025-08.**IBM'in ACP'ini emiriyor.
- **2025-09.**AP2 uzatma (Agent Ödeme) gemileri.
- **2026-04.**150+ destekleyici organizasyonla yayınlanan v1.0.

### MCP ile ilişki

| Dimension | MCP | A2A |
|-----------|-----|-----|
| Use case | Agent-to-tool | Agent-to-agent |
| Opacity | Transparent tool calls | Opaque inner reasoning |
| Typical caller | Agent runtime | Another agent |
| State | Tool-call result | Task with lifecycle |
| Authorization | OAuth 2.1 (Phase 13 · 16) | Agent Card `securitySchemes` + `securityRequirements` |
| Transport | Stdio / Streamable HTTP | JSON-RPC / gRPC / HTTP+JSON |

Bir özel aracı çağrıştırmak istediğinizde MCP kullanın. Bir tüm görevi başka bir ajan'a devretmek istediğinizde A2A kullanın. Birçok üretim sistemi her ikisini de kullanır: bir ajan araç katmanı için MCP'yi ve işbirliği katmanı için A2A'yı kullanır.

```figure
a2a-task-lifecycle
```

## Kullan

`code/main.py`A2A harnesini en az uyguluyor: yazar ajanı kartını yayınlıyor, araştırma ajanı ona bir `SendMessage`PDF bir parçası ve metin talimatı ile başvurun ve görev devam eder `TASK_STATE_WORKING`→ `TASK_STATE_INPUT_REQUIRED`→ `TASK_STATE_WORKING`→ `TASK_STATE_COMPLETED`Tüm stdlib; mesaj şekillerine odaklanmak için bir hafıza taşıyıcısı kullanır.

Neye bakılır:

- Ajan Kartı JSON şekli.
- Sunucu tarafındaki görev kimliği ve durum geçişleri.
- İçerik alanının bulunduğu bölümler.
- `TASK_STATE_INPUT_REQUIRED`- Ara sıra.
- Artifak tamamlandığında geri döner.

## Gönder

Bu ders bize çok yararlı .`outputs/skill-a2a-agent-spec.md`. Diğer ajanlar tarafından çağrılabilir olan yeni bir ajan verildiğinde, yetenek Agent Kart JSON, yetenek skemi ve son nokta çizelgesini üretir.

## Egzersizler

1. Çık .`code/main.py`.Task'ın tüm yaşam döngüsünü takip edin, `TASK_STATE_INPUT_REQUIRED`Çağrılan ajan açıklama istediğinde dur.

2. İmzalanmış bir ajan kartı ekle.`signatures`- Evet .`alg` ayarlanmıştır`HS256`, kartın kanonik JSON'unu imzalamak `signatures`Bir doğrulama yaz ve mutasyonlu bir kartta başarısız olduğunu onayla.

3. Görev akışı ile uygulayın `SendStreamingMessage`: yazar ajanı `task`, üç .`artifactUpdate`parçalar ve bir `statusUpdate`- Evet .`TASK_STATE_COMPLETED`Sonra akış kapanır.

4. Bir MCP sunucusuyla bir A2A ajanı tasarlayın. Her MCP aracı bir A2A yeteneğine göre bir harita yapın.

5. A2A v1.0 duyuruyu okuyun ve Nisan 2026 itibariyle herhangi bir çerçeve tarafından henüz uygulanmayan tek özelliği belirleyin.

## Anahtar Terimler

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

## Daha Fazla Okumak

- [a2a-protocol.org](https://a2a-protocol.org/latest/) Kanonik A2A spesifikasyonu
- [a2aproject/A2A — GitHub](https://github.com/a2aproject/A2A) Referans uygulamalar ve SDK'lar
- [A2A v1.0.1 release](https://github.com/a2aproject/A2A/tree/v1.0.1)Etiketlenmiş`docs/specification.md`ve düzenlemeler.`specification/a2a.proto`Bu ders
- [Linux Foundation — A2A launch press release](https://www.linuxfoundation.org/press/linux-foundation-launches-the-agent2agent-protocol-project-to-enable-secure-intelligent-communication-between-ai-agents) Haziran 2025 yönetim transfer
- [Google Cloud — A2A protocol upgrade](https://cloud.google.com/blog/products/ai-machine-learning/agent2agent-protocol-is-getting-an-upgrade) Yol haritası ve ortakların hareketi
- [Google Dev — A2A 1.0 milestone](https://discuss.google.dev/t/the-a2a-1-0-milestone-ensuring-and-testing-backward-compatibility/352258) v1.0 serbest bırakma notları ve geriye doğru kompak rehberlik
