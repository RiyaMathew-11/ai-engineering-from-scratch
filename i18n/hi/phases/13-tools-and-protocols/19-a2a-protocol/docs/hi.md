# ए2ए  एजेंट-एजेंट प्रोटोकॉल

> एमसीपी एजेंट-टू-टू-टूल है। ए2ए (एजेंट2एजेंट) एजेंट-टू-एजेंट  एक खुला प्रोटोकॉल है जो विभिन्न ढांचे पर निर्मित अस्पष्ट एजेंटों को सहयोग करने की अनुमति देता है। अप्रैल 2025 में Google द्वारा जारी किया गया, जून 2025 में लिनक्स फाउंडेशन को दान किया गया, अप्रैल 2026 में 150+ समर्थकों सहित AWS, सिस्को, माइक्रोसॉफ्ट, सेल्सफोर्स, SAP और सर्विस नाउ सहित v1.0 तक पहुंच गया। इसने आईबीएम के एसीपी को अवशोषित किया और एपी 2 भुगतान विस्तार जोड़ा। यह सबक एजेंट कार्ड, कार्य जीवन चक्र, और तीन प्रोटोकॉल बंधन के माध्यम से चलता है, A2A 1.0.1 तार नामों का उपयोग कर.

**Type:** Build
**Languages:** Python (stdlib, Agent Card + Task harness)
**Prerequisites:** Phase 13 · 06 (MCP fundamentals), Phase 13 · 08 (MCP client)
**Time:** ~75 minutes

## सीखने के लक्ष्य

- एजेंट-टू-टू-टूल (MCP) के उपयोग के मामलों में एजेंट-टू-एजेंट (A2A) के बीच अंतर करना।
-  पर एजेंट कार्ड प्रकाशित करें`/.well-known/agent-card.json`कौशल और`supportedInterfaces`मेटाडेटा।
- कार्य जीवन चक्र का पालन करें: `TASK_STATE_SUBMITTED`,`TASK_STATE_WORKING`,`TASK_STATE_INPUT_REQUIRED`, और टर्मिनल राज्यों `TASK_STATE_COMPLETED`,`TASK_STATE_FAILED`,`TASK_STATE_CANCELED`,`TASK_STATE_REJECTED`. .
- संदेशों का उपयोग करें जिनकी प्रत्येक भाग में एक से एक है `text`,`raw`,`url`या `data`, और कलाकृतियों के रूप में आउटपुट.

## समस्या

ग्राहक सेवा एजेंट को रिपोर्ट लिखने को एक विशेषज्ञ लेखक एजेंट को सौंपने की आवश्यकता होती है।

- कस्टम REST एपीआई काम करता है, लेकिन हर जोड़ने एक बार है.
- साझा कोडबेस. दो एजेंटों को एक ही ढांचे को चलाने की आवश्यकता होती है.
- MCP: MCP को कॉल करने के लिए उपकरण है, दो एजेंटों के लिए नहीं जो एक साथ काम करते हैं जबकि प्रत्येक एजेंट की अस्पष्ट आंतरिक तर्क को संरक्षित करते हैं।

A2A अंतर को भरता है। यह एक एजेंट के जीवन चक्र, संदेशों और कलाकृतियों के साथ एक कार्य को दूसरे को भेजने के रूप में बातचीत का मॉडल बनाता है। बुलाए गए एजेंट की आंतरिक स्थिति अस्पष्ट रहती है।

A2A "चैरेक के माध्यम से एजेंटों को एक दूसरे से बात करने दें" प्रोटोकॉल है। यह MCP की जगह नहीं लेता है; दोनों पूरक हैं।

## अवधारणा

### एजेंट कार्ड

A2A के अनुरूप प्रत्येक एजेंट एक कार्ड प्रकाशित करता है `/.well-known/agent-card.json`:

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

खोज URL पर आधारित हैः कार्ड लाओ, पहले चुनें `supportedInterfaces`प्रविष्टि जिसका `protocolBinding`इनपुट और आउटपुट मोड मीडिया प्रकार हैं।

### हस्ताक्षरित एजेंट कार्ड

एक कार्ड एक `signatures`प्रत्येक प्रविष्टि एक JWS (RFC 7515) है जो कार्ड के RFC 8785 कैनोनिकल JSON पर गणना की जाती है, जिसमें `signatures`उपभोक्ता कार्ड को उसी तरह से कैनोनिकलाइज़ करते हैं और सत्यापित करते हैं. नकलीकरण को रोकता है।

### कार्य जीवन चक्र

```text
TASK_STATE_SUBMITTED
  -> TASK_STATE_WORKING
  -> TASK_STATE_COMPLETED | TASK_STATE_FAILED | TASK_STATE_CANCELED | TASK_STATE_REJECTED

TASK_STATE_WORKING
  -> TASK_STATE_INPUT_REQUIRED
  -> TASK_STATE_WORKING (the client sends a message with the same taskId)
```

ग्राहक  से शुरू करते हैं`SendMessage`तथा सर्वर कार्य बनाता है। कहा एजेंट राज्यों के माध्यम से संक्रमण; ग्राहकों के साथ सर्वेक्षण`GetTask`या SSE पर धारा के साथ `SendStreamingMessage`और `SubscribeToTask`एक धारा ले जाती है`statusUpdate`और `artifactUpdate`कार्य समाप्त होने पर समाप्त होता है।`final`ध्वज।

### संदेश और भाग

एक संदेश में एक `messageId`, ए `role`(`ROLE_USER`या `ROLE_AGENT`), और एक या अधिक भागों. प्रत्येक भाग में एक सामग्री फ़ील्ड होता है, और उस फ़ील्ड का नाम प्रकार होता है। कोई `kind`क्षेत्र।

- `text`: सादा सामग्री।
- `raw`: फ़ाइल बाइट्स, JSON में आधार64, आमतौर पर के साथ `filename`और `mediaType`. .
- `url`: फ़ाइल सामग्री का लिंक।
- `data`: संरचित JSON उपयोगिता लोड (कॉल एजेंट के लिए संरचित इनपुट) ।

उदाहरण:

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

### कलाकृतियाँ

आउटपुट आर्टिफैक्ट हैं, कच्चे स्ट्रिंग नहीं। एक आर्टिफैक्ट एक नामित, टाइप आउटपुट हैः

```json
{
  "artifactId": "art-001",
  "name": "summary",
  "parts": [{"text": "...", "mediaType": "text/markdown"}]
}
```

कलाकृतियों को टुकड़ों के रूप में स्ट्रीम किया जा सकता है।`artifactUpdate`घटना कलाकृतियों के साथ है प्लस `append`और `lastChunk`. . कॉल करने वाला जमा हो जाता है.

### तीन प्रोटोकॉल बंधन

1. **JSON-RPC 2.0 over HTTP**(`JSONRPC`) अनुरोधों के लिए पोस्ट, स्ट्रीमिंग के लिए एसएसई।`SendMessage`,`SendStreamingMessage`,`GetTask`,`ListTasks`,`CancelTask`,`SubscribeToTask`,`CreateTaskPushNotificationConfig`,`GetTaskPushNotificationConfig`,`ListTaskPushNotificationConfigs`,`DeleteTaskPushNotificationConfig`और `GetExtendedAgentCard`. .
2. **gRPC**(`GRPC`) उद्यम वातावरण के लिए जहां gRPC मूल है। समान विधि नाम।
3. **HTTP+JSON/REST**(`HTTP+JSON`) संसाधन URL जैसे `POST /message:send`और `GET /tasks/{id}`. .

सभी तीनों बंधन एक ही डेटा मॉडल रखते हैं।`supportedInterfaces`प्रविष्टि नाम एक बाध्यकारी और उसके `protocolVersion`. ग्राहक हेडर भेजें`A2A-Version: 1.0`हर अनुरोध पर, क्योंकि एक सर्वर संस्करण 0.3 के रूप में एक अनुरोध के बिना पढ़ता है।

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

### खुलेपन का संरक्षण

एक प्रमुख डिजाइन सिद्धांतः बुलाए गए एजेंट की आंतरिक स्थिति अस्पष्ट है। कॉल करने वाला कार्य स्थिति और कलाकृतियों को देखता है। बुलाए गए एजेंट की सोच श्रृंखला, उसके उपकरण कॉल, उसके उप-एजेंट प्रतिनिधि  सभी अदृश्य हैं। यह एमसीपी से अलग है, जहां उपकरण कॉल पारदर्शी हैं।

तर्कः A2A प्रतियोगियों को आंतरिक जानकारी के बिना सहयोग करने की अनुमति देता है। A2A "इस ग्राहक सेवा एजेंट को कॉल करें" हो सकता है, बिना कॉल करने वाले को यह जानने के कि एजेंट सेवा को कैसे लागू करता है।

### समय रेखा

- **2025-04-09.**गूगल A2A की घोषणा करता है।
- **2025-06-23.**लिनक्स फाउंडेशन को दान किया गया।
- **2025-08.**आईबीएम के एसीपी को अवशोषित करता है।
- **2025-09.**एपी2 विस्तार (एजेंट भुगतान) जहाज।
- **2026-04.**150+ सहायक संगठनों के साथ जारी v1.0।

### एमसीपी के साथ संबंध

| Dimension | MCP | A2A |
|-----------|-----|-----|
| Use case | Agent-to-tool | Agent-to-agent |
| Opacity | Transparent tool calls | Opaque inner reasoning |
| Typical caller | Agent runtime | Another agent |
| State | Tool-call result | Task with lifecycle |
| Authorization | OAuth 2.1 (Phase 13 · 16) | Agent Card `securitySchemes` + `securityRequirements` |
| Transport | Stdio / Streamable HTTP | JSON-RPC / gRPC / HTTP+JSON |

जब आप किसी विशिष्ट टूल को कॉल करना चाहते हैं तो MCP का उपयोग करें। जब आप किसी अन्य एजेंट को पूरा कार्य सौंपना चाहते हैं तो A2A का उपयोग करें। कई उत्पादन प्रणालियों दोनों का उपयोग करती हैंः एक एजेंट अपने टूल लेयर के लिए MCP का उपयोग करता है और A2A अपने सहयोग लेयर के लिए।

```figure
a2a-task-lifecycle
```

## इसका प्रयोग करें

`code/main.py`एक न्यूनतम ए 2 ए हर्नल लागू करता हैः लेखक एजेंट अपना कार्ड प्रकाशित करता है, शोध एजेंट उसे एक भेजता है `SendMessage`एक पीडीएफ भाग और एक पाठ निर्देश के साथ अनुरोध, और कार्य के माध्यम से चलता है `TASK_STATE_WORKING`→ `TASK_STATE_INPUT_REQUIRED`→ `TASK_STATE_WORKING`→ `TASK_STATE_COMPLETED`सभी stdlib; संदेश के आकार पर ध्यान केंद्रित करने के लिए एक स्मृति में परिवहन का उपयोग करता है.

क्या देखना हैः

- एजेंट कार्ड JSON आकार।
- सर्वर-साइड टास्क आईडी असाइनमेंट और स्टेट ट्रांजिशन।
- उन भागों को टाइप किया गया है जिनकी सामग्री फ़ील्ड मौजूद है।
- `TASK_STATE_INPUT_REQUIRED`शाखा मध्य कार्य।
- कलाकृतियों को पूरा होने पर वापस।

## इसे भेजें

यह सबक हमें फल देता है`outputs/skill-a2a-agent-spec.md`. एक नए एजेंट को देखते हुए जिसे अन्य एजेंटों द्वारा बुलाया जाना चाहिए, कौशल एजेंट कार्ड JSON, कौशल योजना और अंत बिंदु ब्लूप्रिंट का उत्पादन करता है।

## व्यायाम

1. दौड़ें`code/main.py` `TASK_STATE_INPUT_REQUIRED`रुकें जहां बुलाए गए एजेंट स्पष्टीकरण के लिए पूछता है।

2. एक हस्ताक्षरित एजेंट कार्ड जोड़ें. एक JWS प्रविष्टि डालें.`signatures`के साथ`alg` पर सेट किया गया`HS256`, कार्ड के कैनोनिक JSON हस्ताक्षर बिना `signatures`एक सत्यापनकर्ता लिखें और पुष्टि करें कि यह एक उत्परिवर्तन कार्ड पर विफल रहता है।

3.  के साथ कार्य प्रवाह को लागू करें`SendStreamingMessage`: लेखक एजेंट द्वारा प्रेषित `task`, तीन `artifactUpdate`टुकड़े, और एक `statusUpdate`के साथ`TASK_STATE_COMPLETED`और फिर धारा बंद कर देता है. कॉल करने वाले टुकड़े जमा करते हैं.

4. एक ए 2 ए एजेंट डिजाइन करें जो एक एमसीपी सर्वर को लपेटता है। प्रत्येक एमसीपी टूल को एक ए 2 ए कौशल में मैप करें। व्यापारिक अंतरों पर ध्यान दें  क्या अस्पष्टता खो गई है?

5. A2A v1.0 घोषणा को पढ़ें और एक विशेषता की पहचान करें जो अप्रैल 2026 तक किसी भी ढांचे द्वारा लागू नहीं की गई है। (संकेतः यह मल्टी-हॉप टास्क डेलिगेशन से संबंधित है) ।

## प्रमुख शर्तें

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

## आगे पढ़ना

- [a2a-protocol.org](https://a2a-protocol.org/latest/) कैनोनिक ए2ए विनिर्देश
- [a2aproject/A2A — GitHub](https://github.com/a2aproject/A2A) संदर्भ कार्यान्वयन और एसडीके
- [A2A v1.0.1 release](https://github.com/a2aproject/A2A/tree/v1.0.1): टैग `docs/specification.md`और मानदंड `specification/a2a.proto`यह सबक निम्नलिखित है
- [Linux Foundation — A2A launch press release](https://www.linuxfoundation.org/press/linux-foundation-launches-the-agent2agent-protocol-project-to-enable-secure-intelligent-communication-between-ai-agents) जून 2025 शासन हस्तांतरण
- [Google Cloud — A2A protocol upgrade](https://cloud.google.com/blog/products/ai-machine-learning/agent2agent-protocol-is-getting-an-upgrade) रोडमैप और भागीदार गति
- [Google Dev — A2A 1.0 milestone](https://discuss.google.dev/t/the-a2a-1-0-milestone-ensuring-and-testing-backward-compatibility/352258) v1.0 रिलीज नोट्स और बैकवर्ड कॉम्पैक्ट गाइड
