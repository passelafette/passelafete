"""
Passe La Fete — Portion & Shopping Calculator
Chef Michelle's tool for precise ingredient quantities per event.
Double-click to run. No internet needed.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

# ===== PORTION GUIDELINES (per person) =====
GUIDELINES = {
    "Charcuterie / Grazing Table": {
        "title": "Charcuterie & Grazing Table",
        "note": "Amounts are per person. Scale up for grazing tables lasting 2+ hours (+25%).",
        "items": [
            ("Cured Meats (prosciutto, salami, etc.)", 2.5, "oz"),
            ("Artisan Cheeses (3+ varieties)", 3, "oz"),
            ("Fresh Fruit (grapes, berries, figs)", 3, "oz"),
            ("Crackers & Breadsticks", 2, "oz"),
            ("Nuts (marcona almonds, etc.)", 1, "oz"),
            ("Olives & Pickles", 1.5, "oz"),
            ("Honey, Jam, or Chutney", 0.5, "oz"),
            ("Fresh Herbs for Garnish", 0.1, "oz"),
        ],
    },
    "Sit-Down Dinner": {
        "title": "Sit-Down Dinner (3 Courses)",
        "note": "Based on appetizer + main + dessert. Multiply protein by 1.2 for bone-in cuts.",
        "items": [
            ("Appetizer / Starter", 4, "oz"),
            ("Protein (chicken, fish, beef)", 7, "oz"),
            ("Vegetable Side 1", 5, "oz"),
            ("Starch Side (potatoes, rice, pasta)", 5, "oz"),
            ("Sauce or Gravy", 2, "oz"),
            ("Dinner Rolls or Bread", 1.5, "oz"),
            ("Butter", 0.5, "oz"),
            ("Dessert", 4, "oz"),
        ],
    },
    "Weekly Meal Prep": {
        "title": "Weekly Meal Prep",
        "note": "Per meal, per person. Multiply by number of meals.",
        "items": [
            ("Protein per meal", 6, "oz"),
            ("Vegetable per meal", 4, "oz"),
            ("Carb / Starch per meal", 5, "oz"),
            ("Breakfast Item (eggs, oats, etc.)", 4, "oz"),
            ("Sauce / Dressing per meal", 1.5, "oz"),
        ],
        "extra_prompt": "Number of Meals per Person",
        "extra_default": 5,
    },
    "Appetizer & Dessert Party": {
        "title": "Appetizer & Dessert Party",
        "note": "For cocktail-style events. Increase by 30% if no dinner served.",
        "items": [
            ("Hot Appetizers (3 varieties)", 3, "oz"),
            ("Cold Appetizers (3 varieties)", 3, "oz"),
            ("Dips & Spreads", 2, "oz"),
            ("Crackers, Crostini, Bread", 1.5, "oz"),
            ("Crudites (vegetable platter)", 3, "oz"),
            ("Dessert (mini pastries, tarts)", 2, "oz"),
            ("Dessert (cakes or pies)", 3, "oz"),
            ("Fresh Fruit for Dessert", 2, "oz"),
        ],
    },
}

class PortionCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Passe La Fete — Portion Calculator")
        self.root.geometry("700x750")
        self.root.configure(bg="#faf8f2")
        self.root.resizable(True, True)
        
        # Colors
        self.green = "#4a7c59"
        self.green_dark = "#2d5a3d"
        self.cream = "#faf8f2"
        self.gold = "#c9a96e"
        self.white = "#ffffff"
        
        self.build_ui()
    
    def build_ui(self):
        # Header
        header = tk.Frame(self.root, bg=self.green_dark, height=80)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        tk.Label(header, text="Passe La Fete", font=("Georgia", 22, "bold"),
                bg=self.green_dark, fg=self.white).pack(pady=8)
        tk.Label(header, text="Portion & Shopping Calculator", font=("Helvetica", 11),
                bg=self.green_dark, fg=self.gold).pack()
        
        # Main content
        main = tk.Frame(self.root, bg=self.cream, padx=30, pady=20)
        main.pack(fill="both", expand=True)
        
        # Event type
        tk.Label(main, text="Event Type", font=("Helvetica", 11, "bold"),
                bg=self.cream, fg=self.green_dark).pack(anchor="w", pady=(10, 3))
        
        self.event_var = tk.StringVar()
        self.event_combo = ttk.Combobox(main, textvariable=self.event_var,
                values=list(GUIDELINES.keys()), state="readonly",
                font=("Helvetica", 11))
        self.event_combo.pack(fill="x", pady=(0, 10))
        self.event_combo.bind("<<ComboboxSelected>>", self.on_event_change)
        self.event_combo.current(0)
        
        # Guest count
        tk.Label(main, text="Number of Guests", font=("Helvetica", 11, "bold"),
                bg=self.cream, fg=self.green_dark).pack(anchor="w", pady=(5, 3))
        
        guest_frame = tk.Frame(main, bg=self.cream)
        guest_frame.pack(fill="x", pady=(0, 10))
        
        self.guest_var = tk.IntVar(value=10)
        tk.Spinbox(guest_frame, from_=1, to=200, textvariable=self.guest_var,
                  font=("Helvetica", 14), width=8, justify="center",
                  command=self.on_guest_change).pack(side="left", padx=(0, 10))
        
        # Quick buttons
        for n in [2, 4, 6, 10, 20, 50]:
            btn = tk.Button(guest_frame, text=str(n), font=("Helvetica", 9),
                          bg=self.white, fg=self.green_dark,
                          relief="solid", borderwidth=1,
                          command=lambda x=n: self.set_guests(x))
            btn.pack(side="left", padx=2)
        
        # Meal count (for meal prep)
        self.meal_frame = tk.Frame(main, bg=self.cream)
        tk.Label(self.meal_frame, text="Number of Meals per Person",
                font=("Helvetica", 11, "bold"), bg=self.cream,
                fg=self.green_dark).pack(anchor="w", pady=(5, 3))
        self.meal_var = tk.IntVar(value=5)
        tk.Spinbox(self.meal_frame, from_=1, to=21, textvariable=self.meal_var,
                  font=("Helvetica", 14), width=8, justify="center").pack(anchor="w")
        
        # Calculate button
        tk.Button(main, text="CALCULATE SHOPPING LIST", font=("Helvetica", 13, "bold"),
                 bg=self.green, fg=self.white, activebackground=self.green_dark,
                 activeforeground=self.white, relief="flat", cursor="hand2",
                 padx=20, pady=10, command=self.calculate).pack(fill="x", pady=15)
        
        # Results area
        result_frame = tk.Frame(main, bg=self.white, relief="solid", bd=1)
        result_frame.pack(fill="both", expand=True)
        
        # Treeview for results
        cols = ("Item", "Per Person", "Total Needed", "Buy")
        self.tree = ttk.Treeview(result_frame, columns=cols, show="headings",
                                 height=12)
        self.tree.heading("Item", text="Ingredient")
        self.tree.heading("Per Person", text="Per Person")
        self.tree.heading("Total Needed", text="Total Needed")
        self.tree.heading("Buy", text="Buy This Much")
        self.tree.column("Item", width=280)
        self.tree.column("Per Person", width=100, anchor="center")
        self.tree.column("Total Needed", width=120, anchor="center")
        self.tree.column("Buy", width=150, anchor="center")
        
        scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Note label
        self.note_label = tk.Label(main, text="", font=("Helvetica", 9, "italic"),
                                  bg=self.cream, fg="#888", wraplength=620,
                                  justify="left")
        self.note_label.pack(fill="x", pady=(8, 0))
        
        # Bottom buttons
        btn_frame = tk.Frame(main, bg=self.cream)
        btn_frame.pack(fill="x", pady=(10, 0))
        
        tk.Button(btn_frame, text="Copy to Clipboard", font=("Helvetica", 10),
                 bg=self.white, fg=self.green_dark, relief="solid", borderwidth=1,
                 command=self.copy_to_clipboard).pack(side="left", padx=(0, 5))
        
        tk.Button(btn_frame, text="Save as Text File", font=("Helvetica", 10),
                 bg=self.white, fg=self.green_dark, relief="solid", borderwidth=1,
                 command=self.save_to_file).pack(side="left")
        
        # Footer
        tk.Label(main, text="Portions based on culinary standards. Adjust to your preferences.",
                font=("Helvetica", 8), bg=self.cream, fg="#aaa").pack(pady=(10, 0))
        
        # Initial calculation
        self.on_event_change()
        self.calculate()
    
    def set_guests(self, n):
        self.guest_var.set(n)
        self.on_guest_change()
    
    def on_guest_change(self, *args):
        self.calculate()
    
    def on_event_change(self, event=None):
        event_name = self.event_var.get()
        if "Meal Prep" in event_name:
            self.meal_frame.pack(fill="x", pady=(0, 5), before=self.note_label.master.children.get(
                [k for k in self.note_label.master.children if str(self.note_label.master.children[k]) == str(self.note_label)][0] if False else None))
        else:
            self.meal_frame.pack_forget()
        self.calculate()
    
    def calculate(self, *args):
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        event_name = self.event_var.get()
        if event_name not in GUIDELINES:
            return
        
        guide = GUIDELINES[event_name]
        guests = self.guest_var.get()
        meals = self.meal_var.get() if "Meal Prep" in event_name else 1
        
        self.note_label.config(text=guide.get("note", ""))
        
        total_lbs = 0
        for ingredient, oz_per, unit in guide["items"]:
            per_person = f"{oz_per} {unit}"
            total_oz = oz_per * guests * meals
            
            # Always show lbs primary, oz in parens
            lbs = total_oz / 16
            if total_oz >= 16:
                buy = f"{lbs:.1f} lbs ({total_oz:.0f} oz)"
            elif total_oz >= 1:
                buy = f"{lbs:.2f} lbs ({total_oz:.1f} oz)"
            else:
                buy = f"{lbs:.3f} lbs ({total_oz:.2f} oz)"
            total_lbs += lbs
            
            total_needed = f"{total_oz:.1f} {unit}"
            
            tag = "evenrow" if len(self.tree.get_children()) % 2 == 0 else "oddrow"
            self.tree.insert("", "end", values=(ingredient, per_person, total_needed, buy))
        
        # Total row
        self.tree.insert("", "end", values=(
            "TOTAL FOOD NEEDED", "", "",
            f"{total_lbs:.1f} lbs total"
        ))
        
        # Style total row
        self.tree.tag_configure("total", background=self.gold, foreground=self.white)
        last = self.tree.get_children()[-1]
        self.tree.item(last, tags=("total",))
    
    def copy_to_clipboard(self):
        lines = []
        lines.append(f"Passe La Fete — Shopping List")
        lines.append(f"Event: {self.event_var.get()}")
        lines.append(f"Guests: {self.guest_var.get()}")
        if "Meal Prep" in self.event_var.get():
            lines.append(f"Meals: {self.meal_var.get()}")
        lines.append("=" * 50)
        
        for item in self.tree.get_children():
            vals = self.tree.item(item)["values"]
            if vals[0] == "TOTAL FOOD NEEDED":
                lines.append("")
                lines.append(f"  {vals[3]}")
            else:
                lines.append(f"  {vals[0]:<40} {vals[3]}")
        
        text = "\n".join(lines)
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        messagebox.showinfo("Copied!", "Shopping list copied to clipboard.\nPaste into Notes, email, or print it.")
    
    def save_to_file(self):
        from tkinter import filedialog
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=f"shopping_list_{self.event_var.get().replace(' ','_').replace('/','')}.txt"
        )
        if not filename:
            return
        
        lines = []
        lines.append(f"PASSE LA FETE — SHOPPING LIST")
        lines.append(f"Event: {self.event_var.get()}")
        lines.append(f"Guests: {self.guest_var.get()}")
        if "Meal Prep" in self.event_var.get():
            lines.append(f"Meals per person: {self.meal_var.get()}")
        lines.append("=" * 50)
        
        for item in self.tree.get_children():
            vals = self.tree.item(item)["values"]
            if vals[0] == "TOTAL FOOD NEEDED":
                lines.append("")
                lines.append(f"  >>> {vals[3]} <<<")
            else:
                lines.append(f"  {vals[0]:<42} {vals[3]}")
        
        with open(filename, "w") as f:
            f.write("\n".join(lines))
        
        messagebox.showinfo("Saved!", f"Shopping list saved to:\n{filename}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PortionCalculator(root)
    root.mainloop()
