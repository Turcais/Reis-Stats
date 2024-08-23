import customtkinter as ctk
from tkinter import Toplevel
import threading

class ReisStatsUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.required_number = "12345"  # Predefined number that the user must enter
        self.initUI()
        self.scanner_windows = {}
        self.scanner_threads = {}
        self.scanner_instances = {}

    def initUI(self):
        self.title('ReisStats by Turcais')
        self.geometry('500x300')

        label = ctk.CTkLabel(self, text='Enter the licance key to proceed:')
        label.pack(pady=10)

        self.number_entry = ctk.CTkEntry(self)
        self.number_entry.pack(pady=5)

        self.check_button = ctk.CTkButton(self, text='Submit', command=self.check_number)
        self.check_button.pack(pady=5)

        self.error_label = ctk.CTkLabel(self, text='', text_color='red')
        self.error_label.pack(pady=5)

        # Initially hide the buttons until the correct number is entered
        self.alliance_btn = ctk.CTkButton(self, text='Alliance Scanner', command=self.run_alliance_scanner)
        self.honor_btn = ctk.CTkButton(self, text='Honor Scanner', command=self.run_honor_scanner)
        self.kingdom_btn = ctk.CTkButton(self, text='Kingdom Scanner', command=self.run_kingdom_scanner)
        self.seed_btn = ctk.CTkButton(self, text='Seed Scanner', command=self.run_seed_scanner)
        self.message_label = ctk.CTkLabel(self, text="Scanners started at once must be restarted whether used or not, as they run locally.")

        # Hide the buttons initially
        self.hide_scanner_buttons()

    def check_number(self):
        entered_number = self.number_entry.get()
        if entered_number == self.required_number:
            self.error_label.configure(text="")
            self.hide_input_widgets()
            self.show_scanner_buttons()
        else:
            self.error_label.configure(text="Incorrect licance key. Please try again.")

    def hide_input_widgets(self):
        # Hide the entry and button widgets once the correct number is entered
        self.number_entry.pack_forget()
        self.check_button.pack_forget()
        self.error_label.pack_forget()

    def hide_scanner_buttons(self):
        self.alliance_btn.pack_forget()
        self.honor_btn.pack_forget()
        self.kingdom_btn.pack_forget()
        self.seed_btn.pack_forget()
        self.message_label.pack_forget()

    def show_scanner_buttons(self):
        self.alliance_btn.pack(pady=5)
        self.honor_btn.pack(pady=5)
        self.kingdom_btn.pack(pady=5)
        self.seed_btn.pack(pady=5)
        self.message_label.pack(pady=10)

    def run_alliance_scanner(self):
        self.start_scanner('alliance')

    def run_honor_scanner(self):
        self.start_scanner('honor')

    def run_kingdom_scanner(self):
        self.start_scanner('kingdom')

    def run_seed_scanner(self):
        self.start_scanner('seed')

    def start_scanner(self, scanner_type):
        if scanner_type in self.scanner_windows:
            print(f"{scanner_type.capitalize()} Scanner is already running. Restarting...")
            self.on_scanner_close(scanner_type)

        try:
            scanner = self.load_scanner(scanner_type)
            if not scanner:
                print(f"Failed to load {scanner_type} scanner.")
                return

            top = Toplevel(self)
            top.title(scanner_type.capitalize())
            scanner_frame = ctk.CTkFrame(top)
            scanner_frame.pack(fill='both', expand=True)

            self.scanner_windows[scanner_type] = top
            self.scanner_instances[scanner_type] = scanner
            top.protocol("WM_DELETE_WINDOW", lambda: self.on_scanner_close(scanner_type))

            print(f"{scanner_type.capitalize()} Scanner window created. Starting scanner thread...")
            scanner_thread = threading.Thread(target=self.run_scanner_thread, args=(scanner, scanner_type), daemon=True)
            scanner_thread.start()

            self.scanner_threads[scanner_type] = scanner_thread

        except Exception as e:
            print(f"Error starting {scanner_type.capitalize()} Scanner: {e}")

    def run_scanner_thread(self, scanner, scanner_type):
        try:
            scanner.start()
        except Exception as e:
            print(f"Error running {scanner_type.capitalize()} Scanner: {e}")
        finally:
            # Make sure to clean up when the scanner finishes
            self.on_scanner_close(scanner_type)

    def load_scanner(self, scanner_type):
        try:
            if scanner_type == 'alliance':
                from alliance_scanner_ui import AllianceScanner
                return AllianceScanner()
            elif scanner_type == 'honor':
                from honor_scanner_ui import HonorScanner
                return HonorScanner()
            elif scanner_type == 'kingdom':
                from kingdom_scanner_ui import KingdomScanner
                return KingdomScanner()
            elif scanner_type == 'seed':
                from seed_scanner_ui import SeedScanner
                return SeedScanner()
        except ImportError as e:
            print(f"Error loading {scanner_type.capitalize()} scanner: {e}")
            return None

    def on_scanner_close(self, scanner_type):
        if scanner_type in self.scanner_windows:
            try:
                # Close the window
                window = self.scanner_windows[scanner_type]
                if window.winfo_exists():
                    window.destroy()

                # Stop the scanner
                if scanner_type in self.scanner_instances:
                    scanner = self.scanner_instances[scanner_type]
                    if hasattr(scanner, 'stop'):
                        scanner.stop()  # Assuming scanner has a stop method to clean up
                    del self.scanner_instances[scanner_type]

                # Join the thread
                if scanner_type in self.scanner_threads:
                    self.scanner_threads[scanner_type].join()
                    del self.scanner_threads[scanner_type]

            except Exception as e:
                print(f"Error closing {scanner_type.capitalize()} Scanner: {e}")
            finally:
                if scanner_type in self.scanner_windows:
                    del self.scanner_windows[scanner_type]

if __name__ == '__main__':
    app = ReisStatsUI()
    app.mainloop()
