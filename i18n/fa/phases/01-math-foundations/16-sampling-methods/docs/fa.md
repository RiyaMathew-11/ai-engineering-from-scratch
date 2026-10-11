# روش های نمونه گیری

> نمونه گیری این است که چگونه هوش مصنوعی فضای امکانات را کشف می کند.

**Type:** Build
**Language:**پیتون
**Prerequisites:** Phase 1, Lessons 06-07 (Probability, Bayes' Theorem)
**Time:** ~120 minutes

## اهداف یادگیری

- از صفر نمونه گیری CDF، رد و اهمیت را با استفاده از فقط اعداد تصادفی یکسانی اجرا کنید
- نمونه گیری دمای، top-k و top-p ( هسته) را برای تولید نماد توکن زبان بسازید
- روش بازتوسطه را توضیح دهید و چرا این روش از طریق نمونه گیری در VAEs امکان گسترش پس را می دهد
- از Metropolis-Hastings MCMC برای نمونه گیری از توزیع هدف غیر عادی اجرا کنید

## مشکل

یک مدل زبان پردازش درخواست شما را تمام می کند و یک ویکتور از 50 هزار لوگیت تولید می کند. یک برای هر توکن در لغت خود. حالا باید یکی را انتخاب کند. چگونه؟

اگر همیشه نشانه ی احتمال بالا را انتخاب کند، هر پاسخ یکسان است. تعیین کننده. خسته کننده. اگر به طور تصادفی به طور یکسان انتخاب کند، نتیجه اش بی معنی است. پاسخ در جایی بین این افراط ها زندگی می کند و در جایی توسط نمونه گیری کنترل می شود.

نمونه گیری به تولید متن محدود نیست. یادگیری تقویت کننده، gradient های سیاست را با استفاده از مسیرهای نمونه گیری تخمین می زند. VAEs نمایش های پنهان را با نمونه گیری از توزیع های آموخته و پخش مجدد از طریق تصادفی یاد می گیرند. مدل های انتشار با نمونه گیری از صدا و انکار تکراری تصاویر تولید می کنند. روش های مونت کارلو انتیگراڵی را که هیچ راه حل شکل بسته ای ندارند تخمین می زنند. الگوریتم های MCMC توزیع های بعدی بالاتری را که غیرممکن است که به شمار بیایند، بررسی می کنند.

هر سیستم تولید هوش مصنوعی یک سیستم نمونه گیری است. استراتژی نمونه گیری کیفیت، تنوع و کنترل پذیری محصول را تعیین می کند. این درس هر روش اصلی نمونه گیری را از ابتدا می سازد، از اعداد تصادفی یکسانی شروع می شود و با تکنیک هایی که LLM های مدرن و مدل های تولید کننده را تقویت می کند، به پایان می رسد.

## مفهوم

### چرا نمونه گیری مهم است

نمونه گیری در چهار نقش اساسی در هوش مصنوعی و یادگیری ماشین ظاهر می شود:

**Generation.**مدل های زبان، مدل های انتشار و GAN ها همه با نمونه گیری تولید می کنند. الگوریتم نمونه گیری مستقیماً خلاقیت، همبستگی و تنوع را کنترل می کند. دمای، top-k و نمونه گیری هسته ای دکمه هایی هستند که مهندسان روزانه آن را می چرخند.

**Training.**نمونه های نزول گرادیانتی استوکاستیک نمونه های کوچک. نمونه های نیورون برای غیرفعال سازی. نمونه های افزایش داده ها نمونه های تصادفی تبدیل می شوند. نمونه های مهم برای کاهش تفاوت گرادیانتی در یادگیری تقویت (PPO، TRPO) نمونه ها را وزن می کنند.

**Estimation.**بسیاری از مقادیر در ML هیچ راه حل بسته ای ندارند. از دست دادن انتظار می رود در یک توزیع داده، عملکرد تقسیم یک مدل مبتنی بر انرژی، شواهد در نتیجه گیری بیزیایی. تخمین مونت کارلو با میانگین بر روی نمونه ها همه این موارد را نزدیک می کند.

**Exploration.**الگوریتم های MCMC توزیع های پس ازین را در نتیجه گیری بیزیایی بررسی می کنند. استراتژی های تکاملی اختلالات پارامتر نمونه می گیرند. نمونه گیری تامپسون برابر اکتشاف و بهره برداری در غارتکاران است.

چالش اصلی: شما فقط می توانید نمونه را مستقیما از توزیع های ساده (وحده، عادی) انجام دهید. برای همه چیز دیگر، شما نیاز به یک روش برای تبدیل نمونه های ساده به نمونه های توزیع هدف دارید.

### نمونه گیری تصادفی یکسانی

هر روش نمونه گیری از اینجا شروع می شود. یک ژنراتور اعداد تصادفی یکسانی مقادیر را در [0, 1) تولید می کند که هر فرعی طول برابر احتمال برابر دارد.

```
U ~ Uniform(0, 1)

P(a <= U <= b) = b - a    for 0 <= a <= b <= 1

Properties:
  E[U] = 0.5
  Var(U) = 1/12
```

برای نمونه گیری یکسانی از مجموعه ای از عناصر متمایز، U را تولید کنید و طبقه برگشت کنید. برای نمونه گیری از یک محدوده مداوم [a، b]، a + (b - a) * U را محاسبه کنید.

نکته کلیدی: یک عدد تصادفی یکسانی حاوی مقدار تصادفی درست برای تولید یک نمونه از هر توزیع است.

### روش CDF معکوس (معمولاً نمونه گیری تبدیل معکوس)

عملکرد توزیع تجمعی (CDF) مقادیر را به احتمالات نقشه می زند:

```
F(x) = P(X <= x)

Properties:
  F is non-decreasing
  F(-inf) = 0
  F(+inf) = 1
  F maps the real line to [0, 1]
```

CDF معکوس احتمالات را به مقادیر باز می کند. اگر U ~ یونیفورم ((0, 1) ، پس X = F_inverse ((U) به دنبال توزیع هدف است.

```
Algorithm:
  1. Generate u ~ Uniform(0, 1)
  2. Return F_inverse(u)

Why it works:
  P(X <= x) = P(F_inverse(U) <= x) = P(U <= F(x)) = F(x)
```

**Exponential distribution example:**

```
PDF: f(x) = lambda * exp(-lambda * x),   x >= 0
CDF: F(x) = 1 - exp(-lambda * x)

Solve F(x) = u for x:
  u = 1 - exp(-lambda * x)
  exp(-lambda * x) = 1 - u
  x = -ln(1 - u) / lambda

Since (1 - U) and U have the same distribution:
  x = -ln(u) / lambda
```

این کار به خوبی زمانی که شما می توانید F_inverse را در شکل بسته بنویسید. برای توزیع عادی، CDF برعکس شکل بسته وجود ندارد، بنابراین ما از روش های دیگر (Box-Muller، یا مقربات عددی) استفاده می کنیم.

**Discrete version:**برای توزیع های متمایز، CDF را به عنوان یک مبلغ تجمعی بسازید، U را تولید کنید و اولین شاخص را پیدا کنید که مبلغ تجمعی U را فراتر می گذارد. این نحوه است `sample_categorical`در درس 6 کار می کند.

### نمونه گیری رد

وقتی نمی توانید CDF را برعکس کنید اما می توانید PDF هدف را تا یک ثابت ارزیابی کنید، نمونه گیری رد کار می کند.

```
Target distribution: p(x)  (can evaluate, possibly unnormalized)
Proposal distribution: q(x)  (can sample from)
Bound: M such that p(x) <= M * q(x) for all x

Algorithm:
  1. Sample x ~ q(x)
  2. Sample u ~ Uniform(0, 1)
  3. If u < p(x) / (M * q(x)), accept x
  4. Otherwise, reject and go to step 1

Acceptance rate = 1/M
```

در طول طول M، میزان پذیرش بیشتر می شود. در ابعاد پایین (1-3) نمونه گیری رد خوب کار می کند. در ابعاد بالا، میزان پذیرش به طور نمایی کاهش می یابد زیرا بیشتر حجم پیشنهاد رد می شود. این لعنت ابعاد برای نمونه گیری رد است.

**Example: sampling from a truncated normal.**از یک پیشنهاد یکسانی در محدوده کوتاه استفاده کنید. پاکت M حداکثر PDF معمولی در این محدوده است.

**Example: sampling from a semicircle.**در مستطیل مرزی به طور یکسانی پیشنهاد کنید. اگر نقطه در داخل نیمه دایره قرار گیرد، قبول کنید. اینگونه مونت کارلو پی را محاسبه می کند: نرخ پذیرش برابر نسبت مساحت پی / 4 است.

### نمونه گیری اهمیت

گاهی اوقات شما به نمونه هایی از توزیع هدف p(x نیاز ندارید. شما باید انتظارات را تحت p(x تخمین بزنید و نمونه هایی از توزیع مختلف q(x دارید.

```
Goal: estimate E_p[f(x)] = integral of f(x) * p(x) dx

Rewrite:
  E_p[f(x)] = integral of f(x) * (p(x)/q(x)) * q(x) dx
            = E_q[f(x) * w(x)]

where w(x) = p(x) / q(x)  are the importance weights.

Estimator:
  E_p[f(x)] ~ (1/N) * sum(f(x_i) * w(x_i))    where x_i ~ q(x)
```

این در یادگیری تقویت بسیار مهم است. در PPO (Prosimal Policy Optimization) ، شما مسیرهای تحت یک سیاست قدیمی را جمع آوری می کنید اما می خواهید یک سیاست جدید را بهینه سازی کنید. وزن اهمیت این است که p_new a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a  a   a                      

تفاوت تخمینگر نمونه گیری اهمیت بستگی به این دارد که q چقدر شبیه به p است. اگر q بسیار متفاوت از p باشد، چند نمونه وزن زیادی به دست می آورند و بر تخمین ها تسلط دارند. نمونه گیری اهمیت خود عادی شده با مجموع وزن تقسیم می شود تا این مشکل را کاهش دهد:

```
E_p[f(x)] ~ sum(w_i * f(x_i)) / sum(w_i)
```

### تخمین مونت کارلو

تخمین مونت کارلو از طریق میانگین نمونه های تصادفی تکامل را نزدیک می کند. قانون اعداد بزرگ تضمین کنورژن می کند.

```
Goal: estimate I = integral of g(x) dx over domain D

Method:
  1. Sample x_1, ..., x_N uniformly from D
  2. I ~ (Volume of D / N) * sum(g(x_i))

Error: O(1 / sqrt(N))   regardless of dimension
```

نرخ خطا مستقل از ابعاد است. به همین دلیل روش های مونت کارلو در ابعاد بالا تسلط دارند که در آن یکپارچه سازی مبتنی بر شبکه غیرممکن است.

**Estimating pi:**

```
Sample (x, y) uniformly from [-1, 1] x [-1, 1]
Count how many fall inside the unit circle: x^2 + y^2 <= 1
pi ~ 4 * (count inside) / (total count)
```

**Estimating expectations:**

```
E[f(X)] ~ (1/N) * sum(f(x_i))    where x_i ~ p(x)

The sample mean converges to the true expectation.
Variance of the estimator = Var(f(X)) / N
```

### زنجیره مارکوف مونت کارلو (MCMC): متروپولیس-هستینگز

MCMC یک زنجیره مارکوف را ایجاد می کند که توزیع ثابت آن توزیع هدف p ((x) است. پس از مراحل کافی، نمونه های زنجیره (تقریباً) نمونه های p ((x) هستند.

```
Target: p(x)  (known up to a normalizing constant)
Proposal: q(x'|x)  (how to propose the next state given the current state)

Metropolis-Hastings algorithm:
  1. Start at some x_0
  2. For t = 1, 2, ..., T:
     a. Propose x' ~ q(x'|x_t)
     b. Compute acceptance ratio:
        alpha = [p(x') * q(x_t|x')] / [p(x_t) * q(x'|x_t)]
     c. Accept with probability min(1, alpha):
        - If u < alpha (u ~ Uniform(0,1)): x_{t+1} = x'
        - Otherwise: x_{t+1} = x_t
  3. Discard first B samples (burn-in)
  4. Return remaining samples
```

برای پیشنهادات متقابل (q(x' (x) = q(x) ، نسبت به p(x') / p(x ساده می شود. این الگوریتم اصلی Metropolis است.

**Why it works.**قانون پذیرش تعادل مفصل را تضمین می کند: احتمال بودن در x و حرکت به x' برابر با احتمال بودن در x' و حرکت به x است. تعادل مفصل به این معنی است که p ((x) توزیع ثابت زنجیره است.

**Practical considerations:**
- سوختن: نمونه های اولیه را قبل از رسیدن به تعادل زنجیره ای از بین ببرید
- کاهش وزن: نگه داشتن هر نمونه k-th برای کاهش خود ارتباط
- مقیاس پیشنهادی: بسیار کوچک و زنجیره به آرامی حرکت می کند (قبول بالا، اکتشاف کند) ؛ بسیار بزرگ و اکثر پیشنهادها رد می شوند (قبول پایین، در محل خود گیر کرده است)
- نرخ مطلوب پذیرش برای یک پیشنهاد گاس در ابعاد بالا حدود 0.234 است

### نمونه گیری گیبز

نمونه گیری گیبز یک مورد ویژه MCMC برای توزیع چند متغیر است. به جای پیشنهاد حرکت در همه ابعاد به یکباره، یک متغیر را از توزیع مشروط خود به روز می کند.

```
Target: p(x_1, x_2, ..., x_d)

Algorithm:
  For each iteration t:
    Sample x_1^{t+1} ~ p(x_1 | x_2^t, x_3^t, ..., x_d^t)
    Sample x_2^{t+1} ~ p(x_2 | x_1^{t+1}, x_3^t, ..., x_d^t)
    ...
    Sample x_d^{t+1} ~ p(x_d | x_1^{t+1}, x_2^{t+1}, ..., x_{d-1}^{t+1})
```

نمونه گیری گیبز نیاز دارد که شما می توانید از هر توزیع مشروط نمونه گیری p ((x_i √ x_{-i}) است. این برای بسیاری از مدل ها ساده است:
- شبکه های بیزی: مشروطات از ساختار نمودار پیروی می کنند
- مخلوط های گاوسی: شرایط گاوسی هستند
- مدل های ایزینگ: شرایط هر اسپین تنها به همسایه های آن بستگی دارد

نرخ پذیرش همیشه 1 است (هر پیشنهاد پذیرفته می شود) زیرا نمونه گیری از شرایط دقیق به طور خودکار تعادل دقیق را برآورده می کند.

**Limitation.**وقتی متغیرها به شدت مرتبط هستند، نمونه گیری گیبز به آرامی مخلوط می شود زیرا به روز کردن یک متغیر در یک زمان نمی تواند حرکت های بزرگ دیگال را از طریق توزیع انجام دهد.

### نمونه گیری دمای (در LLM استفاده می شود)

مدل های زبان logits z_1، ..., z_V را برای هر توکن در لغت تولید می کنند. Softmax این ها را به احتمالات تبدیل می کند. دمای دوباره logits را قبل از softmax تغییر می دهد:

```
p_i = exp(z_i / T) / sum(exp(z_j / T))

T = 1.0: standard softmax (original distribution)
T -> 0:  argmax (deterministic, always picks highest logit)
T -> inf: uniform (all tokens equally likely)
T < 1.0: sharpens the distribution (more confident, less diverse)
T > 1.0: flattens the distribution (less confident, more diverse)
```

**Why it works.**تقسیم لوگیت با T < 1 تفاوت بین لوگیت ها را تقویت می کند. اگر z_1 = 2 و z_2 = 1 ، تقسیم با T = 0.5 به z_1/T = 4 و z_2/T = 2 منجر می شود ، که شکاف بزرگتر می شود. پس از softmax ، توکن بالاترین لوگیت سهم بسیار بیشتری می گیرد.

**In practice:**
- T = 0.0: رمزگذاری طمع آمیز، بهترین برای پرسش و پاسخ واقعی
- T = 0.3-0.7: کمی خلاقانه، برای تولید کد خوب
- T = 0.7-1.0: متعادل، برای مکالمه عمومی خوب است
- T = 1.0-1.5: نوشتن خلاقانه، طوفان مغزی
- T > 1.5: به طور فزاینده ای تصادفی، به ندرت مفید است

دمای تغییر نمی کند که کدام توکن ها ممکن هستند بلکه مقدار احتمالی را که به هر توکن اختصاص داده شده تغییر می دهد.

### نمونه گیری از بالای ک

نمونه گیری top-k مجموعه کاندیدایی را به توکن های k با بیشترین احتمال محدود می کند، سپس نمونه ها را از آن مجموعه محدود دوباره عادی می کند.

```
Algorithm:
  1. Compute softmax probabilities for all V tokens
  2. Sort tokens by probability (descending)
  3. Keep only the top k tokens
  4. Renormalize: p_i' = p_i / sum(p_j for j in top-k)
  5. Sample from the renormalized distribution

k = 1:  greedy decoding
k = V:  no filtering (standard sampling)
k = 40: typical setting, removes long tail of unlikely tokens
```

Top-k مانع از انتخاب نماد از توکن های بسیار غیرممکن (تایپو، بی معنی) است که در دم طولانی توزیع لغت وجود دارد. مشکل: k بدون توجه به زمینه ثابت است. هنگامی که مدل مطمئن است (یک توکن دارای احتمال 95٪ است) ، k = 40 هنوز هم 39 گزینه را اجازه می دهد. هنگامی که مدل نامطمئن است (احتمال در 1000 توکن پخش می شود) ، k = 40 گزینه های قابل قبول را قطع می کند.

### نمونه برداری از بالای (نوکلیوس)

نمونه گیری top-p به طور پویا اندازه مجموعه کاندید را تنظیم می کند. به جای نگه داشتن تعداد ثابت توکن ها، کوچکترین مجموعه توکن هایی را نگه می دارد که احتمال تجمعی آن بیش از p است.

```
Algorithm:
  1. Compute softmax probabilities for all V tokens
  2. Sort tokens by probability (descending)
  3. Find smallest k such that sum of top-k probabilities >= p
  4. Keep only those k tokens
  5. Renormalize and sample

p = 0.9:  keeps tokens covering 90% of probability mass
p = 1.0:  no filtering
p = 0.1:  very restrictive, nearly greedy
```

هنگامی که مدل مطمئن است، نمونه گیری هسته چند توکن (شاید 2-3) را حفظ می کند. هنگامی که مدل نامشخص است، بسیاری (شاید 200) را حفظ می کند. این رفتار سازنده به این دلیل است که نمونه گیری هسته به طور کلی متن بهتری نسبت به top-k تولید می کند.

**Common combinations:**
- دمای 0.7 + بالا-p 0.9: تنظیم مناسب برای هدف عمومی
- دمای 0.0 (طمع): بهترین برای وظایف تعیین کننده
- دمای 1.0 + بالای 50: Fan et al. (2018) تنظیم کاغذ اصلی

top-k و top-p را می توان ترکیب کرد. اول top-k را اعمال کنید، سپس top-p را روی مجموعه باقی مانده اعمال کنید.

### ترفند بازسازی (در VAEs استفاده می شود)

خودکار کدگذاری متغیر (VAE) با کدگذاری ورودی ها به یک توزیع در فضای پنهان، نمونه گیری از آن توزیع، و رمزگذاری نمونه را به عقب می آموزد. مشکل: شما نمی توانید با یک عملیات نمونه گیری به عقب گسترش دهید.

```
Standard sampling (not differentiable):
  z ~ N(mu, sigma^2)

  The randomness blocks gradient flow.
  d/d_mu [sample from N(mu, sigma^2)] = ???
```

ترفند بازسازي تصادفي را از پارامترها جدا ميکنه:

```
Reparameterized sampling:
  epsilon ~ N(0, 1)          (fixed random noise, no parameters)
  z = mu + sigma * epsilon   (deterministic function of parameters)

  Now z is a deterministic, differentiable function of mu and sigma.
  d(z)/d(mu) = 1
  d(z)/d(sigma) = epsilon

  Gradients flow through mu and sigma.
```

این کار به این دلیل است که N  mu, sigma^2) دارای توزیع مشابه mu + sigma * N  0, 1 است. نکته کلیدی: تصادف را به یک منبع بدون پارامتر (epsilon) منتقل کنید، سپس نمونه را به عنوان یک تحول قابل تفاوتی از پارامتر ها بیان کنید.

**In the VAE training loop:**
1. خروجی های کدگر mu و log ((sigma^2) برای هر ورودی
2. نمونه ایپسیلون ~ N(0, 1)
3. محاسبه z = mu + sigma * epsilon
4. کد z برای بازسازی ورودی
5. از طریق مراحل ۴، ۳، ۲، ۱ به عقب گسترش دهید (ممکن است زیرا مرحله ۳ قابل جدایی است)

بدون ترفند بازسازی، VAEs نمی توانند با گسترش پس از استاندارد آموزش داده شوند. این بینش تنها VAEs را عملی کرد.

### Gumbel-Softmax (نمونه های دسته بندی قابل تشخیص)

ترفند تنظیم مجدد برای توزیع های مداوم (گوسیان) کار می کند. برای توزیع های دسته بندی متمایز، ما نیاز به رویکرد متفاوتی داریم. Gumbel-Softmax یک تقرب قابل تفاوت را به نمونه گیری دسته بندی ارائه می دهد.

**The Gumbel-Max trick (non-differentiable):**

```
To sample from a categorical distribution with log-probabilities log(p_1), ..., log(p_k):
  1. Sample g_i ~ Gumbel(0, 1) for each category
     (g = -log(-log(u)), where u ~ Uniform(0, 1))
  2. Return argmax(log(p_i) + g_i)

This produces exact categorical samples.
```

**Gumbel-Softmax (differentiable approximation):**

```
Replace the hard argmax with a soft softmax:
  y_i = exp((log(p_i) + g_i) / tau) / sum(exp((log(p_j) + g_j) / tau))

tau (temperature) controls the approximation:
  tau -> 0:  approaches a one-hot vector (hard categorical)
  tau -> inf: approaches uniform (1/k, 1/k, ..., 1/k)
  tau = 1.0: soft approximation
```

Gumbel-Softmax یک آرامش مداوم یک نمونه متمایز تولید می کند. خروجی یک ویکتور احتمال (رنگ یک گرم) به جای یک سخت یک گرم است. گرادیانت ها از طریق نرم حداکثر جریان می کنند. در طول عبور به جلو در تمرین، شما می توانید از تخمین دهنده "راست به طریق" استفاده کنید: برای عبور به جلو از argmax سخت استفاده کنید اما گرادیانت های نرم Gumbel-Softmax برای عبور به عقب.

**Applications:**
- متغیرهای پنهان در VAEs
- جستجوی معماری عصبی (انتخاب عملیات متمایز)
- مکانیسم های دقت سخت
- یادگیری تقویت شده با اقدامات متمایز

### نمونه گیری لایه بندی شده

نمونه گیری استاندارد مونت کارلو می تواند به طور تصادفی شکاف هایی در فضای نمونه را ایجاد کند. نمونه گیری طبقه بندی شده حتی پوشش را با تقسیم فضای به لایه ها و نمونه گیری از هر یک از آنها ایجاد می کند.

```
Standard Monte Carlo:
  Sample N points uniformly from [0, 1]
  Some regions may have clusters, others gaps

Stratified sampling:
  Divide [0, 1] into N equal strata: [0, 1/N), [1/N, 2/N), ..., [(N-1)/N, 1)
  Sample one point uniformly within each stratum
  x_i = (i + u_i) / N   where u_i ~ Uniform(0, 1),  i = 0, ..., N-1
```

نمونه گیری لایه بندی همیشه با تفاوت پایین تر یا برابر با استاندارد مونت کارلو:

```
Var(stratified) <= Var(standard Monte Carlo)

The improvement is largest when f(x) varies smoothly.
For piecewise-constant functions, stratified sampling is exact.
```

**Applications:**
- ادغام عددی (قریب مونت کارلو)
- تقسیم داده های آموزش (ضمان تعادل کلاس در هر فولد)
- نمونه گیری اهمیت با طبقه بندی (جمع کردن هر دو تکنیک)
- NeRF (به نام میدان های نورال تابش) از نمونه گیری لایه ای در امتداد اشعه دوربین استفاده می کند

### ارتباط با مدل های انتشار

مدل های انتشار از طریق یک فرآیند نمونه گیری تصاویر تولید می کنند. فرآیند پیشروی صداهای گاوسی را به یک تصویر در طول مراحل T اضافه می کند تا آن را به صداهای خالص تبدیل کند. فرآیند معکوس یاد می گیرد که از تصویر اصلی قدم به قدم بازیابی کند.

```
Forward process (known):
  x_t = sqrt(alpha_t) * x_{t-1} + sqrt(1 - alpha_t) * epsilon
  where epsilon ~ N(0, I)

  After T steps: x_T ~ N(0, I)  (pure noise)

Reverse process (learned):
  x_{t-1} = (1/sqrt(alpha_t)) * (x_t - (1 - alpha_t)/sqrt(1 - alpha_bar_t) * epsilon_theta(x_t, t)) + sigma_t * z
  where z ~ N(0, I)

  Each denoising step is a sampling step.
```

ارتباط با روش های این درس:
- هر مرحله از دست دادن از ترفند بازتعدی استفاده می کند (صوت نمونه، تغییر تعیین کننده را اعمال کنید)
- برنامه شور {alpha_t} کنترل یک نوع از دمای حرکت
- آموزش با استفاده از تخمین مونت کارلو برای نزدیک شدن به ELBO (دليل در پایین)
- نمونه گیری اجداد در مدل های انتشار یک زنجیره مارکوف است (هر مرحله فقط به وضعیت فعلی بستگی دارد)

کل فرآیند تولید تصویر نمونه گیری تکراری است: از صدا شروع کنید و در هر مرحله، نسخه کمی کمتر شور را که بر اساس مدل شنیدن است، نمونه کنید.

```figure
monte-carlo-pi
```

## آن را بسازید

### مرحله ی ۱: نمونه گیری یکسانی و معکوس CDF

```python
import math
import random

def sample_uniform(a, b):
    return a + (b - a) * random.random()

def sample_exponential_inverse_cdf(lam):
    u = random.random()
    return -math.log(u) / lam
```

10 هزار نمونه نمایی را تولید کنید و متوسط را 1/lambda تأیید کنید.

### مرحله دوم: نمونه گیری رد

```python
def rejection_sample(target_pdf, proposal_sample, proposal_pdf, M):
    while True:
        x = proposal_sample()
        u = random.random()
        if u < target_pdf(x) / (M * proposal_pdf(x)):
            return x
```

از نمونه گیری رد استفاده کنید تا از توزیع معمولی کوتاه شده استفاده کنید. شکل را با هیستوگرافی نمونه ها بررسی کنید.

### مرحله سوم: نمونه گیری اهمیت

```python
def importance_sampling_estimate(f, target_pdf, proposal_pdf, proposal_sample, n):
    total = 0
    for _ in range(n):
        x = proposal_sample()
        w = target_pdf(x) / proposal_pdf(x)
        total += f(x) * w
    return total / n
```

تخمین E[X^2] را با استفاده از یک پیشنهاد یکسانی در یک توزیع طبیعی تخمین بزنید. با پاسخ شناخته شده (mu^2 + sigma^2) مقایسه کنید.

### مرحله 4: تخمین مونت کارلو از pi

```python
def monte_carlo_pi(n):
    inside = 0
    for _ in range(n):
        x = random.uniform(-1, 1)
        y = random.uniform(-1, 1)
        if x*x + y*y <= 1:
            inside += 1
    return 4 * inside / n
```

### مرحله 5: میترپولیس-هستینگز MCMC

```python
def metropolis_hastings(target_log_pdf, proposal_sample, proposal_log_pdf, x0, n_samples, burn_in):
    samples = []
    x = x0
    for i in range(n_samples + burn_in):
        x_new = proposal_sample(x)
        log_alpha = (target_log_pdf(x_new) + proposal_log_pdf(x, x_new)
                     - target_log_pdf(x) - proposal_log_pdf(x_new, x))
        if math.log(random.random()) < log_alpha:
            x = x_new
        if i >= burn_in:
            samples.append(x)
    return samples
```

نمونه از توزیع بیمودالی (مکسله دو گاسیان) ، مسیر زنجیره را تصور کنید.

### مرحله 6: نمونه گیری گیبز

```python
def gibbs_sampling_2d(conditional_x_given_y, conditional_y_given_x, x0, y0, n_samples, burn_in):
    x, y = x0, y0
    samples = []
    for i in range(n_samples + burn_in):
        x = conditional_x_given_y(y)
        y = conditional_y_given_x(x)
        if i >= burn_in:
            samples.append((x, y))
    return samples
```

### مرحله 7: نمونه گیری دمای

```python
def softmax(logits):
    max_l = max(logits)
    exps = [math.exp(z - max_l) for z in logits]
    total = sum(exps)
    return [e / total for e in exps]

def temperature_sample(logits, temperature):
    scaled = [z / temperature for z in logits]
    probs = softmax(scaled)
    return sample_from_probs(probs)
```

نشان دهید که چگونه دمای توزیع خروجی برای مجموعه ای از logits رمزنگاری تغییر می کند.

### مرحله 8: نمونه گیری از بالا و بالا

```python
def top_k_sample(logits, k):
    indexed = sorted(enumerate(logits), key=lambda x: -x[1])
    top = indexed[:k]
    top_logits = [l for _, l in top]
    probs = softmax(top_logits)
    idx = sample_from_probs(probs)
    return top[idx][0]

def top_p_sample(logits, p):
    probs = softmax(logits)
    indexed = sorted(enumerate(probs), key=lambda x: -x[1])
    cumsum = 0
    selected = []
    for token_idx, prob in indexed:
        cumsum += prob
        selected.append((token_idx, prob))
        if cumsum >= p:
            break
    sel_probs = [pr for _, pr in selected]
    total = sum(sel_probs)
    sel_probs = [pr / total for pr in sel_probs]
    idx = sample_from_probs(sel_probs)
    return selected[idx][0]
```

### مرحله 9: ترفند اصلاح

```python
def reparam_sample(mu, sigma):
    epsilon = random.gauss(0, 1)
    return mu + sigma * epsilon

def reparam_gradient(mu, sigma, epsilon):
    dz_dmu = 1.0
    dz_dsigma = epsilon
    return dz_dmu, dz_dsigma
```

نشان دهید که گرادینت ها از طریق نمونه بازسازی شده جریان دارند اما نه از طریق نمونه گیری مستقیم.

### مرحله 10: Gumbel-Softmax

```python
def gumbel_sample():
    u = random.random()
    return -math.log(-math.log(u))

def gumbel_softmax(logits, temperature):
    gumbels = [math.log(p) + gumbel_sample() for p in logits]
    return softmax([g / temperature for g in gumbels])
```

نشان دهید که چگونه کاهش دمای باعث می شود که خروجی به یک ویکتور یک گرم نزدیک شود.

پیاده سازی کامل با تمام تصویرسازی ها در حال انجام است `code/sampling.py`. .

## ازش استفاده کن

با NumPy و SciPy، نسخه های تولید:

```python
import numpy as np

rng = np.random.default_rng(42)

exponential_samples = rng.exponential(scale=2.0, size=10000)
print(f"Exponential mean: {exponential_samples.mean():.4f} (expected 2.0)")

from scipy import stats
normal = stats.norm(loc=0, scale=1)
print(f"CDF at 1.96: {normal.cdf(1.96):.4f}")
print(f"Inverse CDF at 0.975: {normal.ppf(0.975):.4f}")

logits = np.array([2.0, 1.0, 0.5, 0.1, -1.0])
temperature = 0.7
scaled = logits / temperature
probs = np.exp(scaled - scaled.max()) / np.exp(scaled - scaled.max()).sum()
token = rng.choice(len(logits), p=probs)
print(f"Sampled token index: {token}")
```

برای MCMC در مقیاس، از کتابخانه های اختصاصی استفاده کنید:
- PyMC: مدل سازی کامل باایزی با NUTS (HMC سازگار)
- emcee: نمونه گیری MCMC
- NumPyro/JAX: MCMC با GPU سرعت

تو اينها رو از ابتدا ساختي حالا ميدوني که تماس هاي کتابخانه چيکار ميکنن

## تمرینات

1. نمونه گیری CDF معکوس را برای توزیع Cauchy اجرا کنید. CDF F(x) = 0.5 + arctan(x) /pi است. 10,000 نمونه تولید کنید و هیستوگراف را با PDF واقعی نشان دهید. ذرات سنگین را مشاهده کنید (قیمت های شدید دور از مرکز).

2. از نمونه گیری رد برای تولید نمونه از توزیع Beta ((2, 5) با استفاده از یک پیشنهاد یونیفورم ((0, 1) استفاده کنید. نمونه های پذیرفته شده را با PDF واقعی Beta نقشه بزنید. نرخ پذیرش نظری چیست؟

3. یک عدد کامل از sin ((x) را از 0 تا pi با استفاده از مونت کارلو با نمونه های 1000، 10000 و 100،000 تخمین بزنید. خطای هر سطح را مقایسه کنید. بررسی کنید که مقیاس خطای O(1/sqrt(N)).

4. پیاده سازی Metropolis-Hastings برای نمونه گیری از توزیع 2D p ((x, y) متناسب با exp ((-(x^2 * y^2 + x^2 + y^2 - 8*x - 8*y) / 2). نمونه ها و مسیر زنجیره را نقشه برداری کنید. با انحرافات استاندارد پیشنهادی مختلف آزمایش کنید.

5. ساخت یک نمایش کامل تولید متن: با توجه به یک لغت 10 کلمه با logits، تولید تسلسل 20 توکن با استفاده از (a) طمع، (b) دمای=0.7، (c) top-k=3, (d) top-p=0.9. مقایسه تنوع خروجی در 5 اجرا.

## اصطلاحات کلیدی

| Term | What people say | What it actually means |
|------|----------------|----------------------|
| Sampling | "Drawing random values" | Generating values according to a probability distribution. The mechanism behind all generative AI |
| Uniform distribution | "All equally likely" | Every value in [a, b] has equal probability density 1/(b-a). The starting point for all sampling methods |
| Inverse CDF | "Probability transform" | F_inverse(U) converts a uniform sample into a sample from any distribution with known CDF. Exact and efficient |
| Rejection sampling | "Propose and accept/reject" | Generate from a simple proposal, accept with probability proportional to target/proposal ratio. Exact but wastes samples |
| Importance sampling | "Reweight samples" | Estimate expectations under p(x) using samples from q(x) by weighting each sample by p(x)/q(x). Core to PPO in RL |
| Monte Carlo | "Average random samples" | Approximate integrals as sample averages. Error O(1/sqrt(N)) regardless of dimension |
| MCMC | "Random walk that converges" | Construct a Markov chain whose stationary distribution is the target. Metropolis-Hastings is the foundational algorithm |
| Metropolis-Hastings | "Accept uphill, sometimes downhill" | Propose moves, accept based on density ratio. Detailed balance ensures convergence to target distribution |
| Gibbs sampling | "One variable at a time" | Update each variable from its conditional distribution holding others fixed. 100% acceptance rate |
| Temperature | "Confidence knob" | Divides logits by T before softmax. T<1 sharpens (more confident), T>1 flattens (more diverse) |
| Top-k sampling | "Keep the k best" | Zero out all but the k highest-probability tokens, renormalize, sample. Fixed candidate set size |
| Nucleus sampling (top-p) | "Keep the probable ones" | Keep the smallest set of tokens whose cumulative probability exceeds p. Adaptive candidate set size |
| Reparameterization trick | "Move randomness outside" | Write z = mu + sigma * epsilon where epsilon ~ N(0,1). Makes sampling differentiable. Essential for VAE training |
| Gumbel-Softmax | "Soft categorical sampling" | Differentiable approximation to categorical sampling using Gumbel noise + softmax with temperature |
| Stratified sampling | "Forced coverage" | Divide sample space into strata, sample from each. Always lower variance than naive Monte Carlo |
| Burn-in | "Warm-up period" | Initial MCMC samples discarded before the chain reaches its stationary distribution |
| Detailed balance | "Reversibility condition" | p(x) * T(x->y) = p(y) * T(y->x). Sufficient condition for p to be the stationary distribution of a Markov chain |
| Diffusion sampling | "Iterative denoising" | Generate data by starting from noise and applying learned denoising steps. Each step is a conditional sampling operation |

## خواندن بیشتر

- [Holbrook (2023): The Metropolis-Hastings Algorithm](https://arxiv.org/abs/2304.07010)- آموزش دقیق در مورد پایه های MCMC
- [Jang, Gu, Poole (2017): Categorical Reparameterization with Gumbel-Softmax](https://arxiv.org/abs/1611.01144)- کاغذ اصلی Gumbel-Softmax
- [Holtzman et al. (2020): The Curious Case of Neural Text Degeneration](https://arxiv.org/abs/1904.09751)- کاغذ نمونه گیری هسته (در بالا)
- [Kingma & Welling (2014): Auto-Encoding Variational Bayes](https://arxiv.org/abs/1312.6114)- ورق VAE که راه حل اصلاحات را معرفی می کند
- [Ho, Jain, Abbeel (2020): Denoising Diffusion Probabilistic Models](https://arxiv.org/abs/2006.11239)- DDPM نمونه گیری را با تولید تصویر متصل می کند
