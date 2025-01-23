import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import ttkbootstrap as ttkb
import json
import os
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Datei für gespeicherte Daten
DATA_FILE = "verkauf_data.json"

# Daten initialisieren
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as file:
        json.dump({"users": {}, "sales": [], "categories": {}}, file)

# Daten laden und speichern
def load_data():
    with open(DATA_FILE, "r") as file:
        data = json.load(file)

    if "categories" not in data:
        data["categories"] = {}

    if "users" not in data:
        data["users"] = {}
    if "sales" not in data:
        data["sales"] = []

    save_data(data)  # Speichert ggf. korrigierte Struktur zurück
    return data

def save_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

# GUI-Anwendung
class SalesToolApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Verkaufsmanagement-Tool")
        self.root.geometry("1400x1000")
        self.style = ttkb.Style("litera")

        self.data = load_data()
        self.current_user = None

        # Hauptüberschrift
        ttkb.Label(self.root, text="Verkaufsmanagement-Tool", font=("Arial", 22, "bold"), anchor="center").pack(fill="x", pady=10)

        # Tabs erstellen
        self.tabs = ttkb.Notebook(self.root, bootstyle="primary")
        self.tabs.pack(fill="both", expand=True, padx=10, pady=10)

        self.create_login_tab()
        self.create_sales_tab()
        self.create_dashboard_tab()
        self.create_category_management_tab()  # <-- NEU: Kategorien-Tab

    # ------------------------- Login Tab -------------------------
    def create_login_tab(self):
        self.login_tab = ttkb.Frame(self.tabs)
        self.tabs.add(self.login_tab, text="🔑 Login/Registrierung")

        ttkb.Label(self.login_tab, text="Benutzername:", font=("Arial", 14)).pack(pady=10)
        self.username_entry = ttkb.Entry(self.login_tab, font=("Arial", 14), bootstyle="info")
        self.username_entry.pack(pady=5)

        ttkb.Label(self.login_tab, text="Passwort:", font=("Arial", 14)).pack(pady=10)
        self.password_entry = ttkb.Entry(self.login_tab, show="*", font=("Arial", 14), bootstyle="info")
        self.password_entry.pack(pady=5)

        ttkb.Button(self.login_tab, text="Login", command=self.login, bootstyle="success-outline").pack(pady=10)
        ttkb.Button(self.login_tab, text="Registrieren", command=self.register, bootstyle="info-outline").pack(pady=5)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if username in self.data["users"] and self.data["users"][username] == password:
            self.current_user = username
            self.update_dashboard()
            messagebox.showinfo("Erfolg", f"Willkommen zurück, {username}!")
        else:
            messagebox.showerror("Fehler", "Ungültiger Benutzername oder Passwort.")

    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if username in self.data["users"]:
            messagebox.showerror("Fehler", "Benutzername existiert bereits.")
        else:
            self.data["users"][username] = password
            save_data(self.data)
            messagebox.showinfo("Erfolg", "Registrierung erfolgreich!")

    # ------------------------- Verkauf hinzufügen Tab -------------------------
    def create_sales_tab(self):
        self.sales_tab = ttkb.Frame(self.tabs)
        self.tabs.add(self.sales_tab, text="➕ Verkauf hinzufügen")

        ttkb.Label(self.sales_tab, text="Überkategorie:", font=("Arial", 14)).pack(pady=10)
        self.parent_category_combobox = ttkb.Combobox(self.sales_tab, font=("Arial", 14), values=list(self.data["categories"].keys()))
        self.parent_category_combobox.pack(pady=5)
        self.parent_category_combobox.bind("<<ComboboxSelected>>", self.load_subcategories)

        ttkb.Label(self.sales_tab, text="Unterkategorie:", font=("Arial", 14)).pack(pady=10)
        self.subcategory_combobox = ttkb.Combobox(self.sales_tab, font=("Arial", 14))
        self.subcategory_combobox.pack(pady=5)
        self.subcategory_combobox.bind("<<ComboboxSelected>>", self.set_price)

        ttkb.Label(self.sales_tab, text="Datum (YYYY-MM-DD):", font=("Arial", 14)).pack(pady=10)
        self.date_entry = ttkb.Entry(self.sales_tab, font=("Arial", 14))
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.date_entry.pack(pady=5)

        ttkb.Label(self.sales_tab, text="Betrag (€):", font=("Arial", 14)).pack(pady=10)
        self.amount_entry = ttkb.Entry(self.sales_tab, font=("Arial", 14))
        self.amount_entry.pack(pady=5)

        ttkb.Label(self.sales_tab, text="Beschreibung:", font=("Arial", 14)).pack(pady=10)
        self.description_entry = ttkb.Entry(self.sales_tab, font=("Arial", 14))
        self.description_entry.pack(pady=5)

        ttkb.Label(self.sales_tab, text="Käufer:", font=("Arial", 14)).pack(pady=10)
        self.buyer_entry = ttkb.Entry(self.sales_tab, font=("Arial", 14))
        self.buyer_entry.pack(pady=5)

        ttkb.Button(self.sales_tab, text="Verkauf hinzufügen", command=self.add_sale, bootstyle="success-outline").pack(pady=20)

    def load_subcategories(self, event):
        selected_parent = self.parent_category_combobox.get()
        subcategories = self.data["categories"].get(selected_parent, {}).get("subcategories", {})
        self.subcategory_combobox["values"] = list(subcategories.keys())
        self.subcategory_combobox.set("")
        self.amount_entry.delete(0, tk.END)

    def set_price(self, event):
        selected_parent = self.parent_category_combobox.get()
        selected_subcategory = self.subcategory_combobox.get()
        if selected_parent and selected_subcategory:
            price = self.data["categories"].get(selected_parent, {}) \
                                          .get("subcategories", {}) \
                                          .get(selected_subcategory, {}) \
                                          .get("price")
            if price:
                self.amount_entry.delete(0, tk.END)
                self.amount_entry.insert(0, str(price))

    def add_sale(self):
        if not self.current_user:
            messagebox.showerror("Fehler", "Bitte zuerst einloggen.")
            return

        parent_category = self.parent_category_combobox.get()
        subcategory = self.subcategory_combobox.get()

        if not parent_category or not subcategory:
            messagebox.showerror("Fehler", "Bitte eine Kategorie und Unterkategorie auswählen.")
            return

        date = self.date_entry.get()
        amount = self.amount_entry.get()
        description = self.description_entry.get()
        buyer = self.buyer_entry.get()

        try:
            amount = float(amount)
        except ValueError:
            messagebox.showerror("Fehler", "Betrag muss eine Zahl sein.")
            return

        sale = {
            "id": len(self.data["sales"]) + 1,
            "user": self.current_user,
            "category": f"{parent_category} > {subcategory}",
            "date": date,
            "amount": amount,
            "description": description,
            "buyer": buyer,
        }

        self.data["sales"].append(sale)
        save_data(self.data)
        self.update_dashboard()
        messagebox.showinfo("Erfolg", "Verkauf hinzugefügt.")

    # ------------------------- Dashboard Tab -------------------------
    def create_dashboard_tab(self):
        self.dashboard_tab = ttkb.Frame(self.tabs)
        self.tabs.add(self.dashboard_tab, text="📊 Dashboard")

        ttkb.Label(self.dashboard_tab, text="Dashboard Übersicht", font=("Arial", 16, "bold")).pack(pady=10)

        self.dashboard_tree = ttk.Treeview(
            self.dashboard_tab,
            columns=("Umsatz", "Verkäufe"),
            show="tree headings",
            height=20
        )
        self.dashboard_tree.heading("#0", text="Benutzer / Kategorie")
        self.dashboard_tree.heading("Umsatz", text="Umsatz (€)")
        self.dashboard_tree.heading("Verkäufe", text="Anzahl Verkäufe")
        self.dashboard_tree.pack(fill="both", expand=True, pady=10)

        ttkb.Button(self.dashboard_tab, text="Verkauf löschen", command=self.delete_sale, bootstyle="danger-outline").pack(pady=10)
        ttkb.Button(self.dashboard_tab, text="Diagramm anzeigen", command=self.show_chart, bootstyle="info-outline").pack(pady=10)
        ttkb.Button(self.dashboard_tab, text="Aktualisieren", command=self.update_dashboard, bootstyle="primary-outline").pack(pady=10)

    def update_dashboard(self):
        """Aktualisiert die Verkaufsübersicht im Dashboard."""
        self.dashboard_tree.delete(*self.dashboard_tree.get_children())

        total_sales = 0
        total_revenue = 0

        for user in self.data["users"]:
            user_sales = [sale for sale in self.data["sales"] if sale["user"] == user]
            user_revenue = sum(sale["amount"] for sale in user_sales)

            total_sales += len(user_sales)
            total_revenue += user_revenue

            user_node = self.dashboard_tree.insert("", "end", text=user, values=(f"{user_revenue:.2f} €", len(user_sales)))

            category_totals = {}
            for sale in user_sales:
                category = sale["category"]
                if category not in category_totals:
                    category_totals[category] = {"revenue": 0, "sales": 0}
                category_totals[category]["revenue"] += sale["amount"]
                category_totals[category]["sales"] += 1

            for category, totals in category_totals.items():
                category_node = self.dashboard_tree.insert(
                    user_node, "end", text=category, values=(f"{totals['revenue']:.2f} €", totals["sales"])
                )

                # Einzelne Verkäufe unter der Kategorie auflisten
                for s in [s for s in user_sales if s["category"] == category]:
                    self.dashboard_tree.insert(
                        category_node, "end", text=f"Verkauf #{s['id']}: {s['date']}", values=(f"{s['amount']:.2f} €", 1)
                    )

        self.dashboard_tree.insert("", "end", text="Gesamtübersicht", values=(f"{total_revenue:.2f} €", total_sales))

    def show_chart(self):
        category_totals = {}

        for sale in self.data["sales"]:
            category = sale["category"]
            if category not in category_totals:
                category_totals[category] = 0
            category_totals[category] += sale["amount"]

        categories = list(category_totals.keys())
        revenues = list(category_totals.values())

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(categories, revenues, color="skyblue")
        ax.set_title("Umsätze nach Kategorien")
        ax.set_xlabel("Kategorie")
        ax.set_ylabel("Umsatz (€)")
        plt.xticks(rotation=45)

        chart_window = tk.Toplevel(self.root)
        chart_window.title("Umsätze nach Kategorien")
        canvas = FigureCanvasTkAgg(fig, master=chart_window)
        canvas.get_tk_widget().pack()
        canvas.draw()

    def delete_sale(self):
        selected_item = self.dashboard_tree.selection()
        if not selected_item:
            messagebox.showerror("Fehler", "Bitte einen Verkauf auswählen.")
            return

        sale_text = self.dashboard_tree.item(selected_item, "text")
        if "Verkauf #" in sale_text:
            sale_id = int(sale_text.split("#")[1].split(":")[0])
            self.data["sales"] = [sale for sale in self.data["sales"] if sale["id"] != sale_id]
            save_data(self.data)
            self.update_dashboard()
            messagebox.showinfo("Erfolg", "Verkauf gelöscht.")
        else:
            messagebox.showerror("Fehler", "Bitte einen einzelnen Verkauf auswählen.")

    # ------------------------- NEU: Kategorien verwalten Tab -------------------------
    def create_category_management_tab(self):
        """
        Neuer Tab 'Kategorien verwalten'.
        Erlaubt das Anlegen von Hauptkategorien (Überkategorien) und
        Unterkategorien (mit Preis).
        """
        self.category_tab = ttkb.Frame(self.tabs)
        self.tabs.add(self.category_tab, text="🗂 Kategorien verwalten")

        # Frame: Hauptkategorie anlegen
        parent_frame = ttkb.Labelframe(self.category_tab, text="Neue Hauptkategorie")
        parent_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        ttkb.Label(parent_frame, text="Name der Hauptkategorie:", font=("Arial", 12)).pack(pady=5)
        self.parent_category_entry = ttkb.Entry(parent_frame, font=("Arial", 12))
        self.parent_category_entry.pack(pady=5)

        ttkb.Button(parent_frame, text="Anlegen", command=self.add_parent_category, bootstyle="success-outline").pack(pady=5)

        # Frame: Unterkategorie anlegen
        child_frame = ttkb.Labelframe(self.category_tab, text="Neue Unterkategorie")
        child_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        ttkb.Label(child_frame, text="Hauptkategorie:", font=("Arial", 12)).pack(pady=5)
        self.parent_combo = ttkb.Combobox(child_frame, font=("Arial", 12), values=list(self.data["categories"].keys()))
        self.parent_combo.pack(pady=5)

        ttkb.Label(child_frame, text="Name der Unterkategorie:", font=("Arial", 12)).pack(pady=5)
        self.subcategory_entry = ttkb.Entry(child_frame, font=("Arial", 12))
        self.subcategory_entry.pack(pady=5)

        ttkb.Label(child_frame, text="Preis (Euro):", font=("Arial", 12)).pack(pady=5)
        self.subcategory_price_entry = ttkb.Entry(child_frame, font=("Arial", 12))
        self.subcategory_price_entry.pack(pady=5)

        ttkb.Button(child_frame, text="Unterkategorie hinzufügen", command=self.add_sub_category, bootstyle="info-outline").pack(pady=5)

        # Frame: Liste aller Kategorien anzeigen
        list_frame = ttkb.Labelframe(self.category_tab, text="Aktuelle Kategorien")
        list_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        self.categories_text = tk.Text(list_frame, width=50, height=20)
        self.categories_text.pack(pady=5, padx=5)

        ttkb.Button(list_frame, text="Aktualisieren", command=self.refresh_categories_list, bootstyle="secondary-outline").pack(pady=5)

        # Beim ersten Laden die Übersicht aktualisieren
        self.refresh_categories_list()

    def add_parent_category(self):
        """
        Legt eine neue Hauptkategorie an, falls sie noch nicht existiert.
        """
        new_parent = self.parent_category_entry.get().strip()
        if not new_parent:
            messagebox.showerror("Fehler", "Bitte einen Namen eingeben.")
            return

        # Existiert die Hauptkategorie schon?
        if new_parent in self.data["categories"]:
            messagebox.showerror("Fehler", f"Hauptkategorie '{new_parent}' existiert bereits.")
            return

        # Neue Hauptkategorie anlegen
        self.data["categories"][new_parent] = {"subcategories": {}}
        save_data(self.data)

        messagebox.showinfo("Erfolg", f"Hauptkategorie '{new_parent}' wurde angelegt.")
        self.parent_category_entry.delete(0, tk.END)

        # Combobox und Anzeige aktualisieren
        self.parent_combo["values"] = list(self.data["categories"].keys())
        self.refresh_categories_list()

    def add_sub_category(self):
        """
        Legt zu einer bestehenden Hauptkategorie eine neue Unterkategorie (mit price) an.
        """
        parent_cat = self.parent_combo.get()
        if not parent_cat:
            messagebox.showerror("Fehler", "Bitte Hauptkategorie auswählen.")
            return

        subcat_name = self.subcategory_entry.get().strip()
        price_str = self.subcategory_price_entry.get().strip()

        if not subcat_name:
            messagebox.showerror("Fehler", "Bitte einen Namen für die Unterkategorie eingeben.")
            return

        try:
            price_val = float(price_str)
        except ValueError:
            messagebox.showerror("Fehler", "Preis muss eine Zahl sein.")
            return

        if parent_cat not in self.data["categories"]:
            self.data["categories"][parent_cat] = {"subcategories": {}}

        # Schon vorhanden?
        if subcat_name in self.data["categories"][parent_cat]["subcategories"]:
            messagebox.showerror("Fehler", f"Unterkategorie '{subcat_name}' existiert bereits.")
            return

        # Neue Unterkategorie mit Preis anlegen
        self.data["categories"][parent_cat]["subcategories"][subcat_name] = {"price": price_val}
        save_data(self.data)

        messagebox.showinfo("Erfolg", f"Unterkategorie '{subcat_name}' hinzugefügt.")
        self.subcategory_entry.delete(0, tk.END)
        self.subcategory_price_entry.delete(0, tk.END)

        self.refresh_categories_list()

    def refresh_categories_list(self):
        """
        Zeigt alle Haupt-/Unterkategorien samt Preis in einem Text-Widget an.
        """
        self.categories_text.delete("1.0", tk.END)
        for parent_cat, info in self.data["categories"].items():
            self.categories_text.insert(tk.END, f"** {parent_cat} **\n")
            subcats = info.get("subcategories", {})
            if not subcats:
                self.categories_text.insert(tk.END, "   (Keine Unterkategorien)\n\n")
            else:
                for sub_name, sub_info in subcats.items():
                    price = sub_info.get("price", 0)
                    self.categories_text.insert(tk.END, f"   - {sub_name} (Preis: {price} €)\n")
                self.categories_text.insert(tk.END, "\n")

        # Auch die Combobox im Sales-Tab aktualisieren,
        # damit neue Hauptkategorien direkt auswählbar sind
        self.parent_category_combobox["values"] = list(self.data["categories"].keys())


# ------------------------- Start -------------------------
if __name__ == "__main__":
    try:
        print("Programm gestartet...")
        root = ttkb.Window(themename="litera")
        app = SalesToolApp(root)
        root.mainloop()
    except Exception as e:
        print(f"Ein Fehler ist aufgetreten: {e}")
