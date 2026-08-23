"""
مول المكتبة MallMaktaba
منصة طلب الكتب والمستلزمات المدرسية
"""

from flask import Flask, render_template_string, request, redirect, url_for, session, flash, jsonify
import json
import os
import hashlib
import urllib.parse
import re
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'mall-maktaba-secret-key-2024'

# ======================== البيانات ========================

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = hashlib.sha256('admin123456'.encode()).hexdigest()
SITE_NAME = 'مول المكتبة MallMaktaba'
WHATSAPP_NUMBER = '212600000000'
PLATFORM_PROFIT = 15

CITIES = ['أكادير', 'إنزكان', 'أيت ملول', 'الدشيرة الجهادية', 'القليعة', 'أولاد تايمة', 'تارودانت', 'بيوكرى', 'تيزنيت']

# ======================== البيانات ========================

DATA_FILE = 'data/libraries.json'

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'libraries': [], 'orders': [], 'next_id': 1}

def save_data(data):
    os.makedirs('data', exist_ok=True)
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_libraries():
    data = load_data()
    return data.get('libraries', [])

def get_orders():
    data = load_data()
    return data.get('orders', [])

def save_libraries(libraries):
    data = load_data()
    data['libraries'] = libraries
    save_data(data)

def save_order(order):
    data = load_data()
    if 'orders' not in data:
        data['orders'] = []
    data['orders'].append(order)
    save_data(data)

def get_next_id():
    data = load_data()
    next_id = data.get('next_id', 1)
    data['next_id'] = next_id + 1
    save_data(data)
    return next_id

# ======================== تهيئة المكتبات ========================

def init_libraries():
    libraries = get_libraries()
    if not libraries:
        default_libraries = [
            {'id': 1, 'name': 'مكتبة إفران', 'phone': '212611111111', 'email': 'lib_ifran@email.com', 'city': 'أكادير', 'address': 'حي الهدى', 'status': 'pending', 'profit': 0},
            {'id': 2, 'name': 'مكتبة الموكار', 'phone': '212622222222', 'email': 'lib_mokar@email.com', 'city': 'أكادير', 'address': 'تالبرجت', 'status': 'pending', 'profit': 0},
            {'id': 3, 'name': 'مكتبة دار سوس', 'phone': '212633333333', 'email': 'lib_darsouss@email.com', 'city': 'أكادير', 'address': 'حي الداخلة', 'status': 'pending', 'profit': 0},
            {'id': 4, 'name': 'مكتبة يثرب', 'phone': '212644444444', 'email': 'lib_yathrib@email.com', 'city': 'أكادير', 'address': 'حي السلام', 'status': 'pending', 'profit': 0},
            {'id': 5, 'name': 'المكتبة الكبرى', 'phone': '212655555555', 'email': 'lib_kobra@email.com', 'city': 'أكادير', 'address': 'حي السلام', 'status': 'pending', 'profit': 0},
            {'id': 6, 'name': 'مكتبة المدارس', 'phone': '212655555556', 'email': 'lib_madaris@email.com', 'city': 'إنزكان', 'address': 'وسط المدينة', 'status': 'pending', 'profit': 0},
            {'id': 7, 'name': 'مكتبة القدس', 'phone': '212666666667', 'email': 'lib_quds@email.com', 'city': 'إنزكان', 'address': 'وسط المدينة', 'status': 'pending', 'profit': 0},
            {'id': 8, 'name': 'مكتبة أجيال', 'phone': '212677777778', 'email': 'lib_ajyal@email.com', 'city': 'إنزكان', 'address': 'وسط المدينة', 'status': 'pending', 'profit': 0},
            {'id': 9, 'name': 'مكتبة الخوارزمي', 'phone': '212688888889', 'email': 'lib_khawarizmi@email.com', 'city': 'إنزكان', 'address': 'الجهادية', 'status': 'pending', 'profit': 0},
            {'id': 10, 'name': 'مكتبة إيمجار', 'phone': '212699999990', 'email': 'lib_imjar@email.com', 'city': 'إنزكان', 'address': 'حي بام تراست', 'status': 'pending', 'profit': 0},
            {'id': 11, 'name': 'مكتبة لجينكوس', 'phone': '212655555557', 'email': 'lib_lajinkos@email.com', 'city': 'أيت ملول', 'address': 'وسط المدينة', 'status': 'pending', 'profit': 0},
            {'id': 12, 'name': 'مكتبة أوراق ابطان', 'phone': '212666666668', 'email': 'lib_awraq@email.com', 'city': 'أيت ملول', 'address': 'وسط المدينة', 'status': 'pending', 'profit': 0},
            {'id': 13, 'name': 'مكتبة أيت ملول مكتب', 'phone': '212677777779', 'email': 'lib_aitmelloul@email.com', 'city': 'أيت ملول', 'address': 'وسط المدينة', 'status': 'pending', 'profit': 0},
            {'id': 14, 'name': 'المكتبة العصرية', 'phone': '212688888880', 'email': 'lib_asria@email.com', 'city': 'أيت ملول', 'address': 'وسط المدينة', 'status': 'pending', 'profit': 0},
            {'id': 15, 'name': 'مكتبة الكون الدشيرة', 'phone': '212611111114', 'email': 'lib_kawn@email.com', 'city': 'الدشيرة الجهادية', 'address': 'وسط المدينة', 'status': 'pending', 'profit': 0},
            {'id': 16, 'name': 'مكتبة الفصيح', 'phone': '212622222225', 'email': 'lib_faseeh@email.com', 'city': 'القليعة', 'address': 'وسط المدينة', 'status': 'pending', 'profit': 0},
            {'id': 17, 'name': 'مكتبة الطالب', 'phone': '212633333336', 'email': 'lib_talib@email.com', 'city': 'أولاد تايمة', 'address': 'وسط المدينة', 'status': 'pending', 'profit': 0},
            {'id': 18, 'name': 'مكتبة القدس', 'phone': '212644444447', 'email': 'lib_quds_oulad@email.com', 'city': 'أولاد تايمة', 'address': 'وسط المدينة', 'status': 'pending', 'profit': 0},
            {'id': 19, 'name': 'مكتبة سرتي', 'phone': '212655555558', 'email': 'lib_sirti@email.com', 'city': 'تارودانت', 'address': 'وسط المدينة', 'status': 'pending', 'profit': 0},
            {'id': 20, 'name': 'مكتبة الفضاء الحر', 'phone': '212666666669', 'email': 'lib_fadaa@email.com', 'city': 'تارودانت', 'address': 'وسط المدينة', 'status': 'pending', 'profit': 0},
            {'id': 21, 'name': 'مكتبة القدس', 'phone': '212677777780', 'email': 'lib_quds_taroudant@email.com', 'city': 'تارودانت', 'address': 'وسط المدينة', 'status': 'pending', 'profit': 0},
            {'id': 22, 'name': 'مكتبة السرتي', 'phone': '212688888881', 'email': 'lib_sirti2@email.com', 'city': 'تارودانت', 'address': 'قرب الجامع الكبير', 'status': 'pending', 'profit': 0},
            {'id': 23, 'name': 'مكتبة اشتوكة', 'phone': '212699999992', 'email': 'lib_chtouka@email.com', 'city': 'بيوكرى', 'address': 'وسط المدينة', 'status': 'pending', 'profit': 0},
            {'id': 24, 'name': 'مكتبة الإمام الجزولي', 'phone': '212610101013', 'email': 'lib_jazouli@email.com', 'city': 'بيوكرى', 'address': 'وسط المدينة', 'status': 'pending', 'profit': 0},
            {'id': 25, 'name': 'مكتبة القلم', 'phone': '212611111115', 'email': 'lib_alam@email.com', 'city': 'بيوكرى', 'address': 'وسط المدينة', 'status': 'pending', 'profit': 0},
            {'id': 26, 'name': 'مكتبة ابلحوس', 'phone': '212622222226', 'email': 'lib_ablhouss@email.com', 'city': 'بيوكرى', 'address': 'وسط المدينة', 'status': 'pending', 'profit': 0},
            {'id': 27, 'name': 'مكتبة الشيخ ماء العينين', 'phone': '212633333337', 'email': 'lib_maain@email.com', 'city': 'تيزنيت', 'address': 'وسط المدينة', 'status': 'pending', 'profit': 0},
            {'id': 28, 'name': 'مكتبة العهد الجديد', 'phone': '212644444448', 'email': 'lib_ahd@email.com', 'city': 'تيزنيت', 'address': 'وسط المدينة', 'status': 'pending', 'profit': 0},
            {'id': 29, 'name': 'مكتبة سوس العالمة', 'phone': '212655555559', 'email': 'lib_souss_alima@email.com', 'city': 'تيزنيت', 'address': 'وسط المدينة', 'status': 'pending', 'profit': 0},
            {'id': 30, 'name': 'مكتبة ابن رشد', 'phone': '212666666670', 'email': 'lib_ibnrushd@email.com', 'city': 'تيزنيت', 'address': 'وسط المدينة', 'status': 'pending', 'profit': 0},
            {'id': 31, 'name': 'مكتبة الهاشم', 'phone': '212677777781', 'email': 'lib_hachim@email.com', 'city': 'تيزنيت', 'address': 'وسط المدينة', 'status': 'pending', 'profit': 0},
            {'id': 32, 'name': 'مكتبة ساحة المشور', 'phone': '212688888882', 'email': 'lib_machwar@email.com', 'city': 'تيزنيت', 'address': 'ساحة المشور', 'status': 'pending', 'profit': 0},
        ]
        data = load_data()
        data['libraries'] = default_libraries
        data['next_id'] = 33
        save_data(data)
        return default_libraries
    return libraries

# ======================== القوالب ========================

BASE_TEMPLATE = '''
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}{{ site_name }}{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root { --primary: #1a2a3a; --secondary: #e67e22; }
        body { font-family: 'Tahoma', 'Segoe UI', sans-serif; background: #f0f2f5; min-height: 100vh; display: flex; flex-direction: column; }
        main { flex: 1; }
        .navbar { background: var(--primary) !important; padding: 15px 0; }
        .navbar-brand span { color: var(--secondary); }
        .btn-primary { background: var(--secondary); border: none; }
        .btn-primary:hover { background: #d35400; }
        .btn-success { background: #27ae60; border: none; }
        .btn-success:hover { background: #1e8449; }
        .btn-danger { background: #e74c3c; border: none; }
        .btn-danger:hover { background: #c0392b; }
        .btn-info { background: #3498db; border: none; color: white; }
        .btn-info:hover { background: #2980b9; color: white; }
        .card { border-radius: 15px; border: none; box-shadow: 0 5px 20px rgba(0,0,0,0.08); }
        .card-header { background: var(--primary); color: white; border-radius: 15px 15px 0 0 !important; }
        .form-control, .form-select { border-radius: 10px; padding: 12px 15px; }
        .form-control:focus, .form-select:focus { border-color: var(--secondary); box-shadow: 0 0 0 0.2rem rgba(230,126,34,0.25); }
        .alert { border-radius: 10px; border: none; }
        .footer { background: var(--primary); color: white; padding: 20px 0; margin-top: 30px; }
        .footer span { color: var(--secondary); }
        .stat-card { background: white; border-radius: 12px; padding: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.08); transition: transform 0.3s; }
        .stat-card:hover { transform: translateY(-5px); }
        .stat-card .number { font-size: 2.5rem; font-weight: 800; }
        .badge-pending { background: #f39c12; }
        .badge-approved { background: #27ae60; }
        .badge-rejected { background: #e74c3c; }
        .badge-invited { background: #3498db; }
        .sidebar { background: var(--primary); min-height: 100vh; }
        .sidebar .nav-link { color: rgba(255,255,255,0.8); padding: 12px 20px; border-right: 3px solid transparent; }
        .sidebar .nav-link:hover { background: rgba(255,255,255,0.05); color: white; }
        .sidebar .nav-link.active { background: rgba(255,255,255,0.1); color: white; border-right-color: var(--secondary); }
        .sidebar .nav-link i { width: 25px; }
        .login-card { max-width: 400px; margin: 50px auto; }
        @media (max-width: 768px) { .display-4 { font-size: 2.5rem; } }
        @keyframes fadeInUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }
        .animated { animation: fadeInUp 0.5s ease; }
    </style>
    {% block extra_css %}{% endblock %}
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container">
            <a class="navbar-brand" href="{{ url_for('index') }}">
                <i class="fas fa-book"></i> <span>مول المكتبة</span> <small style="color:#888;">MallMaktaba</small>
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('index') }}"><i class="fas fa-home"></i> الرئيسية</a></li>
                    <li class="nav-item"><a class="nav-link" href="#order-form"><i class="fas fa-plus-circle"></i> طلب جديد</a></li>
                    {% if session.get('admin') %}
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="#" id="adminDropdown" role="button" data-bs-toggle="dropdown">
                            <i class="fas fa-user-shield"></i> لوحة التحكم
                        </a>
                        <ul class="dropdown-menu dropdown-menu-end">
                            <li><a class="dropdown-item" href="{{ url_for('admin_dashboard') }}"><i class="fas fa-chart-pie"></i> الرئيسية</a></li>
                            <li><a class="dropdown-item" href="{{ url_for('admin_libraries') }}"><i class="fas fa-store"></i> المكتبات</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item text-danger" href="{{ url_for('admin_logout') }}"><i class="fas fa-sign-out-alt"></i> خروج</a></li>
                        </ul>
                    </li>
                    {% else %}
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('admin_login') }}"><i class="fas fa-user-shield"></i> دخول المدير</a></li>
                    {% endif %}
                </ul>
            </div>
        </div>
    </nav>

    <main class="py-4">
        <div class="container">
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, message in messages %}
                        <div class="alert alert-{{ category }} alert-dismissible fade show">{{ message }}<button type="button" class="btn-close" data-bs-dismiss="alert"></button></div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
            {% block content %}{% endblock %}
        </div>
    </main>

    <footer class="footer text-center">
        <div class="container">
            <p class="mb-0"><i class="fas fa-book text-warning"></i> <span>مول المكتبة</span> MallMaktaba &copy; 2024</p>
        </div>
    </footer>

    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>setTimeout(() => $('.alert').fadeOut('slow'), 5000);</script>
    {% block extra_js %}{% endblock %}
</body>
</html>
'''

# ======================== المسارات ========================

@app.route('/')
def index():
    libraries = get_libraries()
    approved = len([l for l in libraries if l.get('status') == 'approved'])
    return render_template_string(BASE_TEMPLATE.replace('{% block content %}{% endblock %}', '''
    <div class="row justify-content-center">
        <div class="col-lg-8">
            <div class="text-center mb-5">
                <h1 class="display-4 fw-bold"><i class="fas fa-book-open text-primary"></i> <span style="color:#e67e22;">مول المكتبة</span></h1>
                <p class="lead">خدمة طلب الكتب والمستلزمات المدرسية</p>
                <div class="d-flex justify-content-center gap-2 flex-wrap">
                    <span class="badge bg-primary p-2"><i class="fas fa-check-circle"></i> طلب سريع</span>
                    <span class="badge bg-success p-2"><i class="fas fa-store"></i> ''' + str(approved) + ''' مكتبة متعاونة</span>
                    <span class="badge bg-info p-2"><i class="fab fa-whatsapp"></i> تواصل مباشر</span>
                    <span class="badge bg-warning p-2"><i class="fas fa-percent"></i> نسبة ربح ''' + str(PLATFORM_PROFIT) + '''%</span>
                </div>
            </div>

            <div class="card shadow-lg border-0" id="order-form">
                <div class="card-header bg-primary text-white"><h5 class="mb-0"><i class="fas fa-pen"></i> طلب جديد</h5></div>
                <div class="card-body">
                    <form action="{{ url_for('submit_order') }}" method="POST">
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label class="form-label fw-bold">الاسم الكامل <span class="text-danger">*</span></label>
                                <input type="text" name="full_name" class="form-control" required>
                            </div>
                            <div class="col-md-6 mb-3">
                                <label class="form-label fw-bold">رقم الهاتف <span class="text-danger">*</span></label>
                                <input type="tel" name="phone" class="form-control" placeholder="0612345678" required>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label class="form-label fw-bold">المدينة <span class="text-danger">*</span></label>
                                <select name="city" class="form-select" required>
                                    <option value="">اختر المدينة</option>
                                    ''' + ''.join([f'<option value="{c}">{c}</option>' for c in CITIES]) + '''
                                </select>
                            </div>
                            <div class="col-md-6 mb-3">
                                <label class="form-label fw-bold">المستوى الدراسي <span class="text-danger">*</span></label>
                                <select name="grade_level" class="form-select" required>
                                    <option value="">اختر المستوى</option>
                                    <option value="primary">ابتدائي</option>
                                    <option value="middle">متوسط</option>
                                    <option value="secondary">ثانوي</option>
                                    <option value="university">جامعي</option>
                                </select>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label class="form-label fw-bold">الجنس <span class="text-danger">*</span></label>
                                <select name="gender" class="form-select" required>
                                    <option value="">اختر الجنس</option>
                                    <option value="male">ذكر</option>
                                    <option value="female">أنثى</option>
                                </select>
                            </div>
                            <div class="col-md-6 mb-3">
                                <label class="form-label fw-bold">البريد الإلكتروني</label>
                                <input type="email" name="email" class="form-control" placeholder="example@email.com">
                            </div>
                        </div>
                        <div class="mb-3">
                            <label class="form-label fw-bold">الإضافات</label>
                            <div class="row">
                                <div class="col-md-4"><div class="form-check"><input class="form-check-input" type="checkbox" name="extras" value="ملازم"><label class="form-check-label">ملازم</label></div></div>
                                <div class="col-md-4"><div class="form-check"><input class="form-check-input" type="checkbox" name="extras" value="أدوات مدرسية"><label class="form-check-label">أدوات مدرسية</label></div></div>
                                <div class="col-md-4"><div class="form-check"><input class="form-check-input" type="checkbox" name="extras" value="كتب إضافية"><label class="form-check-label">كتب إضافية</label></div></div>
                            </div>
                        </div>
                        <div class="mb-3">
                            <label class="form-label fw-bold">المبلغ الإجمالي <span class="text-danger">*</span></label>
                            <input type="number" name="total_amount" class="form-control" placeholder="المبلغ بالدرهم" step="0.01" required>
                            <small class="text-muted">سيتم خصم ''' + str(PLATFORM_PROFIT) + '''% كعمولة للمنصة</small>
                        </div>
                        <button type="submit" class="btn btn-primary btn-lg w-100"><i class="fas fa-paper-plane"></i> تقديم الطلب</button>
                    </form>
                </div>
            </div>

            <div class="row mt-5 text-center">
                <div class="col-md-3"><div class="rounded-circle bg-primary text-white d-inline-flex align-items-center justify-content-center" style="width:70px;height:70px;"><i class="fas fa-pen fa-2x"></i></div><h5 class="mt-3">تقديم الطلب</h5><p class="text-muted small">قم بتعبئة النموذج</p></div>
                <div class="col-md-3"><div class="rounded-circle bg-success text-white d-inline-flex align-items-center justify-content-center" style="width:70px;height:70px;"><i class="fas fa-store fa-2x"></i></div><h5 class="mt-3">إرسال للمكتبة</h5><p class="text-muted small">نرسل طلبك للمكتبة</p></div>
                <div class="col-md-3"><div class="rounded-circle bg-info text-white d-inline-flex align-items-center justify-content-center" style="width:70px;height:70px;"><i class="fas fa-check-circle fa-2x"></i></div><h5 class="mt-3">تجهيز الطلب</h5><p class="text-muted small">المكتبة تجهز طلبك</p></div>
                <div class="col-md-3"><div class="rounded-circle bg-warning text-white d-inline-flex align-items-center justify-content-center" style="width:70px;height:70px;"><i class="fas fa-truck fa-2x"></i></div><h5 class="mt-3">التوصيل</h5><p class="text-muted small">فريقنا يوصل لك</p></div>
            </div>
        </div>
    </div>
    ''', site_name=SITE_NAME))

@app.route('/submit_order', methods=['POST'])
def submit_order():
    name = request.form.get('full_name')
    phone = request.form.get('phone')
    city = request.form.get('city')
    grade = request.form.get('grade_level')
    gender = request.form.get('gender')
    email = request.form.get('email')
    extras = request.form.getlist('extras')
    amount = float(request.form.get('total_amount', 0))
    
    if not all([name, phone, city, grade, gender]):
        flash('جميع الحقول المطلوبة يجب تعبئتها', 'danger')
        return redirect(url_for('index'))
    
    profit_amount = (amount * PLATFORM_PROFIT) / 100
    
    order = {
        'id': get_next_id(),
        'order_number': f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        'name': name,
        'phone': phone,
        'city': city,
        'grade': grade,
        'gender': gender,
        'email': email,
        'extras': ', '.join(extras) if extras else 'لا يوجد',
        'amount': amount,
        'profit_percent': PLATFORM_PROFIT,
        'profit_amount': profit_amount,
        'status': 'pending',
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    save_order(order)
    
    message = f"""
📚 طلب جديد من مول المكتبة

👤 الاسم: {name}
📱 الهاتف: {phone}
🏙️ المدينة: {city}
📚 المستوى: {grade}
💰 المبلغ: {amount} درهم
📊 رقم الطلب: {order['order_number']}
    """
    
    wa_url = f"https://wa.me/{WHATSAPP_NUMBER}?text={urllib.parse.quote(message)}"
    
    flash(f'✅ تم تقديم الطلب بنجاح! رقم الطلب: {order["order_number"]}', 'success')
    return render_template_string(BASE_TEMPLATE.replace('{% block content %}{% endblock %}', '''
    <div class="row justify-content-center">
        <div class="col-md-8">
            <div class="card text-center shadow-lg border-0">
                <div class="card-body py-5">
                    <i class="fas fa-check-circle text-success" style="font-size:80px;"></i>
                    <h2 class="mt-3">✅ تم تقديم الطلب بنجاح!</h2>
                    <p class="lead">رقم طلبك: <strong class="text-primary">{{ order.order_number }}</strong></p>
                    <div class="card bg-light my-4 text-start">
                        <div class="card-body">
                            <p><strong>👤 الاسم:</strong> {{ order.name }}</p>
                            <p><strong>📱 الهاتف:</strong> {{ order.phone }}</p>
                            <p><strong>🏙️ المدينة:</strong> {{ order.city }}</p>
                            <p><strong>📚 المستوى:</strong> {{ order.grade }}</p>
                            <p><strong>💰 المبلغ:</strong> {{ "%.2f"|format(order.amount) }} درهم</p>
                            <p><strong>📦 الإضافات:</strong> {{ order.extras }}</p>
                        </div>
                    </div>
                    <div class="d-flex gap-3 justify-content-center flex-wrap">
                        <a href="{{ wa_url }}" target="_blank" class="btn btn-success btn-lg"><i class="fab fa-whatsapp"></i> تواصل عبر واتساب</a>
                        <a href="{{ url_for('index') }}" class="btn btn-primary btn-lg"><i class="fas fa-home"></i> العودة للرئيسية</a>
                    </div>
                </div>
            </div>
        </div>
    </div>
    ''', site_name=SITE_NAME, order=order, wa_url=wa_url))

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if session.get('admin'):
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == ADMIN_USERNAME and hashlib.sha256(password.encode()).hexdigest() == ADMIN_PASSWORD:
            session['admin'] = True
            flash('✅ تم تسجيل الدخول بنجاح', 'success')
            return redirect(url_for('admin_dashboard'))
        flash('❌ اسم المستخدم أو كلمة المرور غير صحيحة', 'danger')
    
    return render_template_string(BASE_TEMPLATE.replace('{% block content %}{% endblock %}', '''
    <div class="login-card">
        <div class="card shadow-lg border-0">
            <div class="card-header bg-primary text-white text-center py-4">
                <h4 class="mb-0"><i class="fas fa-lock"></i> تسجيل دخول المدير</h4>
            </div>
            <div class="card-body p-4">
                <form method="POST">
                    <div class="mb-3">
                        <label class="form-label fw-bold">اسم المستخدم</label>
                        <input type="text" name="username" class="form-control" placeholder="admin" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label fw-bold">كلمة المرور</label>
                        <input type="password" name="password" class="form-control" placeholder="••••••••" required>
                    </div>
                    <button type="submit" class="btn btn-primary btn-lg w-100"><i class="fas fa-sign-in-alt"></i> دخول</button>
                </form>
                <div class="text-center mt-3 text-muted"><small>👤 admin | 🔑 admin123456</small></div>
            </div>
        </div>
    </div>
    ''', site_name=SITE_NAME))

@app.route('/admin/logout')
def admin_logout():
    session.clear()
    flash('تم تسجيل الخروج بنجاح', 'success')
    return redirect(url_for('index'))

@app.route('/admin')
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    
    libraries = get_libraries()
    orders = get_orders()
    
    total_libraries = len(libraries)
    pending = len([l for l in libraries if l.get('status') == 'pending'])
    approved = len([l for l in libraries if l.get('status') == 'approved'])
    invited = len([l for l in libraries if l.get('status') == 'invited'])
    rejected = len([l for l in libraries if l.get('status') == 'rejected'])
    total_orders = len(orders)
    total_revenue = sum(o.get('amount', 0) for o in orders if o.get('status') == 'completed')
    total_profit = sum(o.get('profit_amount', 0) for o in orders if o.get('status') == 'completed')
    
    return render_template_string(BASE_TEMPLATE.replace('{% block content %}{% endblock %}', '''
    <div class="row">
        <div class="col-12"><h2 class="mb-4"><i class="fas fa-chart-pie text-primary"></i> لوحة التحكم</h2></div>
    </div>
    <div class="row g-3 mb-4">
        <div class="col-md-3"><div class="stat-card bg-primary text-white"><div class="number">''' + str(total_libraries) + '''</div><div class="text-white-50">إجمالي المكتبات</div></div></div>
        <div class="col-md-3"><div class="stat-card bg-warning text-white"><div class="number">''' + str(pending) + '''</div><div class="text-white-50">في الانتظار</div></div></div>
        <div class="col-md-3"><div class="stat-card bg-success text-white"><div class="number">''' + str(approved) + '''</div><div class="text-white-50">مقبولة</div></div></div>
        <div class="col-md-3"><div class="stat-card bg-info text-white"><div class="number">''' + str(invited) + '''</div><div class="text-white-50">مرسلة دعوة</div></div></div>
        <div class="col-md-3"><div class="stat-card bg-secondary text-white"><div class="number">''' + str(total_orders) + '''</div><div class="text-white-50">إجمالي الطلبات</div></div></div>
        <div class="col-md-3"><div class="stat-card bg-success text-white"><div class="number">''' + f"{total_revenue:.2f}" + '''</div><div class="text-white-50">الإيرادات (درهم)</div></div></div>
        <div class="col-md-3"><div class="stat-card bg-primary text-white"><div class="number">''' + f"{total_profit:.2f}" + '''</div><div class="text-white-50">أرباح المنصة (درهم)</div></div></div>
        <div class="col-md-3"><div class="stat-card bg-danger text-white"><div class="number">''' + str(rejected) + '''</div><div class="text-white-50">مرفوضة</div></div></div>
    </div>
    <div class="card shadow-sm">
        <div class="card-header"><h5 class="mb-0"><i class="fas fa-list"></i> المكتبات</h5></div>
        <div class="card-body">
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead><tr><th>#</th><th>اسم المكتبة</th><th>المدينة</th><th>الهاتف</th><th>الحالة</th></tr></thead>
                    <tbody>
                        ''' + ''.join([f'<tr><td>{l["id"]}</td><td><strong>{l["name"]}</strong></td><td><span class="badge bg-secondary">{l["city"]}</span></td><td>{l["phone"]}</td><td><span class="badge badge-{l["status"]}">{"في الانتظار" if l["status"]=="pending" else "مرشحة" if l["status"]=="invited" else "مقبولة" if l["status"]=="approved" else "مرفوضة"}</span></td></tr>' for l in libraries[:10]]) + '''
                        ''' + ('' if libraries else '<tr><td colspan="5" class="text-center">لا توجد مكتبات</td></tr>') + '''
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    ''', site_name=SITE_NAME))

@app.route('/admin/libraries')
def admin_libraries():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    
    libraries = get_libraries()
    
    return render_template_string(BASE_TEMPLATE.replace('{% block content %}{% endblock %}', '''
    <div class="row mb-4">
        <div class="col-12 d-flex justify-content-between align-items-center">
            <h2><i class="fas fa-store text-primary"></i> إدارة المكتبات</h2>
            <button class="btn btn-success" onclick="showAddLibrary()"><i class="fas fa-plus"></i> إضافة مكتبة</button>
        </div>
    </div>
    <div class="card shadow-sm">
        <div class="card-body">
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead><tr><th>#</th><th>اسم المكتبة</th><th>المدينة</th><th>الهاتف</th><th>البريد</th><th>الحالة</th><th>إجراءات</th></tr></thead>
                    <tbody>
                        ''' + ''.join([f'''
                        <tr>
                            <td>{l["id"]}</td>
                            <td><strong>{l["name"]}</strong></td>
                            <td><span class="badge bg-secondary">{l["city"]}</span></td>
                            <td>{l["phone"]}</td>
                            <td>{l["email"]}</td>
                            <td><span class="badge badge-{l["status"]}">{"في الانتظار" if l["status"]=="pending" else "مرشحة" if l["status"]=="invited" else "مقبولة" if l["status"]=="approved" else "مرفوضة"}</span></td>
                            <td>
                                <button class="btn btn-sm btn-success" onclick="approve({l["id"]})"><i class="fas fa-check"></i></button>
                                <button class="btn btn-sm btn-danger" onclick="reject({l["id"]})"><i class="fas fa-times"></i></button>
                                <button class="btn btn-sm btn-info" onclick="invite({l["id"]})"><i class="fas fa-paper-plane"></i></button>
                            </td>
                        </tr>
                        ''' for l in libraries]) + '''
                        ''' + ('' if libraries else '<tr><td colspan="7" class="text-center">لا توجد مكتبات</td></tr>') + '''
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    
    <!-- مودال إضافة مكتبة -->
    <div class="modal fade" id="addLibraryModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header bg-primary text-white">
                    <h5 class="modal-title"><i class="fas fa-plus"></i> إضافة مكتبة</h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                </div>
                <form action="{{ url_for('add_library') }}" method="POST">
                    <div class="modal-body">
                        <div class="mb-3"><label class="form-label fw-bold">اسم المكتبة <span class="text-danger">*</span></label><input type="text" name="name" class="form-control" required></div>
                        <div class="mb-3"><label class="form-label fw-bold">رقم الهاتف <span class="text-danger">*</span></label><input type="text" name="phone" class="form-control" required></div>
                        <div class="mb-3"><label class="form-label fw-bold">البريد الإلكتروني <span class="text-danger">*</span></label><input type="email" name="email" class="form-control" required></div>
                        <div class="mb-3">
                            <label class="form-label fw-bold">المدينة <span class="text-danger">*</span></label>
                            <select name="city" class="form-select" required>
                                <option value="">اختر المدينة</option>
                                ''' + ''.join([f'<option value="{c}">{c}</option>' for c in CITIES]) + '''
                            </select>
                        </div>
                        <div class="mb-3"><label class="form-label fw-bold">العنوان</label><input type="text" name="address" class="form-control"></div>
                        <div class="mb-3"><label class="form-label fw-bold">نسبة الربح</label><input type="number" name="profit_percent" class="form-control" value="0" step="0.01"></div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">إلغاء</button>
                        <button type="submit" class="btn btn-success">إضافة</button>
                    </div>
                </form>
            </div>
        </div>
    </div>
    
    <script>
    function showAddLibrary() {
        $('#addLibraryModal').modal('show');
    }
    function approve(id) {
        if(confirm('هل أنت متأكد من قبول هذه المكتبة؟')) {
            fetch('/admin/library/'+id+'/approve', {method:'POST'}).then(() => location.reload());
        }
    }
    function reject(id) {
        if(confirm('هل أنت متأكد من رفض هذه المكتبة؟')) {
            fetch('/admin/library/'+id+'/reject', {method:'POST'}).then(() => location.reload());
        }
    }
    function invite(id) {
        if(confirm('هل أنت متأكد من إرسال دعوة لهذه المكتبة؟')) {
            fetch('/admin/library/'+id+'/invite', {method:'POST'})
                .then(r => r.json())
                .then(data => {
                    if(data.success) {
                        alert('✅ تم إرسال الدعوة بنجاح!\\n\\n📱 واتساب: '+data.whatsapp_url+'\\n\\n📧 إيميل: '+data.email_url);
                        location.reload();
                    }
                });
        }
    }
    </script>
    ''', site_name=SITE_NAME, libraries=libraries))

@app.route('/admin/library/add', methods=['POST'])
def add_library():
    if not session.get('admin'):
        return jsonify({'success': False, 'message': 'غير مصرح'})
    
    name = request.form.get('name')
    phone = request.form.get('phone')
    email = request.form.get('email')
    city = request.form.get('city')
    address = request.form.get('address', '')
    profit = float(request.form.get('profit_percent', 0))
    
    if not all([name, phone, email, city]):
        flash('جميع الحقول المطلوبة يجب تعبئتها', 'danger')
        return redirect(url_for('admin_libraries'))
    
    libraries = get_libraries()
    libraries.append({
        'id': get_next_id(),
        'name': name,
        'phone': phone,
        'email': email,
        'city': city,
        'address': address,
        'profit': profit,
        'status': 'pending'
    })
    save_libraries(libraries)
    
    flash('✅ تم إضافة المكتبة بنجاح', 'success')
    return redirect(url_for('admin_libraries'))

@app.route('/admin/library/<int:lib_id>/approve', methods=['POST'])
def approve_library(lib_id):
    if not session.get('admin'):
        return jsonify({'success': False})
    libraries = get_libraries()
    for l in libraries:
        if l['id'] == lib_id:
            l['status'] = 'approved'
            break
    save_libraries(libraries)
    return jsonify({'success': True})

@app.route('/admin/library/<int:lib_id>/reject', methods=['POST'])
def reject_library(lib_id):
    if not session.get('admin'):
        return jsonify({'success': False})
    libraries = get_libraries()
    for l in libraries:
        if l['id'] == lib_id:
            l['status'] = 'rejected'
            break
    save_libraries(libraries)
    return jsonify({'success': True})

@app.route('/admin/library/<int:lib_id>/invite', methods=['POST'])
def invite_library(lib_id):
    if not session.get('admin'):
        return jsonify({'success': False, 'message': 'غير مصرح'})
    
    libraries = get_libraries()
    library = None
    for l in libraries:
        if l['id'] == lib_id:
            library = l
            l['status'] = 'invited'
            break
    
    if not library:
        return jsonify({'success': False, 'message': 'المكتبة غير موجودة'})
    
    message = f"""
📚 دعوة للانضمام إلى منصة مول المكتبة MallMaktaba

السلام عليكم،

يسرنا دعوتكم للانضمام إلى منصة مول المكتبة، المنصة الرائدة في مجال طلب الكتب والمستلزمات المدرسية.

🎯 الهدف: تسهيل عملية طلب الكتب والمستلزمات المدرسية للطلاب وأولياء الأمور.

💼 طريقة العمل:
1️⃣ يتقدم العميل بطلب عبر المنصة
2️⃣ يتم إرسال الطلب مباشرة إلى مكتبتكم
3️⃣ تقومون بتجهيز الطلب والتواصل مع العميل
4️⃣ يتم توصيل الطلب عن طريق فريق المنصة

💰 نسبة الربح: يمكنكم تحديد النسبة التي تناسبكم.

📱 للانضمام والتواصل: يرجى التواصل معنا عبر الرقم: {WHATSAPP_NUMBER}

ننتظر مشاركتكم!
فريق مول المكتبة
"""
    
    phone = re.sub(r'[^0-9]', '', library['phone'])
    if not phone.startswith('212'):
        phone = '212' + phone
    
    whatsapp_url = f"https://wa.me/{phone}?text={urllib.parse.quote(message)}"
    email_url = f"mailto:{library['email']}?subject={urllib.parse.quote('📚 دعوة للانضمام إلى منصة مول المكتبة')}&body={urllib.parse.quote(message)}"
    
    save_libraries(libraries)
    
    return jsonify({
        'success': True,
        'whatsapp_url': whatsapp_url,
        'email_url': email_url
    })

# ======================== التشغيل ========================

if __name__ == '__main__':
    init_libraries()
    print("=" * 60)
    print("📚 مول المكتبة MallMaktaba")
    print("=" * 60)
    print("🌐 http://localhost:5000")
    print("👤 admin")
    print("🔑 admin123456")
    print("=" * 60)
    print(f"📊 {len(get_libraries())} مكتبة")
    print(f"🏙️ {len(CITIES)} مدينة")
    print("=" * 60)
    app.run(debug=True, port=5000)
