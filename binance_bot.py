from binance.client import Client
import logging
import os
from dotenv import load_dotenv
import tkinter as tk
from tkinter import ttk, messagebox

load_dotenv()

binance_key = os.getenv("Api_Key")
binance_secret = os.getenv("Api_Secret")

class BinanceBot:
    def __init__(self, api_key, api_secret):
        self.client = Client(api_key, api_secret)
        self.client.FUTURES_URL = 'https://testnet.binancefuture.com/fapi'

    def place_order(self, symbol, side, order_type, quantity, price=None, stop_price=None):
        valid_sides = {'BUY', 'SELL'}
        valid_types = {'MARKET', 'LIMIT', 'STOP_LIMIT'}

        if side not in valid_sides:
            print("Invalid side. Choose BUY or SELL.")
            return

        if order_type not in valid_types:
            print("Invalid order type. Choose MARKET, LIMIT OR STOP_LIMIT.")
            return

        try:
            if order_type == 'MARKET':
                order = self.client.futures_create_order(
                    symbol=symbol,
                    side=side,
                    type='MARKET',
                    quantity=quantity
                )
            elif order_type == 'LIMIT':
                order = self.client.futures_create_order(
                    symbol=symbol,
                    side=side,
                    type='LIMIT',
                    timeInForce='GTC',
                    quantity=quantity,
                    price=price
                )
            elif order_type == 'STOP_LIMIT':
                order = self.client.futures_create_order(
                    symbol=symbol,
                    side=side,
                    type='STOP',
                    timeInForce='GTC',
                    quantity=quantity,
                    price=price,
                    stopPrice=stop_price
                )
            logging.info(f"Placing order: {symbol} {side} {order_type} {quantity} {price} {stop_price}")
            print("\n✅ Order Summary:")
            print(f"  ID: {order['orderId']}")
            print(f"  Symbol: {order['symbol']}")
            print(f"  Type: {order['type']}")
            print(f"  Side: {order['side']}")
            print(f"  Quantity: {order['origQty']}")
            print(f"  Status: {order['status']}\n")
            if 'price' in order and float(order['price']) > 0:
                print(f"  Limit Price: {order['price']}")
            if 'stopPrice' in order and float(order.get('stopPrice', 0)) > 0:
                print(f"  Stop Price: {order['stopPrice']}")
            return order
        except Exception as e:
            logging.error(f"Error placing order: {e}")
            print("Error placing order:", e)

if __name__ == "__main__":
    logging.basicConfig(
        filename="bot.log",
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    bot = BinanceBot(binance_key, binance_secret)

    root = tk.Tk()
    root.title("Binance Futures Order Bot")
    root.geometry("400x350")

    default_font = ("Segoe UI", 10)

    def update_fields(event=None):
        order_type = type_var.get()
        if order_type == "MARKET":
            price_entry.configure(state='disabled')
            stop_price_entry.configure(state='disabled')
        elif order_type == "LIMIT":
            price_entry.configure(state='normal')
            stop_price_entry.configure(state='disabled')
        elif order_type == "STOP_LIMIT":
            price_entry.configure(state='normal')
            stop_price_entry.configure(state='normal')

    def submit_order():
        symbol = symbol_entry.get().upper()
        side = side_var.get()
        order_type = type_var.get()
        quantity = quantity_entry.get()

        if not symbol or not quantity:
            messagebox.showerror("Error", "Please fill in all required fields.")
            return

        quantity = float(quantity)
        price = None
        stop_price = None

        result_label.config(fg="green")

        try:
            if order_type == "LIMIT":
                price = float(price_entry.get())
            elif order_type == "STOP_LIMIT":
                stop_price = float(stop_price_entry.get())
                price = float(price_entry.get())

            order = bot.place_order(symbol, side, order_type, quantity, price, stop_price)

            summary = (
                f"✅ Order Summary:\n\n"
                f"ID: {order['orderId']}\n"
                f"Symbol: {order['symbol']}\n"
                f"Type: {order['type']}\n"
                f"Side: {order['side']}\n"
                f"Quantity: {order['origQty']}\n"
                f"Status: {order['status']}\n"
            )

            if 'price' in order and float(order['price']) > 0:
                summary += f"Limit Price: {order['price']}\n"

            if 'stopPrice' in order and float(order.get('stopPrice', 0)) > 0:
                summary += f"Stop Price: {order['stopPrice']}\n"

            messagebox.showinfo("Order Placed", summary)
            result_label.config(text=f"{order_type} order placed successfully.")
            return order
        except Exception as e:
            messagebox.showerror("Error", str(e))
            result_label.config(text="Order failed.", fg="red")

    header = tk.Label(root, text="Place Binance Futures Order", font=("Segoe UI", 14, "bold"))
    header.grid(row=0, column=0, columnspan=2, pady=(10, 20))

    tk.Label(root, text="Symbol", font=default_font).grid(row=1, column=0, sticky="e", padx=10, pady=5)
    symbol_entry = tk.Entry(root, font=default_font)
    symbol_entry.grid(row=1, column=1, sticky="we", padx=10, pady=5)

    tk.Label(root, text="Side", font=default_font).grid(row=2, column=0, sticky="e", padx=10, pady=5)
    side_var = ttk.Combobox(root, values=["BUY", "SELL"], font=default_font, state="readonly")
    side_var.grid(row=2, column=1, sticky="we", padx=10, pady=5)
    side_var.current(0)

    tk.Label(root, text="Order Type", font=default_font).grid(row=3, column=0, sticky="e", padx=10, pady=5)
    type_var = ttk.Combobox(root, values=["MARKET", "LIMIT", "STOP_LIMIT"], font=default_font, state="readonly")
    type_var.grid(row=3, column=1, sticky="we", padx=10, pady=5)
    type_var.current(0)

    tk.Label(root, text="Quantity", font=default_font).grid(row=4, column=0, sticky="e", padx=10, pady=5)
    quantity_entry = tk.Entry(root, font=default_font)
    quantity_entry.grid(row=4, column=1, sticky="we", padx=10, pady=5)

    tk.Label(root, text="Limit Price", font=default_font).grid(row=5, column=0, sticky="e", padx=10, pady=5)
    price_entry = tk.Entry(root, font=default_font)
    price_entry.grid(row=5, column=1, sticky="we", padx=10, pady=5)

    tk.Label(root, text="Stop Price", font=default_font).grid(row=6, column=0, sticky="e", padx=10, pady=5)
    stop_price_entry = tk.Entry(root, font=default_font)
    stop_price_entry.grid(row=6, column=1, sticky="we", padx=10, pady=5)

    place_order_btn = tk.Button(root, text="Place Order", command=submit_order, font=default_font, bg="#4CAF50", fg="white")
    place_order_btn.grid(row=7, column=0, columnspan=2, pady=(15, 10), ipadx=10, ipady=5)

    result_label = tk.Label(root, text="", fg="green", font=default_font)
    result_label.grid(row=8, column=0, columnspan=2, pady=5)

    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=3)

    type_var.bind("<<ComboboxSelected>>", update_fields)
    update_fields()

    root.mainloop()
