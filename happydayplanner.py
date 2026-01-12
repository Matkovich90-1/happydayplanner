import tkinter as tk
from tkinter import scrolledtext
from tkcalendar import Calendar 
import datetime
import sqlite3

class HappyDayPlanner:
    def __init__(self, root):
        self.root = root
        self.root.title("🌈 Happy!")
        self.root.geometry("1000x850")
        
        # Colors
        self.C_PRIMARY = "#07415E"
        self.C_LIGHT_BG = "#E8EAEE"
        self.C_ACCENT = "#FF8E53"
        self.C_MEAL = "#D1E8E2" 
        self.C_WHITE = "#FFFFFF"
        
        self.root.configure(bg=self.C_PRIMARY)
        self.db_path = "planner_data.db"
        
        self.conn = sqlite3.connect(self.db_path)
        self.init_db()

        self.save_jobs = {}
        self.current_date = datetime.date.today()
        self.view_mode = "week" 

        # Clock
        self.clock_label = tk.Label(root, font=("Arial", 10, "bold"), fg="white", bg=self.C_PRIMARY, justify="right")
        self.clock_label.place(relx=0.98, y=20, anchor="ne")
        self.update_clock() 

        self.title_label = tk.Label(root, text="📅 My Happy Planner", font=("Arial", 20, "bold"), fg="white", bg=self.C_PRIMARY)
        self.title_label.pack(pady=10)

        self.main_container = tk.Frame(root, bg=self.C_LIGHT_BG, bd=2, relief="ridge")
        self.main_container.pack(pady=10, fill="both", expand=True, padx=20)

        self.nav_frame = tk.Frame(root, bg=self.C_PRIMARY)
        self.nav_frame.pack(pady=10)

        self.render()

    def init_db(self):
        self.conn.execute("CREATE TABLE IF NOT EXISTS notes (date TEXT, hour INTEGER, note TEXT, PRIMARY KEY(date, hour))")
        self.conn.commit()

    def update_clock(self):
        now_str = datetime.datetime.now().strftime("%a, %b %d, %Y\n%I:%M:%S %p")
        self.clock_label.config(text=now_str)
        self.root.after(1000, self.update_clock)

    def render(self):
        for widget in self.main_container.winfo_children(): widget.destroy()
        for widget in self.nav_frame.winfo_children(): widget.destroy()
        
        if self.view_mode == "week":
            self.clock_label.place(relx=0.98, y=20, anchor="ne")
            self.render_split_view()
        else:
            self.clock_label.place_forget()
            self.render_day_view()

    def render_split_view(self):
        # 1. Top Section: Week Row (Main)
        week_frame = tk.LabelFrame(self.main_container, text=" Weekly Overview ", font=("Arial", 14, "bold"), bg=self.C_LIGHT_BG, fg=self.C_PRIMARY)
        week_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        week_start = self.current_date - datetime.timedelta(days=self.current_date.weekday())
        for i in range(7):
            day = week_start + datetime.timedelta(days=i)
            is_today = day == datetime.date.today()
            bg_color = "#0E6691" if is_today else "#4FA1CA"
            
            btn = tk.Button(week_frame, text=day.strftime('%A\n%b %d'), 
                            font=("Arial", 12, "bold"), bg=bg_color, fg="white",
                            relief="flat", highlightthickness=3 if is_today else 0, highlightbackground=self.C_ACCENT,
                            command=lambda d=day: self.open_day(d))
            btn.grid(row=0, column=i, sticky="nsew", padx=8, pady=20)
            week_frame.grid_columnconfigure(i, weight=1)
        week_frame.grid_rowconfigure(0, weight=1)

        # 2. Bottom Section: Calendar (Smaller)
        cal_frame = tk.LabelFrame(self.main_container, text=" Month Picker ", font=("Arial", 10, "bold"), bg=self.C_LIGHT_BG, fg=self.C_PRIMARY)
        cal_frame.pack(fill="x", side="bottom", padx=15, pady=10)

        self.cal = Calendar(cal_frame, selectmode='day', font="Arial 9", 
                           background=self.C_PRIMARY, headersbackground=self.C_ACCENT)
        self.cal.pack(pady=5)
        self.highlight_noted_days()
        self.cal.bind("<<CalendarSelected>>", lambda e: self.open_day(self.cal.selection_get()))

        # --- Nav Buttons ---
        tk.Button(self.nav_frame, text="‹ Prev Week", command=self.prev_week, bg=self.C_ACCENT, fg="white", font=("Arial", 10, "bold"), width=12).pack(side="left", padx=5)
        tk.Button(self.nav_frame, text="✨ Today", command=self.go_today, bg="#FFD700", fg=self.C_PRIMARY, font=("Arial", 10, "bold"), width=12).pack(side="left", padx=5)
        tk.Button(self.nav_frame, text="Next Week ›", command=self.next_week, bg=self.C_ACCENT, fg="white", font=("Arial", 10, "bold"), width=12).pack(side="left", padx=5)

    def render_day_view(self):
        header = tk.Frame(self.main_container, bg=self.C_PRIMARY)
        header.pack(fill="x")
        tk.Label(header, text=self.current_date.strftime('%A, %B %d'), font=("Arial", 16, "bold"), fg="white", bg=self.C_PRIMARY).pack(pady=10)
        
        canvas = tk.Canvas(self.main_container, bg=self.C_LIGHT_BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(self.main_container, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=self.C_LIGHT_BG)

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas_frame = canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(canvas_frame, width=e.width))
        canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        # Hourly slots
        for hour in range(24):
            am_pm = "AM" if hour < 12 else "PM"
            display_hour = hour if hour <= 12 else hour - 12
            if display_hour == 0: display_hour = 12
            
            row_bg = self.C_MEAL if hour in [8, 12, 18] else self.C_WHITE
            row = tk.Frame(scroll_frame, bg=row_bg, bd=1, relief="groove")
            row.pack(fill="x", padx=15, pady=2)
            
            tk.Label(row, text=f"{display_hour}:00 {am_pm}", width=12, font=("Arial", 9, "bold"), bg=row_bg).pack(side="left", padx=5)
            
            txt = tk.Text(row, height=1, font=("Arial", 11), relief="flat")
            txt.pack(side="left", fill="x", expand=True, padx=5, pady=3)
            txt.insert("1.0", self.get_note(self.current_date.isoformat(), hour))
            txt.bind("<KeyRelease>", lambda e, h=hour, t=txt: self.handle_typing(h, t))

        # --- Daily Reflection / Comment Section ---
        comment_frame = tk.LabelFrame(scroll_frame, text=" 📝 Daily Reflections & Notes ", font=("Arial", 12, "bold"), bg="#FFF9C4", fg=self.C_PRIMARY)
        comment_frame.pack(fill="x", padx=15, pady=20)
        
        comment_txt = tk.Text(comment_frame, height=5, font=("Arial", 11), relief="flat", bg="#FFF9C4")
        comment_txt.pack(fill="x", padx=10, pady=10)
        comment_txt.insert("1.0", self.get_note(self.current_date.isoformat(), -1)) # Use -1 for daily notes
        comment_txt.bind("<KeyRelease>", lambda e, h=-1, t=comment_txt: self.handle_typing(h, t))

        tk.Button(self.nav_frame, text="Back to Main View", command=self.back_to_week, 
                  bg=self.C_ACCENT, fg="white", font=("Arial", 11, "bold"), width=20).pack()

    def handle_typing(self, hour, text_widget):
        if hour in self.save_jobs:
            self.root.after_cancel(self.save_jobs[hour])
        content = text_widget.get("1.0", "end-1c")
        self.save_jobs[hour] = self.root.after(750, lambda: self.save_note(self.current_date.isoformat(), hour, content))

    def highlight_noted_days(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT DISTINCT date FROM notes WHERE note != ''")
        for (date_str,) in cursor.fetchall():
            try:
                self.cal.calevent_create(datetime.date.fromisoformat(date_str), 'Note', 'noted')
            except: continue
        self.cal.tag_config('noted', background='#FFD700', foreground='black')

    def open_day(self, day):
        self.current_date = day if not isinstance(day, str) else datetime.date.fromisoformat(day)
        self.view_mode = "day"; self.render()

    def go_today(self):
        self.current_date = datetime.date.today()
        self.view_mode = "week"; self.render()

    def back_to_week(self): self.view_mode = "week"; self.render()
    def get_note(self, date_str, hour):
        res = self.conn.execute("SELECT note FROM notes WHERE date=? AND hour=?", (date_str, hour)).fetchone()
        return res[0] if res else ""
    def save_note(self, date_str, hour, note):
        self.conn.execute("INSERT OR REPLACE INTO notes (date, hour, note) VALUES (?, ?, ?)", (date_str, hour, note))
        self.conn.commit()
    def prev_week(self): self.current_date -= datetime.timedelta(days=7); self.render()
    def next_week(self): self.current_date += datetime.timedelta(days=7); self.render()

if __name__ == "__main__":
    root = tk.Tk()
    app = HappyDayPlanner(root)
    root.mainloop()

