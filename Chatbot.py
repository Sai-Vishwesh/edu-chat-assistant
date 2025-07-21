import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox
from PIL import Image
import pytesseract

# 🧠 Tesseract OCR path (Update if needed)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

class SchoolHelpChatbot(tb.Window):
    def __init__(self):
        super().__init__(themename="flatly")
        self.title("📘 School Help Chatbot")
        self.geometry("950x600")
        self.resizable(True, True)        # ✅ Maximize works
        self.state('zoomed')              # ✅ Start maximized

        self.schedule_data = {}
        self.results_data = {}

        self.create_ui()

    def create_ui(self):
        # Sidebar
        self.sidebar = tb.Frame(self, width=200, padding=10, bootstyle="secondary")
        self.sidebar.pack(side=LEFT, fill=Y)
        self.sidebar.pack_propagate(False)

        # Main area
        self.main_area = tb.Frame(self, padding=10, bootstyle="light")
        self.main_area.pack(side=RIGHT, fill=BOTH, expand=True)

        # Sidebar buttons
        tb.Label(self.sidebar, text="📋 Menu", font=("Segoe UI", 14, "bold")).pack(pady=(10, 20))

        self.btn_upload = tb.Button(self.sidebar, text="📤 Upload Data", bootstyle="info-outline", width=20, command=self.show_upload)
        self.btn_upload.pack(fill=X, pady=6, ipadx=6, ipady=6)

        self.btn_chat = tb.Button(self.sidebar, text="💬 Chat", bootstyle="success-outline", width=20, command=self.show_chat)
        self.btn_chat.pack(fill=X, pady=6, ipadx=6, ipady=6)

        # Dark mode toggle
        tb.Button(self.sidebar, text="🌓 Toggle Theme", bootstyle="dark-outline", width=20, command=self.toggle_theme).pack(side="bottom", pady=20, fill=X)

        # Pages
        self.page_upload = tb.Frame(self.main_area, bootstyle="light", padding=20)
        self.page_chat = tb.Frame(self.main_area, bootstyle="light", padding=20)

        self.create_upload_ui()
        self.create_chat_ui()

        # Default page
        self.page_chat.pack_forget()
        self.page_upload.pack(fill=BOTH, expand=True)
        self.active_page = "upload"

    def create_upload_ui(self):
        tb.Label(self.page_upload, text="Upload Schedule and Results", font=("Segoe UI", 16, "bold")).pack(pady=15)

        tb.Button(self.page_upload, text="Upload Schedule", bootstyle="info-outline", width=25, command=self.upload_schedule).pack(pady=10)
        self.schedule_label = tb.Label(self.page_upload, text="No schedule uploaded yet.", font=("Segoe UI", 10))
        self.schedule_label.pack()

        tb.Button(self.page_upload, text="Upload Results", bootstyle="info-outline", width=25, command=self.upload_results).pack(pady=10)
        self.results_label = tb.Label(self.page_upload, text="No results uploaded yet.", font=("Segoe UI", 10))
        self.results_label.pack()

    def create_chat_ui(self):
        self.chat_text = tb.ScrolledText(self.page_chat, font=("Segoe UI", 11), height=20, wrap="word", state="disabled")
        self.chat_text.pack(fill=BOTH, expand=True, padx=10, pady=10)

        entry_frame = tb.Frame(self.page_chat)
        entry_frame.pack(fill=X, padx=10, pady=5)

        self.user_entry = tb.Entry(entry_frame, font=("Segoe UI", 11), bootstyle="light", width=100)
        self.user_entry.pack(side=LEFT, fill=X, expand=True, ipady=6, padx=(0, 5))
        self.user_entry.bind("<Return>", self.send_message)

        tb.Button(entry_frame, text="Send ➤", bootstyle="primary", width=10, command=self.send_message).pack(side=LEFT)

    def toggle_theme(self):
        current = self.style.theme.name
        new = "darkly" if current in ["flatly", "cosmo", "minty"] else "flatly"
        self.style.theme_use(new)

    def extract_text_from_image(self, file_path):
        try:
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)
            return text
        except Exception as e:
            messagebox.showerror("OCR Error", f"Failed to read image: {e}")
            return ""

    def parse_text_to_dict(self, text):
        result = {}
        lines = text.strip().split("\n")
        for line in lines:
            if ":" in line:
                key, value = line.split(":", 1)
                result[key.strip()] = value.strip()
        return result

    def upload_schedule(self):
        file = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")])
        if file:
            self.schedule_label.config(text=f"Schedule uploaded: {file.split('/')[-1]}")
            text = self.extract_text_from_image(file)
            self.schedule_data = self.parse_text_to_dict(text)
            messagebox.showinfo("Upload Success", "Schedule parsed successfully.")

    def upload_results(self):
        file = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")])
        if file:
            self.results_label.config(text=f"Results uploaded: {file.split('/')[-1]}")
            text = self.extract_text_from_image(file)
            self.results_data = self.parse_text_to_dict(text)
            messagebox.showinfo("Upload Success", "Results parsed successfully.")

    def send_message(self, event=None):
        msg = self.user_entry.get().strip()
        self.user_entry.delete(0, "end")
        if not msg:
            return
        self.append_chat("You", msg)
        self.append_chat("Bot", self.generate_response(msg))

    def append_chat(self, sender, msg):
        self.chat_text.configure(state="normal")
        self.chat_text.insert("end", f"{sender}: {msg}\n\n")
        self.chat_text.configure(state="disabled")
        self.chat_text.see("end")

    def generate_response(self, msg):
        msg = msg.lower()
        if any(w in msg for w in ["schedule", "class", "timing"]):
            if not self.schedule_data:
                return "No schedule data uploaded yet."
            for k in self.schedule_data:
                if k.lower() in msg:
                    return f"{k} class is at {self.schedule_data[k]}"
            return "\n".join(f"{k}: {v}" for k, v in self.schedule_data.items())
        if any(w in msg for w in ["result", "marks", "score"]):
            if not self.results_data:
                return "No results data uploaded yet."
            for k in self.results_data:
                if k.lower() in msg:
                    return f"Your marks in {k}: {self.results_data[k]}"
            return "\n".join(f"{k}: {v}" for k, v in self.results_data.items())
        if "hello" in msg or "hi" in msg:
            return "Hello! You can ask about schedule or results."
        return "Sorry, I didn't understand. Ask about class schedule or results."

    def show_upload(self):
        if self.active_page != "upload":
            self.page_chat.pack_forget()
            self.page_upload.pack(fill=BOTH, expand=True)
            self.btn_upload.config(bootstyle="info-outline")
            self.btn_chat.config(bootstyle="success-outline")
            self.active_page = "upload"

    def show_chat(self):
        if self.active_page != "chat":
            self.page_upload.pack_forget()
            self.page_chat.pack(fill=BOTH, expand=True)
            self.btn_chat.config(bootstyle="success-outline")
            self.btn_upload.config(bootstyle="info-outline")
            self.active_page = "chat"

if __name__ == "__main__":
    app = SchoolHelpChatbot()
    app.mainloop()
