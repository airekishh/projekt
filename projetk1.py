import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class OverBudgetException(Exception):
    pass

class PaymentStrategy:
    def pay(self, amount):
        pass

class CreditCardPayment(PaymentStrategy):
    def pay(self, amount):
        return f"Płacę {amount} zł kartą"

class CashPayment(PaymentStrategy):
    def pay(self, amount):
        return f"Płacę {amount} zł gotówką"

class Transport:
    def __init__(self, price):
        self.price = price
        self.mode = "Unknown"       #atrybut

class Flight(Transport):
    def __init__(self, price, airline, seat):
        super().__init__(price)
        self.airline = airline
        self.seat = seat
        self.mode = "Flight"        #nadpisanie atrybutu

class Hotel:
    def __init__(self, name, price):
        self.price = price
        self.name = name

    def get_price(self):
        return self.price

    def set_price(self, price):
        if price < 0:
            raise ValueError("Cena nie może być ujemna")
        self.price = price

class Trip:
    def __init__(self, destination, budget):
        self.destination = destination
        self.budget = budget
        self.transport = None
        self.hotel = None
        self.departure_date = None
        self.return_date = None

    @classmethod
    def from_dict(cls, data_dict):
        trip = cls(data_dict.get("destination", ""), data_dict.get("budget", 0))
        trip.departure_date = data_dict.get("departure_date")
        trip.return_date = data_dict.get("return_date")
        return trip

    def total_cost(self):
        total = 0
        if self.transport:
            total += self.transport.price
        if self.hotel:
            total += self.hotel.get_price()
        return total

    def confirm(self):
        if self.total_cost() > self.budget:
            raise OverBudgetException("Budżet przekroczony!")

#template method i builder
class TripBuilderTemplate:
    def build_trip(self):
        self.choose_destination()

    def choose_destination(self): raise NotImplementedError   #metoda
    def choose_transport(self): raise NotImplementedError
    def choose_hotel(self): raise NotImplementedError
    def confirm_trip(self): raise NotImplementedError

class TravelPlannerApp(tk.Tk, TripBuilderTemplate):
    def __init__(self):
        super().__init__()
        self.budget = 2000
        self.trip = Trip("", self.budget)

        self.title("Travel Planner")
        self.geometry("400x500")

        self.destination = tk.StringVar()
        self.departure = tk.StringVar()
        self.return_date = tk.StringVar()
        self.airline = tk.StringVar()
        self.seat = tk.StringVar()
        self.hotel_choice = tk.StringVar()
        self.selected_payment = tk.StringVar()

        self.airlines = {"LOT": 800, "Ryanair": 600, "WizzAir": 700}
        self.hotels = {"Hotel A": 600, "Hotel B": 800, "Hotel C": 1000}

        self.budget_label = ttk.Label(self, text=f"Budżet: {self.budget} zł", font=("Arial", 14))
        self.budget_label.pack(pady=5)

        self.build_trip()

    def clear_frame(self):
        for widget in self.winfo_children():
            if widget != self.budget_label:
                widget.destroy()

    def update_budget_label(self):
        self.budget_label.config(text=f"Budżet: {self.budget} zł")

    def choose_destination(self):       #nadpisanie metody
        self.clear_frame()
        frame = ttk.Frame(self)
        frame.pack(expand=True)

        ttk.Label(frame, text="Wybierz miejsce docelowe:").pack(pady=5)
        dest_combo = ttk.Combobox(frame, textvariable=self.destination, values=["Paryż", "Rzym", "Londyn"], state="readonly")
        dest_combo.pack()

        ttk.Label(frame, text="Data wylotu (YYYY-MM-DD):").pack(pady=5)
        ttk.Entry(frame, textvariable=self.departure).pack()

        ttk.Label(frame, text="Data powrotu (YYYY-MM-DD):").pack(pady=5)
        ttk.Entry(frame, textvariable=self.return_date).pack()

        ttk.Button(frame, text="Dalej", command=self.validate_destination).pack(pady=20)

    def validate_destination(self):
        if not self.destination.get():
            messagebox.showerror("Błąd", "Wybierz miejsce docelowe.")
            return
        if not self.departure.get() or not self.return_date.get():
            messagebox.showerror("Błąd", "Wprowadź daty wylotu i powrotu.")
            return
        if not self.is_valid_date_format(self.departure.get()) or not self.is_valid_date_format(self.return_date.get()):
            messagebox.showerror("Błąd formatu", "Wprowadź daty w formacie YYYY-MM-DD.")
            return
        try:
            departure_date = datetime.strptime(self.departure.get(), "%Y-%m-%d").date()
            return_date = datetime.strptime(self.return_date.get(), "%Y-%m-%d").date()
            if return_date < departure_date:
                messagebox.showerror("Błąd daty", "Data powrotu nie może być wcześniejsza niż data wylotu.")
                return
        except ValueError:
            messagebox.showerror("Błąd", "Nieprawidłowa data.")
            return
        self.choose_transport()

    def choose_transport(self):
        self.clear_frame()
        frame = ttk.Frame(self)
        frame.pack(expand=True)

        ttk.Label(frame, text="Wybierz linię lotniczą:").pack(pady=5)
        airline_combo = ttk.Combobox(frame, textvariable=self.airline, values=list(self.airlines.keys()), state="readonly")
        airline_combo.pack()

        ttk.Label(frame, text="Wybierz miejsce w samolocie:").pack(pady=5)
        seat_combo = ttk.Combobox(frame, textvariable=self.seat, values=["Okno", "Środek", "Przejście"], state="readonly")
        seat_combo.pack()

        self.flight_price_label = ttk.Label(frame, text="Cena lotu: -")
        self.flight_price_label.pack(pady=5)

        airline_combo.bind("<<ComboboxSelected>>", lambda e: self.update_flight_price())
        seat_combo.bind("<<ComboboxSelected>>", lambda e: self.update_flight_price())

        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Wróć", command=self.choose_destination).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Dalej", command=self.validate_transport).grid(row=0, column=1, padx=5)

    def update_flight_price(self):
        airline = self.airline.get()
        price = self.airlines.get(airline, "-")
        self.flight_price_label.config(text=f"Cena lotu: {price} zł")

    def validate_transport(self):
        if not self.airline.get():
            messagebox.showerror("Błąd", "Wybierz linię lotniczą.")
            return
        if not self.seat.get():
            messagebox.showerror("Błąd", "Wybierz miejsce w samolocie.")
            return
        self.choose_hotel()

    def choose_hotel(self):
        self.clear_frame()
        frame = ttk.Frame(self)
        frame.pack(expand=True)

        ttk.Label(frame, text="Wybierz hotel:").pack(pady=5)
        hotel_combo = ttk.Combobox(frame, textvariable=self.hotel_choice, values=list(self.hotels.keys()), state="readonly")
        hotel_combo.pack()

        ttk.Label(frame, text="Metoda płatności:").pack(pady=5)
        payment_combo = ttk.Combobox(frame, textvariable=self.selected_payment, values=["Karta", "Gotówka"], state="readonly")
        payment_combo.pack()

        self.total_price_label = ttk.Label(frame, text="Cena całkowita: -")
        self.total_price_label.pack(pady=5)

        hotel_combo.bind("<<ComboboxSelected>>", lambda e: self.update_total_price())
        payment_combo.bind("<<ComboboxSelected>>", lambda e: self.update_total_price())

        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Anuluj", command=self.choose_destination).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Wróć", command=self.choose_transport).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Zaplanuj podróż", command=self.confirm_trip).grid(row=0, column=2, padx=5)

    def update_total_price(self):
        hotel_name = self.hotel_choice.get()
        hotel_price = self.hotels.get(hotel_name, 0)
        flight_price = self.airlines.get(self.airline.get(), 0)
        total = flight_price + hotel_price
        self.total_price_label.config(text=f"Cena całkowita: {total} zł")

    def confirm_trip(self):
        self.trip.destination = self.destination.get()
        self.trip.departure_date = self.departure.get()
        self.trip.return_date = self.return_date.get()

        flight_price = self.airlines.get(self.airline.get(), 0)
        self.trip.transport = Flight(price=flight_price, airline=self.airline.get(), seat=self.seat.get())

        hotel_price = self.hotels.get(self.hotel_choice.get(), 0)
        hotel = Hotel(self.hotel_choice.get(), hotel_price)
        self.trip.hotel = hotel

        try:
            self.trip.budget = self.budget
            self.trip.confirm()
            if self.selected_payment.get() == "Karta":
                payment = CreditCardPayment()
            else:
                payment = CashPayment()
            payment_msg = payment.pay(self.trip.total_cost())

            self.budget -= self.trip.total_cost()
            self.update_budget_label()

            messagebox.showinfo("Sukces", f"Podróż zaplanowana pomyślnie!\n{payment_msg}")
            self.reset_all()
            self.build_trip()
        except OverBudgetException as e:
            messagebox.showerror("Błąd", str(e))

    def reset_all(self):
        self.destination.set("")
        self.departure.set("")
        self.return_date.set("")
        self.airline.set("")
        self.seat.set("")
        self.hotel_choice.set("")
        self.selected_payment.set("")

    @staticmethod
    def is_valid_date_format(date_str):
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

if __name__ == "__main__":
    app = TravelPlannerApp()
    app.mainloop()
