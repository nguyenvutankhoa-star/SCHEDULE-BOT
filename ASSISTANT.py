import os
import sys
import threading
import time
import ctypes
import traceback
import gc  # Thêm thư viện dọn rác bộ nhớ
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from bs4 import BeautifulSoup
from PIL import Image, ImageTk
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from subprocess import CREATE_NO_WINDOW

# Hàm hỗ trợ tìm đường dẫn ảnh khi đóng gói thành file .exe
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

ENV_FILE = ".env"
FILE_CACHE = "tkb_cache.txt"
VIETNAMESE_DAYS = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ nhật"]

class UltimateUniversalAssistant:
    def __init__(self, root):
        self.root = root
        self.drag_data = {"x": 0, "y": 0}
        self.custom_schedule = {
            "08:30": "Vào ca rồi sếp! Mở To-do list ra nào.",
            "12:00": "Nghỉ trưa thôi, cất máy đi ăn cơm!",
            "23:00": "Muộn rồi, tắt máy đi ngủ để bảo vệ sức khỏe!",
        }

        self.root.title("Trung Tâm Trợ Lý Ảo")
        self.root.overrideredirect(True)
        self.root.configure(bg="#1e272e")

        self.main_container = tk.Frame(self.root, bg="#2f3640", bd=0)
        self.main_container.pack(fill="both", expand=True, padx=4, pady=4)

        self.lbl_header = tk.Label(
            self.main_container, text="📅 TRUNG TÂM QUẢN LÝ TRỢ LÝ ẢO",
            font=("Segoe UI", 10, "bold"), fg="#f5f6fa", bg="#353b48", pady=12, cursor="fleur",
        )
        self.lbl_header.pack(fill="x")
        self.lbl_header.bind("<Button-1>", self.start_drag)
        self.lbl_header.bind("<B1-Motion>", self.drag_window)

        self.content_frame = tk.Frame(self.main_container, bg="#2f3640")
        self.content_frame.pack(fill="both", expand=True)

        self.setup_robot_window()
        self.config = self.load_config()
        
        self.show_setup_wizard()
        
        # Gọi hàm ép Widget chìm xuống dưới cùng
        self.root.after(200, self.pin_to_desktop)

    def pin_to_desktop(self):
        try:
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            ctypes.windll.user32.SetWindowPos(hwnd, 1, 0, 0, 0, 0, 0x0002 | 0x0001 | 0x0010)
        except Exception:
            pass
        # Đổi thành 5000ms (5 giây) để giảm tải cho CPU và tránh hiện tượng giật lag WinAPI
        self.root.after(5000, self.pin_to_desktop)

    def load_config(self):
        config = {}
        if os.path.exists(ENV_FILE):
            with open(ENV_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    if "=" in line and not line.strip().startswith("#"):
                        k, v = line.strip().split("=", 1)
                        config[k.strip()] = v.strip()
        return config

    def save_config(self, student_id, password, url, use_widget):
        with open(ENV_FILE, "w", encoding="utf-8") as f:
            f.write(f"MY_STUDENT_ID={student_id}\n")
            f.write(f"MY_PASSWORD={password}\n")
            f.write(f"SCHOOL_URL={url}\n")
            f.write(f"USE_WIDGET={str(use_widget)}\n")

    def show_setup_wizard(self):
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        self.root.geometry(f"350x440+{screen_w - 370}+{screen_h - 510}")

        for widget in self.content_frame.winfo_children():
            widget.destroy()

        tk.Label(self.content_frame, text="⚙️ LỰA CHỌN CHẾ ĐỘ HOẠT ĐỘNG", font=("Segoe UI", 9, "bold"), fg="#fdcb6e", bg="#2f3640", pady=10).pack()

        saved_url = self.config.get("SCHOOL_URL", "https://online.hcmute.edu.vn/student/schedules")
        saved_id = self.config.get("MY_STUDENT_ID", "")
        saved_pass = self.config.get("MY_PASSWORD", "")
        saved_use = self.config.get("USE_WIDGET", "True") == "True"

        self.var_use_widget = tk.BooleanVar(value=saved_use)
        self.chk_widget = tk.Checkbutton(
            self.content_frame, text="Sử dụng tính năng xem Lịch học từ trường", variable=self.var_use_widget,
            command=self.toggle_setup_fields, font=("Segoe UI", 9), fg="#f5f6fa", bg="#2f3640", 
            activebackground="#2f3640", activeforeground="white", selectcolor="#2f3640"
        )
        self.chk_widget.pack(anchor="w", padx=20, pady=5)

        self.lbl_url = tk.Label(self.content_frame, text="Link Đăng nhập / Lịch học:", font=("Segoe UI", 9), fg="#f5f6fa", bg="#2f3640")
        self.lbl_url.pack(anchor="w", padx=20, pady=(5,0))
        self.ent_url = tk.Entry(self.content_frame, font=("Segoe UI", 9), bg="#353b48", fg="white", bd=1, relief="flat")
        self.ent_url.pack(fill="x", padx=20, pady=2, ipady=3)
        self.ent_url.insert(0, saved_url)

        self.lbl_id = tk.Label(self.content_frame, text="Mã số sinh viên (MSSV):", font=("Segoe UI", 9), fg="#f5f6fa", bg="#2f3640")
        self.lbl_id.pack(anchor="w", padx=20, pady=(5,0))
        self.ent_id = tk.Entry(self.content_frame, font=("Segoe UI", 9), bg="#353b48", fg="white", bd=1, relief="flat")
        self.ent_id.pack(fill="x", padx=20, pady=2, ipady=3)
        self.ent_id.insert(0, saved_id)

        self.lbl_pass = tk.Label(self.content_frame, text="Mật khẩu tài khoản:", font=("Segoe UI", 9), fg="#f5f6fa", bg="#2f3640")
        self.lbl_pass.pack(anchor="w", padx=20, pady=(5,0))
        self.ent_pass = tk.Entry(self.content_frame, show="*", font=("Segoe UI", 9), bg="#353b48", fg="white", bd=1, relief="flat")
        self.ent_pass.pack(fill="x", padx=20, pady=2, ipady=3)
        self.ent_pass.insert(0, saved_pass)

        self.btn_exit_setup = tk.Button(
            self.content_frame, text="❌ Thoát Ứng Dụng", command=self.root.destroy,
            bg="#c23616", fg="white", font=("Segoe UI", 9, "bold"), bd=0, pady=6
        )
        self.btn_exit_setup.pack(fill="x", side="bottom", padx=20, pady=(0, 15))

        self.btn_save_wizard = tk.Button(
            self.content_frame, text="🚀 Bắt Đầu Làm Việc", command=self.handle_save_wizard,
            bg="#00a8ff", fg="white", font=("Segoe UI", 10, "bold"), bd=0, pady=8
        )
        self.btn_save_wizard.pack(fill="x", side="bottom", padx=20, pady=(15, 5))
        self.toggle_setup_fields()

    def toggle_setup_fields(self):
        state = "normal" if self.var_use_widget.get() else "disabled"
        self.ent_url.config(state=state)
        self.ent_id.config(state=state)
        self.ent_pass.config(state=state)

    def handle_save_wizard(self):
        use_widget = self.var_use_widget.get()
        url = self.ent_url.get().strip()
        uid = self.ent_id.get().strip()
        pwd = self.ent_pass.get().strip()

        if use_widget and (not url or not uid or not pwd):
            messagebox.showwarning("Cảnh báo", "Sếp vui lòng điền đầy đủ thông tin hoặc bỏ tích chọn xem lịch nhé!")
            return

        self.save_config(uid, pwd, url, use_widget)
        self.config = self.load_config()
        self.show_dashboard()

    def show_dashboard(self):
        self.use_widget_mode = self.config.get("USE_WIDGET", "False") == "True"

        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        
        if self.use_widget_mode:
            tkb_w, tkb_h = 350, 520
        else:
            tkb_w, tkb_h = 350, 270 

        self.root.geometry(f"{tkb_w}x{tkb_h}+{screen_w - tkb_w - 20}+{screen_h - tkb_h - 70}")

        for widget in self.content_frame.winfo_children():
            widget.destroy()

        if self.use_widget_mode:
            self.lbl_tkb_title = tk.Label(self.content_frame, text=" Lịch Học Hệ Thống Hôm Nay:", font=("Segoe UI", 9, "bold"), fg="#fdcb6e", bg="#2f3640", anchor="w")
            self.lbl_tkb_title.pack(fill="x", padx=15, pady=(10, 0))

            self.tkb_frame = tk.Frame(self.content_frame, bg="#20252e", bd=1)
            self.tkb_frame.pack(fill="both", expand=True, padx=15, pady=5)

            self.lbl_tkb_content = tk.Label(
                self.tkb_frame, text="Đang đồng bộ dữ liệu siêu tốc...", font=("Segoe UI", 10),
                fg="#dcdde1", bg="#20252e", justify="left", wraplength=290, anchor="nw", pady=10, padx=10
            )
            self.lbl_tkb_content.pack(fill="both", expand=True)

        self.form_frame = tk.LabelFrame(self.content_frame, text="➕ Thêm Lịch Cho Robot", font=("Segoe UI", 9, "bold"), fg="#00a8ff", bg="#2f3640", bd=1, labelanchor="n")
        self.form_frame.pack(fill="x", padx=15, pady=10, ipady=5)

        self.time_frame = tk.Frame(self.form_frame, bg="#2f3640")
        self.time_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(self.time_frame, text="Thời gian:", font=("Segoe UI", 9), fg="#f5f6fa", bg="#2f3640").pack(side="left")
        
        self.cb_hour = ttk.Combobox(self.time_frame, values=[f"{i:02d}" for i in range(24)], width=4, state="readonly")
        self.cb_hour.set(datetime.now().strftime("%H"))
        self.cb_hour.pack(side="left", padx=5)

        tk.Label(self.time_frame, text=":", font=("Segoe UI", 10, "bold"), fg="white", bg="#2f3640").pack(side="left")

        self.cb_minute = ttk.Combobox(self.time_frame, values=[f"{i:02d}" for i in range(60)], width=4, state="readonly")
        self.cb_minute.set(datetime.now().strftime("%M"))
        self.cb_minute.pack(side="left", padx=5)

        self.txt_job = tk.Entry(self.form_frame, font=("Segoe UI", 10), bg="#353b48", fg="white", insertbackground="white", bd=1, relief="flat")
        self.txt_job.pack(fill="x", padx=10, pady=5, ipady=3)
        self.txt_job.insert(0, "Nhập việc cần làm...")
        self.txt_job.bind("<FocusIn>", lambda e: self.txt_job.delete(0, tk.END) if self.txt_job.get() == "Nhập việc cần làm..." else None)

        self.btn_add = tk.Button(
            self.form_frame, text="⚡ Cập Nhật Lịch Cho Robot", command=self.add_custom_reminder,
            bg="#4cd137", fg="white", font=("Segoe UI", 9, "bold"), bd=0, pady=5
        )
        self.btn_add.pack(fill="x", padx=10, pady=5)

        self.btn_exit_program = tk.Button(
            self.content_frame, text="❌ Tắt Trợ Lý Ngầm Tận Gốc", command=self.root.destroy,
            bg="#c23616", fg="white", font=("Segoe UI", 9, "bold"), bd=0, pady=6
        )
        self.btn_exit_program.pack(fill="x", padx=15, pady=(0, 10))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TCombobox", fieldbackground="#353b48", background="#2f3640", foreground="white")

        if not hasattr(self, 'clock_thread_started'):
            threading.Thread(target=self.clock_watcher, daemon=True).start()
            self.clock_thread_started = True

        if self.use_widget_mode:
            threading.Thread(target=self.spkt_engine, daemon=True).start()

    def add_custom_reminder(self):
        hour = self.cb_hour.get()
        minute = self.cb_minute.get()
        job_text = self.txt_job.get().strip()

        if not job_text or job_text == "Nhập việc cần làm...":
            messagebox.showwarning("Nhắc nhở", "Vui lòng điền việc cần làm sếp ơi!")
            return

        time_key = f"{hour}:{minute}"
        self.custom_schedule[time_key] = job_text
        self.txt_job.delete(0, tk.END)
        messagebox.showinfo("Thành công", f"🤖 Robot ghi nhận nhắc nhở lúc {time_key}!")

    def setup_robot_window(self):
        self.robot_win = tk.Toplevel(self.root)
        self.robot_win.overrideredirect(True)
        self.robot_win.attributes("-topmost", True)

        TRANSPARENT_KEY = "#000001"
        self.robot_win.configure(bg=TRANSPARENT_KEY)
        self.robot_win.attributes("-transparentcolor", TRANSPARENT_KEY)

        screen_h = self.root.winfo_screenheight()
        self.robot_win.geometry(f"240x280+20+{screen_h - 280 - 70}")

        try:
            img = Image.open(resource_path("robot_transparent.png"))
            img = img.resize((200, 180), Image.Resampling.LANCZOS)
            self.robot_photo = ImageTk.PhotoImage(img)
            tk.Label(self.robot_win, image=self.robot_photo, bg=TRANSPARENT_KEY, bd=0).pack()
        except Exception:
            tk.Label(self.robot_win, text="[Thiếu ảnh robot_transparent.png]", fg="#e84118", bg="white").pack()

        self.msg_frame = tk.Frame(self.robot_win, bg="#00a8ff", bd=0)
        self.msg_frame.pack(fill="x", padx=5)

        self.lbl_reminder_text = tk.Label(self.msg_frame, text="", font=("Segoe UI", 10, "bold"), fg="white", bg="#00a8ff", wraplength=210, pady=8)
        self.lbl_reminder_text.pack()

        tk.Button(self.robot_win, text="Đã xử lý ✔", command=self.hide_robot, bg="#4cd137", fg="white", font=("Segoe UI", 9, "bold"), bd=0, pady=4).pack(pady=4)
        self.robot_win.withdraw()

    def hide_robot(self):
        self.robot_win.withdraw()

    def pop_robot(self, text_message):
        self.root.after(0, lambda: self.lbl_reminder_text.config(text=text_message))
        self.root.after(0, self.robot_win.deiconify)
        threading.Timer(60.0, lambda: self.root.after(0, self.hide_robot)).start()

    def start_drag(self, event):
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def drag_window(self, event):
        deltax = event.x - self.drag_data["x"]
        deltay = event.y - self.drag_data["y"]
        self.root.geometry(f"+{self.root.winfo_x() + deltax}+{self.root.winfo_y() + deltay}")

    def clock_watcher(self):
        last_triggered = ""
        while True:
            now = datetime.now().strftime("%H:%M")
            if now in self.custom_schedule and now != last_triggered:
                self.pop_robot(self.custom_schedule[now])
                last_triggered = now
            time.sleep(5)

    def spkt_engine(self):
        time.sleep(5) 
        while True:
            raw_table_data = self.crawl_spkt()
            if raw_table_data:
                with open(FILE_CACHE, "w", encoding="utf-8") as f:
                    f.write(raw_table_data)
            self.root.after(0, self.render_today_schedule)
            
            # Thu hồi rác bộ nhớ do Selenium để lại để tránh đầy RAM
            gc.collect() 
            time.sleep(7200)

    def render_today_schedule(self):
        today_name = VIETNAMESE_DAYS[datetime.now().weekday()]
        self.lbl_tkb_title.config(text=f" Lịch Học Hệ Thống Hôm Nay ({today_name.upper()}):")

        if not os.path.exists(FILE_CACHE):
            self.lbl_tkb_content.config(text="Chưa lấy được dữ liệu lịch học.")
            return

        with open(FILE_CACHE, "r", encoding="utf-8") as f:
            lines = f.readlines()

        today_classes = [line.replace(today_name, "").strip() for line in lines if today_name.lower() in line.lower()]

        if today_classes:
            self.lbl_tkb_content.config(text="\n".join([f"• {c}" for c in today_classes]), fg="#00cec9")
        else:
            self.lbl_tkb_content.config(text="🎉 Hôm nay sếp không có tiết học nào trên trường.", fg="#4cd137")

    def crawl_spkt(self):
        opts = Options()
        
        # CÁC CỜ TỐI ƯU HÓA TỐI ĐA CHO SELENIUM TRÁNH LAG MÁY
        opts.add_argument("--headless=new") # Bắt buộc chạy nền chuẩn mới
        opts.add_argument("--log-level=3")
        opts.add_argument("--disable-gpu") # Tắt xử lý đồ họa
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--disable-software-rasterizer")
        opts.add_argument("--blink-settings=imagesEnabled=false") # Không tải hình ảnh để web load tức thì
        
        opts.page_load_strategy = 'eager' # Chỉ đợi HTML DOM, không đợi toàn bộ tài nguyên
        
        srv = Service()
        srv.creation_flags = CREATE_NO_WINDOW
        
        driver = None
        try:
            driver = webdriver.Chrome(options=opts, service=srv)
            
            driver.set_page_load_timeout(30)
            driver.implicitly_wait(5)
            
            driver.get(self.config.get("SCHOOL_URL", ""))
            
            if "login" in driver.current_url.lower() or "đăng nhập" in driver.page_source.lower():
                driver.find_element(By.XPATH, "//input[@type='text' and not(@hidden)] | //input[contains(@name, 'User')]").send_keys(self.config.get("MY_STUDENT_ID", ""))
                driver.find_element(By.XPATH, "//input[@type='password']").send_keys(self.config.get("MY_PASSWORD", ""))
                driver.find_element(By.XPATH, "//button[@type='submit'] | //input[@type='submit']").click()
                time.sleep(3) # Giảm thời gian chờ do web không tải ảnh nữa

            soup = BeautifulSoup(driver.page_source, "html.parser")
            rows = soup.find_all("tr")
            extracted_rows = []
            for r in rows:
                cols = [c.get_text(strip=True) for c in r.find_all(["td", "th"])]
                if any(cols):
                    extracted_rows.append(" | ".join(cols))
            
            return "\n".join(extracted_rows)

        except Exception as e:
            error_detail = traceback.format_exc()
            self.root.after(0, lambda: messagebox.showerror(
                "🚨 BẮT ĐƯỢC BỆNH CỦA FILE EXE", 
                f"Bot báo cáo lý do không lấy được TKB:\n\n{error_detail}"
            ))
            return None
        finally:
            if driver:
                try: 
                    driver.quit()
                except Exception: 
                    pass

if __name__ == "__main__":
    root = tk.Tk()
    app = UltimateUniversalAssistant(root)
    root.mainloop()