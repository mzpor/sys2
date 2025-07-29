 """
تمرین 28: مستندسازی API
سطح: پیشرفته
هدف: آشنایی با مستندسازی و Swagger
"""

from flask import Flask, jsonify, request
from flask_restx import Api, Resource, fields
import json

# ایجاد Flask app
app = Flask(__name__)
api = Api(app, version='1.0', title='ربات تلاوت API',
          description='API برای مدیریت ربات تلاوت قرآن')

# تعریف namespace ها
user_ns = api.namespace('users', description='عملیات کاربران')
class_ns = api.namespace('classes', description='عملیات کلاس‌ها')
payment_ns = api.namespace('payments', description='عملیات پرداخت')
admin_ns = api.namespace('admin', description='عملیات ادمین')

# تعریف مدل‌های داده
user_model = api.model('User', {
    'user_id': fields.Integer(required=True, description='شناسه کاربر'),
    'first_name': fields.String(required=True, description='نام'),
    'last_name': fields.String(required=True, description='نام خانوادگی'),
    'mobile': fields.String(required=True, description='شماره تلفن'),
    'national_id': fields.String(required=True, description='کد ملی'),
    'registration_date': fields.DateTime(description='تاریخ ثبت‌نام'),
    'status': fields.String(description='وضعیت کاربر')
})

class_model = api.model('Class', {
    'class_id': fields.String(required=True, description='شناسه کلاس'),
    'name': fields.String(required=True, description='نام کلاس'),
    'price': fields.String(required=True, description='قیمت'),
    'schedule': fields.String(required=True, description='برنامه'),
    'description': fields.String(description='توضیحات'),
    'max_students': fields.Integer(description='حداکثر دانشجو'),
    'current_students': fields.Integer(description='تعداد دانشجویان فعلی')
})

registration_model = api.model('Registration', {
    'user_id': fields.Integer(required=True, description='شناسه کاربر'),
    'class_id': fields.String(required=True, description='شناسه کلاس'),
    'registration_date': fields.DateTime(description='تاریخ ثبت‌نام'),
    'payment_status': fields.String(description='وضعیت پرداخت'),
    'payment_amount': fields.String(description='مبلغ پرداخت')
})

# API endpoints برای کاربران
@user_ns.route('/')
class UserList(Resource):
    @user_ns.doc('get_all_users')
    @user_ns.marshal_list_with(user_model)
    def get(self):
        """دریافت لیست تمام کاربران"""
        return list(registered_users.values())
    
    @user_ns.doc('create_user')
    @user_ns.expect(user_model)
    @user_ns.marshal_with(user_model, code=201)
    def post(self):
        """ایجاد کاربر جدید"""
        data = request.json
        
        # اعتبارسنجی داده‌ها
        if not all(key in data for key in ['user_id', 'first_name', 'last_name', 'mobile', 'national_id']):
            api.abort(400, "تمام فیلدهای اجباری باید پر شوند")
        
        # بررسی تکراری نبودن
        if data['user_id'] in registered_users:
            api.abort(409, "کاربر با این شناسه قبلاً وجود دارد")
        
        # ذخیره کاربر
        registered_users[data['user_id']] = data
        save_users_to_file()
        
        return data, 201

@user_ns.route('/<int:user_id>')
@user_ns.response(404, 'کاربر یافت نشد')
@user_ns.param('user_id', 'شناسه کاربر')
class User(Resource):
    @user_ns.doc('get_user')
    @user_ns.marshal_with(user_model)
    def get(self, user_id):
        """دریافت اطلاعات کاربر"""
        if user_id not in registered_users:
            api.abort(404, "کاربر یافت نشد")
        return registered_users[user_id]
    
    @user_ns.doc('update_user')
    @user_ns.expect(user_model)
    @user_ns.marshal_with(user_model)
    def put(self, user_id):
        """به‌روزرسانی اطلاعات کاربر"""
        if user_id not in registered_users:
            api.abort(404, "کاربر یافت نشد")
        
        data = request.json
        registered_users[user_id].update(data)
        save_users_to_file()
        
        return registered_users[user_id]
    
    @user_ns.doc('delete_user')
    @user_ns.response(204, 'کاربر حذف شد')
    def delete(self, user_id):
        """حذف کاربر"""
        if user_id not in registered_users:
            api.abort(404, "کاربر یافت نشد")
        
        del registered_users[user_id]
        save_users_to_file()
        
        return '', 204

# API endpoints برای کلاس‌ها
@class_ns.route('/')
class ClassList(Resource):
    @class_ns.doc('get_all_classes')
    @class_ns.marshal_list_with(class_model)
    def get(self):
        """دریافت لیست تمام کلاس‌ها"""
        return list(CLASSES.values())
    
    @class_ns.doc('create_class')
    @class_ns.expect(class_model)
    @class_ns.marshal_with(class_model, code=201)
    def post(self):
        """ایجاد کلاس جدید"""
        data = request.json
        
        if 'class_id' not in data:
            api.abort(400, "شناسه کلاس اجباری است")
        
        if data['class_id'] in CLASSES:
            api.abort(409, "کلاس با این شناسه قبلاً وجود دارد")
        
        CLASSES[data['class_id']] = data
        return data, 201

@class_ns.route('/<string:class_id>')
@class_ns.response(404, 'کلاس یافت نشد')
@class_ns.param('class_id', 'شناسه کلاس')
class Class(Resource):
    @class_ns.doc('get_class')
    @class_ns.marshal_with(class_model)
    def get(self, class_id):
        """دریافت اطلاعات کلاس"""
        if class_id not in CLASSES:
            api.abort(404, "کلاس یافت نشد")
        return CLASSES[class_id]

# API endpoints برای پرداخت
@payment_ns.route('/')
class PaymentList(Resource):
    @payment_ns.doc('get_all_payments')
    @payment_ns.marshal_list_with(registration_model)
    def get(self):
        """دریافت لیست تمام پرداخت‌ها"""
        # اینجا باید از پایگاه داده استفاده شود
        return []
    
    @payment_ns.doc('create_payment')
    @payment_ns.expect(registration_model)
    @payment_ns.marshal_with(registration_model, code=201)
    def post(self):
        """ایجاد پرداخت جدید"""
        data = request.json
        
        # بررسی وجود کاربر و کلاس
        if data['user_id'] not in registered_users:
            api.abort(404, "کاربر یافت نشد")
        
        if data['class_id'] not in CLASSES:
            api.abort(404, "کلاس یافت نشد")
        
        # ذخیره پرداخت
        # اینجا باید در پایگاه داده ذخیره شود
        
        return data, 201

# API endpoints برای ادمین
@admin_ns.route('/stats')
class AdminStats(Resource):
    @admin_ns.doc('get_admin_stats')
    def get(self):
        """دریافت آمار ادمین"""
        stats = {
            'total_users': len(registered_users),
            'total_classes': len(CLASSES),
            'active_sessions': len(user_states),
            'system_health': health_checker.is_system_healthy() if 'health_checker' in globals() else True
        }
        return stats

@admin_ns.route('/users/search')
class UserSearch(Resource):
    @admin_ns.doc('search_users')
    @admin_ns.param('name', 'نام برای جستجو')
    @admin_ns.param('mobile', 'شماره تلفن برای جستجو')
    def get(self):
        """جستجوی کاربران"""
        name = request.args.get('name', '')
        mobile = request.args.get('mobile', '')
        
        results = []
        for user_id, user_data in registered_users.items():
            if name and name.lower() in user_data.get('first_name', '').lower():
                results.append(user_data)
            elif mobile and mobile in user_data.get('mobile', ''):
                results.append(user_data)
        
        return results

# ایجاد فایل مستندات
def generate_api_documentation():
    """تولید مستندات API"""
    docs = {
        'info': {
            'title': 'ربات تلاوت API',
            'version': '1.0.0',
            'description': 'API کامل برای مدیریت ربات تلاوت قرآن',
            'contact': {
                'name': 'تیم توسعه',
                'email': 'dev@example.com'
            }
        },
        'servers': [
            {
                'url': 'http://localhost:5000',
                'description': 'سرور توسعه'
            },
            {
                'url': 'https://api.example.com',
                'description': 'سرور تولید'
            }
        ],
        'paths': {
            '/users': {
                'get': {
                    'summary': 'دریافت لیست کاربران',
                    'responses': {
                        '200': {
                            'description': 'لیست کاربران',
                            'content': {
                                'application/json': {
                                    'schema': {
                                        'type': 'array',
                                        'items': {'$ref': '#/components/schemas/User'}
                                    }
                                }
                            }
                        }
                    }
                },
                'post': {
                    'summary': 'ایجاد کاربر جدید',
                    'requestBody': {
                        'required': True,
                        'content': {
                            'application/json': {
                                'schema': {'$ref': '#/components/schemas/User'}
                            }
                        }
                    },
                    'responses': {
                        '201': {
                            'description': 'کاربر ایجاد شد'
                        },
                        '400': {
                            'description': 'داده‌های نامعتبر'
                        }
                    }
                }
            },
            '/classes': {
                'get': {
                    'summary': 'دریافت لیست کلاس‌ها',
                    'responses': {
                        '200': {
                            'description': 'لیست کلاس‌ها'
                        }
                    }
                }
            },
            '/admin/stats': {
                'get': {
                    'summary': 'دریافت آمار ادمین',
                    'responses': {
                        '200': {
                            'description': 'آمار سیستم'
                        }
                    }
                }
            }
        },
        'components': {
            'schemas': {
                'User': {
                    'type': 'object',
                    'properties': {
                        'user_id': {
                            'type': 'integer',
                            'description': 'شناسه کاربر'
                        },
                        'first_name': {
                            'type': 'string',
                            'description': 'نام'
                        },
                        'last_name': {
                            'type': 'string',
                            'description': 'نام خانوادگی'
                        },
                        'mobile': {
                            'type': 'string',
                            'description': 'شماره تلفن'
                        },
                        'national_id': {
                            'type': 'string',
                            'description': 'کد ملی'
                        }
                    },
                    'required': ['user_id', 'first_name', 'last_name', 'mobile', 'national_id']
                },
                'Class': {
                    'type': 'object',
                    'properties': {
                        'class_id': {
                            'type': 'string',
                            'description': 'شناسه کلاس'
                        },
                        'name': {
                            'type': 'string',
                            'description': 'نام کلاس'
                        },
                        'price': {
                            'type': 'string',
                            'description': 'قیمت'
                        },
                        'schedule': {
                            'type': 'string',
                            'description': 'برنامه'
                        }
                    },
                    'required': ['class_id', 'name', 'price', 'schedule']
                }
            }
        }
    }
    
    with open('api_documentation.json', 'w', encoding='utf-8') as f:
        json.dump(docs, f, ensure_ascii=False, indent=2)
    
    print("📚 مستندات API در api_documentation.json ذخیره شد")

def create_api_examples():
    """ایجاد مثال‌های API"""
    examples = {
        'create_user': {
            'method': 'POST',
            'url': '/users',
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': {
                'user_id': 12345,
                'first_name': 'علی',
                'last_name': 'محمدی',
                'mobile': '09123456789',
                'national_id': '1234567890'
            }
        },
        'get_user': {
            'method': 'GET',
            'url': '/users/12345'
        },
        'update_user': {
            'method': 'PUT',
            'url': '/users/12345',
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': {
                'mobile': '09123456789'
            }
        },
        'get_classes': {
            'method': 'GET',
            'url': '/classes'
        },
        'create_payment': {
            'method': 'POST',
            'url': '/payments',
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': {
                'user_id': 12345,
                'class_id': 'quran_recitation',
                'payment_amount': '500000'
            }
        }
    }
    
    with open('api_examples.json', 'w', encoding='utf-8') as f:
        json.dump(examples, f, ensure_ascii=False, indent=2)
    
    print("📝 مثال‌های API در api_examples.json ذخیره شد")

def run_api_server():
    """اجرای سرور API"""
    print("🚀 سرور API در حال اجرا روی http://localhost:5000")
    print("📚 مستندات Swagger در http://localhost:5000/")
    app.run(debug=True, host='0.0.0.0', port=5000)

print("✅ تمرین 28: مستندسازی API تکمیل شد!")

# تولید مستندات
generate_api_documentation()
create_api_examples()

# تمرین: تابعی برای تست API بنویسید
# تمرین: تابعی برای تولید مستندات PDF بنویسید
# تمرین: تابعی برای versioning API بنویسید