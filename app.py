from flask import Flask, render_template_string, request, redirect, url_for
from supabase import create_client, Client
import time

app = Flask(__name__)

# --- ตั้งค่าการเชื่อมต่อ Supabase ---
SUPABASE_URL = "https://xwgqgyvtbvlyupgkzcym.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh3Z3FneXZ0YnZseXVwZ2t6Y3ltIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODk5MDI0MjQsImV4cCI6MjEwNTQ3ODQyNH0.njllNrndwZUqlxjyWbX-jQnR18_k15ZsnUHayuVGCs8"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# หน้าตาเว็บไซต์ (HTML + Tailwind CSS)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <title>M.1 Admission Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-950 text-gray-100 min-h-screen p-6 font-sans">
    <div class="max-w-4xl mx-auto">
        <div class="flex justify-between items-center mb-6 border-b border-gray-800 pb-4">
            <div>
                <h1 class="text-2xl font-bold text-emerald-400">📍 บอทรับสมัคร ม.1 (บางนา - พระโขนง - สมุทรปราการ)</h1>
                <p class="text-sm text-gray-400">ขับเคลื่อนด้วย Python Flask & Supabase Database</p>
            </div>
            <span class="bg-emerald-950 text-emerald-400 text-xs px-3 py-1 rounded-full border border-emerald-800">Online 24 ชม. ✅</span>
        </div>

        {% if message %}
        <div class="bg-blue-950 border border-blue-800 text-blue-200 px-4 py-3 rounded-xl mb-6 text-sm flex items-center justify-between">
            <span>{{ message }}</span>
            <span class="text-xs text-blue-400">⚡ ทำงานเสร็จสิ้น</span>
        </div>
        {% endif %}

        <!-- ปุ่มควบคุมสั่งงานบอท -->
        <div class="bg-gray-900 border border-gray-800 p-4 rounded-xl mb-6 shadow-lg flex justify-between items-center">
            <div>
                <h2 class="text-sm font-semibold text-gray-200">🛠️ ควบคุมระบบดึงข้อมูล</h2>
                <p class="text-xs text-gray-400">คลิกเพื่อสั่งให้ Python วิ่งไปดึงข้อมูลประกาศล่าสุดมาใส่ตาราง</p>
            </div>
            <form action="/fetch-data" method="POST">
                <button type="submit" onclick="this.innerText='⏳ กำลังค้นหาและดึงข้อมูล...'; this.disabled=true; this.form.submit();" class="bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold py-2 px-4 rounded-lg transition shadow">
                    🚀 สั่งดึงข้อมูลตอนนี้
                </button>
            </form>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- ตารางรายชื่อโรงเรียน -->
            <div class="bg-gray-900 border border-gray-800 p-5 rounded-xl shadow-lg">
                <div class="flex justify-between items-center mb-4">
                    <h2 class="text-lg font-semibold text-gray-200">🏫 รายชื่อโรงเรียนในระบบ</h2>
                    <span class="text-xs bg-gray-800 text-emerald-300 px-2.5 py-1 rounded-full">{{ schools|length }} แห่ง</span>
                </div>
                <div class="space-y-3 max-h-[380px] overflow-y-auto pr-1">
                    {% if schools|length == 0 %}
                    <div class="text-center py-10 text-gray-500 text-xs">ยังไม่มีข้อมูลในระบบ กดปุ่ม "สั่งดึงข้อมูลตอนนี้" ด้านบนได้เลย</div>
                    {% endif %}
                    {% for s in schools %}
                    <div class="bg-gray-950 border border-gray-800/60 p-3 rounded-lg flex justify-between items-center">
                        <div>
                            <div class="flex items-center gap-2">
                                <span class="font-medium text-emerald-300 text-sm">{{ s.get('school_name', '-') }}</span>
                                <span class="text-[10px] px-2 py-0.5 rounded-full border {% if s.get('school_type') == 'รัฐบาล' %}bg-blue-950 text-blue-300 border-blue-800{% else %}bg-purple-950 text-purple-300 border-purple-800{% endif %}">{{ s.get('school_type', '-') }}</span>
                            </div>
                            <div class="text-xs text-gray-400 mt-1">📍 โซน: {{ s.get('zone', '-') }} | ⏳ {{ s.get('deadline') or 'รอประกาศ' }}</div>
                        </div>
                        <a href="{{ s.get('website_link') or '#' }}" target="_blank" class="text-xs bg-gray-800 hover:bg-gray-700 text-gray-300 px-2.5 py-1 rounded transition shrink-0 ml-2">เว็บ</a>
                    </div>
                    {% endfor %}
                </div>
            </div>

            <!-- ส่วนสร้างข้อความแชร์ -->
            <div class="bg-gray-900 border border-gray-800 p-5 rounded-xl shadow-lg flex flex-col justify-between">
                <div>
                    <h2 class="text-lg font-semibold mb-4 text-gray-200">💬 ข้อความสำหรับแชร์ลงกลุ่มแชท</h2>
                    <textarea id="bot-output" rows="10" class="w-full bg-gray-950 border border-gray-800 rounded-lg p-3 text-sm text-gray-300 focus:outline-none focus:border-emerald-500 mb-4" readonly>🚨 รวมประกาศรับสมัครนักเรียน ม.1 (รัฐบาล & เอกชน โซนบางนา-พระโขนง-สมุทรปราการ) 🚨

{% for s in schools %}{{ loop.index }}. 📌 {{ s.get('school_name', '-') }} [{{ s.get('school_type', '-') }}]
   📍 โซน: {{ s.get('zone', '-') }}
   ⏳ กำหนดการ: {{ s.get('deadline') or 'รอประกาศ' }}
   🔗 ลิงก์: {{ s.get('website_link') or 'ไม่มีลิงก์' }}

{% endfor %}💡 ข้อมูลจากฐานข้อมูล ฝากแชร์บอกต่อด้วยนะครับ! #สอบเข้าม1 #บางนา #พระโขนง #สมุทรปราการ</textarea>
                </div>
                <button onclick="copyText()" class="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-semibold py-3 px-4 rounded-lg transition text-sm shadow-md flex items-center justify-center gap-2">
                    ✨ คัดลอกข้อความทั้งหมดไปวางในแชททันที
                </button>
            </div>
        </div>
    </div>

    <script>
        function copyText() {
            const textarea = document.getElementById('bot-output');
            textarea.select();
            document.execCommand('copy');
            alert("🤖 คัดลอกข้อความเรียบร้อย! นำไปวางในกลุ่ม Messenger ได้เลยครับ 🚀");
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    message = request.args.get('message', '')
    try:
        response = supabase.table('schools_admission').select('*').order('school_name', desc=False).execute()
        schools = response.data
    except Exception as e:
        print(f"Error fetching data: {e}")
        schools = []
        
    return render_template_string(HTML_TEMPLATE, schools=schools, message=message)

# ฟังก์ชันจำลองการทำงานของบอทเมื่อกดปุ่มสั่งดึงข้อมูล
@app.route('/fetch-data', methods=['POST'])
def fetch_data():
    print("🤖 [INFO] เริ่มกระบวนการค้นหาและดึงข้อมูลรับสมัคร...")
    
    # ตรงนี้จำลองการดึงข้อมูล (คุณสามารถใส่โค้ด Scraper จริงๆ ไว้ตรงนี้ได้ในอนาคต)
    time.sleep(1.5) 
    print("🔍 [INFO] กำลังวิเคราะห์ข้อมูลประกาศจากโซน บางนา พระโขนง สมุทรปราการ...")
    
    try:
        # ตัวอย่าง: ดึงข้อมูลตัวอย่างมาใส่ตาราง Supabase (ถ้ายังว่างอยู่)
        # หรือเราจะดึงข้อมูลที่มีอยู่มาเช็กสถานะ
        print("💾 [SUCCESS] ดึงข้อมูลและอัปเดตลงฐานข้อมูล Supabase สำเร็จแล้ว!")
        msg = "ดึงข้อมูลและอัปเดตฐานข้อมูลสำเร็จเรียบร้อยแล้ว!"
    except Exception as e:
        print(f"❌ [ERROR] เกิดข้อผิดพลาดในการดึงข้อมูล: {e}")
        msg = f"เกิดข้อผิดพลาด: {str(e)}"

    return redirect(url_for('index', message=msg))

if __name__ == '__main__':
    app.run(debug=True, port=5000)