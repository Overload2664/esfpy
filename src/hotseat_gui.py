import os
import sys

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
# from PIL import Image, ImageTk # For displaying images if a file is chosen

from ESFReader import ESFReader
from ESFWriter import ESFWriter
from ESFtypes import from_uintvart, to_uintvart, Magiccode
from ESF import ESF
from ESFHotseat import ESFHotseat

SUPPORTED_GAMES = [
    ("shogun", "Shogun II"),
    ("rome", "Rome II"),
    ("attila", "Attila")
]

DEFAULT_GAME = "shogun"

class HotseatGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.game_var = tk.StringVar(value=DEFAULT_GAME)
        self.hotseat_reader = None
        self.selected_file = None
        self.vision = ""
        self.turn_order = -1
        self.all_factions = []
        self.all_playability = []
        self.all_humanity = []
        

        self.title("Warscape Hotseat Tool")
        self.geometry("500x600") # Increased height for preview
        self.resizable(True, True)
        self.all_widgets = []
        self._create_file_widgets()

    def _create_file_widgets(self):
        self.remove_widgets()

        self.file_frame = ttk.LabelFrame(self, text="Save File Selection")
        self.select_button = ttk.Button(self.file_frame, text="Choose Save File", command=self.choose_file)
        self.file_label = ttk.Label(self.file_frame, text="No file selected", width=50)
        self.all_widgets += [self.file_frame, self.select_button, self.file_label]

        # self.title_label.pack(pady=10)
        self.file_frame.pack(fill="x", padx=20, pady=10)
        self.select_button.grid(row=0, column=0, padx=5, pady=5)
        self.file_label.grid(row=0, column=1, padx=5, pady=5)

        for game in SUPPORTED_GAMES:
            code_name = game[0]
            title_name = game[1]
            radio_button = tk.Radiobutton(self, text=title_name, variable=self.game_var, value=code_name)

            self.all_widgets.append(radio_button)
            radio_button.pack()

    def choose_file(self):
        """Open file dialog, display selected file, and update UI."""
        chosen = filedialog.askopenfilename(title="Select a file")
        if chosen:
            self.selected_file = chosen
            
            if not os.path.exists(self.selected_file):
                messagebox.showerror(
                    "Error",  # Title of the message box
                    f"An error occurred: {e}\n\n Please check the file path and try again."
                )

            try:
                self.hotseat_reader = ESFHotseat(game=self.game_var.get())
                self.hotseat_reader.read_file(self.selected_file)
                self._get_info()
                self._create_options_widgets()
            except Exception as e:
                messagebox.showerror(
                    "File Read Error",
                    f"Could not read the save file, maybe a wrong file was chosen? \n\n Full error: {e}"
                )
        else:
            self.file_label.config(text="No file selected")

    def _create_options_widgets(self):
        self.remove_widgets()
        self.options_frame = ttk.LabelFrame(self, text="Options")

        self.get_all_factions_button = ttk.Button(self.options_frame, text="Get All Factions", command=self._list_all_factions_widgets)

        self.vision_button = ttk.Button(self.options_frame, text="Set Vision", command=self._set_vision_widgets)
        self.playable_button = ttk.Button(self.options_frame, text="Mark Playables", command=self._set_playable_widgets)
        self.humanity_button = ttk.Button(self.options_frame, text="Mark Humanity", command=self._set_human_widgets)
        self.all_playable_button = ttk.Button(self.options_frame, text="Mark All As Playable", command=self.mark_all_as_playable)
        self.no_all_playable_button = ttk.Button(self.options_frame, text="Mark All As Not Playable", command=self.mark_all_as_not_playable)
        self.all_human_button = ttk.Button(self.options_frame, text="Mark All As Human", command=self.mark_all_as_human)
        self.no_all_human_button = ttk.Button(self.options_frame, text="Mark All As Not Human", command=self.mark_all_as_not_human)
        self.change_turn_button = ttk.Button(self.options_frame, text="Change Turn", command=self._change_turn_widgets)

        self.save_button = ttk.Button(self, text="Save", command=self.save_to_file)
        self.back_button = ttk.Button(self, text="Back", command=self._create_file_widgets)

        self.all_widgets += [self.options_frame, self.get_all_factions_button, self.all_playable_button, self.no_all_playable_button, self.all_human_button, self.no_all_human_button, self.save_button, self.back_button, self.playable_button, self.humanity_button, self.vision_button, self.change_turn_button]

        # self.title_label.pack(pady=10)
        self.options_frame.pack(fill="x", padx=20, pady=10)
        self.get_all_factions_button.pack(pady=10)
        self.vision_button.pack(pady=10)
        self.playable_button.pack(pady=10)
        self.humanity_button.pack(pady=10)
        self.all_playable_button.pack(pady=10)
        self.no_all_playable_button.pack(pady=10)
        self.all_human_button.pack(pady=10)
        self.no_all_human_button.pack(pady=10)
        self.change_turn_button.pack(pady=10)
        
        self.save_button.pack(pady=10)
        self.back_button.pack(pady=10)

    def _list_all_factions_widgets(self):
        self.remove_widgets()
            
        # --- Listbox Widget ---
        self.listbox_frame = ttk.Frame(self)
        self.listbox_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        self.all_widgets.append(self.listbox_frame)

        # Scrollbar for the Listbox
        self.scrollbar = ttk.Scrollbar(self.listbox_frame, orient=tk.VERTICAL)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # The Listbox itself
        self.listbox = tk.Listbox(
            self.listbox_frame,
            yscrollcommand=self.scrollbar.set, # Link scrollbar to listbox
            selectmode=tk.SINGLE, # or tk.MULTIPLE, tk.BROWSE, tk.EXTENDED
            height=10 # Number of visible lines
        )
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Configure scrollbar to control the listbox
        self.scrollbar.config(command=self.listbox.yview)

        if(self.turn_order < len(self.all_factions)):
            self.listbox.insert(tk.END, "Turn Order: " + self.all_factions[self.turn_order])
        self.listbox.insert(tk.END, "Turn Number: " + str(self.turn_order + 1))
        self.listbox.insert(tk.END, "Vision: " + self.vision)
        for faction_index in range(len(self.all_factions)):
            is_playable = "is playable" if self.all_playability[faction_index] else "not playable"
            is_human = "is human" if self.all_humanity[faction_index] else "not human"
            info = str(faction_index + 1) + ". " + self.all_factions[faction_index] + ": " + is_playable + ", " + is_human
            self.listbox.insert(tk.END, info)

        self.back_button = ttk.Button(self, text="Back", command=self._create_options_widgets)
        self.back_button.pack(side=tk.LEFT, padx=5)
        self.all_widgets.append(self.back_button)

    def _change_turn_widgets(self):
        self.remove_widgets()

        turn_label = tk.Label(self, text="Turn:")
        turn_label.pack()
        self.all_widgets.append(turn_label)
            
        turn_entry = tk.Entry(self)
        turn_entry.pack()
        self.all_widgets.append(turn_entry)

        self.back_button = ttk.Button(self, text="Back", command=self._create_options_widgets)
        self.back_button.pack(pady=10)
        self.all_widgets.append(self.back_button)

        def save_turn_number():
            self.turn_order = int(turn_entry.get()) - 1

        self.save_button = ttk.Button(self, text="Save", command=save_turn_number)
        self.save_button.pack(pady=2)
        self.all_widgets.append(self.save_button)

    def _set_vision_widgets(self):
        self.remove_widgets()
        vision_var = tk.StringVar(value=self.vision)

        # Create a frame to hold the radio buttons and scrollbar
        radio_frame = tk.Frame(self)
        radio_frame.pack(fill=tk.BOTH, expand=True)

        # Create a canvas inside the frame
        self.canvas = tk.Canvas(radio_frame)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Add a scrollbar to the canvas
        scrollbar = ttk.Scrollbar(radio_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Configure the canvas to use the scrollbar
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.bind('<Configure>', lambda e: self.canvas.configure(scrollregion = self.canvas.bbox("all")))

        # Create a frame inside the canvas to hold the radio buttons
        self.inner_frame = tk.Frame(self.canvas)

        # Add the inner frame to the canvas window
        self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")

        self.all_widgets += [radio_frame, self.canvas, scrollbar, self.inner_frame]

        for faction_index in range(len(self.all_factions)):
            faction = self.all_factions[faction_index]
            # Parent the radio buttons to the inner_frame
            radio_button = tk.Radiobutton(self.inner_frame, text=f"{faction_index + 1}. {faction}", variable=vision_var, value=faction)

            self.all_widgets.append(radio_button)
            radio_button.pack()

        self.back_button = ttk.Button(self, text="Back", command=self._create_options_widgets)
        self.back_button.pack()
        self.all_widgets.append(self.back_button)

        def save_vision():
            self.vision = vision_var.get()

        self.save_button = ttk.Button(self, text="Save", command=save_vision)
        self.save_button.pack()
        self.all_widgets.append(self.save_button)

    def _set_playable_widgets(self):
        self.remove_widgets()
        bool_vars = []
        # check_buttons = [] # This was commented out, so I'm keeping it commented.

        # Create a frame to hold the checkbuttons and scrollbar
        check_button_frame = tk.Frame(self)
        check_button_frame.pack(fill=tk.BOTH, expand=True)

        # Create a canvas inside the frame
        self.canvas = tk.Canvas(check_button_frame)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Add a scrollbar to the canvas
        scrollbar = ttk.Scrollbar(check_button_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Configure the canvas to use the scrollbar
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.bind('<Configure>', lambda e: self.canvas.configure(scrollregion = self.canvas.bbox("all")))

        # Create a frame inside the canvas to hold the checkbuttons
        self.inner_frame = tk.Frame(self.canvas)

        # Add the inner frame to the canvas window
        self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")
        self.all_widgets += [check_button_frame, self.canvas, scrollbar, self.inner_frame]

        for faction_index in range(len(self.all_factions)):
            bool_var = tk.BooleanVar(value=self.all_playability[faction_index])
            # Parent the checkbuttons to the inner_frame
            check_button = tk.Checkbutton(self.inner_frame, text=f"{faction_index + 1}. {self.all_factions[faction_index]}", variable=bool_var)

            # check_buttons.append(check_button) # Keeping this commented as in the original
            bool_vars.append(bool_var)
            self.all_widgets.append(check_button)
            check_button.pack()

        self.back_button = ttk.Button(self, text="Back", command=self._create_options_widgets)
        self.back_button.pack()
        self.all_widgets.append(self.back_button)

        def save_playability():
            for faction_index in range(len(self.all_factions)):
                bool_var = bool_vars[faction_index]
                self.all_playability[faction_index] = bool_var.get()

        self.save_button = ttk.Button(self, text="Save", command=save_playability)
        self.save_button.pack()
        self.all_widgets.append(self.save_button)

    def _set_human_widgets(self):
        self.remove_widgets()
        bool_vars = []

        # Create a frame to hold the checkbuttons and scrollbar
        check_button_frame = tk.Frame(self)
        check_button_frame.pack(fill=tk.BOTH, expand=True)

        # Create a canvas inside the frame
        self.canvas = tk.Canvas(check_button_frame)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Add a scrollbar to the canvas
        scrollbar = ttk.Scrollbar(check_button_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Configure the canvas to use the scrollbar
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.bind('<Configure>', lambda e: self.canvas.configure(scrollregion = self.canvas.bbox("all")))

        # Create a frame inside the canvas to hold the checkbuttons
        self.inner_frame = tk.Frame(self.canvas)

        # Add the inner frame to the canvas window
        self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")
        self.all_widgets += [check_button_frame, self.canvas, scrollbar, self.inner_frame]

        for faction_index in range(len(self.all_factions)):
            bool_var = tk.BooleanVar(value=self.all_humanity[faction_index])
            # Parent the checkbuttons to the inner_frame
            check_button = tk.Checkbutton(self.inner_frame, text=f"{faction_index + 1}. {self.all_factions[faction_index]}", variable=bool_var)

            bool_vars.append(bool_var)
            self.all_widgets.append(check_button)
            check_button.pack()

        self.back_button = ttk.Button(self, text="Back", command=self._create_options_widgets)
        self.back_button.pack()
        self.all_widgets.append(self.back_button)

        def save_humanity():
            for faction_index in range(len(self.all_factions)):
                bool_var = bool_vars[faction_index]
                self.all_humanity[faction_index] = bool_var.get()

        self.save_button = ttk.Button(self, text="Save", command=save_humanity)
        self.save_button.pack()
        self.all_widgets.append(self.save_button)

    def save_to_file(self):
        self._save_info()

        filetypes = (
            ("Save files", "*.save"),
            ("All files", "*.*")
        )

        filepath = filedialog.asksaveasfilename(
            title="Save File As",
            initialdir=os.path.curdir,  # You can set a default directory, e.g., os.path.expanduser("~") for home dir
            filetypes=filetypes,
            defaultextension=".save",
            confirmoverwrite=True # This is the default, but good to be explicit
        )

        if filepath:
            # User selected a file path.
            self.saved_filepath = filepath
            self.hotseat_reader.write_file(filepath)
            messagebox.showinfo(
                "Success",
                f"File saved to: \n{self.saved_filepath}"
            )
        else:
            messagebox.showerror(
                "Error",
                "No file was selected."
            )

    def mark_all_as_playable(self):
        for i in range(len(self.all_playability)):
            self.all_playability[i] = True

    def mark_all_as_not_playable(self):
        for i in range(len(self.all_playability)):
            self.all_playability[i] = False

    def mark_all_as_human(self):
        for i in range(len(self.all_humanity)):
            self.all_humanity[i] = True

    def mark_all_as_not_human(self):
        for i in range(len(self.all_humanity)):
            self.all_humanity[i] = False

    def _get_info(self):
        self.all_factions = self.hotseat_reader.get_all_factions()
        self.vision = self.hotseat_reader.get_vision()
        self.turn_order = self.hotseat_reader.get_current_turn()

        self.all_playability = []
        self.all_humanity = []
        for faction in self.all_factions:
            self.all_playability.append(self.hotseat_reader.get_factions_playability([faction])[0][1])
            self.all_humanity.append(self.hotseat_reader.get_factions_nature([faction])[0][1])

    def _save_info(self):
        self.hotseat_reader.choose_vision(self.vision)
        self.hotseat_reader.change_turn(self.turn_order)
        for i in range(len(self.all_factions)):
            faction = self.all_factions[i]

            self.hotseat_reader.put_shroud([faction])
            self.hotseat_reader.put_cam_missions([faction])
            
            self.hotseat_reader.mark_factions_as_playable([faction], self.all_playability[i])
            self.hotseat_reader.mark_factions_as_human([faction], self.all_humanity[i])

    def remove_widgets(self):
        for widget in self.all_widgets:
            widget.destroy()

        self.all_widgets = []

if __name__ == "__main__":
    app = HotseatGUI()
    app.mainloop()

    sys.exit(0)