import socket
from tkinter import *
from tkinter import ttk

from google.auth.exceptions import TransportError
from google.oauth2 import service_account
from googleapiclient.discovery import build

from joint import mainjoint, AgeException, ShoeSizeException

# Authenticate with the service account
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive',
         'https://www.googleapis.com/auth/documents']
credentials = service_account.Credentials.from_service_account_file(
    'credentials.json', scopes=scope)
service = build('docs', 'v1', credentials=credentials)
drive_service = build('drive', 'v3', credentials=credentials)

edits = {}
rownum = None


def main(sheetName, selected_choices):
    global edits
    global rownum

    dobError_frame.pack_forget()
    shoeSize_frame.pack_forget()
    customLead_frame.pack_forget()
    main_Frame.pack(**main_frame_info)
    message_label.grid_forget()

    if rownum is not None:
        paramater3 = int(rownum)
    else:
        paramater3 = ""

    message_style.configure("message.TLabel", foreground="green")
    message_label.configure(text="Running")
    message_label.grid(row=2, column=2)
    window.update()
    print(sheetName)
    print(selected_choices)

    try:
        mainjoint(sheetName, selected_choices, paramater3, credentials, service, drive_service, edits)
    except AgeException:
        main_Frame.pack_forget()
        dobError_frame.pack()
        return
    except ShoeSizeException:
        main_Frame.pack_forget()
        shoeSize_frame.pack()
        return
    except (TransportError, socket.gaierror):
        message_style.configure("message.TLabel", foreground="red")
        message_label.configure(text="A Connection Error Occurred")
        message_label.grid(row=2, column=2, columnspan=4, sticky='w')
        return

    message_style.configure("message.TLabel", foreground="green")
    message_label.configure(text="Done")
    window.update()
    print("all leads are done")
    edits = {}
    rownum = None
    dob_entry.delete(0, 'end')
    shoeSize_entry.delete(0, 'end')


def mainFrame_check():
    selected_choices = [choices[i] for i, var in enumerate(checkbox_vars) if var.get() == 1]
    if len(selected_choices) == 0:
        message_style.configure("message.TLabel", foreground="red")
        message_label.configure(text="Please select at least one user")
        message_label.grid(row=2, column=2, columnspan=4, sticky='w')
        return

    sheetName = sheets_Combobox.get()
    if sheetName == "Select Sheet":
        message_style.configure("message.TLabel", foreground="red")
        message_label.configure(text="Please select a sheet")
        message_label.grid(row=2, column=2, columnspan=4, sticky='w')
        return
    main(sheetName, selected_choices)


def customLead_check():
    global rownum
    customMessage_Label.grid_forget()

    if not row_entry.get().strip().isdigit():
        customMessage_style.configure("customMessage.TLabel", foreground="red", font=("Segoe UI", 18, "bold"))
        customMessage_Label.configure(text="Please enter a valid row number")
        customMessage_Label.grid(row=3, column=1, sticky='sw', padx=10, ipadx=5, ipady=5, columnspan=5)
        return
    if customSheets_Combobox.get() == "Select Sheet":
        customMessage_style.configure("customMessage.TLabel", foreground="red", font=("Segoe UI", 18, "bold"))
        customMessage_Label.configure(text="Please select a sheet")
        customMessage_Label.grid(row=3, column=1, sticky='sw', padx=10, ipadx=5, ipady=5, columnspan=5)
        return

    rownum = row_entry.get().strip()
    main(customSheets_Combobox.get(), choices)


def customLeadSwitch():
    main_Frame.pack_forget()
    customSheets_Combobox.set("Select Sheet")
    fields_Combobox.set("Select Field")
    field_entry.delete(0, 'end')
    row_entry.delete(0, 'end')
    customLead_frame.pack()


def dobErrorInput():
    selected_choices = [choices[i] for i, var in enumerate(checkbox_vars) if var.get() == 1]
    edits["patdob"] = dob_entry.get().strip()
    main(sheets_Combobox.get(), selected_choices)


def shoeErrorInput():
    selected_choices = [choices[i] for i, var in enumerate(checkbox_vars) if var.get() == 1]
    edits["patshoesize"] = shoeSize_entry.get().strip()
    main(sheets_Combobox.get(), selected_choices)


def addField():
    customMessage_Label.grid_forget()
    if fields_Combobox.get() == "Select Field":
        customMessage_style.configure("customMessage.TLabel", foreground="red", font=("Segoe UI", 18, "bold"))
        customMessage_Label.configure(text="Please select a field to add")
        customMessage_Label.grid(row=3, column=1, sticky='sw', padx=10, ipadx=5, ipady=5, columnspan=5)
    else:
        customMessage_style.configure("customMessage.TLabel", foreground="green", font=("Segoe UI", 18, "bold"))
        customMessage_Label.configure(text="Field Added Successfully")
        customMessage_Label.grid(row=3, column=1, sticky='sw', padx=10, ipadx=5, ipady=5, columnspan=5)
        edits[fields_Combobox.get()] = field_entry.get().strip()


def returnMainFrame():
    global edits
    edits = {}
    customMessage_Label.grid_forget()
    dobError_frame.pack_forget()
    shoeSize_frame.pack_forget()
    customLead_frame.pack_forget()
    main_Frame.pack(**main_frame_info)
    message_label.grid_forget()


# window
window = Tk()
window.title('Leads Update')
window.geometry('1100x660')
window.configure(bg="gray")
window.wm_state("zoomed")

# Title
titleLabel_style = ttk.Style()
titleLabel_style.configure("titleLabel.TLabel", font=("8514oem", 25))
title_Label = ttk.Label(window, text="Automator", style="titleLabel.TLabel", anchor="center")
title_Label.pack(pady=50, ipadx=10, ipady=10)

# Main frame
mainFrame_style = ttk.Style()
mainFrame_style.configure("mainFrame.TFrame", background="gray")
main_Frame = ttk.Frame(window, style="mainFrame.TFrame")
main_Frame.pack(expand=True, fill='both')
main_frame_info = main_Frame.pack_info()

# grid in main frame 5x5
main_Frame.columnconfigure((0, 1, 2, 3, 4), weight=1, uniform='a')
main_Frame.rowconfigure((0, 1, 2, 3, 4), weight=1, uniform='a')

# main frame widgets
sheetLabel_style = ttk.Style()
sheetLabel_style.configure("userLabel.TLabel", font=("Arabic Transparent", 15))
user_Label = ttk.Label(main_Frame, text="Choose User(s)", style="userLabel.TLabel", anchor="center")

choices = ["re", "yy", "ya", "    "]
checkbox_vars = []
checkBoxes_frame = ttk.Frame(main_Frame, style="mainFrame.TFrame")
for value in choices:
    var = IntVar()
    checkbox = Checkbutton(checkBoxes_frame, text=value, variable=var, width=4)
    checkbox.pack()
    checkbox_vars.append(var)

sheet_Label = ttk.Label(main_Frame, text="Choose Sheet", style="userLabel.TLabel", anchor="center")

sheets = ["Dani", "HS", "Mohammad", "OS", "Pankaj"]
combo_var = StringVar()
sheets_Combobox = ttk.Combobox(main_Frame, textvariable=combo_var, values=sheets, state="readonly")
sheets_Combobox.set("Select Sheet")

run_button = ttk.Button(main_Frame, text="Run", command=mainFrame_check)

message_style = ttk.Style()
message_style.configure("message.TLabel", foreground="green", font=("Segoe UI", 25, "bold"))
message_label = ttk.Label(main_Frame, text="Running", style="message.TLabel")

customLead_button = ttk.Button(main_Frame, text="Custom Lead", command=customLeadSwitch)

# main frame layout
user_Label.grid(row=0, column=1, sticky='sw', padx=50, ipadx=5, ipady=5)
checkBoxes_frame.grid(row=1, column=1, sticky='nws', padx=50, pady=20, rowspan=3)
sheet_Label.grid(row=0, column=2, sticky='sw', padx=50, ipadx=5, ipady=5)
sheets_Combobox.grid(row=1, column=2, sticky='nw', padx=50, pady=20)
run_button.grid(row=3, column=1, sticky='nw', padx=75)
customLead_button.grid(row=3, column=2, sticky='nw', padx=75)

# DOB error frame
dobError_frame = ttk.Frame(window, style="mainFrame.TFrame")
dobError_frame.columnconfigure((0, 1, 2, 3, 4), weight=1, uniform='a')
dobError_frame.rowconfigure((0, 1, 2, 3, 4), weight=1, uniform='a')

# Dob frame widgets
dob_label = ttk.Label(dobError_frame, text="Please enter the correct DOB", style="userLabel.TLabel", anchor="center")
dob_entry = ttk.Entry(dobError_frame)
dob_button = ttk.Button(dobError_frame, text="Submit", command=dobErrorInput)

# Dob frame layout
dob_label.grid(row=0, column=1, sticky='sw', ipadx=5, ipady=5, columnspan=3)
dob_entry.grid(row=1, column=1, sticky='nw', pady=20)
dob_button.grid(row=2, column=1, sticky='nw')

# Shoe size error frame
shoeSize_frame = ttk.Frame(window, style="mainFrame.TFrame")
shoeSize_frame.columnconfigure((0, 1, 2, 3, 4), weight=1, uniform='a')
shoeSize_frame.rowconfigure((0, 1, 2, 3, 4), weight=1, uniform='a')

# Shoe size frame widgets
shoeSize_label = ttk.Label(shoeSize_frame, text="Please enter the correct Shoe size", style="userLabel.TLabel",
                           anchor="center")
shoeSize_entry = ttk.Entry(shoeSize_frame)
shoeSize_button = ttk.Button(shoeSize_frame, text="Submit", command=shoeErrorInput)

# Dob frame layout
shoeSize_label.grid(row=0, column=1, sticky='sw', ipadx=5, ipady=5, columnspan=3)
shoeSize_entry.grid(row=1, column=1, sticky='nw', pady=20)
shoeSize_button.grid(row=2, column=1, sticky='nw')

# custom lead frame (specify row and some of the data)
customLead_frame = ttk.Frame(window, style="mainFrame.TFrame")
customLead_frame.columnconfigure((0, 1, 2, 3, 4), weight=1, uniform='a')
customLead_frame.rowconfigure((0, 1, 2, 3, 4), weight=1, uniform='a')

# custom lead frame widgets
row_label = ttk.Label(customLead_frame, text="Choose Row", style="userLabel.TLabel", anchor="center")
row_entry = ttk.Entry(customLead_frame)

fields = [
    "drname", "drsigname", "npidr", "dradd2", "dradd3", "dradd4",
    "patfirstname", "patlastname", "patmed", "patadd1", "city", "state",
    "zipcode", "patadd3", "patphone", "patht", "patwt", "patage",
    "patdob", "patgender", "patsizew", "patorderdate", "patpaintr",
    "patpainlevel", "patpainyear", "patpainworse", "patpaincause",
    "patipadd", "patshoesize", "patinjury", "patsurgery", "patweakness",
    "pattwist", "pattogether", "patoneleg", "patbend", "pattime", "painfrequency"
]

field_label = ttk.Label(customLead_frame, text="Choose field to edit", style="userLabel.TLabel", anchor="center")

customLead_var = StringVar()
fields_Combobox = ttk.Combobox(customLead_frame, textvariable=customLead_var, values=fields, state="readonly")
fields_Combobox.set("Select field")

field_entry = ttk.Entry(customLead_frame)

add_button = ttk.Button(customLead_frame, text="Add field", command=addField)

customMessage_style = ttk.Style()
customMessage_style.configure("customMessage.TLabel", foreground="red", font=("Segoe UI", 18, "bold"))
customMessage_Label = ttk.Label(customLead_frame, text="Please select a field to add", style="customMessage.TLabel",
                                anchor="center")

customRun_button = ttk.Button(customLead_frame, text="Run", command=customLead_check)

customBack_button = ttk.Button(customLead_frame, text="Go Back", command=returnMainFrame)

customSheet_Label = ttk.Label(customLead_frame, text="Choose Sheet", style="userLabel.TLabel", anchor="center")
CustomCombo_var = StringVar()
customSheets_Combobox = ttk.Combobox(customLead_frame, textvariable=CustomCombo_var, values=sheets, state="readonly")
customSheets_Combobox.set("Select Sheet")

# custom lead frame layout
row_label.grid(row=0, column=0, sticky='sw', padx=50, ipadx=5, ipady=5)
row_entry.grid(row=1, column=0, sticky='nw', padx=50, pady=20)
field_label.grid(row=0, column=1, sticky='sw', padx=10, ipadx=5, ipady=5)
fields_Combobox.grid(row=1, column=1, sticky='nw', padx=10, pady=20)
field_entry.grid(row=1, column=1, sticky='n', padx=10, pady=20, columnspan=2)
add_button.grid(row=1, column=2, sticky='n', padx=10, pady=20)
customRun_button.grid(row=4, column=0, sticky='nw', padx=50, pady=20)
customBack_button.grid(row=4, column=1, sticky='nw', padx=10, pady=20)
customSheet_Label.grid(row=0, column=3, sticky='n', padx=10, pady=20)
customSheets_Combobox.grid(row=1, column=3, sticky='n', padx=10, pady=20)

window.mainloop()
