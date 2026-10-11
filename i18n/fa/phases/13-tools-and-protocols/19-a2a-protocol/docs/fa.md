# A2A  پروتکل از یک عامل به دیگر

> "مپ" از عامل به ابزار کار ميکنه A2A (Agent2Agent) یک پروتکل باز برای اجازه دادن به اجنتی های غیر شفاف ساخته شده بر روی چارچوب های مختلف همکاری است. در آوریل 2025 توسط گوگل منتشر شد، در ژوئن 2025 به بنیاد لینوکس اهدا شد، در آوریل 2026 به v1.0 رسید و 150+ طرفدار از جمله AWS، سیسکو، مایکروسافت، Salesforce، SAP و ServiceNow رسید. این برنامه ACP IBM را جذب کرد و تمدید پرداخت های AP2 را اضافه کرد. این درس کارت عامل، چرخه عمر کار و سه پروتکل مرتبط با A2A 1.0.1 را با استفاده از نام های سیم انجام می دهد.

**Type:** Build
**Languages:** Python (stdlib, Agent Card + Task harness)
**Prerequisites:** Phase 13 · 06 (MCP fundamentals), Phase 13 · 08 (MCP client)
**Time:** ~75 minutes

## اهداف یادگیری

- از موارد استفاده از عامل به ابزار (MCP) و از موارد استفاده از عامل به عامل (A2A) تفاوت کنید.
- کارت مامور را در `/.well-known/agent-card.json`با مهارت ها و`supportedInterfaces`متاداتا
- چرخه عمر کار رو دنبال کن: `TASK_STATE_SUBMITTED`،`TASK_STATE_WORKING`،`TASK_STATE_INPUT_REQUIRED`، و حالت پايان`TASK_STATE_COMPLETED`،`TASK_STATE_FAILED`،`TASK_STATE_CANCELED`،`TASK_STATE_REJECTED`. .
- از پيام هاي که هر قسمتي از آنها يک عدد دارد استفاده کن`text`،`raw`،`url`، یا`data`و آثار هنری به عنوان محصول

## مشکل

یک مامور خدمات مشتری باید گزارش های را به یک مامور متخصص نویسندگی اختصاص دهد.

- .آپي آي آي آر اس رو سفارشي ميکنه .کار ميکنه ولي هر جفتي يه باريه
- . پايگاه کد مشترک . به دو عامل مي خواد که يه چارچوب رو اجرا کنن
- MCP: مناسب نیست: MCP برای تماس ابزار است، نه برای دو عامل همکاری در حالی که حفظ هر عامل غیر شفاف استدلال داخلی است.

A2A شکاف را پر می کند. این تعامل را به عنوان یک عامل ارسال یک وظیفه به دیگری، با چرخه زندگی، پیام ها و آثار هنری مدل می کند. حالت داخلی عامل نامیده شده نامشخص باقی می ماند.

A2A پروتکل "به اجازه دهید عوامل در چارچوب ها با یکدیگر صحبت کنند" است. این جایگزین MCP نیست؛ این دو مکمل هستند.

## مفهوم

### کارده

هر مامور مطابق با قانون A2A کارت رو به شماره ي `/.well-known/agent-card.json`:

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

کشف بر اساس URL است: کارت رو بیار، اولش رو انتخاب کن`supportedInterfaces`ورودی که `protocolBinding`موظف شما صحبت می کند و مهارت های خود را به شمار می آورد. حالت ورودی و خروجی انواع رسانه ای هستند.

### کارت های امضا شده

کارت مي تونه يه کارت رو نگه داره`signatures`هر ورودی یک JWS (RFC 7515) است که بر روی RFC 8785 JSON کانونیک کارت محاسبه شده است.`signatures`مصرف کنندگان کارت را به همان شیوه می توانند تصدیق کنند.

### چرخه عمر وظایف

```text
TASK_STATE_SUBMITTED
  -> TASK_STATE_WORKING
  -> TASK_STATE_COMPLETED | TASK_STATE_FAILED | TASK_STATE_CANCELED | TASK_STATE_REJECTED

TASK_STATE_WORKING
  -> TASK_STATE_INPUT_REQUIRED
  -> TASK_STATE_WORKING (the client sends a message with the same taskId)
```

مشتریان شروع می کنند با `SendMessage`، و سرور کار رو ایجاد ميکنه. مامور به اسم مياد از طریق ايالت ها مي گذرد.`GetTask`یا جریان در SSE با `SendStreamingMessage`و`SubscribeToTask`. يه رودخانه حمل ميکنه`statusUpdate`و`artifactUpdate`اتفاقات و بسته شدن زمانی که وظیفه به حالت نهایی می رسد.`final`پرچم

### پیام ها و بخش ها

يه پيام يه پيام داره`messageId`، یک`role`(`ROLE_USER`یا`ROLE_AGENT`), و یک یا چند بخش. هر بخش دقیقا یک زمینه محتوا را دارد و نام این زمینه نوع است.`kind`میدان

- `text`: محتوای ساده
- `raw`: بائتهای فایل، base64 در JSON، معمولا با `filename`و`mediaType`. .
- `url`: یک لینک به محتوای فایل
- `data`: ساختار JSON (دخل ساختار یافته برای عامل تماس)

مثال:

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

### آثار هنری

محصولات آثار هنری هستند نه رشته های خام. آثار هنری یک محصول نامگذاری شده و تایپ شده است:

```json
{
  "artifactId": "art-001",
  "name": "summary",
  "parts": [{"text": "...", "mediaType": "text/markdown"}]
}
```

آثار هنری می تونه به شکل قطعه ها پخش بشه`artifactUpdate`اتفاقي که اين آثار رو همراه داره`append`و`lastChunk`. تماس گیرنده جمع می شه

### سه پروتکل متعهد

1. **JSON-RPC 2.0 over HTTP**(`JSONRPC`) POST برای درخواست ها، SSE برای پخش. روش ها PascalCase: `SendMessage`،`SendStreamingMessage`،`GetTask`،`ListTasks`،`CancelTask`،`SubscribeToTask`،`CreateTaskPushNotificationConfig`،`GetTaskPushNotificationConfig`،`ListTaskPushNotificationConfigs`،`DeleteTaskPushNotificationConfig`و`GetExtendedAgentCard`. .
2. **gRPC**(`GRPC`) برای محیط های شرکتی که gRPC بومی است. نام های روش مشابه.
3. **HTTP+JSON/REST**(`HTTP+JSON`). URL منابع مانند `POST /message:send`و`GET /tasks/{id}`. .

هر سه پیوند مدل داده های مشابه را دارند.`supportedInterfaces`نام ورودی یک متعهد و`protocolVersion`. مشتریان سرش رو بفرستند`A2A-Version: 1.0`در هر درخواست، چون یک سرور یک درخواست بدون آن را به عنوان نسخه 0.3 می خواند.

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

### حفظ قابلیت خالی

یک اصل طراحی کلیدی: وضعیت داخلی عامل نامیده شده غیر شفاف است. تماس گیرنده حالت کار و آثار را می بیند. زنجیره فکر عامل نامیده شده، تماس های ابزار آن، نمایندگی فرعی آن  همه نامرئی است. این از MCP متفاوت است، جایی که تماس های ابزار شفاف است.

استدلال: A2A به رقبای خود امکان همکاری را بدون افشای اطلاعات داخلی می دهد. A2A می تواند "به این نماینده خدمات مشتری تماس بگیرید" بدون اینکه تماس گیرنده یاد بگیرد که چگونه این عامل خدمات را اجرا می کند.

### خط زمانی

- **2025-04-09.**گوگل اعلام کرد A2A
- **2025-06-23.**به بنياد لينکس اهدا شد
- **2025-08.**آکسيپ IBM رو جذب ميکنه
- **2025-09.**کشتی های توسعه AP2 (دفع توسط آژانس)
- **2026-04.**نسخه 1.0 با 150+ سازمان پشتیبانی منتشر شد.

### رابطه با MCP

| Dimension | MCP | A2A |
|-----------|-----|-----|
| Use case | Agent-to-tool | Agent-to-agent |
| Opacity | Transparent tool calls | Opaque inner reasoning |
| Typical caller | Agent runtime | Another agent |
| State | Tool-call result | Task with lifecycle |
| Authorization | OAuth 2.1 (Phase 13 · 16) | Agent Card `securitySchemes` + `securityRequirements` |
| Transport | Stdio / Streamable HTTP | JSON-RPC / gRPC / HTTP+JSON |

استفاده از MCP هنگامی که می خواهید یک ابزار خاص را فراخوانید. استفاده از A2A هنگامی که می خواهید یک کار را به یک عامل دیگر اختصاص دهید. بسیاری از سیستم های تولید از هر دو استفاده می کنند: یک عامل از MCP برای لایه ابزار خود و A2A برای لایه همکاری خود استفاده می کند.

```figure
a2a-task-lifecycle
```

## ازش استفاده کن

`code/main.py`استفاده از یک آرم A2A کمترین: نویسنده آژانس کارت خود را منتشر می کند، آژانس تحقیقاتی ارسال می کند `SendMessage`درخواست با یک بخش PDF و یک دستورالعمل متن، و کار حرکت می کند از طریق `TASK_STATE_WORKING`→ `TASK_STATE_INPUT_REQUIRED`→ `TASK_STATE_WORKING`→ `TASK_STATE_COMPLETED`قبل از بازگشت یک متن آرتیفکت. تمام stdlib؛ از یک حمل و نقل در حافظه برای تمرکز بر روی اشکال پیام استفاده می کند.

چه چیزی رو باید ببینیم:

- شکل کارت مامور JSON
- تعیین هویت وظیفه در سمت سرور و انتقال حالت.
- قسمت هایی که با وجود زمینه محتوا تایپ شده اند.
- `TASK_STATE_INPUT_REQUIRED`شاخه وسط کار
- آثار آثار بعد از اتمام بازگردانده شد

## -باده

این درس به ما کمک می کند`outputs/skill-a2a-agent-spec.md`. با توجه به یک عامل جدید که باید توسط سایر عوامل تماس گرفته شود، مهارت JSON کارت عامل، طرح مهارت و طرح نقطه پایان را تولید می کند.

## تمرینات

1. فرار کن`code/main.py`.تراسه کل چرخه عمر وظیفه، از جمله `TASK_STATE_INPUT_REQUIRED`وقتي که مامور تماس گرفته ازش درخواست تصحيحات مي کنه

2. يه کارت مامور امضا شده رو اضافه کن`signatures`با`alg`به `HS256`، امضا کردن JSON کانونیک کارت بدون `signatures`یک تایید کننده بنویسید و تایید کنید که در کارت جهش یافته شکست خورده.

3. اجرا کردن جریان کاری با `SendStreamingMessage`: مامور نویسنده ارسال می کند`task`، سه`artifactUpdate`قطعات و یک`statusUpdate`با`TASK_STATE_COMPLETED`، سپس جریان رو می بندد. تماس گیرنده قطعات را جمع می کند.

4. طراحی یک عامل A2A که یک سرور MCP را بسته کند. هر ابزار MCP را به یک مهارت A2A نقشه بزنید. توجه به تعادلات کنید  عدم شفافیت چه چیزی از دست می دهد؟

5. اعلامیه A2A v1.0 را بخوانید و ویژگی ای را شناسایی کنید که هنوز توسط هیچ چارچوبی از آوریل 2026 اجرا نشده است.

## اصطلاحات کلیدی

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

## خواندن بیشتر

- [a2a-protocol.org](https://a2a-protocol.org/latest/) مشخصات A2A قانونی
- [a2aproject/A2A — GitHub](https://github.com/a2aproject/A2A) پیاده سازی های مرجع و SDK ها
- [A2A v1.0.1 release](https://github.com/a2aproject/A2A/tree/v1.0.1): برچسب ها`docs/specification.md`و قانون سنجش`specification/a2a.proto`این درس میخواد
- [Linux Foundation — A2A launch press release](https://www.linuxfoundation.org/press/linux-foundation-launches-the-agent2agent-protocol-project-to-enable-secure-intelligent-communication-between-ai-agents) انتقال حاکمیت در ژوئن 2025
- [Google Cloud — A2A protocol upgrade](https://cloud.google.com/blog/products/ai-machine-learning/agent2agent-protocol-is-getting-an-upgrade) نقشه راه و حرکت شرکا
- [Google Dev — A2A 1.0 milestone](https://discuss.google.dev/t/the-a2a-1-0-milestone-ensuring-and-testing-backward-compatibility/352258) یادداشت های انتشار v1.0 و راهنمایی های کمپیکت عقب
