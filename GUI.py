import customtkinter as ctk
from PIL import Image, ImageDraw
from matplotlib import container
import requests
from io import BytesIO
from client import ChatClient, get_history

ctk.set_appearance_mode("dark")

class DiscordUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Communist Discord type shit")
        self.geometry("1100x750")
        
        self.client = ChatClient()
        self.client.on_message_received = self.handle_incoming_message
        self.nickname = ""
        self.after(200, self.prompt_login)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Modern Palette
        self.bg_color = "#313338"       
        self.sidebar_color = "#1E1F22"  
        self.member_bg = "#2B2D31"      
        self.accent_color = "#5865F2"   
        self.text_main = "#DBDEE1"
        self.text_muted = "#949BA4"
        self.status_online = "#23A55A"
        self.status_dnd = "#F23F43"

        self.configure(fg_color=self.sidebar_color)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- 1. Left Sidebar ---
        self.sidebar = ctk.CTkFrame(self, width=72, corner_radius=0, fg_color=self.sidebar_color)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.server_icon = ctk.CTkButton(self.sidebar, text="A", width=48, height=48, 
                                         corner_radius=16, fg_color=self.accent_color, 
                                         hover_color="#4752c4", font=("Inter", 18, "bold"))
        self.server_icon.pack(pady=12)
        ctk.CTkFrame(self.sidebar, height=2, width=32, fg_color="#35363C").pack(pady=4)

        # --- 2. Main Chat Area ---
        self.chat_main_container = ctk.CTkFrame(self, corner_radius=15, fg_color=self.bg_color)
        self.chat_main_container.grid(row=0, column=1, sticky="nsew")
        self.chat_main_container.grid_rowconfigure(1, weight=1)
        self.chat_main_container.grid_columnconfigure(0, weight=1)

        # Header
        self.header = ctk.CTkFrame(self.chat_main_container, height=48, corner_radius=0, fg_color="transparent")
        self.header.grid(row=0, column=0, sticky="ew", padx=15)
        ctk.CTkLabel(self.header, text="# general", font=("Inter", 16, "bold"), text_color="#FFFFFF").pack(side="left", pady=15)

        # Message Display
        self.message_list = ctk.CTkTextbox(self.chat_main_container, fg_color="transparent", 
                                           text_color=self.text_main, font=("Inter", 14), 
                                           spacing3=10, state="disabled", border_width=0)
        self.message_list.grid(row=1, column=0, padx=20, pady=0, sticky="nsew")
        
        # Input Area
        self.input_area = ctk.CTkFrame(self.chat_main_container, fg_color="#383A40", height=44, corner_radius=10)
        self.input_area.grid(row=2, column=0, padx=20, pady=20, sticky="ew")
        
        self.entry = ctk.CTkEntry(self.input_area, placeholder_text="Message #general", 
                                  border_width=0, fg_color="transparent", 
                                  text_color=self.text_main, font=("Inter", 14))
        self.entry.pack(side="left", fill="x", expand=True, padx=15)
        self.entry.bind("<Return>", lambda e: self.send_message())

        # --- 3. Right Sidebar (Members) ---
        self.member_frame = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color=self.member_bg)
        self.member_frame.grid(row=0, column=2, sticky="nsew")
        
        self.member_label = ctk.CTkLabel(self.member_frame, text="ONLINE — 3", 
                                         font=("Inter", 11, "bold"), text_color=self.text_muted)
        self.member_label.pack(pady=(20, 10), padx=20, anchor="w")

        # Adding members with status colors
        self.add_member("User-1", "https://i.imgur.com/sxuhpRX.png", self.status_online)
        self.add_member("User-2", "https://i.imgur.com/7c4KG5k.jpeg", self.status_dnd)
        self.add_member("User-3", "https://i.pravatar.cc/150?u=gem", self.status_online)

    def send_message(self):
        msg = self.entry.get().strip()
        if msg:
            if hasattr(self, 'client') and self.client.connected:
                self.client.send(msg)
                self.entry.delete(0, "end")
            else:
                print("Not connected to server")
        else:
            print("Don't send empty messages please.")

    def handle_incoming_message(self, msg):
        self.after(0, lambda: self.display_message(msg))

    def display_message(self, msg):
        self.message_list.configure(state="normal")
        
        sender = msg.get("sender", "Unknown")
        timestamp = msg.get("timestamp", "")
        text = msg.get("text", "")

        is_me = (sender == self.nickname)
        sender_color = self.accent_color if is_me else "#F23F43"
        sender_tag = f"sender_{sender}"

        self.message_list.insert("end", f"{sender} ", sender_tag)
        self.message_list.tag_config(sender_tag, foreground=sender_color) 
        
        self.message_list.insert("end", f"Today at {timestamp}\n", "timestamp")
        self.message_list.tag_config("timestamp", foreground=self.text_muted)
        
        self.message_list.insert("end", f"{text}\n\n")
        
        self.message_list.configure(state="disabled")
        self.message_list.see("end")

    def prompt_login(self):
        # Automatically connect to 127.0.0.1 to avoid popup typos
        ip = "127.0.0.1"
        
        dialog_name = ctk.CTkInputDialog(text="Enter Nickname:", title="Nickname")
        nickname = dialog_name.get_input()
        if not nickname or not nickname.strip(): 
            nickname = "Guest" # fallback to Guest if cancelled or empty
            
        self.nickname = nickname.strip()
        
        print(f"Connecting to {ip}...")
        if self.client.connect(ip, self.nickname):
            print(f"Connected successfully to {ip}!")
            self.entry.configure(placeholder_text=f"Message #general as {self.nickname}")
            
            history = get_history()
            for msg in history:
                self.display_message(msg)
        else:
            print(f"Failed to connect to {ip}!")
            self.entry.configure(placeholder_text="DISCONNECTED. Check server terminal.")

    def on_closing(self):
        if hasattr(self, 'client'):
            self.client.disconnect()
        self.destroy()

    def add_member(self, name, img_url, status_color):
        container = ctk.CTkFrame(self.member_frame, fg_color="transparent", height=45)
        container.pack(fill="x", padx=10, pady=2)

        avatar_canvas = ctk.CTkFrame(container, fg_color="transparent", width=40, height=40)
        avatar_canvas.pack(side="left", padx=5)

        try:
            # We add 'headers' so Imgur thinks we are a real browser
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(img_url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                img_data = Image.open(BytesIO(response.content))
                avatar_img = ctk.CTkImage(light_image=img_data, dark_image=img_data, size=(34, 34))
                
                avatar_label = ctk.CTkLabel(avatar_canvas, text="", image=avatar_img)
                avatar_label.place(relx=0.5, rely=0.5, anchor="center")
            else:
                raise Exception("Imgur said no.")
        except Exception as e:
            # Fallback if Imgur is being a pain
            print(f"Failed to load {name}'s avatar: {e}")
            fallback = ctk.CTkFrame(avatar_canvas, width=34, height=34, fg_color=self.accent_color, corner_radius=17)
            fallback.place(relx=0.5, rely=0.5, anchor="center")

        # The Status Dot
        status_dot = ctk.CTkFrame(avatar_canvas, width=12, height=12, 
                                  fg_color=status_color, corner_radius=6,
                                  border_width=2, border_color=self.member_bg)
        status_dot.place(relx=0.85, rely=0.85, anchor="center")

        name_label = ctk.CTkLabel(container, text=name, text_color=self.text_main, font=("Inter", 14, "bold"))
        name_label.pack(side="left", padx=5)
if __name__ == "__main__":
    app = DiscordUI()
    app.mainloop()