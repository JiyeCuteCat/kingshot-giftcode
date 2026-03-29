"""
kingshot_app.py - 킹샷 기프트코드 자동 등록 GUI
CustomTkinter 모던 UI + 한/영 전환
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import csv, hashlib, threading, time, requests

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

DELAY = 2.0

LOGIN_URL  = "https://kingshot-giftcode.centurygame.com/api/player"
REDEEM_URL = "https://kingshot-giftcode.centurygame.com/api/gift_code"
SECRET     = "mN4!pQs6JrYwV9"

HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Origin": "https://ks-giftcode.centurygame.com",
    "Referer": "https://ks-giftcode.centurygame.com/",
}

# ── 색상 ──
ACCENT  = "#6C63FF"
ACCENT_H = "#5A52E0"
GREEN   = "#2ECC71"
GREEN_H = "#27AE60"
RED     = "#E74C3C"
RED_H   = "#C0392B"
YELLOW  = "#F39C12"
SUBTLE  = "#8B8FAE"

# ── 다국어 텍스트 ──
TEXTS = {
    "ko": {
        "title":          "킹샷 기프트코드",
        "header":         "⚔️  킹샷 기프트코드 자동 등록기",
        "gift_code":      "🎁 기프트 코드",
        "members":        "👥 길드원",
        "csv_btn":        "📂 CSV",
        "clear_btn":      "🗑 초기화",
        "progress":       "📋 진행 상황",
        "waiting":        "대기 중",
        "running":        "진행 중...",
        "done_label":     "완료!",
        "start":          "▶  시작",
        "stop":           "⏹  중단",
        "warn_title":     "경고",
        "err_title":      "오류",
        "warn_no_code":   "기프트 코드를 입력해줘!",
        "warn_no_csv":    "길드원을 먼저 추가해줘!",
        "warn_empty_csv": "CSV에 데이터가 없어!\nplayer_id, nickname 컬럼 확인해줘.",
        "csv_fail":       "CSV 읽기 실패:\n{}",
        "csv_dialog":     "길드원 CSV 선택",
        "loaded":         "✅ {}명 불러왔어!",
        "cleared":        "🗑 초기화됨",
        "log_start":      "\n🚀 시작! 코드 {}개 × {}명",
        "log_stop":       "⏹️  중단 요청...",
        "log_code":       "🎁 코드: [{}]  |  {}명",
        "log_success":    "  ✅ 성공 — {}",
        "log_skip":       "  ⏭️  이미수령 — {}",
        "log_fail":       "  ❌ 실패 — {} ({})",
        "log_summary":    "  [{}] ✅{} / ⏭️{} / ❌{}",
        "log_done":       "\n🏁 완료! ✅{} / ⏭️{} / ❌{}",
        "stat_done":      "✅ {}명   ⏭️ {}명   ❌ {}명",
        "login_fail":     "로그인 실패: {}",
        "code_expired":   "코드 만료/소진: {}",
        "api_error":      "오류 {}: {}",
        "code_not_found": "코드를 찾을 수 없음 (오타 확인)",
        "timeout":        "타임아웃",
        "already":        "이미 수령",
        "success":        "성공",
        "lang_btn":       "English",
        "add_btn":        "➕ 추가",
        "id_placeholder": "플레이어 ID",
        "name_placeholder":"닉네임 (선택)",
        "warn_no_id":     "플레이어 ID를 입력해줘!",
        "warn_dup_id":    "이미 추가된 ID야!",
        "added":          "✅ {} 추가됨!",
    },
    "en": {
        "title":          "KingShot Gift Code",
        "header":         "⚔️  KingShot Gift Code Redeemer",
        "gift_code":      "🎁 Gift Code",
        "members":        "👥 Members",
        "csv_btn":        "📂 CSV",
        "clear_btn":      "🗑 Clear",
        "progress":       "📋 Progress",
        "waiting":        "Waiting",
        "running":        "Running...",
        "done_label":     "Done!",
        "start":          "▶  Start",
        "stop":           "⏹  Stop",
        "warn_title":     "Warning",
        "err_title":      "Error",
        "warn_no_code":   "Please enter gift codes!",
        "warn_no_csv":    "Please add members first!",
        "warn_empty_csv": "No data in CSV!\nCheck player_id, nickname columns.",
        "csv_fail":       "CSV read failed:\n{}",
        "csv_dialog":     "Select Member CSV",
        "loaded":         "✅ {} members loaded!",
        "cleared":        "🗑 Cleared",
        "log_start":      "\n🚀 Start! {} codes × {} members",
        "log_stop":       "⏹️  Stop requested...",
        "log_code":       "🎁 Code: [{}]  |  {} members",
        "log_success":    "  ✅ Success — {}",
        "log_skip":       "  ⏭️  Already claimed — {}",
        "log_fail":       "  ❌ Failed — {} ({})",
        "log_summary":    "  [{}] ✅{} / ⏭️{} / ❌{}",
        "log_done":       "\n🏁 Done! ✅{} / ⏭️{} / ❌{}",
        "stat_done":      "✅ {}   ⏭️ {}   ❌ {}",
        "login_fail":     "Login failed: {}",
        "code_expired":   "Code expired/used: {}",
        "api_error":      "Error {}: {}",
        "code_not_found": "Code not found (check typo)",
        "timeout":        "Timeout",
        "already":        "Already claimed",
        "success":        "Success",
        "lang_btn":       "Korean",
        "add_btn":        "➕ Add",
        "id_placeholder": "Player ID",
        "name_placeholder":"Name (optional)",
        "warn_no_id":     "Please enter a Player ID!",
        "warn_dup_id":    "This ID is already added!",
        "added":          "✅ {} added!",
    },
}


# ══════════════════════════════════════════════════════════
# API 로직
# ══════════════════════════════════════════════════════════

def make_sign(params: dict) -> str:
    sorted_str = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
    return hashlib.md5((sorted_str + SECRET).encode()).hexdigest()

def make_payload(base: dict) -> dict:
    ts = str(int(time.time() * 1000))
    params = {**base, "time": ts}
    return {**params, "sign": make_sign(params)}

def redeem_one(session, pid, code, t):
    try:
        payload = make_payload({"fid": str(pid)})
        r = session.post(LOGIN_URL, json=payload, headers=HEADERS, timeout=10)
        data = r.json()

        if data.get("code") != 0:
            return "FAIL", t["login_fail"].format(data.get("msg", ""))

        payload2 = make_payload({"fid": str(pid), "cdk": code, "captcha_code": ""})
        r2 = session.post(REDEEM_URL, json=payload2, headers=HEADERS, timeout=10)
        data2 = r2.json()

        code2 = data2.get("code", -1)
        msg2  = data2.get("msg", "")

        if code2 == 0:
            return "SUCCESS", t["success"]
        elif "RECEIVED" in msg2.upper():
            return "SKIP", t["already"]
        elif msg2 in ("TIME ERROR", "USED"):
            return "FAIL", t["code_expired"].format(msg2)
        elif "CDK NOT FOUND" in msg2.upper():
            return "FAIL", t["code_not_found"]
        else:
            return "FAIL", t["api_error"].format(code2, msg2)

    except requests.exceptions.Timeout:
        return "FAIL", t["timeout"]
    except Exception as e:
        return "FAIL", str(e)


def run_redemption(codes, players, log_cb, progress_cb, done_cb, stop_flag, t):
    total_ok = total_skip = total_fail = 0
    total_tasks = len(codes) * len(players)
    done_tasks = 0
    session = requests.Session()

    for code in codes:
        if stop_flag():
            break

        log_cb(f"\n{'─'*34}", "info")
        log_cb(t["log_code"].format(code, len(players)), "info")
        log_cb(f"{'─'*34}", "info")

        ok = skip = fail = 0

        for pid, name in players:
            if stop_flag():
                break

            log_cb(f"  👤 {name} ({pid})", "info")
            status, msg = redeem_one(session, pid, code, t)

            if status == "SUCCESS":
                log_cb(t["log_success"].format(name), "success")
                ok += 1
                total_ok += 1
            elif status == "SKIP":
                log_cb(t["log_skip"].format(name), "skip")
                skip += 1
                total_skip += 1
            else:
                log_cb(t["log_fail"].format(name, msg), "fail")
                fail += 1
                total_fail += 1

            done_tasks += 1
            progress_cb(done_tasks, total_tasks)
            time.sleep(DELAY)

        log_cb(t["log_summary"].format(code, ok, skip, fail), "info")

    done_cb(total_ok, total_skip, total_fail)


# ══════════════════════════════════════════════════════════
# GUI
# ══════════════════════════════════════════════════════════

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.lang = "ko"
        self.geometry("640x750")
        self.minsize(560, 650)
        self.players = []
        self._stop = False
        self._ui = {}
        self._build()
        self._apply_lang()

    def t(self, key):
        return TEXTS[self.lang][key]

    def _build(self):
        # ── 헤더 ──
        header = ctk.CTkFrame(self, fg_color=ACCENT, corner_radius=0, height=50)
        header.pack(fill="x")
        header.pack_propagate(False)
        self._ui["header"] = ctk.CTkLabel(
            header, font=ctk.CTkFont(size=16, weight="bold"),
            text_color="white", text="",
        )
        self._ui["header"].pack(side="left", padx=16)

        ctk.CTkLabel(
            header, text="v1.0",
            font=ctk.CTkFont(size=11), text_color="#B8BBFF",
        ).pack(side="right", padx=(0, 16))

        self._ui["lang_btn"] = ctk.CTkButton(
            header, text="", command=self._toggle_lang,
            width=72, height=26, corner_radius=13,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=ACCENT_H, hover_color="#4840C8",
            text_color="white",
        )
        self._ui["lang_btn"].pack(side="right", padx=(0, 10))

        self._ui["theme_btn"] = ctk.CTkButton(
            header, text="☀️", command=self._toggle_theme,
            width=30, height=26, corner_radius=13,
            font=ctk.CTkFont(size=13),
            fg_color=ACCENT_H, hover_color="#4840C8",
            text_color="white",
        )
        self._ui["theme_btn"].pack(side="right", padx=(0, 6))

        # ── 메인 컨텐츠 ──
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=14, pady=(10, 0))

        # 상단: 코드 + 길드원
        top = ctk.CTkFrame(main, fg_color="transparent")
        top.pack(fill="x")

        # 왼쪽: 기프트 코드
        left = ctk.CTkFrame(top)
        left.pack(side="left", fill="both", expand=True, padx=(0, 5))
        self._ui["gift_code"] = ctk.CTkLabel(
            left, font=ctk.CTkFont(size=12, weight="bold"), text="",
        )
        self._ui["gift_code"].pack(anchor="w", padx=10, pady=(8, 4))
        self.code_text = ctk.CTkTextbox(
            left, height=80, font=ctk.CTkFont(family="Menlo", size=12),
        )
        self.code_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # 오른쪽: 길드원
        right = ctk.CTkFrame(top)
        right.pack(side="left", fill="both", expand=True, padx=(5, 0))

        right_top = ctk.CTkFrame(right, fg_color="transparent")
        right_top.pack(fill="x", padx=10, pady=(8, 4))
        self._ui["members"] = ctk.CTkLabel(
            right_top, font=ctk.CTkFont(size=12, weight="bold"),
            text_color=ACCENT, text="",
        )
        self._ui["members"].pack(side="left")

        self._ui["clear_btn"] = ctk.CTkButton(
            right_top, command=self._clear_players,
            width=60, height=26, font=ctk.CTkFont(size=11),
            fg_color="#4A4E6A", hover_color="#3D4058",
            text_color="#CCC", text="",
        )
        self._ui["clear_btn"].pack(side="right")
        self._ui["csv_btn"] = ctk.CTkButton(
            right_top, command=self._load_csv,
            width=68, height=26, font=ctk.CTkFont(size=11),
            fg_color=ACCENT, hover_color=ACCENT_H,
            text_color="white", text="",
        )
        self._ui["csv_btn"].pack(side="right", padx=(0, 6))

        # 수동 추가 입력 행
        add_row = ctk.CTkFrame(right, fg_color="transparent")
        add_row.pack(fill="x", padx=10, pady=(2, 4))

        self._ui["id_entry"] = ctk.CTkEntry(
            add_row, height=28, font=ctk.CTkFont(size=11),
            placeholder_text="", width=100,
        )
        self._ui["id_entry"].pack(side="left", fill="x", expand=True)

        self._ui["name_entry"] = ctk.CTkEntry(
            add_row, height=28, font=ctk.CTkFont(size=11),
            placeholder_text="", width=80,
        )
        self._ui["name_entry"].pack(side="left", fill="x", expand=True, padx=(4, 0))

        self._ui["add_btn"] = ctk.CTkButton(
            add_row, command=self._add_player,
            width=64, height=28, font=ctk.CTkFont(size=11),
            fg_color=GREEN, hover_color=GREEN_H,
            text_color="white", text="",
        )
        self._ui["add_btn"].pack(side="left", padx=(4, 0))

        self._ui["id_entry"].bind("<Return>", lambda e: self._add_player())
        self._ui["name_entry"].bind("<Return>", lambda e: self._add_player())

        # 플레이어 목록 (스크롤 가능, 개별 삭제)
        self.plist_frame = ctk.CTkScrollableFrame(
            right, height=50, label_text="",
        )
        self.plist_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # ── 진행 로그 ──
        log_frame = ctk.CTkFrame(main)
        log_frame.pack(fill="both", expand=True, pady=(8, 0))

        log_header = ctk.CTkFrame(log_frame, fg_color="transparent")
        log_header.pack(fill="x", padx=10, pady=(8, 4))
        self._ui["progress"] = ctk.CTkLabel(
            log_header, font=ctk.CTkFont(size=12, weight="bold"), text="",
        )
        self._ui["progress"].pack(side="left")
        self.prog_lbl = ctk.CTkLabel(
            log_header, font=ctk.CTkFont(size=11), text="",
        )
        self.prog_lbl.pack(side="right")

        self.prog_bar = ctk.CTkProgressBar(log_frame, height=12)
        self.prog_bar.pack(fill="x", padx=10, pady=(0, 6))
        self.prog_bar.set(0)

        self.log = ctk.CTkTextbox(
            log_frame, font=ctk.CTkFont(family="Menlo", size=11),
            state="disabled",
        )
        self.log.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.log._textbox.tag_config("success", foreground="#2ECC71")
        self.log._textbox.tag_config("fail",    foreground="#E74C3C")
        self.log._textbox.tag_config("skip",    foreground="#F1C40F")
        self.log._textbox.tag_config("info",    foreground="#8B8FAE")

        # ── 하단 ──
        bot = ctk.CTkFrame(self, fg_color="transparent")
        bot.pack(fill="x", padx=14, pady=(8, 6))

        self.run_btn = ctk.CTkButton(
            bot, command=self._start,
            fg_color=GREEN, hover_color=GREEN_H,
            text_color="white",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40, width=130, text="",
        )
        self.run_btn.pack(side="left")

        self.stop_btn = ctk.CTkButton(
            bot, command=self._stop_run,
            fg_color=RED, hover_color=RED_H,
            text_color="white",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40, width=130, state="disabled", text="",
        )
        self.stop_btn.pack(side="left", padx=(10, 0))

        self.stat_lbl = ctk.CTkLabel(
            bot, text="", font=ctk.CTkFont(size=13, weight="bold"),
        )
        self.stat_lbl.pack(side="right")

        # ── 푸터 (크레딧) ──
        ctk.CTkLabel(
            self, text="1308 - [EnD]Jiye",
            font=ctk.CTkFont(size=10), text_color=SUBTLE,
        ).pack(pady=(0, 8))

    # ── 언어 / 테마 전환 ─────────────────────────────────

    def _toggle_lang(self):
        self.lang = "en" if self.lang == "ko" else "ko"
        self._apply_lang()

    def _toggle_theme(self):
        current = ctk.get_appearance_mode()
        if current == "Dark":
            ctk.set_appearance_mode("light")
            self._ui["theme_btn"].configure(text="🌙")
        else:
            ctk.set_appearance_mode("dark")
            self._ui["theme_btn"].configure(text="☀️")

    def _apply_lang(self):
        self.title(self.t("title"))
        self._ui["header"].configure(text=self.t("header"))
        self._ui["lang_btn"].configure(text=self.t("lang_btn"))
        self._ui["gift_code"].configure(text=self.t("gift_code"))
        self._update_member_label()
        self._ui["csv_btn"].configure(text=self.t("csv_btn"))
        self._ui["clear_btn"].configure(text=self.t("clear_btn"))
        self._ui["add_btn"].configure(text=self.t("add_btn"))
        self._ui["id_entry"].configure(placeholder_text=self.t("id_placeholder"))
        self._ui["name_entry"].configure(placeholder_text=self.t("name_placeholder"))
        self._ui["progress"].configure(text=self.t("progress"))
        self.prog_lbl.configure(text=self.t("waiting"))
        self.run_btn.configure(text=self.t("start"))
        self.stop_btn.configure(text=self.t("stop"))

    def _update_member_label(self):
        n = len(self.players)
        self._ui["members"].configure(text=f"{self.t('members')}({n})")

    # ── 이벤트 핸들러 ────────────────────────────────────

    def _add_player(self):
        pid = self._ui["id_entry"].get().strip()
        name = self._ui["name_entry"].get().strip()
        if not pid:
            messagebox.showwarning(self.t("warn_title"), self.t("warn_no_id"))
            return
        if any(p[0] == pid for p in self.players):
            messagebox.showwarning(self.t("warn_title"), self.t("warn_dup_id"))
            return
        name = name or pid
        self.players.append((pid, name))
        self._ui["id_entry"].delete(0, "end")
        self._ui["name_entry"].delete(0, "end")
        self._refresh_plist()
        self._log(self.t("added").format(name), "success")

    def _remove_player(self, idx):
        if 0 <= idx < len(self.players):
            self.players.pop(idx)
            self._refresh_plist()

    def _refresh_plist(self):
        for w in self.plist_frame.winfo_children():
            w.destroy()
        for i, (pid, name) in enumerate(self.players):
            row = ctk.CTkFrame(self.plist_frame, fg_color="transparent", height=26)
            row.pack(fill="x", pady=1)
            ctk.CTkLabel(
                row, text=f"{name}  ({pid})",
                font=ctk.CTkFont(size=11), anchor="w",
            ).pack(side="left", fill="x", expand=True)
            ctk.CTkButton(
                row, text="✕", width=24, height=22,
                font=ctk.CTkFont(size=11),
                fg_color="#4A4E6A", hover_color=RED_H,
                text_color="#CCC",
                command=lambda idx=i: self._remove_player(idx),
            ).pack(side="right")
        self._update_member_label()

    def _load_csv(self):
        path = filedialog.askopenfilename(
            title=self.t("csv_dialog"),
            filetypes=[("CSV", "*.csv"), ("All", "*.*")])
        if not path:
            return
        try:
            with open(path, newline="", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f, skipinitialspace=True)
                reader.fieldnames = [h.strip() for h in reader.fieldnames]
                rows = [{k.strip(): (v or "").strip() for k, v in r.items()} for r in reader]
            loaded = [
                (r.get("player_id", ""),
                 r.get("nickname") or r.get("name") or "")
                for r in rows
                if r.get("player_id", "")
                and r.get("player_id", "").lower() != "player_id"
            ]
            loaded = [(pid, name or pid) for pid, name in loaded]
            if not loaded:
                messagebox.showwarning(
                    self.t("warn_title"), self.t("warn_empty_csv"))
                return
            self.players = loaded
            self._refresh_plist()
            self._log(self.t("loaded").format(len(loaded)), "success")
        except Exception as e:
            messagebox.showerror(
                self.t("err_title"), self.t("csv_fail").format(e))

    def _clear_players(self):
        self.players = []
        self._refresh_plist()
        self._log(self.t("cleared"), "info")

    def _start(self):
        codes = [c.strip() for c in self.code_text.get("1.0", "end").splitlines() if c.strip()]

        if not codes:
            messagebox.showwarning(self.t("warn_title"), self.t("warn_no_code"))
            return
        if not self.players:
            messagebox.showwarning(self.t("warn_title"), self.t("warn_no_csv"))
            return

        self._stop = False
        self.run_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.prog_bar.set(0)
        self.prog_lbl.configure(text=self.t("running"))
        self.stat_lbl.configure(text="")

        # 로그 초기화
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")

        self._log(self.t("log_start").format(len(codes), len(self.players)), "info")

        cur_t = TEXTS[self.lang].copy()
        threading.Thread(
            target=run_redemption,
            args=(codes, self.players, self._log,
                  self._upd_prog, self._done, lambda: self._stop, cur_t),
            daemon=True,
        ).start()

    def _stop_run(self):
        self._stop = True
        self.stop_btn.configure(state="disabled")
        self._log(self.t("log_stop"), "info")

    def _log(self, msg, tag="info"):
        def _do():
            self.log.configure(state="normal")
            self.log._textbox.insert("end", msg + "\n", tag)
            self.log.see("end")
            self.log.configure(state="disabled")
        self.after(0, _do)

    def _upd_prog(self, done, total):
        def _do():
            self.prog_bar.set(done / total if total else 0)
            self.prog_lbl.configure(text=f"{done} / {total}")
        self.after(0, _do)

    def _done(self, ok, skip, fail):
        def _do():
            self.run_btn.configure(state="normal")
            self.stop_btn.configure(state="disabled")
            self.prog_lbl.configure(text=self.t("done_label"))
            self.stat_lbl.configure(
                text=self.t("stat_done").format(ok, skip, fail),
                text_color=GREEN,
            )
            self._log(self.t("log_done").format(ok, skip, fail), "success")
        self.after(0, _do)


if __name__ == "__main__":
    App().mainloop()
