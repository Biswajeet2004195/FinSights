import tkinter as tk
from config import *
from base_dashboard import BaseDashboard

class NotificationMixin(BaseDashboard):
    def show_notifications(self):
        self._clear(); self._set_nav("Notifications"); self._set_title("Notifications")
        pg = self._scrollable(self._cf)
        self._sec(pg, "🔔 Notifications", "Financial alerts and updates")

        notifs = _ld("notifications")
        unread = sum(1 for n in notifs if not n.get("read"))

        tb = ctk.CTkFrame(pg, fg_color=BG, corner_radius=10); tb.pack(fill="x", padx=20, pady=(0, 12))

        def _mark_all():
            ns = _ld("notifications")
            for n in ns: n["read"] = True
            _sv("notifications", ns); self._update_bell(); self.show_notifications()

        def _add():
            self._dialog("Add Notification", [
                {"k": "type",  "lbl": "Type",    "type": "combo", "opts": ["info", "success", "warning", "error"]},
                {"k": "title", "lbl": "Title",   "type": "entry"},
                {"k": "msg",   "lbl": "Message", "type": "entry"},
            ], self._save_notif_cb)

        self._tb_btn(tb, f"✓  Mark All Read ({unread} unread)", _mark_all, CB2)
        self._tb_btn(tb, "＋  Add", _add, AC)

        if not notifs:
            tk.Label(pg, text="🎉 No notifications — you're all caught up!",
                     font=("Segoe UI", 13), bg=BG, fg=TS).pack(pady=60)
            return

        NTYPE = {
            "warning": (GO, "#2c2a1c", "⚠️"),
            "success": (GR, "#1c2c1c", "✅"),
            "error":   (RE, "#2c1c1c", "🚨"),
            "info":    (CY, "#1c282c", "ℹ️"),
        }
        for n in sorted(notifs, key=lambda x: x.get("read", False)):
            nt = n.get("type", "info")
            bdr_clr, bg_clr, icon = NTYPE.get(nt, (CY, "#001a2e", "ℹ️"))
            nf = ctk.CTkFrame(pg, fg_color=bdr_clr, corner_radius=10); nf.pack(fill="x", padx=20, pady=4)
            nfi = ctk.CTkFrame(nf, fg_color=bg_clr, corner_radius=10); nfi.pack(padx=1, pady=1, fill="x")
            rw = ctk.CTkFrame(nfi, fg_color=bg_clr, corner_radius=10); rw.pack(fill="x", padx=14, pady=10)
            # Unread dot
            dot_clr = bdr_clr if not n.get("read") else bg_clr
            ctk.CTkFrame(rw, fg_color=dot_clr, width=8, height=8, corner_radius=10).pack(side="left", padx=(0, 8), pady=6)
            tk.Label(rw, text=icon, font=("Segoe UI Emoji", 14), bg=bg_clr).pack(side="left", padx=(0, 10))
            ri = ctk.CTkFrame(rw, fg_color=bg_clr, corner_radius=10); ri.pack(side="left", fill="both", expand=True)
            fw = "bold" if not n.get("read") else "normal"
            tk.Label(ri, text=n["title"], font=("Segoe UI", 11, fw), bg=bg_clr, fg=TP).pack(anchor="w")
            tk.Label(ri, text=n["msg"],   font=("Segoe UI Light", 9),  bg=bg_clr, fg=TS).pack(anchor="w", pady=(2, 0))
            tk.Label(ri, text=n.get("ts", ""), font=("Segoe UI Light", 8), bg=bg_clr, fg=TH).pack(anchor="w")
            # Actions
            acts = ctk.CTkFrame(rw, fg_color=bg_clr, corner_radius=10); acts.pack(side="right")
            if not n.get("read"):
                def _read(nid=n["id"]):
                    ns = _ld("notifications")
                    for x in ns:
                        if x["id"] == nid: x["read"] = True
                    _sv("notifications", ns); self._update_bell(); self.show_notifications()
                rb = tk.Label(acts, text="Mark Read", font=("Segoe UI", 8),
                              bg=bg_clr, fg=CY, cursor="hand2")
                rb.pack(); rb.bind("<Button-1>", lambda e, fn=_read: fn())
            def _del_n(nid=n["id"]):
                ns = [x for x in _ld("notifications") if x["id"] != nid]
                _sv("notifications", ns); self._update_bell(); self.show_notifications()
            db = tk.Label(acts, text="Delete", font=("Segoe UI", 8),
                          bg=bg_clr, fg=RE, cursor="hand2")
            db.pack(pady=(2, 0)); db.bind("<Button-1>", lambda e, fn=_del_n: fn())
        ctk.CTkFrame(pg, fg_color=BG, height=20, corner_radius=10).pack()
