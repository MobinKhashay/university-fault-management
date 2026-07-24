<div align="center">

# 🏛️ سامانه هوشمند گزارش و مدیریت خرابی‌های دانشگاه ارومیه

### University Fault Management System

**پروژه درس مهندسی نرم‌افزار ۲ — دانشگاه ارومیه — نیمسال ۱۴۰۴-۱۴۰۵/۲**

[![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)](https://python.org)
[![Django](https://img.shields.io/badge/Django-4.2-green?logo=django)](https://djangoproject.com)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

</div>

---

## 📋 فهرست مطالب

- [درباره پروژه](#-درباره-پروژه)
- [ویژگی‌ها](#-ویژگیها)
- [معماری سیستم](#-معماری-سیستم)
- [تکنولوژی‌ها](#-تکنولوژیها)
- [پیش‌نیازها](#-پیشنیازها)
- [نصب و راه‌اندازی](#-نصب-و-راهاندازی)
- [ساختار پروژه](#-ساختار-پروژه)
- [نقش‌های کاربری](#-نقشهای-کاربری)
- [API Endpoints](#-api-endpoints)
- [متدولوژی توسعه](#-متدولوژی-توسعه)
- [امنیت](#-امنیت)
- [تست](#-تست)
- [تیم توسعه](#-تیم-توسعه)

---

## 🎯 درباره پروژه

سامانه هوشمند گزارش و مدیریت خرابی‌های دانشگاه ارومیه یک سیستم تحت وب است که فرآیند **گزارش‌دهی، ارجاع و پیگیری خرابی‌ها** را در سطح دانشگاه به صورت هوشمند مدیریت می‌کند.

### مسئله‌ای که حل می‌کند:
- گزارش‌دهی سنتی خرابی‌ها (تلفنی/حضوری) کند و بدون پیگیری است
- تخصیص تکنسین‌ها به صورت دستی و غیربهینه انجام می‌شود
- گزارش‌دهنده از وضعیت تعمیر بی‌خبر می‌ماند
- آمار و اطلاعاتی برای تصمیم‌گیری مدیریتی وجود ندارد

### راه‌حل:
این سامانه با **موتور ارجاع هوشمند** بر اساس تخصص، شیفت کاری و بار کاری تکنسین‌ها، بهترین فرد را برای هر خرابی انتخاب و ارجاع می‌دهد. گزارش‌دهنده می‌تواند وضعیت تعمیر را لحظه‌به‌لحظه پیگیری کند و پس از اتمام، کیفیت کار را امتیازدهی نماید.

---

## ⭐ ویژگی‌ها

### 👤 گزارش‌دهنده (دانشجو / استاد / کارمند)
- ✅ ثبت‌نام با تایید ایمیل + احراز هویت با کارت شناسایی
- ✅ ورود امن با Remember Me + قفل اکانت + کپچای ریاضی
- ✅ بازیابی رمز عبور با کد امنیتی یکبارمصرف
- ✅ ثبت گزارش خرابی با مکان سلسله‌مراتبی (AJAX)
- ✅ پیشنهاد هوشمند سطح فوریت بر اساس کلمات کلیدی
- ✅ تشخیص گزارش تکراری با پیش‌نمایش پاپ‌آپ
- ✅ آپلود تصویر (حداکثر ۳) + ویدیو + فایل صوتی
- ✅ پیش‌نمایش گزارش قبل از ارسال
- ✅ داشبورد با KPI و لیست گزارش‌ها
- ✅ پیگیری وضعیت و پیام‌رسانی با تکنسین
- ✅ امتیازدهی ستاره‌ای پس از تعمیر
- ✅ ویرایش پروفایل + تغییر رمز عبور داینامیک
- ✅ سوالات متداول (FAQ) با لایک/دیسلایک AJAX
- ✅ سیستم اعلان‌ها با فیلتر خوانده/نخوانده

### 🔧 تکنسین
- ✅ داشبورد با آمار، تب‌های تسک (جدید/درحال‌انجام/معلق)
- ✅ سوییچ وضعیت حضور (آماده/مشغول/پایان شیفت) — AJAX
- ✅ مدیریت تسک: شروع → رفتن به محل → تایید حضور → اتمام
- ✅ تعلیق تسک با دلیل + گزینه «سایر» با توضیح
- ✅ ازسرگیری تسک معلق
- ✅ درخواست قطعه
- ✅ آپلود عکس بعد از تعمیر
- ✅ پیام‌رسانی با گزارش‌دهنده (متن + پیوست)
- ✅ صفحه وظایف من با جستجو، فیلتر و تب‌ها
- ✅ تاریخچه کارها با فیلتر زمانی و امتیاز

### 👨‍💼 مدیر سیستم
- ✅ داشبورد با KPI زنده + نمودار Doughnut/Bar (Chart.js)
- ✅ مدیریت گزارش‌ها (جستجو، فیلتر، تغییر تکنسین، لغو، تغییر اولویت)
- ✅ جزئیات گزارش با خط زمانی (AJAX Modal)
- ✅ مدیریت تکنسین‌ها (ثبت، ویرایش، فعال/غیرفعال، ریست رمز)
- ✅ کنترل دستی وضعیت حضور تکنسین
- ✅ کارتابل تکنسین (تسک‌های فعال + تکمیل‌شده)
- ✅ مدیریت کاربران (جستجو، فیلتر نقش/وضعیت، فعال/غیرفعال)
- ✅ تایید هویت کاربران (مشاهده کارت شناسایی + تایید/رد)
- ✅ آمار و گزارش‌گیری با فیلتر زمانی + رتبه‌بندی تکنسین‌ها + نقاط بحرانی
- ✅ خروجی Excel (openpyxl) و PDF (reportlab)
- ✅ مدیریت FAQ (ایجاد/حذف)
- ✅ تنظیمات ساختار دانشگاه (دانشکده/ساختمان/مکان/تخصص/دسته‌بندی)
- ✅ تایید/رد درخواست قطعه

### 🤖 سیستم هوشمند
- ✅ موتور ارجاع خودکار (AssignmentEngine) بر اساس تخصص + شیفت + بار کاری
- ✅ صف انتظار برای زمانی که تکنسین مناسب در دسترس نیست
- ✅ بسته‌شدن خودکار تیکت پس از ۷۲ ساعت بدون واکنش (+ ثبت ۵ ستاره)
- ✅ پاکسازی خودکار اعلان‌های خوانده‌شده بعد از ۳۰ روز
- ✅ بروزرسانی خودکار آمار داشبورد هر ۶۰ ثانیه

---

## 🏗️ معماری سیستم

```
┌─────────────────────────────────────────────┐
│              Client (Browser)                │
│         HTML/CSS/JS + Chart.js               │
└──────────────────┬──────────────────────────┘
                   │ HTTP/AJAX
┌──────────────────▼──────────────────────────┐
│              Django 4.2 (MTV)                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ accounts │  │ reports  │  │technicians│   │
│  └──────────┘  └──────────┘  └──────────┘   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │admin_panel│  │  notifs  │  │   faq    │   │
│  └──────────┘  └──────────┘  └──────────┘   │
│                                              │
│  ┌────────────────────────────────────────┐  │
│  │        AssignmentEngine (Smart)        │  │
│  └────────────────────────────────────────┘  │
└──────────────────┬──────────────────────────┘
                   │ ORM
┌──────────────────▼──────────────────────────┐
│              SQLite3 Database                │
│              17 Models/Tables                │
└─────────────────────────────────────────────┘
```

---

## 🛠️ تکنولوژی‌ها

| لایه | تکنولوژی |
|------|----------|
| Backend | Python 3.12 + Django 4.2 |
| Frontend | HTML5 + CSS3 + JavaScript (Vanilla) |
| Database | SQLite3 |
| Charts | Chart.js 4.4 |
| Export | openpyxl (Excel) + reportlab (PDF) |
| Version Control | Git + GitHub (GitHub Flow) |
| Authentication | Django Auth + Custom Backends |

---

## 📦 پیش‌نیازها

- Python 3.10+
- pip
- Git

---

## 🚀 نصب و راه‌اندازی

### ۱. کلون کردن ریپوزیتوری
```bash
git clone https://github.com/MobinKhashay/university-fault-management.git
cd university-fault-management
```

### ۲. ساخت محیط مجازی
```bash
python -m venv venv
```

فعال‌سازی:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### ۳. نصب وابستگی‌ها
```bash
pip install -r requirements.txt
```

### ۴. اجرای مایگریشن‌ها
```bash
python manage.py makemigrations
python manage.py migrate
```

### ۵. ساخت ادمین
```bash
python manage.py createsuperuser
```

### ۶. اجرای سرور
```bash
python manage.py runserver
```

### ۷. دسترسی
```
سامانه:        http://127.0.0.1:8000/
پنل ادمین:     http://127.0.0.1:8000/django-admin/
```

### ۸. داده‌های اولیه (از Django Admin)
1. `Specialty` (تخصص): برق، لوله‌کشی، تجهیزات کلاس، آی‌تی، تهویه
2. `FaultCategory` (دسته‌بندی خرابی): هر کدام متصل به تخصص مربوطه
3. `Faculty` (دانشکده): دانشکده فنی، علوم، ادبیات
4. `Building` (ساختمان): متصل به دانشکده
5. `Location` (مکان): طبقه و اتاق متصل به ساختمان

---

## 📁 ساختار پروژه

```
university-fault-management/
├── config/                     # تنظیمات Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/                   # مدیریت کاربران و احراز هویت
│   ├── models.py               # User, EmailVerification, PasswordResetToken
│   ├── views.py                # register, login, logout, password_reset
│   ├── forms.py                # RegistrationForm, LoginForm, ...
│   ├── backends.py             # StudentIDBackend
│   ├── profile_views.py        # profile_view
│   └── profile_forms.py        # ProfileForm, ChangePasswordForm
├── reports/                    # گزارش‌ها و ارجاع
│   ├── models.py               # Report, ReportMedia, RepairLog, TicketMessage, ...
│   ├── views.py                # submit, dashboard, my_reports, detail, rate, message
│   ├── forms.py                # ReportForm
│   ├── assignment_engine.py    # AssignmentEngine (موتور ارجاع هوشمند)
│   └── management/commands/    # auto_close_tickets, process_queue
├── technicians/                # پنل تکنسین
│   ├── models.py               # Technician
│   └── views.py                # dashboard, task_detail, start, complete, suspend, resume
├── admin_panel/                # پنل مدیر
│   ├── views.py                # dashboard, manage_reports, statistics, export, users
│   ├── forms.py                # TechnicianRegistrationForm
│   └── structure_views.py      # structure_settings, add/delete faculty/building/...
├── notifications/              # سیستم اعلان‌ها
│   ├── models.py               # Notification
│   ├── views.py                # list, mark_read, mark_all_read, unread_count
│   └── management/commands/    # cleanup_notifications
├── faq/                        # سوالات متداول
│   ├── models.py               # FAQ, FAQVote
│   └── views.py                # list, vote, manage, create, delete
├── templates/                  # قالب‌های HTML
│   ├── base.html               # قالب پایه با navbar ریسپانسیو
│   ├── landing.html            # صفحه اصلی
│   ├── includes/pagination.html
│   ├── accounts/               # register, login, verify, reset, profile
│   ├── reports/                # dashboard, submit, my_reports, detail
│   ├── technicians/            # dashboard, task_detail, my_tasks, work_history
│   ├── admin_panel/            # dashboard, reports, technicians, statistics, users, structure
│   ├── notifications/          # notifications list
│   └── faq/                    # faq_list, faq_manage, faq_form
├── static/
│   ├── css/                    # main.css, auth.css, reports.css, admin.css, technician.css, faq.css
│   └── js/                     # submit_report.js, admin_reports.js, technician.js, notifications.js
├── tests/
│   └── test_accounts.py        # Unit Tests
├── docs/
│   ├── User Stories.pdf
│   ├── SRS-Document.pdf
│   ├── diagrams/               # Use Case, ER, Class Diagram
│   └── reports/                # Sprint 0-3 Reports
├── manage.py
├── requirements.txt
├── .gitignore
├── README.md
└── CONTRIBUTING.md
```

---

## 👥 نقش‌های کاربری

| نقش | دسترسی | نحوه ایجاد |
|-----|--------|-----------|
| دانشجو/استاد/کارمند | ثبت گزارش، پیگیری، امتیازدهی | ثبت‌نام از سایت |
| تکنسین | مدیریت تسک‌ها، تعمیر، پیام‌رسانی | ثبت توسط مدیر |
| مدیر سیستم | دسترسی کامل | `createsuperuser` |

---

## 🔗 API Endpoints

### Accounts (`/accounts/`)
| URL | متد | توضیح |
|-----|-----|-------|
| `/register/` | GET/POST | ثبت‌نام |
| `/login/` | GET/POST | ورود |
| `/logout/` | GET | خروج |
| `/verify-email/` | GET/POST | تایید ایمیل |
| `/password-reset/` | GET/POST | بازیابی رمز |
| `/profile/` | GET/POST | ویرایش پروفایل |

### Reports (`/reports/`)
| URL | متد | توضیح |
|-----|-----|-------|
| `/dashboard/` | GET | داشبورد گزارش‌دهنده |
| `/submit/` | GET/POST | ثبت گزارش |
| `/my-reports/` | GET | لیست گزارش‌ها |
| `/detail/<id>/` | GET | جزئیات گزارش |
| `/rate/<id>/` | POST | امتیازدهی |
| `/message/<id>/` | POST | ارسال پیام |
| `/ajax/buildings/` | GET | AJAX ساختمان‌ها |
| `/ajax/locations/` | GET | AJAX مکان‌ها |
| `/ajax/check-duplicate/` | GET | بررسی تکراری |

### Technicians (`/technicians/`)
| URL | متد | توضیح |
|-----|-----|-------|
| `/dashboard/` | GET | داشبورد تکنسین |
| `/my-tasks/` | GET | وظایف من |
| `/task/<id>/` | GET | جزئیات تسک |
| `/task/<id>/start/` | POST | شروع کار |
| `/task/<id>/complete/` | POST | اتمام کار |
| `/task/<id>/suspend/` | POST | تعلیق |
| `/task/<id>/resume/` | POST | ازسرگیری |
| `/toggle-status/` | POST | تغییر وضعیت حضور |
| `/history/` | GET | تاریخچه |

### Admin Panel (`/panel/`)
| URL | متد | توضیح |
|-----|-----|-------|
| `/dashboard/` | GET | داشبورد مدیر |
| `/reports/` | GET | مدیریت گزارش‌ها |
| `/technicians/` | GET | مدیریت تکنسین‌ها |
| `/users/` | GET | مدیریت کاربران |
| `/statistics/` | GET | آمار |
| `/structure/` | GET | تنظیمات ساختار |
| `/verify-users/` | GET | تایید هویت |
| `/export/excel/` | GET | خروجی اکسل |
| `/export/pdf/` | GET | خروجی PDF |

---

## 📊 متدولوژی توسعه

- **متدولوژی:** Agile / Scrum
- **اسپرینت‌ها:** ۴ اسپرینت ۱ هفته‌ای
- **ابزار مدیریت:** GitHub Projects
- **شاخه‌بندی:** GitHub Flow (`develop` + `feature/*` branches)
- **Commit Convention:** Conventional Commits (`feat:`, `fix:`, `docs:`)

| اسپرینت | هدف | SP |
|---------|-----|-----|
| Sprint 0 | مستندات + راه‌اندازی | 35 |
| Sprint 1 | احراز هویت + ثبت گزارش + پنل مدیر + ارجاع خودکار | 36 |
| Sprint 2 | پنل تکنسین + اعلان‌ها + داشبورد گزارش‌دهنده + آمار | 23 |
| Sprint 3 | تکمیل + تست + باگ‌فیکس + تحویل | 34 |
| **مجموع** | | **128** |

---

## 🔒 امنیت

| تهدید | راه‌حل |
|-------|--------|
| CSRF | Django CSRF Middleware |
| Brute Force | Account Lockout (۵ تلاش) + IP Block (۳ قفل) |
| Bot | کپچای ریاضی پس از ۳ تلاش ناموفق |
| Password | PBKDF2 Hashing + Strength Checker |
| Session Hijacking | Secure Cookie + Session Expiry |
| Rate Limiting | ۳ درخواست بازیابی در ساعت (per user + per IP) |
| Input Validation | Django Forms + Server-side Validation |
| XSS | Django Auto-escaping Templates |

---

## 🧪 تست

```bash
python manage.py test tests/
```

### پوشش تست:
- ✅ ثبت‌نام (موفق، ایمیل تکراری، رمز ضعیف، عدم تطابق رمز)
- ✅ ورود (موفق، رمز اشتباه، کاربر نامعتبر، کاربر تایید نشده)
- ✅ بازیابی رمز (ایمیل، شماره دانشجویی، کاربر ناموجود)
- ✅ مدل User (ایجاد، superuser، properties نقش)

---

## 👨‍💻 تیم توسعه

| نقش | نام |
|-----|-----|
| Product Owner | [نام] |
| Scrum Master | [نام] |
| Backend Developer | MobinKhashay |
| Frontend Developer 1 | [نام] |
| Frontend Developer 2 | [نام] |

---

## 📄 مستندات

| سند | توضیح |
|-----|-------|
| [User Stories](docs/User%20Stories.pdf) | ۲۳ داستان کاربری |
| [SRS Document](docs/SRS-Document.pdf) | سند نیازمندی‌ها (IEEE 830) |
| [Sprint 0 Report](docs/reports/Sprint%200%20Document.pdf) | گزارش اسپرینت ۰ |
| [Sprint 1 Report](docs/reports/Sprint_1_Report.pdf) | گزارش اسپرینت ۱ |
| [Sprint 2 Report](docs/reports/sprint2-report.pdf) | گزارش اسپرینت ۲ |
| [Sprint 3 Report](docs/reports/Sprint_3_Report.docx) | گزارش اسپرینت ۳ |

---

## 📜 لایسنس

This project is licensed under the MIT License.

---

<div align="center">

**ساخته شده با ❤️ در دانشگاه ارومیه**

</div>
