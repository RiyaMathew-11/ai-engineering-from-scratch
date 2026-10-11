# ساخت یک سرور MCP: پایتون بدون حالت و تایپ اسکریپت

> یک سرور MCP مدرن دست دادن را به یاد نمی آورد. این متادتا را در هر درخواست تأیید می کند، یک دستیار را اجرا می کند و یک نتیجه تایپ شده را باز می گرداند.

**Type:** Build
**Languages:** Python, TypeScript
**Prerequisites:** Phase 13, Lesson 06
**Time:** ~85 minutes

## اهداف یادگیری

- اجرای اجباری`server/discover`برای MCP `2026-07-28`. .
- نسخه پروتکل و قابلیت های مشتری را در هر درخواست تأیید کنید.
- ابزارها، منابع و پیام ها را با ترتیب لیست تعیین کننده نشان دهید.
- برگشت`resultType`، هویت سرور و اطلاعات مربوط به نتایج درست
- به همان قرارداد بدون دولت در استودیو محدود خط جدید در پایتون و تایپ اسکریپت خدمت کنید.

## مشکل

یک سرور که قابلیت های مشتری را پس از پیام اول ذخیره می کند، ساخت آسان و کار دشواری است. همان فرآیند ممکن است به مشتریان دنباله دار خدمت کند. یک درخواست از راه دور ممکن است روی یک کارگر مختلف فرود بیاید. یک بیانیه قابلیت قدیمی می تواند رفتاری را در سراسر مرزهای مجوز افشاند.

MCP `2026-07-28`برنامه شما هنوز هم می تواند یادداشت های ماندگار، شغل ها یا دستی های حالت صریح را نگه دارد. آنچه که نمی تواند نگه دارد، حالت پروتکل پنهان است که نحوه رمزگذاری یک درخواست بعدی را تغییر می دهد.

این درس یک سرور یادداشت دو بار ایجاد می کند. نسخه های پایتون و تایپ اسکریپت فقط از کتابخانه های استاندارد خود برای هسته پروتکل استفاده می کنند. هر دو روش های مشابه را نشان می دهند و قرارداد سیمی مشابه را اجرا می کنند.

## مفهوم

### حلقه جدید ارسال

```text
read one JSON-RPC line
parse the envelope
if it is a notification, do not respond
validate params._meta for this request
route by method
wrap success with resultType and serverInfo
write one JSON-RPC response line
forget request-scoped metadata
```

سه قانون استودیو هنوز مهمه:

- فقط پيام JSON-RPC رو به stdout بنويسين.
- پیام ها را با یک خط جدید تعریف کنید و هر پاسخ را به صورت آبی نشان دهید.
- وقتي که ستدين به دفتر خارجيه برسه فوراً بيرون برو

طول عمر فرآیند یک طول عمر حمل و نقل است. این یک جلسه MCP مدرن نیست.

### تایید درخواست

هر درخواست باید:

```json
{
  "params": {
    "_meta": {
      "io.modelcontextprotocol/protocolVersion": "2026-07-28",
      "io.modelcontextprotocol/clientCapabilities": {},
      "io.modelcontextprotocol/clientInfo": {
        "name": "notes-client",
        "version": "1.0.0"
      }
    }
  }
}
```

اولين دو ميدان مورد نياز است.`clientInfo`یک شکل هویت موجود را تأیید کنید، اما آن را به عنوان تأیید هویت نپذیرید.

اگر نسخه پشتیبانی نشده باشد، کد بازگشت را ارسال کنید`-32022`با`requested`و`supported`. متاداتا درخواست گمشده ، پارام های باطل ، کد`-32602`هرگز از تماس قبلی به جا نبرید

### کشف اجباری

سرورهای مدرن باید اجرا کنند`server/discover`. یک نتیجه کشف کامل شامل نسخه های مدرن پشتیبانی شده، قابلیت ها، دستورالعمل های اختیاری، راهنمایی های کش و هویت سرور در نتیجه است `_meta`:

```json
{
  "resultType": "complete",
  "supportedVersions": ["2026-07-28"],
  "capabilities": {
    "tools": {"listChanged": false},
    "resources": {"listChanged": false, "subscribe": false},
    "prompts": {"listChanged": false}
  },
  "ttlMs": 3600000,
  "cacheScope": "public",
  "_meta": {
    "io.modelcontextprotocol/serverInfo": {
      "name": "notes-server",
      "version": "2.0.0"
    }
  }
}
```

دیسکوری سرور رو باز نمی کنه.`tools/list`بدون اینکه به کشف زنگ بزنم چون`tools/list`قبلاً همان متاداتا درخواست را در خود دارد.

### ابزار

`tools/list`یک لیست تعیین کننده از توصیفات ابزار را باز می گرداند. ترتیب پایدار به بهبود حافظه پیشگیری پاسخ و حفظ ثبات زمینه مدل کمک می کند. نتیجه همچنین نیاز به `ttlMs`و`cacheScope`. .

`tools/call`بلوک های محتوا را بازمی گرداند و`isError`. هنگام عدم اعتبار بروکول یا پارامترهای روش، یک خطای JSON-RPC را استفاده کنید.`isError: true`وقتی یک درخواست ابزار معتبر اجرا می شود اما خود ابزار شکست می خورد.

تشریحات ابزار به عنوان اشاره باقی می ماند، نه اجرای:

- `readOnlyHint`
- `destructiveHint`
- `idempotentHint`
- `openWorldHint`

میزبان باید از آنها برای تایید و ارائه استفاده کند. سرور باید هنوز مجوز واقعی را اجرا کند.

### منابع

`resources/list`توضیحات URI ثابت را باز می گرداند. `resources/read`محتوای تایپ شده را باز می گرداند. هر دو در حافظه کش قابل ذخیره هستند`2026-07-28`، پس هر دو شامل`ttlMs`و`cacheScope`. .

استفاده کنید`cacheScope: "private"`برای اطلاعات یادداشت مخصوص کاربر. یک کش مشترک نباید از یک پاسخ خصوصی در زمینه های مجوز استفاده مجدد کند.

تحویل جدید تغییر استفاده نمی کند`resources/subscribe`. يه مشتري باز ميشه`subscriptions/listen`و درخواست ها`resourceSubscriptions`یا دسته بندی های تغییر لیست. درس 10 این جریان را ایجاد می کند.

### پیام ها

`prompts/list`قابل پنهان کردن و تعیین کننده است.`prompts/get`یک پیامک نامگذاری شده با استدلال را ارائه می دهد. نتیجه پیامک ارائه شده کامل است، اما یکی از لیست های ذخیره سازی یا نتایج خواندن نیست که نیاز به اشاره های ذخیره سازی دارد.

### هر نتیجه موفق به صورت تایپ شده

در مثال ها برای هر موفقیت یک بسته بندی استفاده می شود:

```python
def complete(payload):
    return {
        "resultType": "complete",
        **payload,
        "_meta": {SERVER_INFO_KEY: SERVER_INFO},
    }
```

لیست، خواندن و کشف دستیاران اضافه کنید `ttlMs`و اضافه`cacheScope`. مرکزي کردن اين بسته مانع از اينکه يک بازيگر خاموشي از حلقات نتيجه مدرن حذف کنه

### هیچ درخواست از سوی سرور آغاز نشده

یک سرور مدرن می تواند اطلاعات مربوط به یک درخواست مشتری یا اطلاعات را در یک سرور باز شده توسط مشتری ارسال کند `subscriptions/listen`.این نباید درخواست JSON-RPC خود را ارسال کند

وقتی یک عامل نیاز به نمونه گیری، ایجاد یا ورود ریشه دارد، یک `input_required`نتیجه. مشتری درخواست های ورودی داخلی را برآورده می کند و روش اصلی را با یک ID درخواست جدید دوباره امتحان می کند. درس 11 این الگوی درخواست چند دور دور را پوشش می دهد.

### مطابقت صریح میراث

یک سرور دو عصر نیز می تواند `2025-11-25`دست زدن به شاخه ی میراث کاملاً جداگانه ای. رفتار مدرن را انتخاب می کند وقتی که نیاز به مدرن است.`_meta`حاشیه ها در حال حاضر و در حال دریافت رفتار میراث هستند `initialize`. .

قرار ندهید`2026-07-28`درخواست از طریق مسیر دست دادن میراث.`resultType`کد در این درس به طور عمدی جدید است فقط به طوری که متغیرات آن باقی می ماند قابل مشاهده.

```figure
t3-dispatch-loop
```

## ازش استفاده کن

نمایش و تست های محدود سرور پایتون را اجرا کنید:

```bash
cd code
python3 main.py --demo
python3 -m unittest discover tests -v
```

پورت TypeScript را با یک نوع کاربری TypeScript اجرا کنید:

```bash
npx tsx main.ts --demo
```

نمایش ارسال شده`server/discover`در هر درخواست مدرن متاداتا تکرار می شود. هر موفقیت شامل هویت سرور است.

## -باده

اين درس به ما ميگيره`outputs/skill-mcp-server-scaffolder.md`. این یک برنامه سرور مدرن با قرارداد کشف، تأیید هر درخواست، لیست های تعیین کننده کش قابل، و یک آداپتور متمایز میراث اختیاری تولید می کند.

## تمرینات

1. قابلیت ها را از یک درخواست حذف کنید و ثابت کنید که سرور اعلامیه درخواست قبلی را مجددا استفاده نمی کند.
2. برگردونيد`TOOLS`،`PROMPTS`، و ترتيب وارد کردن يادداشت. تمام نتایج فهرست ثابت باقی مانده است.
3. يه تخريب دهنده اضافه کن`notes_delete`ابزار و نیاز به چک مجوز در داخل اجرا کننده. نگه دارید `destructiveHint`فقط به عنوان یک اشاره UX.
4. اضافه کردن`resources/templates/list`با`ttlMs`،`cacheScope`، و نظم تعیین کننده
5. یک آداپتور قدیمی جداگانه برای `2025-11-25`. تست هاي جديد رو اضافه کنيد که ثابت کنه درخواست جديد هرگز واردش نميکنه

## اصطلاحات کلیدی

| Term | Meaning |
|------|---------|
| Stateless server | Handles each request from its own metadata without protocol-session memory |
| `server/discover` | Mandatory modern method that advertises versions and capabilities |
| Complete result | Successful modern result with `resultType: "complete"` |
| Cacheable result | Discovery, list, or resource-read result with `ttlMs` and `cacheScope` |
| Deterministic list | Same logical registry produces the same item order |
| Server identity | Recommended `io.modelcontextprotocol/serverInfo` in result `_meta` |
| Tool error | Valid tool call that returns content with `isError: true` |
| Protocol error | Invalid JSON-RPC or MCP request returned through `error` |

## خواندن بیشتر

- [MCP Specification 2026-07-28](https://modelcontextprotocol.io/specification/2026-07-28/)
- [MCP Server Discovery](https://modelcontextprotocol.io/specification/2026-07-28/server/discover)
- [MCP Tools](https://modelcontextprotocol.io/specification/2026-07-28/server/tools)
- [MCP Resources](https://modelcontextprotocol.io/specification/2026-07-28/server/resources)
- [MCP Prompts](https://modelcontextprotocol.io/specification/2026-07-28/server/prompts)
- [MCP stdio Transport](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/stdio)
