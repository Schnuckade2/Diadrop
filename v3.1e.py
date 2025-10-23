import customtkinter as ctk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from tkinter import messagebox, filedialog
from PIL import Image
import pandas as pd
import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from datetime import datetime
import re
import traceback

# Extended color palettes
COLOR_SCHEMES = {
    "Modern Blue": ["#0066FF", "#00B4D8", "#90E0EF", "#CAF0F8", "#ADE8F4"],
    "Sunset": ["#FF6B35", "#F7931E", "#FDC830", "#F37335", "#C44536"],
    "Forest": ["#2D6A4F", "#40916C", "#52B788", "#74C69D", "#95D5B2"],
    "Purple Haze": ["#7209B7", "#9D4EDD", "#C77DFF", "#E0AAFF", "#F0D9FF"],
    "Ocean": ["#03045E", "#023E8A", "#0077B6", "#0096C7", "#00B4D8"],
    "Neon": ["#FF006E", "#FB5607", "#FFBE0B", "#3A86FF", "#8338EC"],
    "Pastel": ["#FFADAD", "#FFD6A5", "#FDFFB6", "#CAFFBF", "#9BF6FF"],
    "Earth": ["#D4A373", "#BC6C25", "#606C38", "#283618", "#FEFAE0"],
    "Ruby": ["#590D22", "#800F2F", "#A4133C", "#C9184A", "#FF4D6D"],
    "Ice": ["#012A4A", "#013A63", "#01497C", "#014F86", "#2A6F97"]
}

class DiagramProject:
    def __init__(self, name="New Project"):
        self.name = name
        self.created = datetime.now().isoformat()
        self.modified = datetime.now().isoformat()
        self.data = {"labels": [], "values": [], "colors": []}
        self.chart_type = "Bar"
        self.color_scheme = "Modern Blue"
        self.title = "My Chart"
        # Fixed diagram size (no longer changeable)
        self.width = 10
        self.height = 6
        self.custom_colors = {}
    
    def to_dia_format(self):
        """Convert project to .dia format"""
        dia_content = ["[<TYPE dia>]", ""]
        
        # Settings Section
        dia_content.append("[__Settings__]")
        dia_content.append(f"[Project Settings: created=\"{self.created}\" modified=\"{self.modified}\"]")
        dia_content.append("")
        
        # Data Section
        dia_content.append("[__Data__]")
        for label, value, color in zip(self.data["labels"], self.data["values"], self.data["colors"]):
            dia_content.append(f"[{label} | {value} | {color}]")
        dia_content.append("")
        
        # DiaInfo Section
        dia_content.append("[__DiaInfo__]")
        dia_content.append(f"[Name: \"{self.name}\"]")
        dia_content.append(f"[Type: \"{self.chart_type}\"]")
        dia_content.append(f"[ColorScheme: \"{self.color_scheme}\"]")
        dia_content.append(f"[Title: \"{self.title}\"]")
        # Size no longer included in format since it's fixed
        dia_content.append("")
        
        # Custom Colors
        if self.custom_colors:
            dia_content.append("[__CustomColors__]")
            for key, color in self.custom_colors.items():
                dia_content.append(f"[{key}: {color}]")
            dia_content.append("")
        
        dia_content.append("# .dia File - DiaDrop Chart Format")
        
        return "\n".join(dia_content)
    
    def from_dia_format(self, dia_content):
        """Load project from .dia format"""
        try:
            lines = dia_content.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                
                # Skip comments
                if line.startswith('#') or not line:
                    continue
                
                # Detect section headers
                if line.startswith('[') and line.endswith(']'):
                    content = line[1:-1]
                    
                    if content == '<TYPE dia>':
                        continue  # Header, ignore
                    elif content.startswith('__') and content.endswith('__'):
                        current_section = content
                        continue
                
                # Process data according to section
                if current_section == "__Settings__":
                    if "Project Settings:" in line:
                        # Extract Created and Modified
                        match = re.search(r'created="([^"]+)" modified="([^"]+)"', line)
                        if match:
                            self.created = match.group(1)
                            self.modified = match.group(2)
                
                elif current_section == "__Data__":
                    if line.startswith('[') and line.endswith(']'):
                        data_line = line[1:-1]
                        parts = [part.strip() for part in data_line.split('|')]
                        if len(parts) == 3:
                            self.data["labels"].append(parts[0])
                            self.data["values"].append(float(parts[1]))
                            self.data["colors"].append(parts[2])
                
                elif current_section == "__DiaInfo__":
                    if line.startswith('[') and line.endswith(']'):
                        info_line = line[1:-1]
                        if "Name:" in info_line:
                            match = re.search(r'Name:\s*"([^"]+)"', info_line)
                            if match:
                                self.name = match.group(1)
                        elif "Type:" in info_line:
                            match = re.search(r'Type:\s*"([^"]+)"', info_line)
                            if match:
                                self.chart_type = match.group(1)
                        elif "ColorScheme:" in info_line:
                            match = re.search(r'ColorScheme:\s*"([^"]+)"', info_line)
                            if match:
                                self.color_scheme = match.group(1)
                        elif "Title:" in info_line:
                            match = re.search(r'Title:\s*"([^"]+)"', info_line)
                            if match:
                                self.title = match.group(1)
                        # Size no longer loaded since it's fixed
                
                elif current_section == "__CustomColors__":
                    if line.startswith('[') and line.endswith(']'):
                        color_line = line[1:-1]
                        if ':' in color_line:
                            key, color = color_line.split(':', 1)
                            self.custom_colors[key.strip()] = color.strip()
            
            return True
        except Exception as e:
            print(f"Error parsing .dia file: {e}")
            return False

class EncryptionManager:
    def __init__(self):
        self.key = self._generate_key()
    
    def _generate_key(self):
        password = b"dia_drop_secret_key_2024"
        salt = b"dia_drop_salt_2024"
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password))
    
    def encrypt_data(self, data):
        fernet = Fernet(self.key)
        encrypted_data = fernet.encrypt(data.encode())
        return encrypted_data
    
    def decrypt_data(self, encrypted_data):
        fernet = Fernet(self.key)
        try:
            decrypted_data = fernet.decrypt(encrypted_data)
            return decrypted_data.decode()
        except Exception:
            return None

class RenameDialog(ctk.CTkToplevel):
    def __init__(self, parent, current_name):
        super().__init__(parent)
        self.title("Rename Project")
        self.geometry("400x150")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        # Set icon
        try:
            self.iconbitmap('icon.ico')
        except Exception as e:
            print(f"Could not load icon: {e}")
        
        self.result = None
        
        ctk.CTkLabel(self, text="Enter new project name:", font=ctk.CTkFont(weight="bold")).pack(pady=10)
        self.name_entry = ctk.CTkEntry(self, width=300)
        self.name_entry.pack(pady=5)
        self.name_entry.insert(0, current_name)
        
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(pady=20)
        
        ctk.CTkButton(
            btn_frame,
            text="Rename",
            command=self.rename,
            width=100
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=self.cancel,
            width=100,
            fg_color="#E57373",
            hover_color="#EF5350"
        ).pack(side="left", padx=10)
        
        self.name_entry.focus()
        self.name_entry.select_range(0, 'end')
        
        # Bind Enter key
        self.bind('<Return>', lambda e: self.rename())
        self.bind('<Escape>', lambda e: self.cancel())
    
    def rename(self):
        name = self.name_entry.get().strip()
        if name:
            self.result = name
            self.destroy()
    
    def cancel(self):
        self.destroy()

class StartMenu(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("DiaDrop - Start")
        self.geometry("1200x700")
        
        # Set icon
        try:
            self.iconbitmap('icon.ico')
        except Exception as e:
            print(f"Could not load icon: {e}")
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.setup_directories()
        self.encryption = EncryptionManager()
        self.projects = self.load_projects()
        
        # Fullscreen status
        self.is_fullscreen = False
        
        self.create_ui()
        
        # Fullscreen bindings
        self.bind('<F11>', self.toggle_fullscreen)
        self.bind('<Escape>', self.exit_fullscreen)
        
        # Handle close event
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def setup_directories(self):
        self.app_data_dir = os.path.join(os.getenv('APPDATA'), 'DiaDrop')
        self.projects_dir = os.path.join(self.app_data_dir, 'projects')
        
        for directory in [self.app_data_dir, self.projects_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)
    
    def load_projects(self):
        projects = []
        if os.path.exists(self.projects_dir):
            for file in os.listdir(self.projects_dir):
                if file.endswith('.dia'):
                    file_path = os.path.join(self.projects_dir, file)
                    try:
                        with open(file_path, 'rb') as f:
                            encrypted_data = f.read()
                        
                        dia_content = self.encryption.decrypt_data(encrypted_data)
                        if dia_content:
                            project = DiagramProject()
                            if project.from_dia_format(dia_content):
                                projects.append(project)
                    except Exception as e:
                        print(f"Error loading {file}: {e}")
        
        projects.sort(key=lambda x: x.modified, reverse=True)
        return projects
    
    def create_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header
        header_frame = ctk.CTkFrame(self)
        header_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="📊 DiaDrop - Chart Editor",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.pack(pady=20)
        
        # Button Frame
        button_frame = ctk.CTkFrame(header_frame)
        button_frame.pack(pady=10)
        
        new_project_btn = ctk.CTkButton(
            button_frame,
            text="➕ New Project",
            command=self.new_project,
            height=40,
            width=200
        )
        new_project_btn.pack(side="left", padx=10)
        
        import_project_btn = ctk.CTkButton(
            button_frame,
            text="📁 Import Project",
            command=self.import_project,
            height=40,
            width=200
        )
        import_project_btn.pack(side="left", padx=10)
        
        # Projects List
        self.projects_frame = ctk.CTkScrollableFrame(self)
        self.projects_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        
        self.refresh_projects_list()
    
    def refresh_projects_list(self):
        for widget in self.projects_frame.winfo_children():
            widget.destroy()
        
        if not self.projects:
            empty_label = ctk.CTkLabel(
                self.projects_frame,
                text="No projects available.\nCreate a new project!",
                font=ctk.CTkFont(size=16),
                text_color="#888888"
            )
            empty_label.pack(pady=50)
            return
        
        for i, project in enumerate(self.projects):
            project_card = self.create_project_card(project, i)
            project_card.pack(fill="x", padx=10, pady=5)
    
    def create_project_card(self, project, index):
        card = ctk.CTkFrame(self.projects_frame, height=80)
        
        # Project Info
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=15, pady=10)
        
        name_label = ctk.CTkLabel(
            info_frame,
            text=project.name,
            font=ctk.CTkFont(size=18, weight="bold")
        )
        name_label.pack(anchor="w")
        
        created_label = ctk.CTkLabel(
            info_frame,
            text=f"Created: {datetime.fromisoformat(project.created).strftime('%m/%d/%Y %H:%M')}",
            text_color="#888888"
        )
        created_label.pack(anchor="w")
        
        modified_label = ctk.CTkLabel(
            info_frame,
            text=f"Modified: {datetime.fromisoformat(project.modified).strftime('%m/%d/%Y %H:%M')}",
            text_color="#888888"
        )
        modified_label.pack(anchor="w")
        
        # Button Frame
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(side="right", padx=10, pady=10)
        
        open_btn = ctk.CTkButton(
            btn_frame,
            text="Open",
            command=lambda p=project: self.open_project(p),
            width=80
        )
        open_btn.pack(pady=2)
        
        rename_btn = ctk.CTkButton(
            btn_frame,
            text="Rename",
            command=lambda p=project: self.rename_project(p),
            width=80,
            fg_color="#FFB74D",
            hover_color="#FF9800"
        )
        rename_btn.pack(pady=2)
        
        delete_btn = ctk.CTkButton(
            btn_frame,
            text="Delete",
            command=lambda p=project: self.delete_project(p),
            width=80,
            fg_color="#E57373",
            hover_color="#EF5350"
        )
        delete_btn.pack(pady=2)
        
        return card
    
    def new_project(self):
        dialog = NewProjectDialog(self)
        self.wait_window(dialog)
        
        if dialog.result:
            project_name, import_excel = dialog.result
            project = DiagramProject(project_name)
            
            if import_excel:
                file_path = filedialog.askopenfilename(
                    filetypes=[("Excel files", "*.xlsx *.xls")]
                )
                if file_path:
                    try:
                        df = pd.read_excel(file_path)
                        if len(df.columns) >= 2:
                            project.data["labels"] = df.iloc[:, 0].astype(str).tolist()
                            project.data["values"] = df.iloc[:, 1].astype(float).tolist()
                            colors = COLOR_SCHEMES[project.color_scheme]
                            project.data["colors"] = [colors[i % len(colors)] for i in range(len(project.data["labels"]))]
                    except Exception as e:
                        messagebox.showerror("Error", f"Could not import Excel file: {str(e)}")
            
            self.save_project(project)
            self.projects.insert(0, project)
            self.refresh_projects_list()
            self.open_project(project)
    
    def import_project(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("DiaDrop Projects", "*.dia")]
        )
        
        if file_path:
            try:
                with open(file_path, 'rb') as f:
                    encrypted_data = f.read()
                
                dia_content = self.encryption.decrypt_data(encrypted_data)
                if dia_content:
                    project = DiagramProject()
                    if project.from_dia_format(dia_content):
                        self.save_project(project)
                        self.projects.insert(0, project)
                        self.refresh_projects_list()
                        messagebox.showinfo("Success", f"Project '{project.name}' successfully imported!")
                    else:
                        messagebox.showerror("Error", "The .dia file could not be read!")
                else:
                    messagebox.showerror("Error", "The file could not be decrypted!")
            except Exception as e:
                messagebox.showerror("Error", f"Project could not be imported: {str(e)}")
    
    def open_project(self, project):
        self.withdraw()
        app = DiagramCreator(project, self)
        
        # Important: Pause mainloop of StartMenu
        self.wait_window(app)
    
    def rename_project(self, project):
        dialog = RenameDialog(self, project.name)
        self.wait_window(dialog)
        
        if dialog.result:
            new_name = dialog.result
            # Delete old file
            old_file_path = os.path.join(self.projects_dir, f"{project.name}.dia")
            if os.path.exists(old_file_path):
                os.remove(old_file_path)
            
            project.name = new_name.strip()
            project.modified = datetime.now().isoformat()
            self.save_project(project)
            self.refresh_projects_list()
    
    def delete_project(self, project):
        result = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete project '{project.name}'?"
        )
        
        if result:
            # Remove from list
            self.projects = [p for p in self.projects if p.name != project.name]
            
            # Delete file
            file_name = f"{project.name}.dia"
            file_path = os.path.join(self.projects_dir, file_name)
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    print(f"Project file deleted: {file_path}")
                except Exception as e:
                    messagebox.showerror("Error", f"File could not be deleted: {str(e)}")
            else:
                print(f"File not found: {file_path}")
            
            self.refresh_projects_list()
    
    def save_project(self, project):
        try:
            project.modified = datetime.now().isoformat()
            file_path = os.path.join(self.projects_dir, f"{project.name}.dia")
            dia_content = project.to_dia_format()
            encrypted_data = self.encryption.encrypt_data(dia_content)
            
            with open(file_path, 'wb') as f:
                f.write(encrypted_data)
            print(f"Project saved: {project.name}")
            return True
        except Exception as e:
            print(f"Error saving project: {e}")
            messagebox.showerror("Error", f"Project could not be saved: {str(e)}")
            return False
    
    def show_menu(self):
        self.deiconify()
        # Reload projects to ensure list is current
        self.projects = self.load_projects()
        self.refresh_projects_list()
    
    def toggle_fullscreen(self, event=None):
        self.is_fullscreen = not self.is_fullscreen
        self.attributes('-fullscreen', self.is_fullscreen)
        return "break"
    
    def exit_fullscreen(self, event=None):
        self.is_fullscreen = False
        self.attributes('-fullscreen', False)
        return "break"
    
    def on_closing(self):
        # When closing the start menu, exit the program
        self.destroy()

class NewProjectDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("New Project")
        self.geometry("400x200")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        # Set icon
        try:
            self.iconbitmap('icon.ico')
        except Exception as e:
            print(f"Could not load icon: {e}")
        
        self.result = None
        
        ctk.CTkLabel(self, text="Project name:", font=ctk.CTkFont(weight="bold")).pack(pady=10)
        self.name_entry = ctk.CTkEntry(self, width=300)
        self.name_entry.pack(pady=5)
        self.name_entry.insert(0, "New Project")
        
        self.excel_var = ctk.BooleanVar()
        excel_check = ctk.CTkCheckBox(
            self, 
            text="Import Excel file", 
            variable=self.excel_var
        )
        excel_check.pack(pady=10)
        
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(pady=20)
        
        ctk.CTkButton(
            btn_frame,
            text="Create",
            command=self.create,
            width=100
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=self.cancel,
            width=100,
            fg_color="#E57373",
            hover_color="#EF5350"
        ).pack(side="left", padx=10)
        
        self.name_entry.focus()
        self.name_entry.select_range(0, 'end')
        
        # Bind Enter key
        self.bind('<Return>', lambda e: self.create())
        self.bind('<Escape>', lambda e: self.cancel())
    
    def create(self):
        name = self.name_entry.get().strip()
        if name:
            self.result = (name, self.excel_var.get())
            self.destroy()
    
    def cancel(self):
        self.destroy()

class DiagramCreator(ctk.CTk):
    def __init__(self, project, start_menu):
        super().__init__()
        
        self.project = project
        self.start_menu = start_menu
        self.encryption = EncryptionManager()
        
        self.title(f"DiaDrop - {project.name}")
        self.geometry("1400x800")
        self.state('zoomed')
        
        # Set icon
        try:
            self.iconbitmap('icon.ico')
        except Exception as e:
            print(f"Could not load icon: {e}")
        
        self.is_fullscreen = False
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.auto_save_id = None
        self.setup_auto_save()
        
        self.create_ui()
        
        self.bind('<F11>', self.toggle_fullscreen)
        self.bind('<Escape>', self.exit_fullscreen)
        self.bind('<Control-s>', lambda e: self.save_project())
        
        # Handle close event
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.update_chart()
        
    def setup_auto_save(self):
        # Auto-save with error handling
        try:
            self.auto_save_id = self.after(30000, self.auto_save)
        except Exception as e:
            print(f"Error setting up auto-save: {e}")
    
    def auto_save(self):
        try:
            if self.winfo_exists():  # Check if window still exists
                self.save_project()
                # Schedule next auto-save
                self.auto_save_id = self.after(30000, self.auto_save)
        except Exception as e:
            print(f"Error during auto-save: {e}")
            # Try to restart timer
            if self.winfo_exists():
                self.auto_save_id = self.after(30000, self.auto_save)
    
    def create_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.sidebar = ctk.CTkTabview(self, width=400)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        
        self.sidebar.add("Data")
        self.sidebar.add("Design")
        self.sidebar.add("Dia Code")
        
        self.setup_data_tab()
        self.setup_design_tab()
        self.setup_dia_code_tab()
        
        self.chart_container = ctk.CTkFrame(self)
        self.chart_container.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.chart_container.grid_columnconfigure(0, weight=1)
        self.chart_container.grid_rowconfigure(0, weight=1)
        
        # Fixed chart size (10x6)
        self.figure = Figure(figsize=(10, 6), facecolor='#2B2B2B')
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.chart_container)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
    def setup_data_tab(self):
        tab = self.sidebar.tab("Data")
        
        data_frame = ctk.CTkFrame(tab)
        data_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            data_frame, 
            text="Enter data:", 
            font=ctk.CTkFont(weight="bold")
        ).pack(padx=10, pady=(10, 5), anchor="w")
        
        ctk.CTkLabel(data_frame, text="Label:").pack(padx=10, pady=5, anchor="w")
        self.label_entry = ctk.CTkEntry(data_frame, placeholder_text="e.g. January")
        self.label_entry.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(data_frame, text="Value:").pack(padx=10, pady=5, anchor="w")
        self.value_entry = ctk.CTkEntry(data_frame, placeholder_text="e.g. 100")
        self.value_entry.pack(fill="x", padx=10, pady=5)
        
        add_button = ctk.CTkButton(
            data_frame, 
            text="➕ Add", 
            command=self.add_data,
            fg_color="#2CC985",
            hover_color="#25A166"
        )
        add_button.pack(fill="x", padx=10, pady=10)
        
        list_frame = ctk.CTkFrame(tab)
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(
            list_frame, 
            text="Current data:", 
            font=ctk.CTkFont(weight="bold")
        ).pack(padx=10, pady=(10, 5), anchor="w")
        
        self.data_scrollable = ctk.CTkScrollableFrame(list_frame, height=200)
        self.data_scrollable.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.clear_button = ctk.CTkButton(
            list_frame, 
            text="🗑️ Clear All", 
            command=self.clear_data,
            fg_color="#E63946",
            hover_color="#C62828"
        )
        self.clear_button.pack(fill="x", padx=10, pady=5)
        
        self.update_data_display()
    
    def setup_design_tab(self):
        tab = self.sidebar.tab("Design")
        
        type_frame = ctk.CTkFrame(tab)
        type_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            type_frame, 
            text="Chart Type:", 
            font=ctk.CTkFont(weight="bold")
        ).pack(padx=10, pady=(10, 5), anchor="w")
        
        self.chart_type = ctk.CTkSegmentedButton(
            type_frame,
            values=["Bar", "Line", "Pie", "Scatter"],
            command=self.update_chart
        )
        self.chart_type.set(self.project.chart_type)
        self.chart_type.pack(fill="x", padx=10, pady=5)
        
        color_frame = ctk.CTkFrame(tab)
        color_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            color_frame, 
            text="Color Scheme:", 
            font=ctk.CTkFont(weight="bold")
        ).pack(padx=10, pady=(10, 5), anchor="w")
        
        self.color_scheme = ctk.CTkOptionMenu(
            color_frame,
            values=list(COLOR_SCHEMES.keys()),
            command=self.change_color_scheme
        )
        self.color_scheme.set(self.project.color_scheme)
        self.color_scheme.pack(fill="x", padx=10, pady=5)
        
        # Size settings removed (no longer changeable)
        
        title_frame = ctk.CTkFrame(tab)
        title_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            title_frame, 
            text="Chart Title:", 
            font=ctk.CTkFont(weight="bold")
        ).pack(padx=10, pady=(10, 5), anchor="w")
        
        self.chart_title_entry = ctk.CTkEntry(
            title_frame, 
            placeholder_text="My Chart"
        )
        self.chart_title_entry.pack(fill="x", padx=10, pady=5)
        self.chart_title_entry.insert(0, self.project.title)
        self.chart_title_entry.bind("<KeyRelease>", lambda e: self.update_chart())
        
        # Add export button
        export_frame = ctk.CTkFrame(tab)
        export_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            export_frame, 
            text="Export Chart:", 
            font=ctk.CTkFont(weight="bold")
        ).pack(padx=10, pady=(10, 5), anchor="w")
        
        self.export_button = ctk.CTkButton(
            export_frame,
            text="📷 Save as Image",
            command=self.save_chart,
            height=40,
            fg_color="#9C27B0",
            hover_color="#7B1FA2"
        )
        self.export_button.pack(fill="x", padx=10, pady=5)
    
    def setup_dia_code_tab(self):
        tab = self.sidebar.tab("Dia Code")
        
        ctk.CTkLabel(
            tab, 
            text=".dia Code Editor:", 
            font=ctk.CTkFont(weight="bold")
        ).pack(padx=10, pady=(10, 5), anchor="w")
        
        info_label = ctk.CTkLabel(
            tab,
            text="Here you can edit the .dia code directly.\nChanges will be applied when you click 'Apply Code'.",
            text_color="#888888",
            font=ctk.CTkFont(size=12)
        )
        info_label.pack(padx=10, pady=(0, 10), anchor="w")
        
        self.dia_code_text = ctk.CTkTextbox(tab, font=ctk.CTkFont(family="Courier", size=12))
        self.dia_code_text.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.update_dia_code_display()
        
        btn_frame = ctk.CTkFrame(tab, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(
            btn_frame,
            text="Apply Code",
            command=self.apply_dia_code,
            fg_color="#2CC985",
            hover_color="#25A166"
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="Refresh Code",
            command=self.update_dia_code_display
        ).pack(side="left", padx=5)
    
    def update_data_display(self):
        for widget in self.data_scrollable.winfo_children():
            widget.destroy()
        
        if not self.project.data["labels"]:
            empty_label = ctk.CTkLabel(
                self.data_scrollable,
                text="No data available",
                text_color="#888888"
            )
            empty_label.pack(pady=20)
            return
        
        for i, (label, value, color) in enumerate(zip(
            self.project.data["labels"], 
            self.project.data["values"],
            self.project.data["colors"]
        )):
            self.create_data_row(i, label, value, color)
    
    def create_data_row(self, index, label, value, color):
        row_frame = ctk.CTkFrame(self.data_scrollable, height=40)
        row_frame.pack(fill="x", pady=2)
        row_frame.pack_propagate(False)
        
        color_button = ctk.CTkButton(
            row_frame,
            text="",
            width=30,
            height=30,
            fg_color=color,
            hover_color=color,
            command=lambda idx=index: self.change_data_color(idx)
        )
        color_button.pack(side="left", padx=5, pady=5)
        
        text_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        text_frame.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        
        ctk.CTkLabel(
            text_frame,
            text=f"{label}: {value}",
            anchor="w"
        ).pack(fill="x")
        
        delete_btn = ctk.CTkButton(
            row_frame,
            text="🗑️",
            width=30,
            height=30,
            fg_color="transparent",
            hover_color="#E63946",
            text_color="#E63946",
            command=lambda idx=index: self.delete_data(idx)
        )
        delete_btn.pack(side="right", padx=5, pady=5)
    
    def add_data(self):
        label = self.label_entry.get().strip()
        value_str = self.value_entry.get().strip()
        
        if not label or not value_str:
            messagebox.showwarning("Input Error", "Please enter both label and value!")
            return
        
        try:
            value = float(value_str)
        except ValueError:
            messagebox.showerror("Error", "Value must be a number!")
            return
        
        colors = COLOR_SCHEMES[self.project.color_scheme]
        color = colors[len(self.project.data["labels"]) % len(colors)]
        
        self.project.data["labels"].append(label)
        self.project.data["values"].append(value)
        self.project.data["colors"].append(color)
        
        self.update_data_display()
        self.label_entry.delete(0, 'end')
        self.value_entry.delete(0, 'end')
        self.update_chart()
        self.update_dia_code_display()
        self.save_project()
    
    def delete_data(self, index):
        if 0 <= index < len(self.project.data["labels"]):
            self.project.data["labels"].pop(index)
            self.project.data["values"].pop(index)
            self.project.data["colors"].pop(index)
            
            self.update_data_display()
            self.update_chart()
            self.update_dia_code_display()
            self.save_project()
    
    def change_data_color(self, index):
        color = ctk.filedialog.askcolor(
            title="Choose color",
            initialcolor=self.project.data["colors"][index]
        )
        
        if color[1]:
            self.project.data["colors"][index] = color[1]
            self.update_data_display()
            self.update_chart()
            self.save_project()
    
    def clear_data(self):
        self.project.data = {"labels": [], "values": [], "colors": []}
        self.update_data_display()
        self.update_chart()
        self.update_dia_code_display()
        self.save_project()
    
    def change_color_scheme(self, choice):
        self.project.color_scheme = choice
        colors = COLOR_SCHEMES[choice]
        self.project.data["colors"] = [colors[i % len(colors)] for i in range(len(self.project.data["labels"]))]
        self.update_data_display()
        self.update_chart()
        self.save_project()
    
    def update_chart(self, *args):
        try:
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            
            self.project.chart_type = self.chart_type.get()
            self.project.title = self.chart_title_entry.get() or "My Chart"
            
            self.figure.patch.set_facecolor('#2B2B2B')
            ax.set_facecolor('#1E1E1E')
            ax.spines['bottom'].set_color('#666666')
            ax.spines['top'].set_color('#666666')
            ax.spines['left'].set_color('#666666')
            ax.spines['right'].set_color('#666666')
            ax.tick_params(colors='#CCCCCC', which='both')
            ax.xaxis.label.set_color('#CCCCCC')
            ax.yaxis.label.set_color('#CCCCCC')
            
            if not self.project.data["labels"] or not self.project.data["values"]:
                ax.text(0.5, 0.5, 'No data available\nPlease enter data!', 
                       horizontalalignment='center',
                       verticalalignment='center',
                       transform=ax.transAxes,
                       fontsize=16,
                       color='#888888')
                self.canvas.draw()
                return
            
            colors = self.project.data["colors"]
            chart_type = self.project.chart_type
            
            if chart_type == "Bar":
                bars = ax.bar(self.project.data["labels"], self.project.data["values"], 
                             color=colors, edgecolor='white', linewidth=1.5, alpha=0.9)
                
            elif chart_type == "Line":
                line = ax.plot(self.project.data["labels"], self.project.data["values"], 
                       color=colors[0] if colors else COLOR_SCHEMES[self.project.color_scheme][0], 
                       marker='o', linewidth=3, markersize=10, 
                       markerfacecolor=colors[1] if len(colors) > 1 else COLOR_SCHEMES[self.project.color_scheme][1],
                       markeredgecolor='white', markeredgewidth=2)
                ax.fill_between(range(len(self.project.data["labels"])), 
                               self.project.data["values"], alpha=0.3, color=colors[0] if colors else COLOR_SCHEMES[self.project.color_scheme][0])
                ax.set_ylabel('Values', color='#CCCCCC', fontsize=12)
                ax.grid(True, alpha=0.2, color='#666666')
                
            elif chart_type == "Pie":
                wedges, texts, autotexts = ax.pie(
                    self.project.data["values"], 
                    labels=self.project.data["labels"],
                    autopct='%1.1f%%',
                    colors=colors,
                    startangle=90,
                    wedgeprops={'edgecolor': 'white', 'linewidth': 2}
                )
                for text in texts:
                    text.set_color('#CCCCCC')
                for autotext in autotexts:
                    autotext.set_color('white')
                    autotext.set_fontsize(10)
                    autotext.set_weight('bold')
                
            elif chart_type == "Scatter":
                scatter = ax.scatter(range(len(self.project.data["labels"])), 
                                   self.project.data["values"],
                                   c=colors,
                                   s=300, alpha=0.8, edgecolors='white', linewidth=2)
                ax.set_xticks(range(len(self.project.data["labels"])))
                ax.set_xticklabels(self.project.data["labels"])
                ax.set_ylabel('Values', color='#CCCCCC', fontsize=12)
                ax.grid(True, alpha=0.2, color='#666666')
            
            ax.set_title(self.project.title, color='#FFFFFF', fontsize=18, weight='bold', pad=20)
            
            if chart_type != "Pie":
                ax.set_xlabel('Categories', color='#CCCCCC', fontsize=12)
            
            plt.tight_layout()
            self.canvas.draw()
        except Exception as e:
            print(f"Error updating chart: {e}")
            traceback.print_exc()
    
    def update_dia_code_display(self):
        dia_content = self.project.to_dia_format()
        self.dia_code_text.delete("1.0", "end")
        self.dia_code_text.insert("1.0", dia_content)
    
    def apply_dia_code(self):
        try:
            code_text = self.dia_code_text.get("1.0", "end-1c")
            
            # Temporary project to test code
            temp_project = DiagramProject()
            if temp_project.from_dia_format(code_text):
                # Code is valid, update main project
                self.project.from_dia_format(code_text)
                
                # Update UI
                self.chart_type.set(self.project.chart_type)
                self.color_scheme.set(self.project.color_scheme)
                self.chart_title_entry.delete(0, 'end')
                self.chart_title_entry.insert(0, self.project.title)
                
                self.update_data_display()
                self.update_chart()
                self.save_project()
                
                messagebox.showinfo("Success", ".dia code successfully applied!")
            else:
                messagebox.showerror("Error", "Invalid .dia code!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error applying code: {str(e)}")
    
    def save_project(self):
        try:
            self.start_menu.save_project(self.project)
            return True
        except Exception as e:
            print(f"Error saving project: {e}")
            messagebox.showerror("Error", f"Project could not be saved: {str(e)}")
            return False
    
    def save_chart(self):
        """Saves the chart as an image (PNG, JPG, JPEG, PDF, SVG)"""
        if not self.project.data["labels"]:
            messagebox.showwarning("No Data", "Please enter data first!")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("PNG Files", "*.png"), 
                ("JPEG Files", "*.jpg"),
                ("JPEG Files", "*.jpeg"),
                ("PDF Files", "*.pdf"),
                ("SVG Files", "*.svg"),
                ("All Files", "*.*")
            ],
            title="Save Chart as Image"
        )
        
        if file_path:
            try:
                self.figure.savefig(file_path, dpi=300, facecolor='#2B2B2B', 
                                  edgecolor='none', bbox_inches='tight')
                messagebox.showinfo("Success", f"Chart saved at:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Chart could not be saved: {str(e)}")
    
    def toggle_fullscreen(self, event=None):
        self.is_fullscreen = not self.is_fullscreen
        self.attributes('-fullscreen', self.is_fullscreen)
        return "break"
    
    def exit_fullscreen(self, event=None):
        self.is_fullscreen = False
        self.attributes('-fullscreen', False)
        return "break"
    
    def on_closing(self):
        # Stop auto-save timer
        if self.auto_save_id:
            try:
                self.after_cancel(self.auto_save_id)
            except:
                pass  # Ignore errors when stopping timer
        
        # Perform final save
        self.save_project()
        
        # Return to start menu
        self.destroy()
        self.start_menu.show_menu()

if __name__ == "__main__":
    try:
        app = StartMenu()
        app.mainloop()
    except Exception as e:
        print(f"Error starting application: {e}")
        traceback.print_exc()
        messagebox.showerror("Error", f"The application could not be started: {str(e)}")