"""
Passe La Fete — Business Command Center v3
Keyboard-first. Tab to move. Enter to save. Space to select. Escape to go back.
Designed for speed — you barely need the mouse.
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json, os, re, webbrowser, tempfile
from datetime import datetime

DATA = os.path.join(os.path.expanduser("~"), "PasseLaFete")
os.makedirs(DATA, exist_ok=True)

# ═══ COLORS (high contrast, easy to read) ═══
C = {
    "bg":        "#F0F0F0",
    "card":      "#FFFFFF",
    "text":      "#1A1A1A",
    "subtle":    "#555555",
    "green":     "#2E7D32",
    "green_lt":  "#E8F5E9",
    "gold":      "#E65100",
    "gold_lt":   "#FFF3E0",
    "red":       "#C62828",
    "red_lt":    "#FFEBEE",
    "blue":      "#1565C0",
    "blue_lt":   "#E3F2FD",
    "border":    "#BDBDBD",
    "focus":     "#1565C0",
}

FONT = {"title": 20, "heading": 15, "body": 13, "small": 11, "mono": 12}

# ═══ DATA ═══
def load(n):
    p = os.path.join(DATA, n)
    return json.load(open(p)) if os.path.exists(p) else []

def save(n, d):
    with open(os.path.join(DATA, n), "w") as f: json.dump(d, f, indent=2)

GUIDELINES = {
    "Charcuterie / Grazing Table": {
        "note": "Per guest. Add 25% for events over 2 hours.",
        "items": [
            ("Cured Meats", 2.5), ("Artisan Cheeses (3+ varieties)", 3),
            ("Fresh Fruit", 3), ("Crackers & Breadsticks", 2),
            ("Nuts", 1), ("Olives & Pickles", 1.5),
            ("Honey, Jam, Chutney", 0.5), ("Fresh Herbs (garnish)", 0.1),
        ],
    },
    "Sit-Down Dinner (3 courses)": {
        "note": "Per guest. Multiply protein by 1.2x for bone-in cuts.",
        "items": [
            ("Appetizer / Starter", 4), ("Protein", 7),
            ("Vegetable Side", 5), ("Starch Side", 5),
            ("Sauce or Gravy", 2), ("Bread & Butter", 2), ("Dessert", 4),
        ],
    },
    "Weekly Meal Prep": {
        "note": "Per meal, per person.",
        "items": [
            ("Protein per meal", 6), ("Vegetable per meal", 4),
            ("Carb / Starch per meal", 5), ("Breakfast Item", 4),
            ("Sauce / Dressing", 1.5),
        ],
        "extra": "Meals per Person",
    },
    "Appetizer & Dessert Party": {
        "note": "Cocktail-style. Add 30% if no dinner served.",
        "items": [
            ("Hot Appetizers (3 varieties)", 3), ("Cold Appetizers (3 varieties)", 3),
            ("Dips & Spreads", 2), ("Crackers, Crostini, Bread", 1.5),
            ("Crudites Platter", 3), ("Mini Pastries & Tarts", 2),
            ("Cakes or Pies", 3), ("Fresh Fruit (dessert)", 2),
        ],
    },
}

DEFAULT_SUPPLIERS = [
    {"name":"Tampa Wholesale Produce","type":"Produce","phone":"(813) 555-0101",
     "address":"2201 E 7th Ave, Tampa, FL 33605","hours":"Mon-Sat 4am-2pm","notes":"Organic & local farms"},
    {"name":"Gulf Coast Seafood Co.","type":"Seafood","phone":"(727) 555-0202",
     "address":"4500 34th St S, St. Petersburg, FL 33711","hours":"Mon-Sat 6am-3pm","notes":"Fresh daily catch"},
    {"name":"Tampa Bay Dairy Collective","type":"Dairy & Cheese","phone":"(813) 555-0303",
     "address":"1401 W Dr MLK Jr Blvd, Plant City, FL 33563","hours":"Tue-Sat 8am-4pm","notes":"Artisan cheeses"},
    {"name":"Beef N' Bun Butcher Shop","type":"Meat","phone":"(813) 555-0404",
     "address":"3215 S MacDill Ave, Tampa, FL 33629","hours":"Mon-Sat 7am-6pm","notes":"Grass-fed, non-GMO"},
    {"name":"Ybor City Farmers Market","type":"Market","phone":"(813) 555-0505",
     "address":"1800 E 9th Ave, Tampa, FL 33605","hours":"Sat 9am-3pm","notes":"Local vendors, seasonal"},
    {"name":"Sweetwater Organic Farm","type":"Produce","phone":"(813) 555-0606",
     "address":"6942 W Comanche Ave, Tampa, FL 33634","hours":"Sun 12pm-4pm","notes":"CSA boxes available"},
    {"name":"Dunedin Fish Market","type":"Seafood","phone":"(727) 555-0707",
     "address":"651 Broadway, Dunedin, FL 34698","hours":"Tue-Sun 9am-6pm","notes":"Gulf-to-table"},
    {"name":"Mazzaro's Italian Market","type":"Specialty","phone":"(727) 555-0808",
     "address":"2909 22nd Ave N, St. Petersburg, FL 33713","hours":"Mon-Sat 9am-5:30pm","notes":"Imported cheeses, oils"},
    {"name":"Cacciatore & Sons","type":"Meat","phone":"(813) 555-0909",
     "address":"4403 N Armenia Ave, Tampa, FL 33603","hours":"Mon-Sat 8am-5pm","notes":"Italian specialty meats"},
    {"name":"Sanwa Farmers Market","type":"Wholesale","phone":"(813) 555-1010",
     "address":"2621 E Hillsborough Ave, Tampa, FL 33610","hours":"Mon-Sat 5am-3pm","notes":"Bulk produce, Asian specialties"},
    {"name":"Bearss Groves","type":"Produce","phone":"(813) 555-1111",
     "address":"14316 Lake Magdalene Blvd, Tampa, FL 33613","hours":"Mon-Sat 9am-5:30pm","notes":"Citrus, local honey"},
    {"name":"Gulf Coast Sourdough","type":"Bakery","phone":"(727) 555-1212",
     "address":"2425 Central Ave, St. Petersburg, FL 33713","hours":"Wed-Sun 7am-2pm","notes":"Artisan bread"},
    {"name":"Alessi Bakery","type":"Bakery","phone":"(813) 555-1313",
     "address":"2909 W Cypress St, Tampa, FL 33609","hours":"Mon-Sat 7am-6pm","notes":"Cuban bread, pastries"},
    {"name":"Locale Market","type":"Specialty","phone":"(727) 555-1414",
     "address":"179 2nd Ave N, St. Petersburg, FL 33701","hours":"Mon-Sat 10am-7pm, Sun 11am-5pm","notes":"Gourmet ingredients"},
    {"name":"Oldsmar Farmers Market","type":"Market","phone":"(813) 555-1515",
     "address":"101 State St W, Oldsmar, FL 34677","hours":"Sat 9am-1:30pm","notes":"Local growers, artisan goods"},
]

def lbs(oz):
    lb = oz / 16
    if lb >= 1:     return f"{lb:.1f} lb ({oz:.0f} oz)"
    elif lb >= 0.1: return f"{lb:.2f} lb ({oz:.1f} oz)"
    return f"{lb:.3f} lb ({oz:.2f} oz)"

# ═══════════════ SHORTCUT BAR ═══════════════
SHORTCUTS = """TAB = Next Field   |   ENTER = Save / Calculate   |   SPACE = Select / Check
ESC = Clear / Go Back   |   Ctrl+1..6 = Switch Tabs   |   DELETE = Remove Selected"""

# ═══════════════ APP ═══════════════
class Suite:
    def __init__(self, root):
        self.root = root
        self.root.title("Passe La Fete — Business Suite  |  Keyboard: Tab · Enter · Space · Esc")
        self.root.geometry("1060x800")
        self.root.configure(bg=C["bg"])
        self.root.minsize(900, 650)
        
        # Undo stack
        self._undo = []
        self._last_status = ""
        
        # Style
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook", background=C["bg"], borderwidth=0)
        style.configure("TNotebook.Tab", font=("Segoe UI", 12), padding=[20, 8],
                       background="#E0E0E0", borderwidth=0)
        style.map("TNotebook.Tab", background=[("selected", C["card"])],
                 foreground=[("selected", C["text"])], expand=[("selected", [1,1,1,0])])
        style.configure("Treeview", font=("Segoe UI", 11), rowheight=32,
                       background=C["card"], fieldbackground=C["card"])
        style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"),
                       background=C["border"], padding=[10, 6])
        
        # Data
        self.customers = load("customers.json")
        self.orders    = load("orders.json")
        self.suppliers = load("suppliers.json") or DEFAULT_SUPPLIERS
        self.shopping  = load("shopping.json")
        
        self.build()
        self._bind_keys()
    
    # ═══ KEYBOARD BINDINGS ═══
    def _bind_keys(self):
        r = self.root
        r.bind("<Control-Key-1>", lambda e: self.nb.select(0))
        r.bind("<Control-Key-2>", lambda e: self.nb.select(1))
        r.bind("<Control-Key-3>", lambda e: self.nb.select(2))
        r.bind("<Control-Key-4>", lambda e: self.nb.select(3))
        r.bind("<Control-Key-5>", lambda e: self.nb.select(4))
        r.bind("<Control-Key-6>", lambda e: self.nb.select(5))
        r.bind("<Escape>", lambda e: self._escape_current())
        r.bind("<Delete>", lambda e: self._delete_current())
        r.bind("<Control-z>", lambda e: self._undo_last())
    
    def _escape_current(self):
        tab = self.nb.index(self.nb.select())
        if tab == 0: self._clear_client()
        elif tab == 3:
            if messagebox.askyesno("Clear", "Clear entire shopping list? (Ctrl+Z to undo)"):
                self._undo = [("shopping", list(self.shopping))]
                self.shopping = []; save("shopping.json", [])
                self._refresh_shopping()
                self._status("Shopping list cleared. Ctrl+Z to undo.")
    
    def _delete_current(self):
        tab = self.nb.index(self.nb.select())
        if tab == 0: self._delete_client()
        elif tab == 1: self._delete_order()
        elif tab == 3: self._remove_shop()
        elif tab == 4: self._delete_supplier()
    
    def _undo_last(self):
        if not self._undo: return
        action, data = self._undo.pop()
        if action == "shopping":
            self.shopping = data; save("shopping.json", self.shopping)
            self._refresh_shopping()
            self._status("UNDO: Shopping list restored.")
        elif action == "client":
            self.customers = data; save("customers.json", self.customers)
            self._refresh_clients(); self._refresh_order_clients()
            self._status("UNDO: Customer restored.")
        elif action == "order":
            self.orders = data; save("orders.json", self.orders)
            self._refresh_orders()
            self._status("UNDO: Order restored.")
    
    # ═══ HELPERS ═══
    def _status(self, msg):
        self._last_status = msg
        self.status_var.set(f"  {msg}")
        self.root.after(5000, lambda: self.status_var.set(f"  {SHORTCUTS}") if self._last_status == msg else None)
    
    def card(self, parent, **kw):
        return tk.Frame(parent, bg=C["card"], highlightbackground=C["border"],
                       highlightthickness=1, padx=20, pady=15, **kw)
    
    def _label(self, parent, text, size="body", bold=False):
        s = {"title": FONT["title"], "heading": FONT["heading"], "body": FONT["body"],
             "small": FONT["small"]}.get(size, FONT["body"])
        return tk.Label(parent, text=text, font=("Segoe UI", s, "bold" if bold else "normal"),
                       bg=parent["bg"], fg=C["text"])
    
    def _btn(self, parent, text, color="green", cmd=None):
        colors = {"green": (C["green"],"#FFFFFF"), "red": (C["red"],"#FFFFFF"),
                  "blue": (C["blue"],"#FFFFFF"), "white": (C["card"],C["text"]),
                  "clear": (C["bg"],C["text"])}
        bg, fg = colors.get(color, (C["green"],"#FFFFFF"))
        b = tk.Button(parent, text=f"  {text}  ", font=("Segoe UI", 12, "bold"),
                     bg=bg, fg=fg, activebackground=bg, activeforeground=fg,
                     relief="flat", cursor="hand2", padx=14, pady=6, bd=0, command=cmd)
        b.bind("<Return>", lambda e: cmd() if cmd else None)
        return b
    
    def _entry(self, parent, width=24, **kw):
        e = tk.Entry(parent, font=("Segoe UI", 13), relief="solid", bd=1,
                    highlightbackground=C["border"], highlightthickness=1,
                    highlightcolor=C["focus"], width=width, **kw)
        e.bind("<Return>", lambda ev: self._save_on_enter())
        return e
    
    def _save_on_enter(self):
        tab = self.nb.index(self.nb.select())
        if tab == 0: self._save_client()
        elif tab == 1: self._build_order()
    
    def _header(self, text, parent):
        tk.Label(parent, text=text, font=("Segoe UI", FONT["title"], "bold"),
                bg=parent["bg"], fg=C["text"]).pack(anchor="w", pady=(0, 12))
    
    # ═══ BUILD ═══
    def build(self):
        # Top bar
        top = tk.Frame(self.root, bg="#1A1A1A", height=50)
        top.pack(fill="x"); top.pack_propagate(False)
        tk.Label(top, text="  Passe La Fete  —  Business Suite",
                font=("Segoe UI", 16, "bold"), bg="#1A1A1A", fg="#FFFFFF").pack(side="left", pady=8)
        
        # Tabs
        self.nb = ttk.Notebook(self.root)
        self.nb.pack(fill="both", expand=True, padx=8, pady=(8, 0))
        
        self.tab_clients()
        self.tab_orders()
        self.tab_recipes()
        self.tab_shopping()
        self.tab_suppliers()
        self.tab_quick()
        
        # Status bar
        bar = tk.Frame(self.root, bg="#E0E0E0", height=30)
        bar.pack(fill="x", side="bottom")
        self.status_var = tk.StringVar(value=f"  {SHORTCUTS}")
        tk.Label(bar, textvariable=self.status_var, font=("Segoe UI", 10),
                bg="#E0E0E0", fg=C["subtle"]).pack(side="left", padx=8)
        tk.Label(bar, text=f"Data: {DATA}  ", font=("Segoe UI", 9),
                bg="#E0E0E0", fg="#999").pack(side="right", padx=8)
    
    # ═══ TAB 1: CLIENTS ═══
    def tab_clients(self):
        t = tk.Frame(self.nb, bg=C["bg"]); self.nb.add(t, text="  1. Customers  ")
        self._header("Customer Directory  —  Tab to move, Enter to save", t)
        
        top = tk.Frame(t, bg=C["bg"]); top.pack(fill="x")
        
        # Search
        sr = tk.Frame(t, bg=C["bg"]); sr.pack(fill="x", pady=(0, 8))
        self._label(sr, "Search:", "body", True).pack(side="left", padx=(0, 6))
        self.cs = self._entry(sr, width=30)
        self.cs.pack(side="left"); self.cs.bind("<KeyRelease>", lambda e: self._refresh_clients())
        self._btn(sr, "Clear", "clear").pack(side="left", padx=6)
        
        # Split: list + form
        panes = tk.Frame(t, bg=C["bg"]); panes.pack(fill="both", expand=True)
        
        # List
        lc = self.card(panes); lc.pack(side="left", fill="both", expand=True, padx=(0, 6))
        cols = ("Name", "Phone", "Dietary Needs", "Budget", "Location")
        self.ctree = ttk.Treeview(lc, columns=cols, show="headings", height=10)
        for c in cols: self.ctree.heading(c, text=c); self.ctree.column(c, width=140, minwidth=80)
        self.ctree.pack(fill="both", expand=True)
        self.ctree.bind("<<TreeviewSelect>>", self._on_client_select)
        self.ctree.bind("<space>", lambda e: self._on_client_select(None))
        
        # Form
        fc = self.card(panes); fc.pack(side="right", fill="y", padx=(6, 0))
        self._label(fc, "Customer Details  (Enter to Save)", "heading", True).pack(anchor="w", pady=(0, 10))
        
        fields = [
            ("* Name", "c_name"), ("Phone", "c_phone"), ("Email", "c_email"),
            ("Dietary Needs", "c_diet"), ("Allergies", "c_allergies"),
            ("Budget Range", "c_budget"), ("Location / Address", "c_location"),
            ("Travel Time (min)", "c_travel"), ("Notes", "c_notes"),
        ]
        self.cf = {}
        for label, key in fields:
            r = tk.Frame(fc, bg=C["card"]); r.pack(fill="x", pady=2)
            tk.Label(r, text=label, font=("Segoe UI", 11), bg=C["card"],
                    fg=C["subtle"], width=18, anchor="e").pack(side="left", padx=(0, 6))
            e = self._entry(r, width=22); e.pack(side="left")
            if key == "c_name": e.focus_set()
            self.cf[key] = e
        
        br = tk.Frame(fc, bg=C["card"]); br.pack(fill="x", pady=(10, 0))
        self._btn(br, "Save Customer  (Enter)", "green", self._save_client).pack(side="left", padx=(0, 6))
        self._btn(br, "New  (Esc)", "clear", self._clear_client).pack(side="left", padx=(0, 6))
        self._btn(br, "Delete  (Del)", "red", self._delete_client).pack(side="left")
        
        self._refresh_clients()
        self.cf["c_name"].focus_set()
    
    def _refresh_clients(self):
        for i in self.ctree.get_children(): self.ctree.delete(i)
        q = self.cs.get().lower()
        for c in self.customers:
            if q and q not in json.dumps(c).lower(): continue
            self.ctree.insert("", "end", values=(
                c.get("c_name",""), c.get("c_phone",""), c.get("c_diet",""),
                c.get("c_budget",""), c.get("c_location","")))
    
    def _on_client_select(self, e):
        sel = self.ctree.selection()
        if not sel: return
        i = self.ctree.index(sel[0])
        # Find matching customer by name
        vals = self.ctree.item(sel[0])["values"]
        for c in self.customers:
            if c.get("c_name") == vals[0]:
                for k, entry in self.cf.items():
                    entry.delete(0, "end"); entry.insert(0, c.get(k, ""))
                self.cf["c_name"].focus_set()
                return
    
    def _clear_client(self):
        for e in self.cf.values(): e.delete(0, "end")
        self.cf["c_name"].focus_set()
        self._status("Form cleared. Ready for new customer.")
    
    def _save_client(self):
        d = {k: v.get() for k, v in self.cf.items()}
        if not d.get("c_name"):
            self._status("Name is required!")
            self.cf["c_name"].focus_set()
            return
        sel = self.ctree.selection()
        if sel:
            vals = self.ctree.item(sel[0])["values"]
            for j, c in enumerate(self.customers):
                if c.get("c_name") == vals[0]:
                    self.customers[j] = d; break
        else:
            self.customers.append(d)
        save("customers.json", self.customers)
        self._refresh_clients(); self._clear_client()
        self._refresh_order_clients()
        self._status(f"Saved: {d['c_name']}")
    
    def _delete_client(self):
        sel = self.ctree.selection()
        if not sel: return self._status("Select a customer first. (Space or click)")
        vals = self.ctree.item(sel[0])["values"]
        for j, c in enumerate(self.customers):
            if c.get("c_name") == vals[0]:
                if messagebox.askyesno("Delete", f"Delete {vals[0]}?\n\nCtrl+Z to undo."):
                    self._undo = [("client", list(self.customers))]
                    del self.customers[j]; save("customers.json", self.customers)
                    self._refresh_clients(); self._clear_client()
                    self._status(f"Deleted: {vals[0]}. Ctrl+Z to undo.")
                return
    
    # ═══ TAB 2: ORDERS ═══
    def tab_orders(self):
        t = tk.Frame(self.nb, bg=C["bg"]); self.nb.add(t, text="  2. Orders  ")
        self._header("Order Builder  —  Enter to Calculate", t)
        
        card = self.card(t); card.pack(fill="x", pady=(0, 10))
        
        r1 = tk.Frame(card, bg=C["card"]); r1.pack(fill="x", pady=3)
        self._label(r1, "Customer:", "body", True).pack(side="left")
        self.ocli = ttk.Combobox(r1, font=("Segoe UI", 13), width=22, state="readonly")
        self.ocli.pack(side="left", padx=8)
        self._label(r1, "Event:", "body", True).pack(side="left", padx=(16, 0))
        self.oev = ttk.Combobox(r1, values=list(GUIDELINES.keys()), font=("Segoe UI", 13),
                               width=26, state="readonly"); self.oev.pack(side="left", padx=8)
        self.oev.current(0)
        
        r2 = tk.Frame(card, bg=C["card"]); r2.pack(fill="x", pady=3)
        self._label(r2, "Guests:", "body", True).pack(side="left")
        self.ogu = tk.IntVar(value=10)
        s = tk.Spinbox(r2, from_=1, to=200, textvariable=self.ogu, font=("Segoe UI", 14),
                      width=5); s.pack(side="left", padx=6)
        for n in [2, 4, 6, 8, 10, 15, 20, 30, 50]:
            tk.Button(r2, text=str(n), font=("Segoe UI", 9), bg=C["border"], relief="flat",
                     command=lambda x=n: (self.ogu.set(x), s.focus())).pack(side="left", padx=1)
        
        self._label(r2, "Date:", "body", True).pack(side="left", padx=(16, 0))
        self.oda = self._entry(r2, width=12); self.oda.pack(side="left", padx=6)
        self.oda.insert(0, datetime.now().strftime("%m/%d/%Y"))
        self._label(r2, "Price $:", "body", True).pack(side="left", padx=(16, 0))
        self.opr = tk.DoubleVar(value=340)
        self._entry(r2, width=8, textvariable=self.opr).pack(side="left", padx=6)
        self._label(r2, "Food Cost $:", "body", True).pack(side="left", padx=(16, 0))
        self.oco = tk.DoubleVar(value=120)
        self._entry(r2, width=8, textvariable=self.oco).pack(side="left", padx=6)
        
        r3 = tk.Frame(card, bg=C["card"]); r3.pack(fill="x", pady=3)
        self._label(r3, "Custom Menu Items (optional, one per line):", "small").pack(anchor="w")
        self.omu = tk.Text(card, height=3, font=("Consolas", 11), relief="solid", bd=1,
                          highlightbackground=C["border"]); self.omu.pack(fill="x", pady=(2, 8))
        
        self._btn(card, "Calculate & Add to Shopping List  (Enter)", "green", self._build_order).pack(fill="x")
        
        self.ores = tk.Label(card, text="", font=("Segoe UI", 13, "bold"), bg=C["card"], fg=C["green"])
        self.ores.pack(pady=(6, 0))
        
        # History
        self._header("Order History  —  Select + Delete to remove", t)
        hist = self.card(t); hist.pack(fill="both", expand=True)
        ocols = ("Date", "Customer", "Event", "Guests", "Price", "Cost", "Profit", "Margin")
        self.otree = ttk.Treeview(hist, columns=ocols, show="headings", height=6)
        for c in ocols: self.otree.heading(c, text=c); self.otree.column(c, width=105, minwidth=70)
        self.otree.pack(fill="both", expand=True)
        
        obtn = tk.Frame(hist, bg=C["card"]); obtn.pack(fill="x", pady=(8, 0))
        self._btn(obtn, "Delete Order  (Del)", "red", self._delete_order).pack(side="left")
        
        self._refresh_order_clients(); self._refresh_orders()
    
    def _refresh_order_clients(self):
        self.ocli["values"] = [c.get("c_name","") for c in self.customers]
    
    def _build_order(self):
        ev = self.oev.get()
        if ev not in GUIDELINES: return
        g = GUIDELINES[ev]; guests = self.ogu.get()
        price = self.opr.get(); cost = self.oco.get()
        profit = price - cost; margin = (profit/price*100) if price else 0
        client = self.ocli.get()
        
        for name, oz in g["items"]:
            t = oz * guests
            tag = f"[{client}] " if client else ""
            self.shopping.append(f"{tag}{name} — {lbs(t)}")
        for line in self.omu.get("1.0","end-1c").strip().split("\n"):
            if line.strip():
                tag = f"[{client}] " if client else ""
                self.shopping.append(f"{tag}{line.strip()}")
        
        save("shopping.json", self.shopping)
        
        order = {"date":self.oda.get(),"client":client,"event":ev,"guests":guests,
                "price":price,"cost":cost,"profit":profit,"margin":f"{margin:.0f}%"}
        self.orders.append(order); save("orders.json", self.orders)
        self._refresh_orders(); self._refresh_shopping()
        
        self.ores.config(text=f"SAVED!  ${price:.0f} - ${cost:.0f} cost = ${profit:.0f} profit ({margin:.0f}% margin)  |  Shopping list updated")
        self._status(f"Order saved: {client} — {ev} — {guests} guests — ${profit:.0f} profit")
    
    def _refresh_orders(self):
        for i in self.otree.get_children(): self.otree.delete(i)
        for o in reversed(self.orders[-30:]):
            self.otree.insert("", "end", values=(
                o.get("date",""), o.get("client",""), o.get("event",""),
                o.get("guests",""), f'${o.get("price",0):.0f}',
                f'${o.get("cost",0):.0f}', f'${o.get("profit",0):.0f}', o.get("margin","")))
    
    def _delete_order(self):
        sel = self.otree.selection()
        if not sel: return self._status("Select an order first.")
        ti = self.otree.index(sel[0])
        shown = self.orders[-30:]; rev = len(shown) - 1 - ti
        ai = len(self.orders) - len(shown) + rev
        if 0 <= ai < len(self.orders):
            o = self.orders[ai]
            if messagebox.askyesno("Delete Order",
                f"Delete: {o.get('client','?')} — {o.get('event','?')} — {o.get('date','?')}?\n\nCtrl+Z to undo."):
                self._undo = [("order", list(self.orders))]
                del self.orders[ai]; save("orders.json", self.orders)
                self._refresh_orders()
                self._status(f"Order deleted. Ctrl+Z to undo.")
    
    # ═══ TAB 3: RECIPES ═══
    def tab_recipes(self):
        t = tk.Frame(self.nb, bg=C["bg"]); self.nb.add(t, text="  3. Recipes  ")
        self._header("Recipe Scaler  —  Paste recipe, Enter to scale", t)
        
        card = self.card(t); card.pack(fill="both", expand=True)
        
        self._label(card, "Paste any recipe. One ingredient per line. Examples: \"2 cups flour\" or \"1.5 lbs chicken\"",
                   "small").pack(anchor="w")
        
        row = tk.Frame(card, bg=C["card"]); row.pack(fill="x", pady=(8, 4))
        self._label(row, "Servings in recipe:", "body").pack(side="left")
        self.rs_o = tk.IntVar(value=4)
        tk.Spinbox(row, from_=1, to=100, textvariable=self.rs_o, font=("Segoe UI", 14),
                  width=4).pack(side="left", padx=6)
        self._label(row, "Servings needed:", "body").pack(side="left", padx=(16, 0))
        self.rs_n = tk.IntVar(value=10)
        tk.Spinbox(row, from_=1, to=300, textvariable=self.rs_n, font=("Segoe UI", 14),
                  width=4).pack(side="left", padx=6)
        
        self._label(card, "Ingredients:", "small", True).pack(anchor="w", pady=(8, 2))
        self.rs_in = tk.Text(card, height=8, font=("Consolas", 11), relief="solid", bd=1,
                            highlightbackground=C["border"], wrap="word")
        self.rs_in.pack(fill="x")
        
        bf = tk.Frame(card, bg=C["card"]); bf.pack(fill="x", pady=8)
        self._btn(bf, "Scale Recipe  (Enter)", "green", self._scale_recipe).pack(side="left", padx=(0, 6))
        self._btn(bf, "Clear", "clear").pack(side="left")
        
        self._label(card, "Scaled Ingredients:", "small", True).pack(anchor="w", pady=(0, 2))
        self.rs_out = tk.Text(card, height=8, font=("Consolas", 11), relief="solid", bd=1,
                             highlightbackground=C["border"], bg="#F5F5F5", wrap="word")
        self.rs_out.pack(fill="x")
        
        bf2 = tk.Frame(card, bg=C["card"]); bf2.pack(fill="x", pady=(8, 0))
        self._btn(bf2, "Copy Scaled Recipe", "white", lambda: (
            self.root.clipboard_clear(), self.root.clipboard_append(self.rs_out.get("1.0","end-1c")),
            self._status("Scaled recipe copied to clipboard!"))).pack(side="left", padx=(0, 6))
        self._btn(bf2, "Add to Shopping List", "blue", self._recipe_to_shop).pack(side="left")
    
    def _scale_recipe(self):
        text = self.rs_in.get("1.0","end-1c"); orig = self.rs_o.get(); need = self.rs_n.get()
        if orig <= 0: return
        ratio = need / orig; out = []
        for line in text.strip().split("\n"):
            line = line.strip()
            if not line: continue
            m = re.match(r'^([\d./\s]+)\s*(.*)', line)
            if m:
                ns = m.group(1).strip(); rest = m.group(2)
                try:
                    parts = ns.replace("/"," / ").split(); val = 0; frac = 0
                    for p in parts:
                        if p == "/": continue
                        if "/" in p: n,d = p.split("/"); frac += float(n)/float(d)
                        else: val += float(p)
                    s = (val + frac) * ratio
                    out.append(f"{s:.2f} {rest}" if s < 10 else f"{s:.1f} {rest}")
                except:
                    out.append(f"{line}  (x{ratio:.1f})")
            else:
                out.append(line)
        self.rs_out.delete("1.0","end"); self.rs_out.insert("1.0", "\n".join(out))
        self._status(f"Recipe scaled {orig} -> {need} servings (x{ratio:.1f})")
    
    def _recipe_to_shop(self):
        for line in self.rs_out.get("1.0","end-1c").strip().split("\n"):
            if line.strip(): self.shopping.append(line.strip())
        save("shopping.json", self.shopping); self._refresh_shopping()
        self._status("Recipe ingredients sent to Shopping List!")
    
    # ═══ TAB 4: SHOPPING ═══
    def tab_shopping(self):
        t = tk.Frame(self.nb, bg=C["bg"]); self.nb.add(t, text="  4. Shopping  ")
        
        self._header("Shopping List  —  Space to check off, Del to remove, Esc to clear all", t)
        
        btn_row = tk.Frame(t, bg=C["bg"]); btn_row.pack(fill="x", pady=(0, 8))
        self._btn(btn_row, "Print List", "blue", self._print_shopping).pack(side="left", padx=(0, 6))
        self._btn(btn_row, "Copy All", "white", self._copy_shopping).pack(side="left", padx=(0, 6))
        self._btn(btn_row, "Clear All  (Esc)", "red", lambda: (
            self._undo.append(("shopping", list(self.shopping))),
            setattr(self, 'shopping', []), save("shopping.json", []),
            self._refresh_shopping(),
            self._status("Shopping list cleared. Ctrl+Z to undo.")
        ) if messagebox.askyesno("Clear", "Clear entire shopping list?\n\nCtrl+Z to undo.") else None).pack(side="left", padx=(0, 6))
        self._btn(btn_row, "Remove Selected  (Del)", "clear", self._remove_shop).pack(side="left")
        
        card = self.card(t); card.pack(fill="both", expand=True)
        self.stree = ttk.Treeview(card, columns=("Check","Item"), show="headings", height=16)
        self.stree.heading("Check", text="✓"); self.stree.column("Check", width=35, anchor="center")
        self.stree.heading("Item", text="Items to Purchase"); self.stree.column("Item", width=750)
        self.stree.pack(fill="both", expand=True)
        self.stree.bind("<space>", lambda e: self._toggle_check())
        self.stree.bind("<Double-1>", lambda e: self._toggle_check())
        
        self._refresh_shopping()
    
    def _refresh_shopping(self):
        for i in self.stree.get_children(): self.stree.delete(i)
        for item in self.shopping:
            ck = "☑" if item.startswith("☑") else "☐"
            disp = item.replace("☑","").replace("☐","").strip()
            self.stree.insert("", "end", values=(ck, disp))
    
    def _toggle_check(self):
        sel = self.stree.selection()
        if not sel: return
        i = self.stree.index(sel[0])
        if i < len(self.shopping):
            self.shopping[i] = self.shopping[i][1:] if self.shopping[i].startswith("☑") else "☑" + self.shopping[i]
            save("shopping.json", self.shopping); self._refresh_shopping()
    
    def _copy_shopping(self):
        lines = ["PASSE LA FETE — SHOPPING LIST", datetime.now().strftime('%B %d, %Y'), "="*55]
        for item in self.shopping:
            mk = "☑" if item.startswith("☑") else "☐"
            lines.append(f"  {mk}  {item.replace('☑','').replace('☐','').strip()}")
        self.root.clipboard_clear(); self.root.clipboard_append("\n".join(lines))
        self._status("Shopping list copied to clipboard!")
    
    def _print_shopping(self):
        html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<title>Passe La Fete — Shopping List</title>
<style>
  @page{{size:letter;margin:.5in}} body{{font-family:Segoe UI,sans-serif;max-width:7in;margin:0 auto;color:#000}}
  h1{{font-size:22pt;margin-bottom:4pt}} .date{{color:#666;font-size:11pt;margin-bottom:16pt}}
  table{{width:100%;border-collapse:collapse}} td{{padding:10px 8px;border-bottom:1px solid #ddd;font-size:12pt}}
  .check{{width:30px;font-size:16pt;text-align:center}}
  .total{{font-weight:bold;font-size:14pt;border-top:3px solid #000;margin-top:16pt;padding-top:12pt}}
  @media print{{body{{-webkit-print-color-adjust:exact}}}}
</style></head><body>
<h1>Passe La Fete — Shopping List</h1>
<div class="date">{datetime.now().strftime('%A, %B %d, %Y')}</div><table>"""
        count = 0
        for item in self.shopping:
            mk = "☑" if item.startswith("☑") else "☐"
            html += f"<tr><td class='check'>{mk}</td><td>{item.replace('☑','').replace('☐','').strip()}</td></tr>"
            count += 1
        html += f"</table><div class='total'>{count} items</div><script>window.onload=function(){{window.print()}}</script></body></html>"
        f = tempfile.NamedTemporaryFile(suffix=".html", delete=False)
        f.write(html.encode("utf-8")); f.close(); webbrowser.open(f.name)
        self._status("Print page opened. Press Ctrl+P if print dialog didn't appear.")
    
    def _remove_shop(self):
        sel = self.stree.selection()
        if not sel: return
        i = self.stree.index(sel[0])
        if i < len(self.shopping):
            item = self.shopping[i]; del self.shopping[i]
            save("shopping.json", self.shopping); self._refresh_shopping()
            self._status(f"Removed: {item[:50]}")
    
    # ═══ TAB 5: SUPPLIERS ═══
    def tab_suppliers(self):
        t = tk.Frame(self.nb, bg=C["bg"]); self.nb.add(t, text="  5. Suppliers  ")
        
        self._header("Supplier Directory  —  Type to search, Space to select", t)
        
        sr = tk.Frame(t, bg=C["bg"]); sr.pack(fill="x", pady=(0, 8))
        self._label(sr, "Search:", "body", True).pack(side="left", padx=(0, 6))
        self.sup_search = self._entry(sr, width=30)
        self.sup_search.pack(side="left"); self.sup_search.bind("<KeyRelease>", lambda e: self._refresh_suppliers())
        self._btn(sr, "Clear Search", "clear").pack(side="left", padx=6)
        
        panes = tk.Frame(t, bg=C["bg"]); panes.pack(fill="both", expand=True)
        
        lc = self.card(panes); lc.pack(side="left", fill="both", expand=True, padx=(0, 6))
        cols = ("Name", "Type", "Phone", "Location")
        self.sutree = ttk.Treeview(lc, columns=cols, show="headings", height=14)
        for c in cols: self.sutree.heading(c, text=c); self.sutree.column(c, width=145)
        self.sutree.pack(fill="both", expand=True)
        self.sutree.bind("<<TreeviewSelect>>", self._on_sup_select)
        self.sutree.bind("<space>", lambda e: self._on_sup_select(None))
        
        self.sup_card = self.card(panes); self.sup_card.pack(side="right", fill="both", padx=(6, 0))
        self.sup_detail = tk.Text(self.sup_card, font=("Segoe UI", 12), bg=C["card"],
                                 relief="flat", height=16, wrap="word", state="disabled")
        self.sup_detail.pack(fill="both", expand=True)
        
        bf = tk.Frame(t, bg=C["bg"]); bf.pack(fill="x", pady=(8, 0))
        self._btn(bf, "+ Add Supplier", "green", self._add_supplier).pack(side="left", padx=(0, 6))
        self._btn(bf, "Edit Selected", "white", self._edit_supplier).pack(side="left", padx=(0, 6))
        self._btn(bf, "Delete  (Del)", "red", self._delete_supplier).pack(side="left")
        
        self._refresh_suppliers()
    
    def _refresh_suppliers(self):
        for i in self.sutree.get_children(): self.sutree.delete(i)
        q = self.sup_search.get().lower()
        for s in self.suppliers:
            if q and q not in json.dumps(s).lower(): continue
            self.sutree.insert("", "end", values=(
                s.get("name",""), s.get("type",""), s.get("phone",""), s.get("location","")))
    
    def _on_sup_select(self, e):
        sel = self.sutree.selection()
        if not sel: return
        vals = self.sutree.item(sel[0])["values"]
        for s in self.suppliers:
            if s.get("name") == vals[0]:
                self.sup_detail.config(state="normal"); self.sup_detail.delete("1.0","end")
                self.sup_detail.insert("1.0", f"""NAME:  {s.get('name','')}
TYPE:  {s.get('type','')}
PHONE:  {s.get('phone','')}
ADDRESS:  {s.get('address','')}
HOURS:  {s.get('hours','')}
NOTES:  {s.get('notes','')}""")
                self.sup_detail.config(state="disabled"); return
    
    def _sup_dialog(self, title, prefill=None):
        d = tk.Toplevel(self.root); d.title(title); d.geometry("440x380")
        d.configure(bg=C["bg"]); d.transient(self.root); d.grab_set()
        d.bind("<Escape>", lambda e: d.destroy())
        tk.Label(d, text=title, font=("Segoe UI", 18, "bold"), bg=C["bg"]).pack(pady=(15, 10))
        fields = ["Name", "Type", "Phone", "Address", "Hours", "Notes"]
        entries = {}
        for f in fields:
            r = tk.Frame(d, bg=C["bg"]); r.pack(fill="x", padx=40, pady=2)
            tk.Label(r, text=f, font=("Segoe UI", 12), bg=C["bg"], fg=C["subtle"],
                    width=10, anchor="e").pack(side="left", padx=(0, 8))
            e = tk.Entry(r, font=("Segoe UI", 13), width=28); e.pack(side="left")
            if prefill: e.insert(0, prefill.get(f.lower(), ""))
            entries[f.lower()] = e
            if f == "Name": e.focus_set()
        def save_sup():
            nd = {f: entries[f].get() for f in entries}
            if nd.get("name"):
                if prefill:
                    for k in nd: prefill[k] = nd[k]
                else:
                    self.suppliers.append(nd)
                save("suppliers.json", self.suppliers); self._refresh_suppliers(); d.destroy()
                self._status(f"Supplier saved: {nd['name']}")
        b = tk.Button(d, text="Save Supplier  (Enter)", font=("Segoe UI", 13, "bold"),
                     bg=C["green"], fg="white", relief="flat", padx=20, pady=8, command=save_sup)
        b.pack(pady=15); b.bind("<Return>", lambda e: save_sup())
        d.bind("<Return>", lambda e: save_sup())
    
    def _add_supplier(self): self._sup_dialog("Add Supplier")
    def _edit_supplier(self):
        sel = self.sutree.selection()
        if not sel: return self._status("Select a supplier first. (Space or click)")
        vals = self.sutree.item(sel[0])["values"]
        for s in self.suppliers:
            if s.get("name") == vals[0]: self._sup_dialog("Edit Supplier", s); return
    
    def _delete_supplier(self):
        sel = self.sutree.selection()
        if not sel: return self._status("Select a supplier first.")
        vals = self.sutree.item(sel[0])["values"]
        for j, s in enumerate(self.suppliers):
            if s.get("name") == vals[0]:
                if messagebox.askyesno("Delete", f"Delete {vals[0]}?"):
                    del self.suppliers[j]; save("suppliers.json", self.suppliers)
                    self._refresh_suppliers()
                    self._status(f"Deleted: {vals[0]}")
                return
    
    # ═══ TAB 6: QUICK CALC ═══
    def tab_quick(self):
        t = tk.Frame(self.nb, bg=C["bg"]); self.nb.add(t, text="  6. Quick Calc  ")
        self._header("Quick Portion Calculator", t)
        
        card = self.card(t); card.pack(fill="both", expand=True)
        
        r1 = tk.Frame(card, bg=C["card"]); r1.pack(fill="x", pady=3)
        self._label(r1, "Event:", "body", True).pack(side="left")
        self.qev = ttk.Combobox(r1, values=list(GUIDELINES.keys()), font=("Segoe UI", 13),
                               width=32, state="readonly"); self.qev.pack(side="left", padx=8)
        self.qev.current(0); self.qev.bind("<<ComboboxSelected>>", lambda e: self._quick_calc())
        
        r2 = tk.Frame(card, bg=C["card"]); r2.pack(fill="x", pady=3)
        self._label(r2, "Guests:", "body", True).pack(side="left")
        self.qgu = tk.IntVar(value=10)
        tk.Spinbox(r2, from_=1, to=200, textvariable=self.qgu, font=("Segoe UI", 14),
                  width=5, command=self._quick_calc).pack(side="left", padx=6)
        for n in [2, 4, 6, 10, 20, 50]:
            tk.Button(r2, text=str(n), font=("Segoe UI", 9), bg=C["border"],
                     relief="flat", command=lambda x=n: (self.qgu.set(x), self._quick_calc())).pack(side="left", padx=1)
        
        self.qmf = tk.Frame(card, bg=C["card"])
        self._label(self.qmf, "Meals/person:", "body", True).pack(side="left")
        self.qme = tk.IntVar(value=5)
        tk.Spinbox(self.qmf, from_=1, to=21, textvariable=self.qme, font=("Segoe UI", 14),
                  width=5, command=self._quick_calc).pack(side="left", padx=6)
        
        self.qnote = tk.Label(card, text="", font=("Segoe UI", 10), bg=C["card"], fg=C["subtle"])
        self.qnote.pack(anchor="w", pady=(6, 0))
        
        cols = ("Ingredient", "Per Person", "Buy")
        self.qtree = ttk.Treeview(card, columns=cols, show="headings", height=10)
        self.qtree.heading("Ingredient", text="Ingredient"); self.qtree.column("Ingredient", width=380)
        self.qtree.heading("Per Person", text="Per Person"); self.qtree.column("Per Person", width=130, anchor="center")
        self.qtree.heading("Buy", text="Buy"); self.qtree.column("Buy", width=240, anchor="center")
        self.qtree.pack(fill="both", expand=True, pady=(8, 0))
        
        bf = tk.Frame(card, bg=C["card"]); bf.pack(fill="x", pady=(8, 0))
        self._btn(bf, "Copy List", "white", lambda: self._copy_tree(self.qtree)).pack(side="left", padx=(0, 6))
        self._btn(bf, "Send to Shopping", "blue", self._quick_to_shop).pack(side="left")
        
        self._quick_calc()
    
    def _quick_calc(self):
        for i in self.qtree.get_children(): self.qtree.delete(i)
        ev = self.qev.get()
        if ev not in GUIDELINES: return
        g = GUIDELINES[ev]; guests = self.qgu.get()
        meals = self.qme.get() if "Meal Prep" in ev else 1
        self.qnote.config(text=g.get("note",""))
        if "Meal Prep" in ev: self.qmf.pack(fill="x", pady=3, before=self.qnote)
        else: self.qmf.pack_forget()
        total = 0
        for name, oz in g["items"]:
            t = oz * guests * meals; total += t
            self.qtree.insert("", "end", values=(name, f"{oz} oz", lbs(t)))
        self.qtree.insert("", "end", values=("TOTAL", "", lbs(total)))
    
    def _copy_tree(self, tree):
        lines = ["Passe La Fete — Quick Calc", "="*50]
        for item in tree.get_children():
            v = tree.item(item)["values"]
            lines.append(f"  {v[0]:<40} {v[-1] if v[-1] else ''}")
        self.root.clipboard_clear(); self.root.clipboard_append("\n".join(lines))
        self._status("Quick Calc copied to clipboard!")
    
    def _quick_to_shop(self):
        for item in self.qtree.get_children():
            v = self.qtree.item(item)["values"]
            if v[0] != "TOTAL" and v[-1]: self.shopping.append(f"{v[0]} — {v[-1]}")
        save("shopping.json", self.shopping); self._refresh_shopping()
        self._status("Portions sent to Shopping List!")

if __name__ == "__main__":
    root = tk.Tk()
    Suite(root)
    root.mainloop()
