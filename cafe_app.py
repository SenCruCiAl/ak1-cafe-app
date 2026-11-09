"""
AK1 Café - simple customer-facing cafe interface (frontend only).

Plain Tkinter + the Python standard library only - no extra packages.

Run:  python cafe_app.py
"""

import datetime
import random
import tkinter as tk

# ------------------------------------------------------------------ theme
W, H = 1280, 800
NAV_H = 70
CH = H - NAV_H

BG = "#15100d"
CARD = "#211915"
CARD_HI = "#2b211b"
LINE = "#3a2b22"
INPUT = "#1a1310"
CREAM = "#f3e9df"
MUTED = "#a8988a"
DIM = "#6f6157"
ACCENT = "#c8935f"
ACCENT_HI = "#deac7b"
DARK = "#1a120d"
GREEN = "#8fcf9a"

# Fonts that ship with Windows; Tk falls back to a default font elsewhere.
SERIF = "Georgia"
SANS = "Segoe UI"


def font(size, weight="normal"):
    return (SANS, -size, "bold" if weight in ("semi", "bold") else "normal")


def num(size):
    return (SANS, -round(size * 0.85), "bold")


def serif(size):
    return (SERIF, -int(size * 0.75), "bold")


# ------------------------------------------------------------------ data
MENU = {
    "Coffee": [
        ("Espresso", 120, "A strong single shot"),
        ("Americano", 150, "Espresso with hot water"),
        ("Cappuccino", 190, "Espresso, milk and foam"),
        ("Caramel Latte", 240, "Latte with caramel"),
        ("Caffè Mocha", 230, "Espresso with chocolate"),
        ("Flat White", 210, "Smooth and milky"),
    ],
    "Sandwiches": [
        ("Club Sandwich", 260, "Three layers, herb mayo"),
        ("Grilled Cheese", 220, "Sourdough, three cheeses"),
        ("Bagel & Cream", 180, "Bagel with cream cheese"),
        ("Paneer Wrap", 240, "Grilled paneer, mint chutney"),
        ("Falafel Pita", 230, "Falafel and hummus"),
        ("Egg & Bacon", 250, "On a brioche bun"),
    ],
    "Cold Drinks": [
        ("Brown Sugar Boba", 220, "Milk tea with pearls"),
        ("Mocha Frappé", 250, "Blended iced mocha"),
        ("Iced Americano", 170, "Espresso over ice"),
        ("Virgin Mojito", 190, "Mint, lime and soda"),
        ("Lemon Iced Tea", 150, "Black tea with lemon"),
        ("Berry Smoothie", 230, "Berries, yogurt, honey"),
    ],
    "Cakes & Pastries": [
        ("Butter Croissant", 140, "Flaky and buttery"),
        ("Red Velvet Slice", 210, "With cream cheese frosting"),
        ("Choco Cupcake", 130, "Chocolate with ganache"),
        ("Glazed Donut", 110, "Classic vanilla glaze"),
        ("Celebration Cake", 320, "Vanilla sponge, berries"),
        ("Apple Pie", 190, "Cinnamon apples"),
    ],
}
ITEMS = {it[0]: it for cat in MENU.values() for it in cat}
OWNERS = "Sidhant Sinha  ·  Ritesh Singh Solanki  ·  Aneek Sen"


# ------------------------------------------------------------------ drawing helpers
def rr_points(x0, y0, x1, y1, r):
    r = min(r, (x1 - x0) / 2, (y1 - y0) / 2)
    return [x0 + r, y0, x0 + r, y0, x1 - r, y0, x1 - r, y0, x1, y0, x1, y0 + r,
            x1, y0 + r, x1, y1 - r, x1, y1 - r, x1, y1, x1 - r, y1, x1 - r, y1,
            x0 + r, y1, x0 + r, y1, x0, y1, x0, y1 - r, x0, y1 - r, x0, y0 + r,
            x0, y0 + r, x0, y0]


def rrect(cv, x0, y0, x1, y1, r, **kw):
    return cv.create_polygon(rr_points(x0, y0, x1, y1, r), smooth=True, **kw)


# ------------------------------------------------------------------ widgets
def hover_cursor(cv, tag):
    cv.tag_bind(tag, "<Enter>", lambda e: cv.config(cursor="hand2"), add="+")
    cv.tag_bind(tag, "<Leave>", lambda e: cv.config(cursor=""), add="+")


class Btn:
    STYLES = {
        "solid": (ACCENT, ACCENT_HI, "", DARK),
        "ghost": (BG, CARD_HI, MUTED, CREAM),
        "dark": (CARD_HI, LINE, LINE, CREAM),
    }

    def __init__(self, cv, x, y, w, h, text, cmd, style="solid", r=None, size=14, tags=()):
        fill, hover, outline, fg = self.STYLES[style]
        tag = f"btn{id(self)}"
        T = tuple(tags) + (tag,)
        bg = rrect(cv, x, y, x + w, y + h, h / 2 if r is None else r, fill=fill, outline=outline, width=1, tags=T)
        cv.create_text(x + w / 2, y + h / 2, text=text, fill=fg, font=font(size, "semi"), tags=T)
        cv.tag_bind(tag, "<Enter>", lambda e: cv.itemconfigure(bg, fill=hover))
        cv.tag_bind(tag, "<Leave>", lambda e: cv.itemconfigure(bg, fill=fill))
        cv.tag_bind(tag, "<Button-1>", lambda e: cmd())
        hover_cursor(cv, tag)


class Choice:
    """Row/grid of option tiles; one is selected."""

    def __init__(self, cv, rects, labels, on_change=None, selected=0, disabled=(), r=10, size=13, tags=()):
        self.cv, self.sel, self.on_change, self.disabled = cv, selected, on_change, set(disabled)
        self.tiles = []
        for i, (rc, label) in enumerate(zip(rects, labels)):
            t = f"ch{id(self)}_{i}"
            box = rrect(cv, *rc, r, width=1, tags=tuple(tags) + (t,))
            txt = cv.create_text((rc[0] + rc[2]) / 2, (rc[1] + rc[3]) / 2, text=label, justify="center",
                                 font=font(size, "semi"), tags=tuple(tags) + (t,))
            self.tiles.append((box, txt))
            if i not in self.disabled:
                cv.tag_bind(t, "<Button-1>", lambda e, i=i: self.select(i))
                hover_cursor(cv, t)
        self._paint()

    def _paint(self):
        for i, (box, txt) in enumerate(self.tiles):
            on = i == self.sel
            self.cv.itemconfigure(box, fill=ACCENT if on else CARD_HI, outline="" if on else LINE)
            self.cv.itemconfigure(txt, fill=DIM if i in self.disabled else (DARK if on else CREAM))

    def select(self, i):
        self.sel = i
        self._paint()
        if self.on_change:
            self.on_change(i)


class Field:
    """Text input with placeholder."""

    def __init__(self, cv, x, y, w, h, placeholder, tags=()):
        self.ph = placeholder
        self.frame = tk.Frame(cv, bg=INPUT, highlightthickness=1, highlightbackground=LINE)
        self.e = tk.Entry(self.frame, bg=INPUT, fg=DIM, insertbackground=CREAM, relief="flat", bd=0,
                          font=font(14), highlightthickness=0)
        self.e.pack(fill="both", expand=True, padx=12, pady=6)
        self.e.insert(0, placeholder)
        self.empty = True
        self.e.bind("<FocusIn>", self._in)
        self.e.bind("<FocusOut>", self._out)
        cv.create_window(x, y, window=self.frame, width=w, height=h, anchor="nw", tags=tags)

    def _in(self, e):
        self.frame.config(highlightbackground=ACCENT)
        if self.empty:
            self.e.delete(0, "end")
            self.e.config(fg=CREAM)
            self.empty = False

    def _out(self, e):
        self.frame.config(highlightbackground=LINE)
        if not self.e.get().strip():
            self.e.delete(0, "end")
            self.e.insert(0, self.ph)
            self.e.config(fg=DIM)
            self.empty = True

    def value(self):
        return "" if self.empty else self.e.get().strip()

    def destroy(self):
        self.frame.destroy()


# ------------------------------------------------------------------ pages
class Page(tk.Canvas):
    def __init__(self, app, content_h=CH):
        super().__init__(app, width=W, height=CH, bg=BG, highlightthickness=0, bd=0, yscrollincrement=20)
        self.app = app
        self.content_h = content_h
        self.config(scrollregion=(0, 0, W, max(CH, content_h)))

    def wheel(self, delta):
        if self.content_h > CH:
            self.yview_scroll(-3 if delta > 0 else 3, "units")

    def on_show(self):
        pass

    def heading(self, title, sub):
        self.create_text(70, 50, text=title, anchor="w", font=serif(42), fill=CREAM)
        self.create_text(72, 88, text=sub, anchor="w", font=font(14), fill=MUTED)

    def card(self, x0, y0, x1, y1, title=None):
        rrect(self, x0, y0, x1, y1, 18, fill=CARD, outline=LINE, width=1)
        if title:
            self.create_text(x0 + 24, y0 + 32, text=title, anchor="w", font=serif(24), fill=CREAM)


MENU_Y = 330
CARD_W, CARD_H, GAP = 366, 110, 21
CAT_H = 50 + 2 * (CARD_H + 16) + 34
HOME_H = MENU_Y + 70 + len(MENU) * CAT_H + 120


class HomePage(Page):
    def __init__(self, app):
        super().__init__(app, HOME_H)
        a = app
        # ---------- intro ----------
        self.create_text(72, 70, text="WELCOME TO AK1 CAFÉ", anchor="w", font=font(13, "semi"), fill=ACCENT)
        self.create_text(68, 130, text="Good coffee, made fresh.", anchor="w", font=serif(68), fill=CREAM)
        self.create_text(72, 192, text="Coffee, sandwiches, cold drinks and cakes. Open daily, 8 AM – 11 PM.",
                         anchor="w", font=font(15), fill=MUTED)
        Btn(self, 72, 232, 150, 48, "Order now", lambda: a.show("Order"))
        Btn(self, 236, 232, 160, 48, "Book a table", lambda: a.show("Reserve"), style="ghost")

        # ---------- menu ----------
        self.create_line(70, MENU_Y - 20, 1210, MENU_Y - 20, fill=LINE)
        self.create_text(68, MENU_Y + 24, text="Menu", anchor="w", font=serif(44), fill=CREAM)
        y = MENU_Y + 70
        for cat, items in MENU.items():
            self.create_text(70, y + 20, text=cat, anchor="w", font=serif(26), fill=ACCENT)
            for i, (nm, price, desc) in enumerate(items):
                x0 = 70 + (i % 3) * (CARD_W + GAP)
                y0 = y + 50 + (i // 3) * (CARD_H + 16)
                self.menu_card(x0, y0, nm, price, desc)
            y += CAT_H

        # ---------- footer ----------
        self.create_line(70, y + 10, 1210, y + 10, fill=LINE)
        self.create_text(640, y + 44, text="AK1 Café  ·  Open daily 8 AM – 11 PM", font=font(13), fill=MUTED)
        self.create_text(640, y + 70, text=f"Owners: {OWNERS}", font=font(12), fill=DIM)

    def menu_card(self, x0, y0, nm, price, desc):
        rrect(self, x0, y0, x0 + CARD_W, y0 + CARD_H, 14, fill=CARD, outline=LINE, width=1)
        tx = x0 + 22
        self.create_text(tx, y0 + 28, text=nm, anchor="w", font=serif(20), fill=CREAM)
        self.create_text(tx, y0 + 52, text=desc, anchor="w", font=font(12), fill=MUTED)
        self.create_text(tx, y0 + 84, text=f"₹{price}", anchor="w", font=num(22), fill=CREAM)
        Btn(self, x0 + CARD_W - 86, y0 + CARD_H - 44, 72, 32, "+ Add", lambda: self.app.add_to_cart(nm),
            r=10, size=12)

    def scroll_to_menu(self):
        self.yview_moveto((MENU_Y - 20) / HOME_H)


class OrderPage(Page):
    MODES = ["Takeaway", "At my table", "Delivery"]
    PAYS = ["Card", "UPI", "Cash"]
    PICKUP = ["ASAP", "15 min", "30 min", "1 hour"]
    TABLES = [f"T{k}" for k in range(1, 9)]

    def __init__(self, app):
        super().__init__(app)
        self.heading("Your order", "Check your items, choose how you want them, then pay.")
        self.mode, self.pay, self.detail_field, self.detail_choice = 0, 0, None, None

        # cart
        self.card(70, 120, 730, 470, "Cart")
        self.count_txt = self.create_text(706, 152, anchor="e", font=font(13), fill=MUTED)
        self.list = tk.Canvas(self, width=636, height=280, bg=CARD, highlightthickness=0, bd=0,
                              yscrollincrement=16)
        self.create_window(82, 176, window=self.list, anchor="nw")
        self.list.bind("<MouseWheel>", lambda e: self.list.yview_scroll(-1 if e.delta > 0 else 1, "units"))

        # how
        self.card(70, 490, 730, 700, "How do you want it?")
        rects = [(94 + i * 210, 546, 94 + i * 210 + 196, 592) for i in range(3)]
        Choice(self, rects, self.MODES, on_change=self._mode_changed, size=14)

        # payment
        self.card(760, 120, 1210, 700, "Payment")
        rects = [(784 + i * 136, 178, 784 + i * 136 + 126, 224) for i in range(3)]
        Choice(self, rects, self.PAYS, on_change=lambda i: setattr(self, "pay", i), size=14)
        self.create_line(784, 250, 1186, 250, fill=LINE)
        self.rows = {}
        for i, label in enumerate(("Subtotal", "GST (5%)", "Delivery")):
            y = 282 + i * 34
            self.create_text(784, y, text=label, anchor="w", font=font(14), fill=MUTED)
            self.rows[label] = self.create_text(1186, y, text="₹0", anchor="e", font=font(14, "semi"), fill=CREAM)
        self.create_line(784, 382, 1186, 382, fill=LINE)
        self.create_text(784, 420, text="Total", anchor="w", font=serif(28), fill=CREAM)
        self.total_txt = self.create_text(1186, 420, text="₹0", anchor="e", font=num(36), fill=ACCENT)
        Btn(self, 784, 620, 402, 52, "Place order", self.place_order, size=16)
        self._mode_changed(0)

    def _mode_changed(self, i):
        self.mode = i
        self.delete("detail")
        if self.detail_field:
            self.detail_field.destroy()
            self.detail_field = None
        self.detail_choice = None
        y = 610
        label = ("Pickup", "Table", "Address")[i]
        self.create_text(94, y + 22, text=label, anchor="w", font=font(13, "semi"), fill=MUTED, tags="detail")
        if i == 2:
            self.detail_field = Field(self, 180, y, 526, 44, "House no., street, area", tags=("detail",))
        else:
            opts = self.PICKUP if i == 0 else self.TABLES
            step = 132 if i == 0 else 66
            rects = [(180 + k * step, y, 180 + k * step + step - 10, y + 44) for k in range(len(opts))]
            self.detail_choice = Choice(self, rects, opts, tags=("detail",))
        self.update_totals()

    def on_show(self):
        self.refresh()

    def refresh(self):
        cv = self.list
        cv.delete("all")
        cart = self.app.cart
        n = sum(cart.values())
        self.itemconfigure(self.count_txt, text=f"{n} item{'s' if n != 1 else ''}")
        if not cart:
            cv.create_text(318, 110, text="Your cart is empty", font=serif(24), fill=CREAM)
            cv.create_text(318, 142, text="Add something from the menu.", font=font(13), fill=MUTED)
            Btn(cv, 253, 170, 130, 40, "See menu", self.app.open_menu, size=13)
            cv.config(scrollregion=(0, 0, 636, 280))
        else:
            for r, (name, qty) in enumerate(cart.items()):
                self._row(cv, r, name, qty)
            cv.config(scrollregion=(0, 0, 636, max(280, len(cart) * 62)))
        self.update_totals()

    def _row(self, cv, r, name, qty):
        nm, price, desc = ITEMS[name]
        y = r * 62
        rrect(cv, 4, y + 4, 632, y + 56, 12, fill=CARD_HI, outline="")
        cv.create_text(22, y + 21, text=nm, anchor="w", font=serif(19), fill=CREAM)
        cv.create_text(22, y + 41, text=f"₹{price} each", anchor="w", font=font(12), fill=MUTED)
        for sym, dx, d in (("−", 360, -1), ("+", 444, 1)):
            st = f"row{r}{sym}"
            cv.create_oval(dx - 15, y + 15, dx + 15, y + 45, fill=LINE, outline="", tags=st)
            cv.create_text(dx, y + 29, text=sym, font=font(17, "bold"), fill=CREAM, tags=st)
            cv.tag_bind(st, "<Button-1>", lambda e, d=d: self.app.change_qty(name, d))
            hover_cursor(cv, st)
        cv.create_text(402, y + 30, text=str(qty), font=font(16, "bold"), fill=CREAM)
        cv.create_text(568, y + 30, text=f"₹{price * qty}", anchor="e", font=num(22), fill=ACCENT)
        rm = f"row{r}x"
        cv.create_text(606, y + 30, text="✕", font=font(14, "bold"), fill=DIM, tags=rm)
        cv.tag_bind(rm, "<Button-1>", lambda e: self.app.change_qty(name, -999))
        hover_cursor(cv, rm)

    def totals(self):
        sub = sum(ITEMS[n][1] * q for n, q in self.app.cart.items())
        gst = round(sub * 0.05)
        fee = 40 if (self.mode == 2 and sub) else 0
        return sub, gst, fee, sub + gst + fee

    def update_totals(self):
        sub, gst, fee, total = self.totals()
        self.itemconfigure(self.rows["Subtotal"], text=f"₹{sub}")
        self.itemconfigure(self.rows["GST (5%)"], text=f"₹{gst}")
        self.itemconfigure(self.rows["Delivery"], text=f"₹{fee}" if self.mode == 2 else "—")
        self.itemconfigure(self.total_txt, text=f"₹{total}")

    def place_order(self):
        if not self.app.cart:
            self.app.toast("Your cart is empty")
            return
        if self.mode == 2 and not self.detail_field.value():
            self.app.toast("Please add a delivery address")
            return
        total = self.totals()[3]
        extra = ""
        if self.detail_choice:
            opts = self.PICKUP if self.mode == 0 else self.TABLES
            extra = f"  ·  {opts[self.detail_choice.sel]}"
        no = f"AK1-{random.randint(1000, 9999)}"
        self.app.confirm("Order placed", f"Order #{no}",
                         f"{self.MODES[self.mode]}{extra}  ·  {self.PAYS[self.pay]}  ·  Total ₹{total}",
                         after=self.app.clear_cart)


class ReservePage(Page):
    TIMES = ["8:00 AM", "9:30 AM", "11:00 AM", "12:30 PM", "2:00 PM", "3:30 PM",
             "5:00 PM", "6:00 PM", "7:00 PM", "8:00 PM", "9:00 PM", "10:00 PM"]
    BOOKED = {3, 8}

    def __init__(self, app):
        super().__init__(app)
        self.heading("Book a table", "Pick a date and time. We hold tables for 15 minutes.")
        self.guests = 2
        today = datetime.date.today()
        self.dates = [today + datetime.timedelta(days=i) for i in range(7)]

        self.card(70, 120, 760, 700)
        self.create_text(94, 156, text="Date", anchor="w", font=serif(22), fill=CREAM)
        rects = [(94 + i * 90, 180, 94 + i * 90 + 82, 246) for i in range(7)]
        labels = [("Today" if i == 0 else d.strftime("%a")) + f"\n{d.day}" for i, d in enumerate(self.dates)]
        self.date_choice = Choice(self, rects, labels, on_change=lambda i: self.update_summary(), size=14)

        self.create_text(94, 290, text="Time", anchor="w", font=serif(22), fill=CREAM)
        self.create_text(736, 290, text="Grey = booked", anchor="e", font=font(12), fill=DIM)
        rects = [(94 + (i % 4) * 160, 314 + (i // 4) * 56, 94 + (i % 4) * 160 + 148, 314 + (i // 4) * 56 + 44)
                 for i in range(12)]
        self.time_choice = Choice(self, rects, self.TIMES, on_change=lambda i: self.update_summary(), selected=7,
                                  disabled=self.BOOKED, size=14)

        self.create_text(94, 520, text="Guests", anchor="w", font=serif(22), fill=CREAM)
        Btn(self, 94, 546, 44, 44, "−", lambda: self.set_guests(-1), style="dark", size=18)
        self.guest_txt = self.create_text(170, 568, text="2", font=font(18, "bold"), fill=CREAM)
        Btn(self, 202, 546, 44, 44, "+", lambda: self.set_guests(1), style="dark", size=18)

        self.card(790, 120, 1210, 700, "Your details")
        self.name = Field(self, 814, 176, 372, 46, "Full name")
        self.phone = Field(self, 814, 236, 372, 46, "Phone number")
        self.note = Field(self, 814, 296, 372, 46, "Any requests? (optional)")
        self.create_line(814, 380, 1186, 380, fill=LINE)
        self.summary = self.create_text(814, 420, anchor="w", font=font(14, "semi"), fill=ACCENT, width=372)
        Btn(self, 814, 620, 372, 52, "Confirm booking", self.confirm, size=16)
        self.update_summary()

    def set_guests(self, d):
        self.guests = max(1, min(12, self.guests + d))
        self.itemconfigure(self.guest_txt, text=str(self.guests))
        self.update_summary()

    def summary_text(self):
        d = self.dates[self.date_choice.sel]
        t = self.TIMES[self.time_choice.sel]
        return f"{d.strftime('%a, %d %b')}  ·  {t}  ·  {self.guests} guest{'s' if self.guests > 1 else ''}"

    def update_summary(self):
        self.itemconfigure(self.summary, text=self.summary_text())

    def confirm(self):
        if not self.name.value() or not self.phone.value():
            self.app.toast("Please add your name and phone number")
            return
        self.app.confirm("Table booked", f"See you soon, {self.name.value().split()[0]}", self.summary_text())


# ------------------------------------------------------------------ app
class App(tk.Tk):
    TABS = ["Home", "Order", "Reserve"]

    def __init__(self):
        super().__init__()
        self.title("AK1 Café")
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{W}x{H}+{max(0, (sw - W) // 2)}+{max(0, (sh - H) // 2 - 30)}")
        self.resizable(False, False)
        self.configure(bg=BG)
        self.cart = {}
        self.modal = None
        self.toast_lbl = None

        self._build_nav()
        self.pages = {"Home": HomePage(self), "Order": OrderPage(self), "Reserve": ReservePage(self)}
        for p in self.pages.values():
            p.place(x=0, y=NAV_H)
        self.current = "Order"
        self.show("Home")
        self.pages["Order"].refresh()
        self.bind_all("<MouseWheel>", self._wheel)
        for key, d in (("<Next>", -360), ("<Prior>", 360), ("<Down>", -120), ("<Up>", 120)):
            self.bind(key, lambda e, d=d: self._wheel_delta(d))

    def _wheel(self, e):
        if e.widget is not self.pages["Order"].list:     # the cart list scrolls itself
            self._wheel_delta(e.delta)

    def _wheel_delta(self, d):
        if not self.modal and not isinstance(self.focus_get(), tk.Entry):
            self.pages[self.current].wheel(d)

    # ---------- nav ----------
    def _build_nav(self):
        nv = self.nav = tk.Canvas(self, width=W, height=NAV_H, highlightthickness=0, bd=0, bg=BG)
        nv.place(x=0, y=0)
        nv.create_line(0, NAV_H - 1, W, NAV_H - 1, fill=LINE)
        nv.create_text(70, NAV_H / 2, text="AK1 Café", anchor="w", font=serif(32), fill=CREAM, tags="logo")
        nv.tag_bind("logo", "<Button-1>", lambda e: self.show("Home"))
        hover_cursor(nv, "logo")

        self.tab_items = {}
        x = 520
        for name in self.TABS:
            t = nv.create_text(x, NAV_H / 2, text=name, font=font(15, "semi"), fill=MUTED, tags=f"tab_{name}")
            self.tab_items[name] = t
            nv.tag_bind(f"tab_{name}", "<Button-1>", lambda e, n=name: self.show(n))
            hover_cursor(nv, f"tab_{name}")
            x += 120
        self.tab_bar = nv.create_line(0, 0, 0, 0, fill=ACCENT, width=2)

        rrect(nv, 1090, 17, 1210, 53, 18, fill=CARD_HI, outline=LINE, tags="cart")
        self.cart_txt = nv.create_text(1150, 35, text="Cart  0", font=font(14, "semi"), fill=CREAM, tags="cart")
        nv.tag_bind("cart", "<Button-1>", lambda e: self.show("Order"))
        hover_cursor(nv, "cart")

    def show(self, name):
        self.close_modal()
        if name == self.current:
            return
        self.current = name
        page = self.pages[name]
        page.on_show()
        tk.Misc.lift(page)
        for n, item in self.tab_items.items():
            self.nav.itemconfigure(item, fill=CREAM if n == name else MUTED)
        x0, _, x1, _ = self.nav.bbox(self.tab_items[name])
        self.nav.coords(self.tab_bar, x0, NAV_H - 14, x1, NAV_H - 14)

    def open_menu(self):
        self.show("Home")
        self.pages["Home"].scroll_to_menu()

    # ---------- cart ----------
    def add_to_cart(self, name):
        self.cart[name] = self.cart.get(name, 0) + 1
        self._cart_changed()
        self.toast(f"Added {name}")

    def change_qty(self, name, d):
        q = self.cart.get(name, 0) + d
        if q <= 0:
            self.cart.pop(name, None)
        else:
            self.cart[name] = q
        self._cart_changed()

    def clear_cart(self):
        self.cart.clear()
        self._cart_changed()

    def _cart_changed(self):
        self.nav.itemconfigure(self.cart_txt, text=f"Cart  {sum(self.cart.values())}")
        self.pages["Order"].refresh()

    # ---------- toast ----------
    def toast(self, text):
        if self.toast_lbl:
            self.toast_lbl.destroy()
        lbl = self.toast_lbl = tk.Label(self, text=text, bg=CARD_HI, fg=CREAM, font=font(14, "semi"),
                                        padx=22, pady=10, highlightthickness=1, highlightbackground=ACCENT)
        lbl.place(relx=0.5, y=H - 30, anchor="s")
        self.after(1800, lambda: lbl.winfo_exists() and lbl.destroy())

    # ---------- confirmation popup ----------
    def confirm(self, title, line1, details, after=None):
        self.close_modal()
        cv = self.modal = tk.Canvas(self, width=W, height=H, bg="#0c0907", highlightthickness=0, bd=0)
        cv.place(x=0, y=0)
        pw, ph = 480, 320
        px, py = (W - pw) // 2, (H - ph) // 2
        rrect(cv, px, py, px + pw, py + ph, 22, fill=CARD, outline=LINE, width=1)
        cx = px + pw / 2
        cv.create_text(cx, py + 64, text="✓", font=font(40, "bold"), fill=GREEN)
        cv.create_text(cx, py + 124, text=title, font=serif(34), fill=CREAM)
        cv.create_text(cx, py + 164, text=line1, font=font(15, "semi"), fill=ACCENT)
        cv.create_text(cx, py + 200, text=details, font=font(13), fill=MUTED, justify="center", width=420)

        def done():
            self.close_modal()
            if after:
                after()
        Btn(cv, cx - 80, py + ph - 72, 160, 46, "Done", done, size=15)
        self.bind("<Escape>", lambda e: done())

    def close_modal(self):
        if self.modal:
            self.modal.destroy()
            self.modal = None
            self.unbind("<Escape>")


if __name__ == "__main__":
    App().mainloop()
