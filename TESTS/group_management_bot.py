
import requests
import sqlite3
import logging
import jdatetime
import schedule
import time
import threading
import json
from datetime import datetime, time as dt_time
import pytz
from uuid import uuid4

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='bot.log',
    filemode='a'
)
logger = logging.getLogger(__name__)

# BALE API settings
BALE_API_URL = "https://tapi.bale.ai/bot{token}/{method}"
TOKEN = "qhTkuourrvpM4nF1xrE6MyD93rSgJBfVZFwXbJU1"  # Replace with your bot token
TIMEZONE = pytz.timezone("Asia/Tehran")
BOT_ID = "YOUR_BOT_ID"  # Replace with your bot ID

# Database initialization
def init_db():
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        role TEXT,
        first_name TEXT,
        last_name TEXT,
        coach_id TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        date TEXT,
        status TEXT,
        group_id TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS exercises (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        date TEXT,
        group_id TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS evaluations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        exercise_id INTEGER,
        evaluator_id TEXT,
        evaluator_role TEXT,
        grade TEXT,
        date TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        evaluator_id TEXT,
        evaluator_role TEXT,
        rating INTEGER,
        date TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS config (
        key TEXT PRIMARY KEY,
        value TEXT
    )''')
    conn.commit()
    conn.close()
    logger.info("Database initialized")

# Save monthly/yearly reports to JSON
def save_reports():
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("SELECT * FROM attendance")
    attendance = c.fetchall()
    c.execute("SELECT * FROM exercises")
    exercises = c.fetchall()
    c.execute("SELECT * FROM evaluations")
    evaluations = c.fetchall()
    c.execute("SELECT * FROM feedback")
    feedback = c.fetchall()
    c.execute("SELECT user_id, first_name, last_name, role FROM users WHERE role='student'")
    students = c.fetchall()
    conn.close()

    report = {
        "students": [{"user_id": s[0], "first_name": s[1], "last_name": s[2], "role": s[3]} for s in students],
        "attendance": [{"id": a[0], "user_id": a[1], "date": a[2], "status": a[3], "group_id": a[4]} for a in attendance],
        "exercises": [{"id": e[0], "user_id": e[1], "date": e[2], "group_id": e[3]} for e in exercises],
        "evaluations": [{"id": e[0], "exercise_id": e[1], "evaluator_id": e[2], "evaluator_role": e[3], "grade": e[4], "date": e[5]} for e in evaluations],
        "feedback": [{"id": f[0], "user_id": f[1], "evaluator_id": f[2], "evaluator_role": f[3], "rating": f[4], "date": f[5]} for f in feedback]
    }
    with open(f"report_{jdatetime.datetime.now(TIMEZONE).strftime('%Y-%m')}.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=4)
    logger.info("Monthly report saved to JSON")

# API request helper
def send_request(method, data):
    url = BALE_API_URL.format(token=TOKEN, method=method)
    try:
        response = requests.post(url, json=data, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"API request failed: {method}, error: {str(e)}")
        return None

# Send message
def send_message(chat_id, text, reply_markup=None):
    data = {
        "chat_id": chat_id,
        "text": text,
        "reply_markup": reply_markup
    }
    return send_request("sendMessage", data)

# Send inline keyboard
def send_inline_keyboard(chat_id, text, buttons):
    reply_markup = {
        "inline_keyboard": buttons
    }
    return send_message(chat_id, text, reply_markup)

# Get Persian date
def get_persian_date():
    dt = datetime.now(TIMEZONE)
    jdt = jdatetime.datetime.fromgregorian(datetime=dt)
    return jdt.strftime("%A %d %B")

# Initialize bot in group
def handle_group_joined(update):
    chat_id = update["message"]["chat"]["id"]
    text = "برای استفاده از امکانات من، مرا مدیر کنید. با تشکر!"
    send_message(chat_id, text)
    logger.info(f"Bot joined group {chat_id}")

# Handle admin promotion
def handle_admin_promoted(update):
    chat_id = update["message"]["chat"]["id"]
    date = get_persian_date()
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("SELECT user_id, first_name, last_name, role FROM users WHERE role IN ('admin', 'coach', 'assistant_coach')")
    admins_coaches = c.fetchall()
    c.execute("SELECT user_id, first_name, last_name, coach_id FROM users WHERE role='student'")
    students = c.fetchall()
    conn.close()

    # Send to group (students only)
    student_list = "\n".join([f"{s[1]} {s[2]} - {s[3]}" for s in students])
    send_message(chat_id, f"تاریخ: {date}\nلیست قرآن‌آموزان:\n{student_list}\nبرای عضویت در روم، قرآن‌آموزان عزیز روی /عضو ضربه بزنید.")

    # Send to coaches
    admin_list = "\n".join([f"{a[1]} {a[2]} - {a[3]}" for a in admins_coaches])
    for coach in admins_coaches:
        send_message(coach[0], f"تاریخ: {date}\nلیست مدیران و مربیان:\n{admin_list}\nلیست قرآن‌آموزان:\n{student_list}")
    logger.info(f"Admin promoted in group {chat_id}, lists sent")

# Handle /عضو command
def handle_member_command(update):
    chat_id = update["message"]["chat"]["id"]
    user_id = update["message"]["from"]["id"]
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("SELECT role FROM users WHERE user_id=?", (str(user_id),))
    result = c.fetchone()
    if result and result[0] == "student":
        c.execute("SELECT user_id, first_name, last_name, coach_id FROM users WHERE role='student'")
        students = c.fetchall()
        student_list = "\n".join([f"{s[1]} {s[2]} - {s[3]}" for s in students])
        send_message(chat_id, f"لیست به‌روزرسانی‌شده قرآن‌آموزان:\n{student_list}")
        logger.info(f"Student {user_id} used /عضو, list updated")
    else:
        send_message(chat_id, "لطفاً ابتدا در چت خصوصی ثبت‌نام کنید.")
    conn.close()

# Handle private chat registration
def handle_private_message(update):
    chat_id = update["message"]["chat"]["id"]
    buttons = [
        [{"text": "مربی", "callback_data": "role_coach"}],
        [{"text": "کمک مربی", "callback_data": "role_assistant_coach"}],
        [{"text": "قرآن‌آموز", "callback_data": "role_student"}]
    ]
    send_inline_keyboard(chat_id, "لطفاً نقش خود را انتخاب کنید:", buttons)
    logger.info(f"Role selection sent to user {chat_id}")

# Handle role selection
def handle_role_selection(update):
    chat_id = update["callback_query"]["message"]["chat"]["id"]
    user_id = update["callback_query"]["from"]["id"]
    role = update["callback_query"]["data"].split("_")[1]
    send_message(chat_id, "لطفاً نام و نام خانوادگی خود را وارد کنید:")
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)", (f"temp_role_{user_id}", role))
    conn.commit()
    conn.close()
    logger.info(f"User {user_id} selected role {role}")

# Handle name input
def handle_name_input(update):
    chat_id = update["message"]["chat"]["id"]
    user_id = update["message"]["from"]["id"]
    text = update["message"]["text"]
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("SELECT value FROM config WHERE key=?", (f"temp_role_{user_id}",))
    result = c.fetchone()
    if not result:
        send_message(chat_id, "لطفاً ابتدا نقش خود را انتخاب کنید.")
        conn.close()
        return
    role = result[0]
    if role in ["coach", "assistant_coach"]:
        send_message(chat_id, "لطفاً شماره مربی خود را وارد کنید (یا خالی بگذارید):")
    else:
        send_message(chat_id, "لطفاً شماره مربی خود را وارد کنید:")
    c.execute("INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)", (f"temp_name_{user_id}", text))
    conn.commit()
    conn.close()
    logger.info(f"User {user_id} provided name: {text}")

# Handle coach ID input
def handle_coach_id_input(update):
    chat_id = update["message"]["chat"]["id"]
    user_id = update["message"]["from"]["id"]
    coach_id = update["message"]["text"] or ""
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("SELECT value FROM config WHERE key=?", (f"temp_role_{user_id}",))
    result = c.fetchone()
    if not result:
        send_message(chat_id, "لطفاً ابتدا نقش خود را انتخاب کنید.")
        conn.close()
        return
    role = result[0]
    c.execute("SELECT value FROM config WHERE key=?", (f"temp_name_{user_id}",))
    result = c.fetchone()
    if not result:
        send_message(chat_id, "لطفاً ابتدا نام و نام خانوادگی خود را وارد کنید.")
        conn.close()
        return
    name = result[0]
    first_name, last_name = name.split(" ", 1) if " " in name else (name, "")
    c.execute("INSERT OR REPLACE INTO users (user_id, role, first_name, last_name, coach_id) VALUES (?, ?, ?, ?, ?)",
              (str(user_id), role, first_name, last_name, coach_id))
    conn.commit()
    conn.close()
    if role in ["coach", "assistant_coach"]:
        send_message(chat_id, "ثبت‌نام شما تکمیل شد. لیست حضور و غیاب و گزارش‌ها در روزهای مربوطه ارسال خواهد شد.")
    else:
        send_message(chat_id, "ثبت‌نام شما تکمیل شد. لطفاً تمرین‌های خود را در روزهای تمرین ارسال کنید و برای عضویت در گروه از /عضو استفاده کنید.")
    logger.info(f"User {user_id} registered as {role} with coach ID {coach_id}")

# Handle attendance
def handle_attendance(update):
    callback_data = update["callback_query"]["data"]
    user_id = update["callback_query"]["from"]["id"]
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("SELECT role FROM users WHERE user_id=?", (str(user_id),))
    result = c.fetchone()
    if not result or result[0] not in ["coach", "assistant_coach"]:
        send_message(update["callback_query"]["message"]["chat"]["id"], "فقط مربیان می‌توانند حضور و غیاب را ثبت کنند.")
        conn.close()
        return
    student_id, status = callback_data.split("_")[1:3]
    date = get_persian_date()
    group_id = update["callback_query"]["message"]["chat"]["id"]
    c.execute("INSERT INTO attendance (user_id, date, status, group_id) VALUES (?, ?, ?, ?)",
              (student_id, date, status, group_id))
    conn.commit()
    conn.close()
    send_message(update["callback_query"]["message"]["chat"]["id"], f"وضعیت {status} برای کاربر {student_id} ثبت شد.")
    logger.info(f"Attendance recorded for {student_id}: {status}")

# Handle exercise submission
def handle_exercise_submission(update):
    chat_id = update["message"]["chat"]["id"]
    user_id = update["message"]["from"]["id"]
    date = get_persian_date()
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("SELECT role FROM users WHERE user_id=?", (str(user_id),))
    result = c.fetchone()
    if not result or result[0] != "student":
        send_message(chat_id, "فقط قرآن‌آموزان می‌توانند تمرین ارسال کنند.")
        conn.close()
        return
    c.execute("INSERT INTO exercises (user_id, date, group_id) VALUES (?, ?, ?)", (str(user_id), date, chat_id))
    exercise_id = c.lastrowid
    conn.commit()
    conn.close()
    buttons = [
        [{"text": "نیاز به تلاش بیشتر", "callback_data": f"eval_{exercise_id}_effort"}],
        [{"text": "متوسط", "callback_data": f"eval_{exercise_id}_average"}],
        [{"text": "خوب", "callback_data": f"eval_{exercise_id}_good"}],
        [{"text": "عالی", "callback_data": f"eval_{exercise_id}_excellent"}],
        [{"text": "ممتاز", "callback_data": f"eval_{exercise_id}_outstanding"}]
    ]
    send_inline_keyboard(chat_id, "تمرین دریافت شد. لطفاً مربی یا کمک مربی ارزیابی کند:", buttons)
    update_exercise_list(chat_id)
    logger.info(f"Exercise submitted by {user_id} in group {chat_id}")

# Update exercise list
def update_exercise_list(group_id):
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("SELECT u.first_name, u.last_name, e.date FROM exercises e JOIN users u ON e.user_id=u.user_id WHERE e.group_id=?",
              (group_id,))
    exercises = c.fetchall()
    conn.close()
    text = "لیست تمرین‌های ارسالی:\n" + "\n".join([f"{e[0]} {e[1]} - {e[2]}" for e in exercises])
    send_message(group_id, text)
    logger.info(f"Exercise list updated in group {group_id}")

# Handle evaluation
def handle_evaluation(update):
    callback_data = update["callback_query"]["data"]
    user_id = update["callback_query"]["from"]["id"]
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("SELECT role FROM users WHERE user_id=?", (str(user_id),))
    result = c.fetchone()
    if not result or result[0] not in ["coach", "assistant_coach"]:
        send_message(update["callback_query"]["message"]["chat"]["id"], "فقط مربیان می‌توانند ارزیابی کنند.")
        conn.close()
        return
    evaluator_role = result[0]
    exercise_id, grade = callback_data.split("_")[1:3]
    date = get_persian_date()
    c.execute("INSERT INTO evaluations (exercise_id, evaluator_id, evaluator_role, grade, date) VALUES (?, ?, ?, ?, ?)",
              (exercise_id, str(user_id), evaluator_role, grade, date))
    c.execute("SELECT user_id FROM exercises WHERE id=?", (exercise_id,))
    student_id = c.fetchone()[0]
    conn.commit()
    conn.close()
    send_message(update["callback_query"]["message"]["chat"]["id"], f"ارزیابی {grade} برای تمرین ثبت شد.")
    send_feedback_survey(student_id, user_id, evaluator_role)
    logger.info(f"Evaluation {grade} recorded for exercise {exercise_id} by {user_id} ({evaluator_role})")

# Send feedback survey
def send_feedback_survey(student_id, evaluator_id, evaluator_role):
    buttons = [
        [{"text": str(i), "callback_data": f"feedback_{evaluator_id}_{evaluator_role}_{i}"}] for i in range(1, 6)
    ]
    send_inline_keyboard(student_id, f"نظر شما نسبت به تشریح {evaluator_role} از ۱ تا ۵ چگونه است؟", buttons)
    logger.info(f"Feedback survey sent to {student_id} for {evaluator_id} ({evaluator_role})")

# Handle feedback
def handle_feedback(update):
    callback_data = update["callback_query"]["data"]
    student_id = update["callback_query"]["from"]["id"]
    evaluator_id, evaluator_role, rating = callback_data.split("_")[1:4]
    date = get_persian_date()
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("INSERT INTO feedback (user_id, evaluator_id, evaluator_role, rating, date) VALUES (?, ?, ?, ?, ?)",
              (str(student_id), evaluator_id, evaluator_role, rating, date))
    c.execute("SELECT value FROM config WHERE key='admin_id'")
    result = c.fetchone()
    admin_id = result[0] if result else None
    conn.commit()
    conn.close()
    if admin_id:
        send_message(admin_id, f"نظرسنجی برای {evaluator_role} {evaluator_id}: امتیاز {rating} توسط {student_id}")
    send_message(update["callback_query"]["message"]["chat"]["id"], f"نظرتون با امتیاز {rating} ثبت شد.")
    update_feedback_report(evaluator_id, evaluator_role)
    logger.info(f"Feedback {rating} recorded for {evaluator_id} ({evaluator_role}) by {student_id}")

# Update feedback report
def update_feedback_report(evaluator_id, evaluator_role):
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("SELECT rating, date FROM feedback WHERE evaluator_id=? AND evaluator_role=?", (evaluator_id, evaluator_role))
    feedback = c.fetchall()
    c.execute("SELECT value FROM config WHERE key='admin_id'")
    result = c.fetchone()
    admin_id = result[0] if result else None
    conn.close()
    if admin_id:
        text = f"گزارش نظرسنجی برای {evaluator_role} {evaluator_id}:\n" + "\n".join([f"امتیار: {f[0]} - تاریخ: {f[1]}" for f in feedback])
        send_message(admin_id, text)
    logger.info(f"Feedback report sent to admin for {evaluator_id} ({evaluator_role})")

# Schedule tasks
def schedule_tasks():
    def send_attendance_list():
        conn = sqlite3.connect("bot.db")
        c = conn.cursor()
        c.execute("SELECT group_id, user_id, status, date FROM attendance WHERE date=?", (get_persian_date(),))
        attendance = c.fetchall()
        c.execute("SELECT value FROM config WHERE key='admin_id'")
        result = c.fetchone()
        admin_id = result[0] if result else None
        conn.close()
        for group_id in set(a[0] for a in attendance):
            text = "لیست حضور و غیاب:\n" + "\n".join([f"کاربر {a[1]}: {a[2]}" for a in attendance if a[0] == group_id])
            send_message(group_id, text)
            if admin_id:
                send_message(admin_id, text)
        logger.info("Attendance list sent")

    def save_monthly_report():
        save_reports()
        logger.info("Monthly report task executed")

    schedule.every().day.at("14:00").do(send_attendance_list)
    schedule.every().month.do(save_monthly_report)
    while True:
        schedule.run_pending()
        time.sleep(60)

# Main update handler
def handle_update(update):
    if "message" in update:
        message = update["message"]
        if message["chat"]["type"] == "group":
            if message.get("new_chat_member", {}).get("id") == BOT_ID:
                handle_group_joined(update)
            elif message.get("text") == "/عضو":
                handle_member_command(update)
            elif message.get("caption") == "تمرین":
                handle_exercise_submission(update)
        elif message["chat"]["type"] == "private":
            if message.get("text") == "/start":
                handle_private_message(update)
            elif "temp_role_" in [row[0] for row in sqlite3.connect("bot.db").execute("SELECT key FROM config WHERE key LIKE ?", (f"temp_role_{message['from']['id']}%",)).fetchall()]:
                handle_name_input(update)
            elif "temp_name_" in [row[0] for row in sqlite3.connect("bot.db").execute("SELECT key FROM config WHERE key LIKE ?", (f"temp_name_{message['from']['id']}%",)).fetchall()]:
                handle_coach_id_input(update)
    elif "callback_query" in update:
        callback_data = update["callback_query"]["data"]
        if callback_data.startswith("role_"):
            handle_role_selection(update)
        elif callback_data.startswith("attendance_"):
            handle_attendance(update)
        elif callback_data.startswith("eval_"):
            handle_evaluation(update)
        elif callback_data.startswith("feedback_"):
            handle_feedback(update)

# Main loop
def main():
    init_db()
    threading.Thread(target=schedule_tasks, daemon=True).start()
    offset = None
    while True:
        try:
            data = {"offset": offset} if offset else {}
            updates = send_request("getUpdates", data)
            if updates and updates.get("ok"):
                for update in updates["result"]:
                    handle_update(update)
                    offset = update["update_id"] + 1
        except Exception as e:
            logger.error(f"Error in main loop: {str(e)}")
            time.sleep(5)

if __name__ == "__main__":
    main()
```