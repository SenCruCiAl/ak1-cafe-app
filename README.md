# AK1 Café – Ordering and Table Booking App

A simple desktop front end for a café, written in Python with **Tkinter**.
Customers can browse the menu, add items to a cart, place an order and book a table.
It is a front end only: nothing is saved or sent anywhere.

## Run

```bash
python cafe_app.py
```

Needs Python 3 only. No extra packages to install: the app uses just `tkinter`, `datetime` and `random` from the standard library.

## Built with Tkinter

Tkinter is Python's built-in GUI library. The app uses these parts of it:

| Tkinter part | Used for |
|---|---|
| `tk.Tk` | The main window (`App` class) |
| `tk.Canvas` | Every page; buttons, cards and tiles are drawn on it |
| `create_polygon(..., smooth=True)` | Rounded rectangles for cards and buttons |
| `tag_bind` / `bind` | Clicks, hover, mouse wheel and keyboard scrolling |
| `yview_scroll` + `scrollregion` | Scrollable pages |
| `tk.Entry` + `create_window` | Text boxes placed on a canvas |
| `tk.Label` + `after()` | The short message at the bottom of the window |
| `lift()` | Switching between pages |

## Features

- **Home** – welcome line and the full menu (Coffee, Sandwiches, Cold Drinks, Cakes & Pastries), each item with an “+ Add” button.
- **Cart** – add, remove and change quantities; the cart count shows in the top bar.
- **Order** – Takeaway, At my table or Delivery; Card, UPI or Cash; subtotal, 5% GST, ₹40 delivery fee and total.
- **Reserve** – next 7 dates, 12 time slots (booked ones greyed out), 1–12 guests, name, phone and a note.
- **Checks** – empty cart, missing address, or a booking without name and phone are stopped with a message.
- **Confirmation** – a pop-up with the order or booking details.
- Scroll with the mouse wheel, arrow keys or Page Up / Page Down.

## Code structure

Everything is in `cafe_app.py`.

| Name | Kind | What it does |
|---|---|---|
| `font`, `num`, `serif` | functions | Font tuples for body text, prices and headings |
| `rr_points`, `rrect` | functions | Draw a rounded rectangle on a canvas |
| `MENU`, `ITEMS` | data | Menu as a dict of category → list of `(name, price, description)` |
| `Btn` | class | Rounded button drawn on a canvas |
| `Choice` | class | Group of selectable tiles (service, payment, date, time) |
| `Field` | class | Text box with placeholder text |
| `Page` | class (`tk.Canvas`) | Base page: scrolling, heading, card |
| `HomePage` | class (`Page`) | Intro and menu |
| `OrderPage` | class (`Page`) | Cart, service, payment, totals, `place_order()` |
| `ReservePage` | class (`Page`) | Date, time, guests, details, `confirm()` |
| `App` | class (`tk.Tk`) | Nav bar, page switching, cart dict, `toast()`, `confirm()` pop-up |

## Author

Sidhant Sinha – RA2511026010619
21CSC203P – Advanced Programming Practice
