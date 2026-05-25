import tkinter as tk
from tkinter import messagebox, scrolledtext
from datetime import datetime
import pandas as pd
import os

class TrainingTimer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Training Tracker Timer")
        self.root.geometry("520x480")
        self.root.resizable(False, False)

        self.start_time = None
        self.total_elapsed = 0          # Accumulated time when paused
        self.running = False
        self.paused = False

        # Title
        tk.Label(self.root, text="Training Timer", font=("Arial", 16, "bold")).pack(pady=10)

        # Timer Display
        self.timer_label = tk.Label(self.root, text="00:00:00", font=("Arial", 36, "bold"), fg="#1e3a8a")
        self.timer_label.pack(pady=20)

        # Buttons Frame
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)

        self.start_btn = tk.Button(btn_frame, text="START", font=("Arial", 12, "bold"),
                                   bg="#22c55e", fg="white", width=10, height=2, command=self.start_timer)
        self.start_btn.grid(row=0, column=0, padx=8)

        self.pause_btn = tk.Button(btn_frame, text="PAUSE", font=("Arial", 12, "bold"),
                                   bg="#eab308", fg="black", width=10, height=2, 
                                   command=self.toggle_pause, state="disabled")
        self.pause_btn.grid(row=0, column=1, padx=8)

        self.stop_btn = tk.Button(btn_frame, text="STOP & SAVE", font=("Arial", 12, "bold"),
                                  bg="#ef4444", fg="white", width=12, height=2, 
                                  command=self.stop_timer, state="disabled")
        self.stop_btn.grid(row=0, column=2, padx=8)

        # Notes Section
        tk.Label(self.root, text="Notes (optional):", font=("Arial", 11, "bold")).pack(anchor="w", padx=30, pady=(15,5))
        
        self.notes_text = scrolledtext.ScrolledText(self.root, height=6, width=55, font=("Arial", 10))
        self.notes_text.pack(padx=30, pady=5)

        # Status
        self.status_label = tk.Label(self.root, text="Ready - Click START to begin", 
                                    font=("Arial", 10), fg="gray")
        self.status_label.pack(pady=15)

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def format_time(self, total_seconds):
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def update_timer(self):
        if self.running and not self.paused:
            elapsed = datetime.now() - self.start_time
            current_total = self.total_elapsed + int(elapsed.total_seconds())
            
            self.timer_label.config(text=self.format_time(current_total))
            self.root.after(200, self.update_timer)

    def start_timer(self):
        if not self.running:
            self.start_time = datetime.now()
            self.total_elapsed = 0
            self.running = True
            self.paused = False
            
            self.start_btn.config(state="disabled")
            self.pause_btn.config(state="normal", text="PAUSE", bg="#eab308")
            self.stop_btn.config(state="normal")
            
            self.status_label.config(text="Training in progress...", fg="green")
            self.update_timer()

    def toggle_pause(self):
        if self.running:
            if not self.paused:
                # Pause
                elapsed = datetime.now() - self.start_time
                self.total_elapsed += int(elapsed.total_seconds())
                self.paused = True
                self.pause_btn.config(text="RESUME", bg="#22c55e")
                self.status_label.config(text="PAUSED", fg="#eab308")
            else:
                # Resume
                self.start_time = datetime.now()
                self.paused = False
                self.pause_btn.config(text="PAUSE", bg="#eab308")
                self.status_label.config(text="Training in progress...", fg="green")
                self.update_timer()

    def stop_timer(self):
        if self.running:
            end_time = datetime.now()
            
            # Calculate final duration
            if not self.paused:
                elapsed = datetime.now() - self.start_time
                final_duration = self.total_elapsed + int(elapsed.total_seconds())
            else:
                final_duration = self.total_elapsed

            # Get notes
            notes = self.notes_text.get("1.0", tk.END).strip()

            # Prepare data
            data = {
                "Date": [datetime.now().strftime("%Y-%m-%d")],
                "Start Time": [self.start_time.strftime("%H:%M:%S") if self.total_elapsed == 0 else "Multiple"],
                "End Time": [end_time.strftime("%H:%M:%S")],
                "Duration (minutes)": [round(final_duration / 60, 2)],
                "Notes": [notes]
            }

            df_new = pd.DataFrame(data)

            # Save to Excel
            filename = "TrainingTracker1.xlsx"
            
            try:
                if os.path.exists(filename):
                    with pd.ExcelWriter(filename, mode='a', engine='openpyxl', 
                                      if_sheet_exists='overlay') as writer:
                        df_new.to_excel(writer, index=False, header=False, 
                                      startrow=writer.sheets['Sheet1'].max_row)
                else:
                    df_new.to_excel(filename, index=False)

                messagebox.showinfo("Success", 
                                  f"Training session saved!\n"
                                  f"Duration: {round(final_duration/60, 1)} minutes")

                self.reset_ui()

            except Exception as e:
                messagebox.showerror("Error", f"Failed to save: {str(e)}")

    def reset_ui(self):
        self.running = False
        self.paused = False
        self.total_elapsed = 0
        self.timer_label.config(text="00:00:00")
        self.start_btn.config(state="normal")
        self.pause_btn.config(state="disabled", text="PAUSE")
        self.stop_btn.config(state="disabled")
        self.notes_text.delete("1.0", tk.END)
        self.status_label.config(text="Session saved successfully ✓", fg="green")

    def on_close(self):
        if self.running:
            if messagebox.askyesno("Quit", "Timer is still running.\nStop and save before quitting?"):
                self.stop_timer()
        self.root.destroy()


if __name__ == "__main__":
    app = TrainingTimer()
    app.root.mainloop()