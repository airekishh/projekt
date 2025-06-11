import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime


# ✅ Własny wyjątek
class OverBudgetException(Exception):
    pass


# ✅ Strategia płatności
class PaymentStrategy:
    def pay(self, amount):
        pass


class CreditCardPayment(PaymentStrategy):
    def pay(self, amount):
        print(f"Płacę {amount} zł kartą kredytową")


class CashPayment(PaymentStrategy):
    def pay(self, amount):
        print(f"Płacę {amount} zł gotówką")


# ✅ Klasa + Dziedziczenie + Nadpisywanie atrybutów i metod + super()
class Transport:
    def __init__(self, price):
        self.price = price
        self.mode = "Unknown"

    def travel_time(self):
        return 0


class Flight(Transport):
    def __init__(self, price, airline, seat):
        super().__init__(price)
        self.airline = airline
        self.seat = seat
        self.mode = "Flight"

    def travel_time(self):
        return 2


# ✅ Enkapsulacja
class Hotel:
    def __init__(self, name, price):
        self.__price = price
        self.name = name

    def get_price(self):
        return self.__price

    def set_price(self, price):
        if price < 0:
            raise ValueError("Cena nie może być ujemna")
        self.__price = price


# ✅ Klasa z wieloma konstruktorami
class Trip:
    def __init__(self, destination, budget):
        self.destination = destination
        self.budget = budget
        self.transport = None
        self.hotel = None
        self.departure_date = None
        self.return_date = None

    @classmethod
    def from_dict(cls, data):
        return cls(data["destination"], data["budget"])

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

    def to_string(self):
        return f"{self.destination}|{self.departure_date}|{self.return_date}"

    @staticmethod
    def from_string(data):
        parts = data.strip().split("|")
        trip = Trip(parts[0], 1500)
        trip.departure_date = parts[1]
        trip.return_date = parts[2]
        return trip


# ✅ Polecenie
class Command:
    def execute(self):
        pass


class AddHotelCommand(Command):
    def __init__(self, trip, hotel):
        self.trip = trip
        self.hotel = hotel

    def execute(self):
        self.trip.hotel = self.hotel


# ✅ Template Method
class TripBuilderTemplate:
    def build_trip(self):
        self.choose_destination()
        self.choose_transport()
        self.choose_hotel()
        self.confirm_trip()

    def choose_destination(self): raise NotImplementedError

    def choose_transport(self): raise NotImplementedError

    def choose_hotel(self): raise NotImplementedError

    def confirm_trip(self): raise NotImplementedError


# GUI + konkretna implementacja
class TravelPlannerApp(tk.Tk, TripBuilderTemplate):
    def __init__(self):
        super().__init__()
        self.trips_history = []
        self.load_trips_from_file()  # <<<< DODAJ TO TUTAJ
        self.title("Travel Planner")
        self.geometry("400x500")

        self.trip = None
        self.trips_history = []  # Lista zaplanowanych lotów

        self.selected_payment = tk.StringVar()
        self.destination = tk.StringVar()
        self.departure = tk.StringVar()
        self.return_date = tk.StringVar()
        self.seat = tk.StringVar()
        self.hotel_choice = tk.StringVar()

        self.create_menu()
        self.create_widgets()

    def create_menu(self):
        menu_bar = tk.Menu(self)

        main_menu = tk.Menu(menu_bar, tearoff=0)
        main_menu.add_command(label="Rezerwacja lotu", command=self.show_booking_form)
        main_menu.add_command(label="Moje loty", command=self.show_my_trips)
        main_menu.add_command(label="Odwołanie lotu", command=self.cancel_trip)
        main_menu.add_separator()
        main_menu.add_command(label="Wyjście", command=self.quit)

        menu_bar.add_cascade(label="Menu", menu=main_menu)
        self.config(menu=menu_bar)

    def show_booking_form(self):
        for widget in self.winfo_children():
            if not isinstance(widget, tk.Menu):
                widget.destroy()
        self.create_widgets()

    def show_my_trips(self):
        if not self.trips_history:
            messagebox.showinfo("Moje loty", "Brak zapisanych lotów.")
        else:
            msg = ""
            for i, trip in enumerate(self.trips_history, start=1):
                msg += f"{i}. {trip.destination} (od {trip.departure_date} do {trip.return_date})\n"
            messagebox.showinfo("Moje loty", msg)

    def cancel_trip(self):
        if not self.trips_history:
            messagebox.showinfo("Odwołanie", "Brak zaplanowanych lotów do odwołania.")
            return

        cancel_window = tk.Toplevel(self)
        cancel_window.title("Odwołanie lotu")
        cancel_window.geometry("400x250")
        cancel_window.minsize(400, 250)

        tk.Label(cancel_window, text="Wybierz lot do odwołania:").grid(row=0, column=0, columnspan=2, pady=10)

        listbox = tk.Listbox(cancel_window, height=8, width=50)
        listbox.grid(row=1, column=0, columnspan=2, padx=10, sticky="nsew")

        for i, trip in enumerate(self.trips_history):
            listbox.insert(tk.END, f"{trip.destination} (od {trip.departure_date} do {trip.return_date})")

        def confirm_cancel():
            selection = listbox.curselection()
            if not selection:
                messagebox.showwarning("Błąd", "Nie wybrano lotu.")
                return
            index = selection[0]
            canceled_trip = self.trips_history.pop(index)
            self.save_trips_to_file()
            cancel_window.destroy()
            messagebox.showinfo("Odwołanie", f"Lot do {canceled_trip.destination} został odwołany.")

        cancel_button = tk.Button(cancel_window, text="Odwołaj wybrany lot", command=confirm_cancel)
        cancel_button.grid(row=2, column=0, columnspan=2, pady=10)

        # Ustawienia siatki, żeby okno się prawidłowo skalowało
        cancel_window.grid_rowconfigure(1, weight=1)
        cancel_window.grid_columnconfigure(0, weight=1)
        cancel_window.grid_columnconfigure(1, weight=1)

    def create_widgets(self):
        # Kontener do centrowania formularza
        form_frame = ttk.Frame(self)
        form_frame.place(relx=0.5, rely=0.5, anchor="center")  # <<<<<< CENTROWANIE W PIONIE I POZIOMIE

        ttk.Label(form_frame, text="Miejsce docelowe:").pack(pady=5)
        ttk.Combobox(form_frame, textvariable=self.destination, values=["Paryż", "Rzym", "Londyn"],
                     state="readonly").pack()

        ttk.Label(form_frame, text="Data wylotu (YYYY-MM-DD):").pack(pady=5)
        ttk.Entry(form_frame, textvariable=self.departure).pack()

        ttk.Label(form_frame, text="Data powrotu (YYYY-MM-DD):").pack(pady=5)
        ttk.Entry(form_frame, textvariable=self.return_date).pack()

        ttk.Label(form_frame, text="Miejsce w samolocie:").pack(pady=5)
        ttk.Combobox(form_frame, textvariable=self.seat, values=["Okno", "Środek", "Przejście"],
                     state="readonly").pack()

        ttk.Label(form_frame, text="Hotel:").pack(pady=5)
        ttk.Combobox(form_frame, textvariable=self.hotel_choice, values=["Hotel A", "Hotel B", "Hotel C"],
                     state="readonly").pack()

        ttk.Label(form_frame, text="Metoda płatności:").pack(pady=5)
        ttk.Combobox(form_frame, textvariable=self.selected_payment, values=["Karta", "Gotówka"],
                     state="readonly").pack()

        ttk.Button(form_frame, text="Zaplanuj podróż", command=self.build_trip).pack(pady=20)

    def choose_destination(self):
        # Walidacja pustych pól
        if not self.destination.get():
            messagebox.showerror("Błąd", "Wybierz miejsce docelowe.")
            raise ValueError("Brak miejsca docelowego.")

        if not self.departure.get() or not self.return_date.get():
            messagebox.showerror("Błąd", "Wprowadź daty wylotu i powrotu.")
            raise ValueError("Brak dat.")

        if not self.seat.get():
            messagebox.showerror("Błąd", "Wybierz miejsce w samolocie.")
            raise ValueError("Brak miejsca.")

        if not self.hotel_choice.get():
            messagebox.showerror("Błąd", "Wybierz hotel.")
            raise ValueError("Brak hotelu.")

        if not self.selected_payment.get():
            messagebox.showerror("Błąd", "Wybierz metodę płatności.")
            raise ValueError("Brak metody płatności.")

        # Walidacja formatu dat
        departure_str = self.departure.get()
        return_str = self.return_date.get()

        try:
            departure_date = datetime.strptime(departure_str, "%Y-%m-%d").date()
            return_date = datetime.strptime(return_str, "%Y-%m-%d").date()

            if return_date < departure_date:
                messagebox.showerror("Błąd daty", "Data powrotu nie może być wcześniejsza niż data wylotu.")
                raise ValueError("Nieprawidłowa kolejność dat.")

        except ValueError:
            messagebox.showerror("Błąd formatu", "Wprowadź daty w formacie YYYY-MM-DD.")
            raise

        self.trip = Trip(self.destination.get(), 1500)
        self.trip.departure_date = departure_str
        self.trip.return_date = return_str

    def choose_transport(self):
        self.trip.transport = Flight(price=800, airline="LOT", seat=self.seat.get())

    def choose_hotel(self):
        hotel = Hotel(self.hotel_choice.get(), 600)
        AddHotelCommand(self.trip, hotel).execute()

    def confirm_trip(self):
        try:
            self.trip.confirm()
            payment = CreditCardPayment() if self.selected_payment.get() == "Karta" else CashPayment()
            payment.pay(self.trip.total_cost())
            self.trips_history.append(self.trip)
            self.save_trips_to_file()  # <<<< DODAJ TO TUTAJ
            messagebox.showinfo("Sukces", "Podróż zaplanowana pomyślnie!")
            self.clear_form()
        except OverBudgetException as e:
            messagebox.showerror("Błąd", str(e))

    def clear_form(self):
        self.destination.set("")
        self.departure.set("")
        self.return_date.set("")
        self.seat.set("")
        self.hotel_choice.set("")
        self.selected_payment.set("")

    def save_trips_to_file(self):
        with open("loty.txt", "w", encoding="utf-8") as f:
            for trip in self.trips_history:
                f.write(trip.to_string() + "\n")

    def load_trips_from_file(self):
        try:
            with open("loty.txt", "r", encoding="utf-8") as f:
                for line in f:
                    trip = Trip.from_string(line)
                    self.trips_history.append(trip)
        except FileNotFoundError:
            pass  # plik nie istnieje przy pierwszym uruchomieniu

    def delete_last_trip_from_file(self):
        if not self.trips_history:
            return
        self.trips_history.pop()
        self.save_trips_to_file()


if __name__ == "__main__":
    app = TravelPlannerApp()
    app.mainloop()