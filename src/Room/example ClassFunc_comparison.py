# مثال 1: تابع ساده
def calculate_rectangle_area(width, height):
    """تابع ساده برای محاسبه مساحت"""
    return width * height

# استفاده از تابع
area1 = calculate_rectangle_area(5, 3)
print(f"مساحت از تابع: {area1}")  # 15

# مثال 2: کلاس
class Rectangle:
    """کلاس برای مدیریت مستطیل"""
    def __init__(self, width, height):
        # اینجا داده‌ها ذخیره می‌شوند
        self.width = width
        self.height = height
        self.color = "قرمز"  # حالت پیش‌فرض
    
    def calculate_area(self):
        """محاسبه مساحت"""
        return self.width * self.height
    
    def calculate_perimeter(self):
        """محاسبه محیط"""
        return 2 * (self.width + self.height)
    
    def change_color(self, new_color):
        """تغییر رنگ"""
        self.color = new_color
    
    def get_info(self):
        """دریافت اطلاعات"""
        return f"مستطیل {self.width}x{self.height} به رنگ {self.color}"

# مثال 3: ایجاد اشیاء مختلف
rect1 = Rectangle(5, 3)  # شیء اول
rect2 = Rectangle(10, 5)  # شیء دوم

# هر شیء داده‌های خودش را دارد
print(f"شیء 1: {rect1.get_info()}")
print(f"شیء 2: {rect2.get_info()}")

# تغییر رنگ یکی از اشیاء
rect1.change_color("آبی")
print(f"شیء 1 بعد از تغییر: {rect1.get_info()}")

# شیء دوم تغییری نکرده
print(f"شیء 2 بدون تغییر: {rect2.get_info()}")

# مثال 4: مقایسه با تابع
def calculate_multiple_areas(rectangles_data):
    """تابع برای محاسبه مساحت چندین مستطیل"""
    areas = []
    for width, height in rectangles_data:
        areas.append(width * height)
    return areas

# استفاده از تابع
data = [(5, 3), (10, 5), (3, 7)]
areas = calculate_multiple_areas(data)
print(f"مساحت‌ها از تابع: {areas}")

# استفاده از کلاس
rectangles = [Rectangle(5, 3), Rectangle(10, 5), Rectangle(3, 7)]
areas_from_objects = [rect.calculate_area() for rect in rectangles]
print(f"مساحت‌ها از اشیاء: {areas_from_objects}")

# مزایای کلاس و شیء
print("\n=== مزایای کلاس و شیء ===")
rect = Rectangle(8, 4)
print(f"اطلاعات اولیه: {rect.get_info()}")
print(f"مساحت: {rect.calculate_area()}")
print(f"محیط: {rect.calculate_perimeter()}")

rect.change_color("سبز")
print(f"بعد از تغییر رنگ: {rect.get_info()}")

# تابع نمی‌تواند حالت را حفظ کند
print("\n=== محدودیت تابع ===")
print("تابع نمی‌تواند رنگ یا سایر ویژگی‌ها را حفظ کند")
print("هر بار باید همه پارامترها را دوباره بدهیم") 