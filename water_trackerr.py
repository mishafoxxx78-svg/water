import customtkinter as ctk
import json
import os
from datetime import datetime, timedelta
import math
import random

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

DATA_FILE = "water_data.json"

ACHIEVEMENTS = [
    ("💧", "Первый глоток",    "Вы выпили первый стакан воды!",             1),
    ("🌊", "Пол-литра",        "500 мл за день — хорошее начало!",          500),
    ("💪", "Литр силы",        "1 литр воды! Ваше тело благодарит.",        1000),
    ("🎯", "Цель достигнута",  "Вы выполнили дневную норму воды!",          "goal"),
    ("🔥", "5 дней подряд",    "Пять дней подряд — вы пьёте достаточно!",  "streak_5"),
    ("⭐", "10 дней подряд",   "Десять дней — это привычка!",               "streak_10"),
    ("👑", "30 дней подряд",   "Месяц водного режима! Вы чемпион!",        "streak_30"),
    ("🏆", "Водный чемпион",   "Суммарно выпито 50 литров воды!",          50000),
    ("🌍", "100 литров",       "100 литров! Вы спасли планету!",           100000),
    ("💎", "Рекордсмен",       "Личный рекорд — больше 150% нормы!",       "over_150"),
]

MOTIVATION_QUOTES = [
    "💙 Каждый глоток — шаг к здоровью.",
    "🌟 Твоё тело на 60% состоит из воды.",
    "🧠 Мозг работает лучше, когда ты пьёшь воду.",
    "✨ Чистая вода — чистое тело.",
    "🔋 Вода — твоё топливо. Заправляйся!",
    "🏃 Вода ускоряет метаболизм.",
    "💤 Недостаток воды = усталость.",
    "🍃 Вода выводит токсины.",
    "❤️ Пей за здоровое сердце!",
    "🌙 Начни утро со стакана воды!",
    "🔥 Жажда — уже обезвоживание.",
    "🎨 Не дай себе засохнуть!",
]

WATER_FACTS = [
    "Вода составляет около 75% мозга.",
    "Человек может прожить без воды всего 3–5 дней.",
    "1 стакан до еды помогает пищеварению.",
    "Лёгкое обезвоживание снижает концентрацию на 15%.",
    "Холодная вода сжигает калории — тело тратит энергию на её нагрев.",
    "Кожа на 64% состоит из воды.",
    "Вода переносит кислород ко всем клеткам тела.",
    "Недостаток воды — главная причина дневной усталости.",
]

HYDRATION_TIPS = [
    "Держите бутылку воды на рабочем столе — будете пить чаще.",
    "Добавьте в воду лимон или мяту для вкуса.",
    "Пейте воду комнатной температуры — она усваивается быстрее.",
    "Начинайте утро со стакана воды, до кофе.",
    "После каждого похода в туалет — стакан воды.",
    "Во время тренировки пейте каждые 15–20 минут.",
    "Ешьте больше фруктов и овощей — они содержат воду.",
    "Цвет мочи — лучший индикатор: светло-жёлтый = норма.",
]


class WaterTrackerApp:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("💧 Водный баланс")
        self.window.geometry("460x800")
        self.window.resizable(False, False)

        self.data = self.load_data()
        self.today = datetime.now().strftime("%Y-%m-%d")
        self._notified_achievements = set(self.data.get("notified_achievements", []))
        self._quote_index = self.data.get("quote_index", 0)
        self._wave_phase = 0.0
        self.ensure_today()

        self.build_ui()
        self.update_display()
        self._animate_wave()
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        self.window.mainloop()

    # ── Данные ───────────────────────────────────────────────────────────
    def load_data(self):
        defaults = {
            "daily_goal_ml": 2000,
            "history": {},
            "notified_achievements": [],
            "quote_index": 0,
            "streak": 0,
            "best_streak": 0,
            "total_ml": 0,
            "best_day_ml": 0,
            "best_day_date": "",
        }
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            for k, v in defaults.items():
                if k not in data:
                    data[k] = v
            return data
        return defaults

    def save_data(self):
        self.data["notified_achievements"] = list(self._notified_achievements)
        self.data["quote_index"] = self._quote_index
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def ensure_today(self):
        if self.today not in self.data["history"]:
            self.data["history"][self.today] = {"drunk_ml": 0, "portions": []}
            self.save_data()

    def get_today_drunk(self):
        return self.data["history"].get(self.today, {}).get("drunk_ml", 0)

    def calculate_streak(self):
        streak = 0
        today = datetime.now()
        for i in range(365):
            day = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            if day in self.data["history"]:
                if self.data["history"][day]["drunk_ml"] >= self.data["daily_goal_ml"]:
                    streak += 1
                else:
                    break
            else:
                break
        return streak

    # ── Интерфейс ────────────────────────────────────────────────────────
    def build_ui(self):
        # Основной скролл-контейнер
        self.main_scroll = ctk.CTkScrollableFrame(
            self.window, fg_color="#0d0d1a", corner_radius=0
        )
        self.main_scroll.pack(fill="both", expand=True)

        # ── Шапка ──────────────────────────────────────────────────
        header = ctk.CTkFrame(self.main_scroll, fg_color="#111128", corner_radius=16)
        header.pack(fill="x", padx=14, pady=(14, 6))

        ctk.CTkLabel(
            header, text="💧 Водный баланс",
            font=ctk.CTkFont(family="Georgia", size=26, weight="bold"),
            text_color="#7ec8f5"
        ).pack(pady=(14, 2))

        ctk.CTkLabel(
            header,
            text=datetime.now().strftime("%A, %d %B %Y").capitalize(),
            font=ctk.CTkFont(size=12),
            text_color="#445577"
        ).pack()

        self.quote_label = ctk.CTkLabel(
            header, text="",
            font=ctk.CTkFont(size=11, slant="italic"),
            text_color="#5599cc",
            wraplength=400, justify="center"
        )
        self.quote_label.pack(pady=(6, 14))
        self._update_quote()

        # ── Стакан + прогресс ──────────────────────────────────────
        glass_card = ctk.CTkFrame(self.main_scroll, fg_color="#111128", corner_radius=16)
        glass_card.pack(fill="x", padx=14, pady=6)

        glass_row = ctk.CTkFrame(glass_card, fg_color="transparent")
        glass_row.pack(pady=(14, 6))

        # Стакан (Canvas)
        self.canvas = ctk.CTkCanvas(
            glass_row, width=160, height=220,
            bg="#111128", highlightthickness=0
        )
        self.canvas.pack(side="left", padx=(20, 10))

        # Правая панель прогресса
        info_col = ctk.CTkFrame(glass_row, fg_color="transparent")
        info_col.pack(side="left", padx=(10, 20), anchor="center")

        self.progress_label = ctk.CTkLabel(
            info_col, text="0 / 2000",
            font=ctk.CTkFont(family="Georgia", size=30, weight="bold"),
            text_color="#e0f0ff"
        )
        self.progress_label.pack()

        ctk.CTkLabel(
            info_col, text="мл",
            font=ctk.CTkFont(size=12),
            text_color="#445577"
        ).pack()

        self.percent_label = ctk.CTkLabel(
            info_col, text="0%",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#4A9EFF"
        )
        self.percent_label.pack(pady=(6, 0))

        self.remain_label = ctk.CTkLabel(
            info_col, text="осталось: 2000 мл",
            font=ctk.CTkFont(size=11),
            text_color="#445577"
        )
        self.remain_label.pack()

        # Полоса прогресса
        self.progress_bar = ctk.CTkProgressBar(
            glass_card, width=410, height=12, corner_radius=6
        )
        self.progress_bar.pack(pady=(0, 16), padx=20)
        self.progress_bar.set(0)

        # ── Быстрые кнопки ─────────────────────────────────────────
        quick_card = ctk.CTkFrame(self.main_scroll, fg_color="#111128", corner_radius=16)
        quick_card.pack(fill="x", padx=14, pady=6)

        ctk.CTkLabel(
            quick_card, text="Быстрое добавление",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#556688"
        ).pack(pady=(12, 6))

        quick_frame = ctk.CTkFrame(quick_card, fg_color="transparent")
        quick_frame.pack(pady=(0, 14))

        quick_opts = [
            (150, "🥤", "Стакан"),
            (250, "🥛", "Стакан"),
            (350, "🍵", "Кружка"),
            (500, "🍾", "Бутылка"),
        ]
        for ml, emoji, label in quick_opts:
            btn_frame = ctk.CTkFrame(quick_frame, fg_color="#1a1a38", corner_radius=12)
            btn_frame.pack(side="left", padx=4)
            ctk.CTkButton(
                btn_frame,
                text=f"{emoji}\n{ml} мл",
                width=88, height=60,
                font=ctk.CTkFont(size=13),
                fg_color="transparent",
                hover_color="#2a2a55",
                corner_radius=12,
                command=lambda m=ml: self.add_water(m),
            ).pack()

        # ── Свой объём ─────────────────────────────────────────────
        custom_card = ctk.CTkFrame(self.main_scroll, fg_color="#111128", corner_radius=16)
        custom_card.pack(fill="x", padx=14, pady=6)

        custom_inner = ctk.CTkFrame(custom_card, fg_color="transparent")
        custom_inner.pack(pady=14, padx=14)

        self.custom_entry = ctk.CTkEntry(
            custom_inner,
            placeholder_text="Свой объём (мл)",
            width=180, height=40,
            font=ctk.CTkFont(size=14),
            fg_color="#1a1a38",
            border_color="#2a2a55",
        )
        self.custom_entry.pack(side="left", padx=(0, 8))
        self.custom_entry.bind("<Return>", lambda e: self.add_custom())

        ctk.CTkButton(
            custom_inner,
            text="➕ Добавить",
            width=120, height=40,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#1b5e8e",
            hover_color="#256ba8",
            command=self.add_custom,
        ).pack(side="left", padx=(0, 8))

        self.undo_btn = ctk.CTkButton(
            custom_inner,
            text="↩ Отмена",
            width=100, height=40,
            font=ctk.CTkFont(size=12),
            fg_color="#3a1a1a",
            hover_color="#5a2a2a",
            state="disabled",
            command=self.undo_last,
        )
        self.undo_btn.pack(side="left")

        # ── История сегодня ────────────────────────────────────────
        hist_card = ctk.CTkFrame(self.main_scroll, fg_color="#111128", corner_radius=16)
        hist_card.pack(fill="x", padx=14, pady=6)

        hist_header = ctk.CTkFrame(hist_card, fg_color="transparent")
        hist_header.pack(fill="x", padx=14, pady=(12, 0))

        ctk.CTkLabel(
            hist_header, text="📝 Сегодняшние порции",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#556688"
        ).pack(side="left")

        self.portions_frame = ctk.CTkScrollableFrame(
            hist_card, height=80, fg_color="transparent"
        )
        self.portions_frame.pack(fill="x", padx=10, pady=(4, 12))

        # ── Кнопки действий ────────────────────────────────────────
        action_row = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        action_row.pack(pady=6)

        for text, color, hover, cmd in [
            ("⚙️ Норма",      "#1a2a3a", "#2a3a55", self.open_settings),
            ("💡 Совет",      "#1a2a1a", "#2a3a2a", self.show_tip),
            ("📊 Статистика", "#1a1a3a", "#2a2a55", self.show_stats),
        ]:
            ctk.CTkButton(
                action_row,
                text=text, width=130, height=38,
                font=ctk.CTkFont(size=13),
                fg_color=color, hover_color=hover,
                corner_radius=10,
                command=cmd,
            ).pack(side="left", padx=4)

        # Мини-статистика
        self.stats_label = ctk.CTkLabel(
            self.main_scroll, text="",
            font=ctk.CTkFont(size=11),
            text_color="#334455"
        )
        self.stats_label.pack(pady=4)

        # ── Достижения ─────────────────────────────────────────────
        ach_card = ctk.CTkFrame(self.main_scroll, fg_color="#111128", corner_radius=16)
        ach_card.pack(fill="x", padx=14, pady=(6, 16))

        ctk.CTkLabel(
            ach_card, text="🏅 Достижения",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#7ec8f5"
        ).pack(pady=(12, 6))

        ach_inner = ctk.CTkScrollableFrame(
            ach_card, height=90, fg_color="transparent"
        )
        ach_inner.pack(fill="x", padx=8, pady=(0, 12))

        self.ach_labels = {}
        row_frame = None
        for i, (icon, name, desc, trigger) in enumerate(ACHIEVEMENTS):
            if i % 5 == 0:
                row_frame = ctk.CTkFrame(ach_inner, fg_color="transparent")
                row_frame.pack(fill="x", pady=2)
            lbl = ctk.CTkLabel(
                row_frame, text=icon,
                font=ctk.CTkFont(size=20),
                width=52, height=40,
                corner_radius=8,
                fg_color="#1a1a38",
                text_color="#333355",
            )
            lbl.pack(side="left", padx=3)
            key = trigger if isinstance(trigger, str) else trigger
            self.ach_labels[key] = lbl

    # ── Анимация волны ──────────────────────────────────────────────────
    def _animate_wave(self):
        self._wave_phase += 0.18
        self.draw_glass()
        self.window.after(60, self._animate_wave)

    def draw_glass(self):
        self.canvas.delete("all")
        c = self.canvas
        drunk = self.get_today_drunk()
        goal = self.data["daily_goal_ml"]
        fill_ratio = min(drunk / goal, 1.0) if goal > 0 else 0

        W, H = 160, 220
        gx1, gx2 = 30, 130
        gy1, gy2 = 10, 200

        # Тень стакана
        c.create_rectangle(gx1 + 4, gy1 + 4, gx2 + 4, gy2 + 4,
                           fill="#070714", outline="", width=0)

        # Фон стакана
        c.create_rectangle(gx1, gy1, gx2, gy2,
                           fill="#0d0d22", outline="")

        if fill_ratio > 0:
            water_h = (gy2 - gy1) * fill_ratio
            water_y = gy2 - water_h

            # Цвет воды
            if fill_ratio < 0.4:
                col = "#0d4f7a"
            elif fill_ratio < 0.75:
                col = "#1272b0"
            elif fill_ratio < 1.0:
                col = "#1a90e0"
            else:
                col = "#00cc88"

            # Тело воды
            c.create_rectangle(gx1, water_y, gx2, gy2, fill=col, outline="")

            # Волна
            pts = []
            for x in range(gx1, gx2 + 1):
                t = (x - gx1) / (gx2 - gx1)
                wy = water_y + math.sin(t * math.pi * 4 + self._wave_phase) * 5 \
                             + math.sin(t * math.pi * 7 - self._wave_phase * 0.7) * 2
                pts += [x, wy]
            pts += [gx2, gy2, gx1, gy2]
            c.create_polygon(pts, fill=col, outline="")

            # Блик воды
            c.create_rectangle(gx1, water_y - 1, gx2, water_y + 2,
                               fill="#3a5a7a", outline="")

            # Пузырьки
            if fill_ratio > 0.25:
                rng = random.Random(int(self._wave_phase * 2) % 97)
                for _ in range(int(fill_ratio * 6)):
                    bx = rng.randint(gx1 + 10, gx2 - 10)
                    by = rng.randint(int(water_y) + 15, gy2 - 20)
                    r = rng.randint(2, 4)
                    c.create_oval(bx - r, by - r, bx + r, by + r,
                                  outline="#5599bb", fill="", width=1)

        # Стенки стакана (поверх воды)
        c.create_line(gx1, gy1, gx1, gy2, fill="#2a4466", width=2)
        c.create_line(gx2, gy1, gx2, gy2, fill="#2a4466", width=2)
        c.create_line(gx1, gy2, gx2, gy2, fill="#2a4466", width=3)

        # Блик стакана
        c.create_line(gx1 + 6, gy1 + 10, gx1 + 6, gy2 - 10,
                      fill="#1e2a3a", width=3)

        # Ручка
        c.create_arc(gx2 - 5, gy1 + 50, gx2 + 28, gy1 + 120,
                     start=270, extent=180,
                     outline="#2a4466", width=2, style="arc")

        # Метки уровня
        for frac, label in [(0.25, "25%"), (0.5, "50%"), (0.75, "75%")]:
            ly = gy2 - (gy2 - gy1) * frac
            c.create_line(gx2 - 10, ly, gx2, ly, fill="#2a4466", width=1)
            c.create_text(gx2 + 18, ly, text=label,
                         fill="#2a3355", font=("Arial", 7), anchor="e")

        # Текст объёма
        tx = (gx1 + gx2) // 2
        ty = (gy1 + gy2) // 2
        c.create_text(tx, ty, text=f"{int(drunk)}\nмл",
                     fill="#c0e8ff", font=("Arial", 14, "bold"), justify="center")

        # Смайл при выполнении
        if fill_ratio >= 1.0:
            c.create_text(tx, gy1 - 5, text="✓", fill="#00cc88",
                         font=("Arial", 14, "bold"))

    # ── Обновление дисплея ──────────────────────────────────────────────
    def update_display(self):
        drunk = self.get_today_drunk()
        goal = self.data["daily_goal_ml"]
        pct = min(drunk / goal, 1.0) if goal > 0 else 0
        pct_int = int(pct * 100)

        self.progress_label.configure(text=f"{drunk} / {goal}")
        self.percent_label.configure(text=f"{pct_int}%")
        remain = max(goal - drunk, 0)
        self.remain_label.configure(text=f"осталось: {remain} мл" if remain else "✅ Норма выполнена!")
        self.progress_bar.set(pct)

        if pct < 0.3:
            bar_col = "#e05555"
        elif pct < 0.6:
            bar_col = "#e0a020"
        elif pct < 0.9:
            bar_col = "#1e90ff"
        else:
            bar_col = "#00cc88"
        self.progress_bar.configure(progress_color=bar_col)
        self.percent_label.configure(text_color=bar_col)

        # Серия
        streak = self.calculate_streak()
        self.data["streak"] = streak
        if streak > self.data["best_streak"]:
            self.data["best_streak"] = streak

        # Мини-статистика
        week_total, week_days = 0, 0
        for i in range(7):
            day = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            if day in self.data["history"]:
                week_total += self.data["history"][day]["drunk_ml"]
                week_days += 1
        parts = []
        if week_days:
            parts.append(f"📊 7 дней: {int(week_total/week_days)} мл/день")
        if streak:
            parts.append(f"🔥 {streak} дн. подряд")
        if self.data["best_streak"]:
            parts.append(f"👑 Рекорд: {self.data['best_streak']} дн.")
        self.stats_label.configure(text="   ".join(parts))

        self._update_portions_list()
        self._update_achievements()
        self._update_undo_btn()
        self.save_data()

    def _update_portions_list(self):
        for w in self.portions_frame.winfo_children():
            w.destroy()
        portions = self.data["history"].get(self.today, {}).get("portions", [])
        if not portions:
            ctk.CTkLabel(
                self.portions_frame, text="Пока ничего не добавлено",
                font=ctk.CTkFont(size=11), text_color="#334455"
            ).pack(side="left", padx=6)
            return
        for p in reversed(portions[-10:]):
            t = datetime.fromisoformat(p["time"]).strftime("%H:%M")
            chip = ctk.CTkLabel(
                self.portions_frame,
                text=f"  💧 {p['ml']} мл  {t}  ",
                font=ctk.CTkFont(size=11),
                text_color="#88bbdd",
                fg_color="#1a1a38",
                corner_radius=8,
                height=26,
            )
            chip.pack(side="left", padx=3, pady=2)

    def _update_undo_btn(self):
        portions = self.data["history"].get(self.today, {}).get("portions", [])
        if portions:
            self.undo_btn.configure(state="normal")
        else:
            self.undo_btn.configure(state="disabled")

    # ── Достижения ──────────────────────────────────────────────────────
    def _update_achievements(self):
        drunk = self.get_today_drunk()
        goal = self.data["daily_goal_ml"]
        total = self.data.get("total_ml", 0)
        streak = self.data.get("streak", 0)
        best_day = self.data.get("best_day_ml", 0)

        for (icon, name, desc, trigger) in ACHIEVEMENTS:
            key = trigger if isinstance(trigger, str) else trigger
            lbl = self.ach_labels.get(key)
            if lbl is None:
                continue
            unlocked = False
            if isinstance(trigger, int):
                unlocked = total >= trigger or drunk >= trigger
            elif trigger == "goal":
                unlocked = drunk >= goal
            elif trigger == "streak_5":
                unlocked = streak >= 5
            elif trigger == "streak_10":
                unlocked = streak >= 10
            elif trigger == "streak_30":
                unlocked = streak >= 30
            elif trigger == "over_150":
                unlocked = goal > 0 and best_day >= goal * 1.5

            if unlocked:
                lbl.configure(fg_color="#0f2a1f", text_color="#55ee99")
                if key not in self._notified_achievements:
                    self._notified_achievements.add(key)
                    self._show_achievement_popup(icon, name, desc)
            else:
                lbl.configure(fg_color="#1a1a38", text_color="#333355")

    def _show_achievement_popup(self, icon, name, desc):
        popup = ctk.CTkToplevel(self.window)
        popup.title("🏅 Достижение!")
        popup.geometry("340x200")
        popup.grab_set()
        popup.resizable(False, False)
        ctk.CTkLabel(popup, text="🏅 НОВОЕ ДОСТИЖЕНИЕ!",
                    font=ctk.CTkFont(size=14, weight="bold"), text_color="#ffdd00").pack(pady=(18, 4))
        ctk.CTkLabel(popup, text=f"{icon} {name}",
                    font=ctk.CTkFont(size=20, weight="bold"), text_color="#55ee99").pack(pady=4)
        ctk.CTkLabel(popup, text=desc,
                    font=ctk.CTkFont(size=12), wraplength=300, text_color="white").pack(pady=6)
        ctk.CTkButton(popup, text="Круто! 💪", width=120, command=popup.destroy).pack(pady=10)

    # ── Цитаты ──────────────────────────────────────────────────────────
    def _update_quote(self):
        drunk = self.get_today_drunk()
        goal = self.data["daily_goal_ml"]
        pct = min(drunk / goal, 1.0) if goal > 0 else 0
        if pct >= 1.0:
            q = "🎉 Норма выполнена! Твоё тело счастливо!"
        else:
            q = MOTIVATION_QUOTES[self._quote_index % len(MOTIVATION_QUOTES)]
        self.quote_label.configure(text=q)
        self._quote_index = (self._quote_index + 1) % len(MOTIVATION_QUOTES)
        self.window.after(30000, self._update_quote)

    # ── Добавление воды ─────────────────────────────────────────────────
    def add_water(self, ml):
        self.data["history"][self.today]["drunk_ml"] += ml
        self.data["history"][self.today]["portions"].append({
            "ml": ml,
            "time": datetime.now().isoformat()
        })
        self.data["total_ml"] = self.data.get("total_ml", 0) + ml
        today_drunk = self.get_today_drunk()
        if today_drunk > self.data.get("best_day_ml", 0):
            self.data["best_day_ml"] = today_drunk
            self.data["best_day_date"] = self.today
        prev = today_drunk - ml
        self.save_data()
        self.update_display()
        if today_drunk >= self.data["daily_goal_ml"] > prev:
            self._show_goal_reached_popup()

    def add_custom(self):
        try:
            ml = int(self.custom_entry.get())
            if ml > 0:
                self.add_water(ml)
                self.custom_entry.delete(0, "end")
        except ValueError:
            pass

    def undo_last(self):
        portions = self.data["history"].get(self.today, {}).get("portions", [])
        if not portions:
            return
        last = portions.pop()
        self.data["history"][self.today]["drunk_ml"] = max(
            0, self.data["history"][self.today]["drunk_ml"] - last["ml"]
        )
        self.data["total_ml"] = max(0, self.data.get("total_ml", 0) - last["ml"])
        self.save_data()
        self.update_display()

    def _show_goal_reached_popup(self):
        popup = ctk.CTkToplevel(self.window)
        popup.title("🎯 Цель достигнута!")
        popup.geometry("340x180")
        popup.grab_set()
        popup.resizable(False, False)
        ctk.CTkLabel(popup, text="🎉 ПОЗДРАВЛЯЮ!",
                    font=ctk.CTkFont(size=16, weight="bold"), text_color="#ffdd00").pack(pady=(18, 4))
        ctk.CTkLabel(popup, text="Дневная норма выполнена!",
                    font=ctk.CTkFont(size=14), text_color="#55ee99").pack(pady=4)
        ctk.CTkLabel(popup, text="Ваш организм скажет вам спасибо!\nПродолжайте в том же духе.",
                    font=ctk.CTkFont(size=12), wraplength=300, text_color="white").pack(pady=6)
        ctk.CTkButton(popup, text="Спасибо! 💙", width=140, command=popup.destroy).pack(pady=10)

    # ── Советы ──────────────────────────────────────────────────────────
    def show_tip(self):
        popup = ctk.CTkToplevel(self.window)
        popup.title("💡 Совет")
        popup.geometry("380x230")
        popup.grab_set()
        popup.resizable(False, False)
        ctk.CTkLabel(popup, text="💡 СОВЕТ ДНЯ",
                    font=ctk.CTkFont(size=15, weight="bold"), text_color="#88ccff").pack(pady=(18, 8))
        ctk.CTkLabel(popup, text=random.choice(HYDRATION_TIPS),
                    font=ctk.CTkFont(size=13), wraplength=340, text_color="white").pack(pady=4)
        ctk.CTkLabel(popup, text="",font=ctk.CTkFont(size=4)).pack()
        ctk.CTkLabel(popup, text="💧 " + random.choice(WATER_FACTS),
                    font=ctk.CTkFont(size=11), wraplength=340, text_color="#556677").pack(pady=4)
        ctk.CTkButton(popup, text="Понял! 💙", width=140, command=popup.destroy).pack(pady=12)

    # ── Статистика ──────────────────────────────────────────────────────
    def show_stats(self):
        dialog = ctk.CTkToplevel(self.window)
        dialog.title("📊 Статистика")
        dialog.geometry("380x440")
        dialog.grab_set()
        dialog.resizable(False, False)
        ctk.CTkLabel(dialog, text="📊 Ваша статистика",
                    font=ctk.CTkFont(size=18, weight="bold")).pack(pady=15)
        total_ml = self.data.get("total_ml", 0)
        streak = self.data.get("streak", 0)
        best_streak = self.data.get("best_streak", 0)
        best_day = self.data.get("best_day_ml", 0)
        best_date = self.data.get("best_day_date", "")
        total_days = len(self.data["history"])
        days_met = sum(1 for d in self.data["history"].values()
                      if d["drunk_ml"] >= self.data["daily_goal_ml"])
        stats = [
            f"💧 Всего выпито: {total_ml/1000:.1f} литров",
            f"📅 Дней с записями: {total_days}",
            f"🎯 Дней с выполненной нормой: {days_met}",
            f"🔥 Текущая серия: {streak} дн.",
            f"👑 Лучшая серия: {best_streak} дн.",
            f"🏆 Рекордный день: {best_day} мл",
        ]
        if best_date:
            try:
                dt = datetime.strptime(best_date, "%Y-%m-%d")
                stats.append(f"   ({dt.strftime('%d.%m.%Y')})")
            except:
                pass
        stats.append(f"📊 Цель: {self.data['daily_goal_ml']} мл/день")
        if total_days:
            stats.append(f"📈 Среднее за всё время: {int(total_ml/total_days)} мл/день")
        for s in stats:
            ctk.CTkLabel(dialog, text=s, font=ctk.CTkFont(size=13),
                        wraplength=340).pack(pady=3, anchor="w", padx=30)
        ctk.CTkButton(dialog, text="Закрыть", width=120, command=dialog.destroy).pack(pady=15)

    # ── Настройки ───────────────────────────────────────────────────────
    def open_settings(self):
        dialog = ctk.CTkToplevel(self.window)
        dialog.title("⚙️ Настройки")
        dialog.geometry("350x260")
        dialog.grab_set()
        dialog.resizable(False, False)
        ctk.CTkLabel(dialog, text="Дневная норма воды",
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=15)
        ctk.CTkLabel(dialog, text="Цель (мл):").pack()
        goal_entry = ctk.CTkEntry(dialog, width=250)
        goal_entry.insert(0, str(self.data["daily_goal_ml"]))
        goal_entry.pack(pady=5)
        ctk.CTkLabel(dialog, text="💡 Рекомендация: 30 мл × ваш вес (кг)",
                    font=ctk.CTkFont(size=11), text_color="gray").pack(pady=3)

        def save():
            try:
                v = int(goal_entry.get())
                if v > 0:
                    self.data["daily_goal_ml"] = v
                    self.save_data()
                    self.update_display()
                    dialog.destroy()
            except ValueError:
                pass

        ctk.CTkButton(dialog, text="Сохранить", command=save).pack(pady=15)

        # Кнопка сброса сегодняшнего дня
        def reset_today():
            self.data["history"][self.today] = {"drunk_ml": 0, "portions": []}
            self.save_data()
            self.update_display()
            dialog.destroy()

        ctk.CTkButton(
            dialog, text="🗑 Сбросить сегодня",
            fg_color="#3a1a1a", hover_color="#5a2a2a",
            command=reset_today
        ).pack()

    def on_close(self):
        self.save_data()
        self.window.destroy()


if __name__ == "__main__":
    WaterTrackerApp()
