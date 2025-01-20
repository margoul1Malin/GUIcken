from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty
from kivy.clock import mainthread
from kivy.graphics import Color, Rectangle
from kivy.core.text import LabelBase
import serial.tools.list_ports
import os, subprocess
import threading
from kivy.core.window import Window
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Line
import time

LabelBase.register(name="OswaldBoldZer", fn_regular="fonts/Oswald/static/Oswald-Bold.ttf")
LabelBase.register(name="Jersey15Normal", fn_regular="fonts/Jersey15/Jersey15-Regular.ttf")



def find_chicken():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if "Pico" in port.description or "ttyACM" in port.device:
            return port.device
    return None


class ColoredGridLayout(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            # Définir la couleur de fond (ici, un rouge)
            Color(0, 0, 0, 0)  # RGB (noir ici)
            # Dessiner un rectangle de la taille du GridLayout
            self.rect = Rectangle(size=self.size, pos=self.pos)

        
        
        # Mettre à jour le rectangle à chaque changement de taille ou de position
        self.bind(size=self.update_rect, pos=self.update_rect)
    
    def update_rect(self, *args):
        # Met à jour la position et la taille du rectangle pour correspondre à celle du GridLayout
        self.rect.pos = self.pos
        self.rect.size = self.size




class ConfigEditor(BoxLayout):
    
    mode_var = StringProperty("")
    lang_var = StringProperty("")
    target_sys_var = StringProperty("")
    
    # Recon Mode variables
    server_type_var = StringProperty("")
    server_var = StringProperty("")
    ssh_server_var = StringProperty("")
    ssh_password_var = StringProperty("")
    ssh_server_folder_var = StringProperty("")

    # ReverseShell Mode variables
    rhost_var = StringProperty("")
    rport_var = StringProperty("")
    shell_type_var = StringProperty("")

    # PKI Mode variables
    pki_username_var = StringProperty("")
    pki_password_var = StringProperty("")

    # Custom Mode variables
    custom_inline_entry_var = StringProperty("")

    # Upload Mode variables
    upload_cmd_var = StringProperty("")
    remote_file_var = StringProperty("")
    output_file_var = StringProperty("")
    automatic_var = StringProperty("")
    auto_tool_var = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", **kwargs)
        self.layout = ColoredGridLayout(cols=2, spacing=10, padding=10)
        self.optionsLayout = ColoredGridLayout(cols=2, spacing=10, padding=10)
        self.layout1 = BoxLayout(size_hint_y=None, height=50)
        self.layout0_5 = ColoredGridLayout(cols=1, spacing=10, padding=10)
        self.save_button_added = False
        self.layout05Added = False
        



        # Mode Spinner
        self.modeLabel = Label(text="Mode")
        self.modeLabel.font_name = "OswaldBoldZer"
        self.modeLabel.font_size = 20
        self.modeLabel.height = 40
        self.modeLabel.size_hint = (1, None)
        self.layout.add_widget(self.modeLabel)
        
        self.mode_spinner = Spinner(
            text="Recon",
            values=["Recon", "Upload", "PKI", "ReverseShell", "Custom"],
            height=40,
            size_hint=(1,None)
        )

        self.mode_spinner.background_normal = ""  # Désactiver la texture normale
        self.mode_spinner.background_color = (0.2, 0.8, 0.8, 1)  # Turquoise
        self.mode_spinner.color = (1, 1, 1, 1)
        self.mode_spinner.bind(text=self.on_mode_change)
        self.mode_spinner.font_name="Jersey15Normal"
        self.mode_spinner.font_size=20
        self.layout.add_widget(self.mode_spinner)
        
        # Language Spinner
        self.langLabel = Label(text="Language")
        self.langLabel.font_name = "OswaldBoldZer"
        self.langLabel.font_size = 20
        self.langLabel.height = 40
        self.langLabel.size_hint = (1, None)
        self.layout.add_widget(self.langLabel)

        self.lang_spinner = Spinner(text="FR", 
                                    values=["FR", "US"], 
                                    height=40, 
                                    size_hint=(1,None))
        
        self.lang_spinner.background_normal = ""  # Désactiver la texture normale
        self.lang_spinner.background_color = (0.2, 0.8, 0.8, 1)  # Rouge Corail
        self.lang_spinner.color = (1, 1, 1, 1)
        self.lang_spinner.font_name="Jersey15Normal"
        self.lang_spinner.font_size=20
        self.layout.add_widget(self.lang_spinner)

        # Target System Spinner
        self.targetSysLabel = Label(text="Target System")
        self.targetSysLabel.font_name = "OswaldBoldZer"
        self.targetSysLabel.font_size = 20
        self.targetSysLabel.height = 40
        self.targetSysLabel.size_hint = (1, None)
        self.layout.add_widget(self.targetSysLabel)

        self.target_sys_spinner = Spinner(text="Linux", 
                                          values=["Linux", "Windows", "Mac"], 
                                          height=40, 
                                          size_hint=(1,None))
        
        self.target_sys_spinner.background_normal = ""  # Désactiver la texture normale
        self.target_sys_spinner.background_color = (0.2, 0.8, 0.8, 1)  # Jaune Or
        self.target_sys_spinner.color = (1, 1, 1, 1)
        self.target_sys_spinner.font_name="Jersey15Normal"
        self.target_sys_spinner.bind(text=self.on_Sys_ShellUpdate)
        self.target_sys_spinner.font_size=20
        self.layout.add_widget(self.target_sys_spinner)

        with self.target_sys_spinner.canvas.after:
            Color(1, 1, 1, 1)  # Couleur de la ligne
            # Ligne en dessous du spinner
            Line(rectangle=(2, -8, self.target_sys_spinner.width, 2), width=2)

        # Add the layouts to the BoxLayout
        self.add_widget(self.layout)
        self.add_widget(self.layout0_5)
        self.add_widget(self.layout1)
        
        self.chicken = find_chicken()
        if not self.chicken:
            self.layout.add_widget(Label(text="Pico not found!", color=(1, 0, 0, 1)))

        # Initial update of fields
        self.update_fields()

    def on_mode_change(self, spinner, text):
        self.mode_var = text
        self.update_fields()

    shell_Options = {
    "Linux": ["Linux Python3 Shell", "Linux Shell C/C++", "Metasploit Staged Shell", "Metasploit Stageless Shell", "Lua Shell (Lua Required)"],
    "Mac": ["Mac Python3 Shell", "Mac Shell C/C++"],
    "Windows": ["Windows ConPty Shell", "PowerReverseShell"]
    }

    def on_Sys_ShellUpdate(self, spinner, text):
        if self.mode_var == "ReverseShell":
            self.target_sys_var = text
            self.update_ShellFields()

    def update_ShellFields(self):
        # Mise à jour des valeurs du spinner pour le type de shell en fonction du système
        if self.target_sys_var in self.shell_Options:
            shell_values = self.shell_Options[self.target_sys_var]
        else:
            shell_values = []  # Liste vide si le système n'est pas trouvé

        self.shell_type_input.values = shell_values  # Mise à jour des valeurs du spinner
        self.shell_type_input.text = shell_values[0] if shell_values else ""  # Sélection du premier shell par défaut

    def update_fields(self):
        # Clear all dynamically added widgets except the spinners and labels
        self.layout.clear_widgets()
        self.layout0_5.clear_widgets()

        # Add common fields (spinners and labels)
        self.layout.add_widget(self.modeLabel)
        self.layout.add_widget(self.mode_spinner)

        self.layout.add_widget(self.langLabel)
        self.layout.add_widget(self.lang_spinner)

        self.layout.add_widget(self.targetSysLabel)
        self.layout.add_widget(self.target_sys_spinner)

        # Update based on the mode selection
        if self.mode_var == "Recon":
            self.add_recon_fields()
        elif self.mode_var == "PKI":
            self.add_pki_fields()
        elif self.mode_var == "ReverseShell":
            self.add_reverse_shell_fields()
        elif self.mode_var == "Upload":
            self.add_upload_fields()
        elif self.mode_var == "Custom":
            self.add_custom_fields()

        

        # Add "Save Configuration" button after the fields
        if not self.save_button_added:
            self.add_save_button()
            self.save_button_added = True

    def add_save_button(self):
        # Ajout du bouton "Save Configuration" et utilisation de size_hint_x pour qu'il occupe toute la largeur
        self.saveConfigBtn = Button(text="Save Configuration", on_press=self.save_config)  # Prend toute la largeur de la fenêtre
        self.saveConfigBtn.height = 50
        self.saveConfigBtn.size_hint_y = None
        self.saveConfigBtn.background_normal = ""  # Désactiver la texture normale
        self.saveConfigBtn.background_color = (0.45, 0.68, 0.15, 1)  # Appliquer la couleur vive
        self.saveConfigBtn.color = (1, 1, 1, 1)
        self.saveConfigBtn.font_name="Jersey15Normal"
        self.saveConfigBtn.font_size=30
        self.layout1.add_widget(self.saveConfigBtn)

    def add_recon_fields(self):
    # Add Recon-related fields
        self.serverTypeLabel = Label(text="Choose Server Type (SSH or WEB(HTTPS))")
        self.serverTypeLabel.font_name = "OswaldBoldZer"
        self.serverTypeLabel.font_size = 15
        self.serverTypeLabel.height = 40
        self.serverTypeLabel.size_hint = (1, None)
        self.layout.add_widget(self.serverTypeLabel)
        
        self.server_type_input = Spinner(
            text="SSH",
            values=["SSH", "WEB"],  # Initialiser avec des valeurs vides pour les mettre à jour après
            height=40,
            size_hint=(1, None),
        )

        self.server_type_input.background_normal = ""  # Désactiver la texture normale
        self.server_type_input.background_color = (0.2, 0.8, 0.8, 1)  # Appliquer la couleur vive
        self.server_type_input.color = (1, 1, 1, 1)
        self.server_type_input.font_name = "Jersey15Normal"
        self.server_type_input.font_size = 20
        self.layout.add_widget(self.server_type_input)

        # Les champs à afficher si "WEB" est choisi dans le Spinner
        self.remoteServLabel = Label(text="Remote HTTPS Server")
        self.remoteServLabel.font_name = "OswaldBoldZer"
        self.remoteServLabel.font_size = 15
        self.remoteServLabel.height = 40
        self.remoteServLabel.size_hint = (1, None)

        self.server_input = TextInput(hint_text="(ex: https://myserv/VictimsReports)", size_hint=(1, None), height=30)
        self.server_input.font_name = "Jersey15Normal"
        self.server_input.font_size = 15
        self.server_input.height = 40

        # Champs à afficher si "SSH" est choisi dans le Spinner
        self.sshServLabel = Label(text="SSH Server")
        self.sshServLabel.font_name = "OswaldBoldZer"
        self.sshServLabel.font_size = 15
        self.sshServLabel.height = 40
        self.sshServLabel.size_hint = (1, None)

        self.ssh_server_input = TextInput(hint_text="root@10.10.10.10", size_hint=(1, None), height=30)
        self.ssh_server_input.font_name = "Jersey15Normal"
        self.ssh_server_input.font_size = 15
        self.ssh_server_input.height = 40

        self.sshPassLabel = Label(text="SSH Server Password")
        self.sshPassLabel.font_name = "OswaldBoldZer"
        self.sshPassLabel.font_size = 15
        self.sshPassLabel.height = 40
        self.sshPassLabel.size_hint = (1, None)

        self.ssh_password_input = TextInput(hint_text="root45!", password=True, size_hint=(1, None), height=30)
        self.ssh_password_input.font_name = "Jersey15Normal"
        self.ssh_password_input.font_size = 15
        self.ssh_password_input.height = 40

        self.sshFolderLabel = Label(text="SSH Server Folder")
        self.sshFolderLabel.font_name = "OswaldBoldZer"
        self.sshFolderLabel.font_size = 15
        self.sshFolderLabel.height = 40
        self.sshFolderLabel.size_hint = (1, None)

        self.ssh_server_folder_input = TextInput(hint_text="VictimsDumpReport", size_hint=(1, None), height=30)
        self.ssh_server_folder_input.font_name = "Jersey15Normal"
        self.ssh_server_folder_input.font_size = 15
        self.ssh_server_folder_input.height = 40

        # Fonction pour mettre à jour l'affichage des champs en fonction du choix du serveur
        def update_server_fields(*args):
            if self.server_type_input.text == "WEB":
                # Si "WEB" est sélectionné, afficher les champs relatifs à HTTPS
                self.layout.add_widget(self.remoteServLabel)
                self.layout.add_widget(self.server_input)

                # Masquer les champs relatifs à SSH
                if self.sshServLabel in self.layout.children:
                    self.layout.remove_widget(self.sshServLabel)
                if self.ssh_server_input in self.layout.children:
                    self.layout.remove_widget(self.ssh_server_input)
                if self.sshPassLabel in self.layout.children:
                    self.layout.remove_widget(self.sshPassLabel)
                if self.ssh_password_input in self.layout.children:
                    self.layout.remove_widget(self.ssh_password_input)
                if self.sshFolderLabel in self.layout.children:
                    self.layout.remove_widget(self.sshFolderLabel)
                if self.ssh_server_folder_input in self.layout.children:
                    self.layout.remove_widget(self.ssh_server_folder_input)
            elif self.server_type_input.text == "SSH":
                # Si "SSH" est sélectionné, afficher les champs relatifs à SSH
                self.layout.add_widget(self.sshServLabel)
                self.layout.add_widget(self.ssh_server_input)
                self.layout.add_widget(self.sshPassLabel)
                self.layout.add_widget(self.ssh_password_input)
                self.layout.add_widget(self.sshFolderLabel)
                self.layout.add_widget(self.ssh_server_folder_input)

                # Masquer les champs relatifs à HTTPS
                if self.remoteServLabel in self.layout.children:
                    self.layout.remove_widget(self.remoteServLabel)
                if self.server_input in self.layout.children:
                    self.layout.remove_widget(self.server_input)

        # Lier la fonction à l'événement de changement de sélection dans le Spinner
        self.server_type_input.bind(text=update_server_fields)

        # Appeler la fonction initialement pour prendre en compte la sélection par défaut
        update_server_fields()


    def add_reverse_shell_fields(self):
        # Ajout des champs ReverseShell
        self.hostLabel = Label(text="Remote Host (Your IP)")
        self.hostLabel.font_name = "OswaldBoldZer"
        self.hostLabel.font_size = 15
        self.hostLabel.height = 40
        self.hostLabel.size_hint = (1, None)
        self.layout.add_widget(self.hostLabel)

        self.rhost_input = TextInput(hint_text="(ex: 192.168.1.245)", size_hint=(1, None), height=30)
        self.rhost_input.font_name = "Jersey15Normal"
        self.rhost_input.font_size = 15
        self.rhost_input.height = 40
        self.layout.add_widget(self.rhost_input)

        self.portLabel = Label(text="Remote Port")
        self.portLabel.font_name = "OswaldBoldZer"
        self.portLabel.font_size = 15
        self.portLabel.height = 40
        self.portLabel.size_hint = (1, None)
        self.layout.add_widget(self.portLabel)

        self.rport_input = TextInput(hint_text="(ex: 4444)", size_hint=(1, None), height=30)
        self.rport_input.font_name = "Jersey15Normal"
        self.rport_input.font_size = 15
        self.rport_input.height = 40
        self.layout.add_widget(self.rport_input)

        self.shellTypeLabel = Label(text="Choose Shell Type")
        self.shellTypeLabel.font_name = "OswaldBoldZer"
        self.shellTypeLabel.font_size = 15
        self.shellTypeLabel.height = 40
        self.shellTypeLabel.size_hint = (1, None)
        self.layout.add_widget(self.shellTypeLabel)

        # Spinner pour le type de shell
        self.shell_type_input = Spinner(
            text="",
            values=["", ""],  # Initialiser avec des valeurs vides pour les mettre à jour après
            height=40,
            size_hint=(1, None)
        )

        self.shell_type_input.background_normal = ""  # Désactiver la texture normale
        self.shell_type_input.background_color = (0.45, 0.68, 0.15, 1)  # Appliquer la couleur vive
        self.shell_type_input.color = (1, 1, 1, 1)
        self.shell_type_input.font_name = "Jersey15Normal"
        self.shell_type_input.font_size = 20
        self.layout.add_widget(self.shell_type_input)

    def add_pki_fields(self):
        # Add PKI-related fields
        self.pkiUsernameLabel = Label(text="Username")
        self.pkiUsernameLabel.font_name = "OswaldBoldZer"
        self.pkiUsernameLabel.font_size = 15
        self.pkiUsernameLabel.height = 40
        self.pkiUsernameLabel.size_hint = (1, None)
        self.layout.add_widget(self.pkiUsernameLabel)

        self.pki_username_input = TextInput(hint_text="(ex: TonyMontana3)", size_hint=(1, None), height=30)
        self.pki_username_input.font_name = "Jersey15Normal"
        self.pki_username_input.font_size = 15
        self.pki_username_input.height = 40
        self.layout.add_widget(self.pki_username_input)

        self.pkiPassLabel = Label(text="Password")
        self.pkiPassLabel.font_name = "OswaldBoldZer"
        self.pkiPassLabel.font_size = 15
        self.pkiPassLabel.height = 40
        self.pkiPassLabel.size_hint = (1, None)
        self.layout.add_widget(self.pkiPassLabel)

        self.pki_password_input = TextInput(hint_text="(ex: FuckSosa:3)", password=True, size_hint=(1, None), height=30)
        self.pki_password_input.font_name = "Jersey15Normal"
        self.pki_password_input.font_size = 15
        self.pki_password_input.height = 40
        self.layout.add_widget(self.pki_password_input)

    def add_custom_fields(self):
        # Add Custom Mode-related fields 
        self.TopGrid = ColoredGridLayout(cols=1, spacing=10, padding=10)
        self.layout0_5.add_widget(self.TopGrid)


        self.saveKeycodeSheet = Button(text="Show Keycodes Sheet", on_press=self.showKeycodesSheet)  # Prend toute la largeur de la fenêtre
        self.saveKeycodeSheet.height = 40
        self.saveKeycodeSheet.size_hint=(1, None)
        self.saveKeycodeSheet.background_normal = ""  # Désactiver la texture normale
        self.saveKeycodeSheet.background_color = (0.2, 0.8, 0.8, 1)  # Appliquer la couleur vive
        self.saveKeycodeSheet.color = (1, 1, 1, 1)
        self.saveKeycodeSheet.font_name="Jersey15Normal"
        self.saveKeycodeSheet.font_size=20
        self.TopGrid.add_widget(self.saveKeycodeSheet)

        self.saveCustomNotice = Button(text="Show Notice (Must)", on_press=self.showCustomNotice)  # Prend toute la largeur de la fenêtre
        self.saveCustomNotice.height = 40
        self.saveCustomNotice.size_hint=(1, None)
        self.saveCustomNotice.background_normal = ""  # Désactiver la texture normale
        self.saveCustomNotice.background_color = (0.2, 0.8, 0.8, 1)  # Appliquer la couleur vive
        self.saveCustomNotice.color = (1, 1, 1, 1)
        self.saveCustomNotice.font_name="Jersey15Normal"
        self.saveCustomNotice.font_size=20
        self.TopGrid.add_widget(self.saveCustomNotice)



        self.customLabel = Label(text="Type Your Commands Below")
        self.customLabel.font_name = "OswaldBoldZer"
        self.customLabel.font_size = 20
        self.customLabel.height = 40
        self.customLabel.size_hint = (1, None)
        self.TopGrid.add_widget(self.customLabel)

        
        self.custom_inline_entry_input = TextInput(hint_text="Custom Entry", size_hint=(1, None), height=200)
        self.custom_inline_entry_input.font_name = "Jersey15Normal"
        self.custom_inline_entry_input.font_size = 20
        self.layout0_5.add_widget(self.custom_inline_entry_input)

        

        self.saveCustomFileBtn = Button(text="Save Custom Config", on_press=self.saveCustomFile)  # Prend toute la largeur de la fenêtre
        self.saveCustomFileBtn.height = 40
        self.saveCustomFileBtn.size_hint=(1, None)
        self.saveCustomFileBtn.background_normal = ""  # Désactiver la texture normale
        self.saveCustomFileBtn.background_color = (0.45, 0.68, 0.15, 1)  # Appliquer la couleur vive
        self.saveCustomFileBtn.color = (1, 1, 1, 1)
        self.saveCustomFileBtn.font_name="Jersey15Normal"
        self.saveCustomFileBtn.font_size=20
        self.TopGrid.add_widget(self.saveCustomFileBtn)

    def add_upload_fields(self):
        # Add Upload-related fields
        self.uploadCmdLabel1 = Label(text="Upload Command")
        self.uploadCmdLabel1.font_name = "OswaldBoldZer"
        self.uploadCmdLabel1.font_size = 15
        self.uploadCmdLabel1.height = 40
        self.uploadCmdLabel1.size_hint = (1, None)
        self.layout.add_widget(self.uploadCmdLabel1)
        
        self.uploadCmdLabel2 = Label(text="Curl if Linux/MacOS, Invoke-WebRequest if Windows")
        self.uploadCmdLabel2.font_name = "OswaldBoldZer"
        self.uploadCmdLabel2.font_size = 15
        self.uploadCmdLabel2.height = 40
        self.uploadCmdLabel2.size_hint = (1, None)
        self.layout.add_widget(self.uploadCmdLabel2)

        self.remoteFileLabel = Label(text="Remote File")
        self.remoteFileLabel.font_name = "OswaldBoldZer"
        self.remoteFileLabel.font_size = 15
        self.remoteFileLabel.height = 40
        self.remoteFileLabel.size_hint = (1, None)
        self.layout.add_widget(self.remoteFileLabel)

        self.remote_file_input = TextInput(hint_text="(ex: https://mydomain.com/evilUploads/metasploit.elf)", size_hint=(1, None), height=30)
        self.remote_file_input.font_name = "Jersey15Normal"
        self.remote_file_input.font_size = 15
        self.remote_file_input.height = 40
        self.layout.add_widget(self.remote_file_input)

        self.outputFileLabel = Label(text="Output File Name")
        self.outputFileLabel.font_name = "OswaldBoldZer"
        self.outputFileLabel.font_size = 15
        self.outputFileLabel.height = 40
        self.outputFileLabel.size_hint = (1, None)
        self.layout.add_widget(self.outputFileLabel)

        self.output_file_input = TextInput(hint_text="(ex: some_unsuspectful_name.elf)", size_hint=(1, None), height=30)
        self.output_file_input.font_name = "Jersey15Normal"
        self.output_file_input.font_size = 15
        self.output_file_input.height = 40
        self.layout.add_widget(self.output_file_input)

        self.autoLabel = Label(text="Set Exec Automation ?")
        self.autoLabel.font_name = "OswaldBoldZer"
        self.autoLabel.font_size = 15
        self.autoLabel.height = 40
        self.autoLabel.size_hint = (1, None)
        self.layout.add_widget(self.autoLabel)

        self.automatic_input = Spinner(
            text="No",
            values=["Yes", "No"], 
            height=40,
            size_hint=(1, None)
        )

        self.automatic_input.background_normal = "" 
        self.automatic_input.background_color = (0.45, 0.68, 0.15, 1)
        self.automatic_input.color = (1, 1, 1, 1)
        self.automatic_input.font_name = "Jersey15Normal"
        self.automatic_input.font_size = 20
        self.layout.add_widget(self.automatic_input)

        # Check if automation is enabled and system is Linux or MacOS before showing the automation tool fields
        self.autoToolLabel = Label(text="Program Used for Automation")
        self.autoToolLabel.font_name = "OswaldBoldZer"
        self.autoToolLabel.font_size = 15
        self.autoToolLabel.height = 40
        self.autoToolLabel.size_hint = (1, None)
        
        self.auto_tool_input = TextInput(hint_text="Tool is in /usr/bin/, so put py if python file, or sh if bash file, etc...", size_hint=(1, None), height=30)
        self.auto_tool_input.font_name = "Jersey15Normal"
        self.auto_tool_input.font_size = 15
        self.auto_tool_input.height = 40

        # Function to check if the conditions are met and show the automation tool fields
        def update_automation_fields(*args):
            if self.automatic_input.text == "Yes" and self.target_sys_spinner.text in ["Linux", "Mac"]:
                # Show automation tool fields if conditions are met
                self.layout.add_widget(self.autoToolLabel)
                self.layout.add_widget(self.auto_tool_input)
            else:
                # Remove the automation tool fields if the conditions are not met
                if self.autoToolLabel in self.layout.children:
                    self.layout.remove_widget(self.autoToolLabel)
                if self.auto_tool_input in self.layout.children:
                    self.layout.remove_widget(self.auto_tool_input)

        # Bind the Spinner to update the fields when "Yes/No" is selected
        self.automatic_input.bind(text=update_automation_fields)
        
        # Also bind the system selection change to update automation fields
        self.target_sys_spinner.bind(text=update_automation_fields)
        
        # Initial check in case conditions are already satisfied
        update_automation_fields()

    def save_config(self, instance):
    # Gather configuration content
        config_content = f"""#MODE (Recon, Upload, PKI, ReverseShell, Custom)
mode={self.mode_var}
lang={self.lang_spinner.text if hasattr(self, 'lang_spinner') else ''}
targetSys={self.target_sys_spinner.text if hasattr(self, 'target_sys_spinner') else ''}

############################ Additional settings required for Recon
serverType={self.server_type_input.text if hasattr(self, 'server_type_input') else ''}
server={self.server_input.text if hasattr(self, 'server_input') else ''}
sshServer={self.ssh_server_input.text if hasattr(self, 'ssh_server_input') else ''}
sshPassword={self.ssh_password_input.text if hasattr(self, 'ssh_password_input') else ''}
sshServerFolder={self.ssh_server_folder_input.text if hasattr(self, 'ssh_server_folder_input') else ''}

############################ Additional settings required for ReverseShell
rHost={self.rhost_input.text if hasattr(self, 'rhost_input') else ''}
rPort={self.rport_input.text if hasattr(self, 'rport_input') else ''}
shellType={self.shell_type_input.text if hasattr(self, 'shell_type_input') else ''}

############################ Additional settings required for PKI (Yubikey/Onlykey)
PKIUname={self.pki_username_input.text if hasattr(self, 'pki_username_input') else ''}
PKIPass={self.pki_password_input.text if hasattr(self, 'pki_password_input') else ''}

############################ Additional settings required for Custom
userEntry=

############################ Additional settings required for Upload
uploadCmd={self.upload_cmd_input.text if hasattr(self, 'upload_cmd_input') else ''}
remoteFile={self.remote_file_input.text if hasattr(self, 'remote_file_input') else ''}
outputFile={self.output_file_input.text if hasattr(self, 'output_file_input') else ''}
Automatic={self.automatic_input.text if hasattr(self, 'automatic_input') else ''}
autoTool={self.auto_tool_input.text if hasattr(self, 'auto_tool_input') else ''}
    """

        # Save to Pico (simulated by an os system command)
        def save_task():
            try:
                command = f'mpremote exec "f = open(\'config.txt\', \'w\'); f.write(\'{config_content.replace(chr(10), "\\n")}\'); f.close()"'
                os.system(command)
                #subprocess.run(command, shell=True, check=True)
                self.show_popup("Success", "Configuration saved successfully on RobberChicken!")
            except Exception as e:
                self.show_popup("Error", f"Error saving config file: {e}")

        threading.Thread(target=save_task).start()

    @mainthread
    def show_popup(self, title, message):
        popup = Popup(
            title=title,
            content=Label(text=message),
            size_hint=(0.8, 0.4),
        )
        popup.open()

    def saveCustomFile(self, instance):

        custom_text = self.custom_inline_entry_input.text

        inputted_lines = custom_text.splitlines()

        custom_content = f"""from .utils import *
from usb.device.keyboard import KeyCode as kc

def rootLang(language):
    global _A
    global _B
    global _C
    global _D
    global _E
    global _F
    global _G
    global _H
    global _I
    global _J
    global _K
    global _L
    global _M
    global _N
    global _O
    global _P
    global _Q
    global _R
    global _S
    global _T
    global _U
    global _V
    global _W
    global _X
    global _Y
    global _Z

    global _N1
    global _N2
    global _N3
    global _N4
    global _N5
    global _N6
    global _N7
    global _N8
    global _N9
    global _N0

    global _ENTER
    global _ESCAPE
    global _BACKSPACE
    global _TAB
    global _SPACE
    global _MINUS
    global _EQUAL
    global _OPEN_BRACKET
    global _CLOSE_BRACKET
    global _BACKSLASH
    global _HASH
    global _SEMICOLON
    global _QUOTE
    global _GRAVE
    global _COMMA
    global _DOT
    global _SLASH

    global _CAPS_LOCK
    global _F1
    global _F2
    global _F3
    global _F4
    global _F5
    global _F6
    global _F7
    global _F8
    global _F9
    global _F10
    global _F11
    global _F12
    global _PRINTSCREEN
    global _SCROLL_LOCK
    global _PAUSE
    global _INSERT
    global _HOME
    global _PAGEUP
    global _DELETE
    global _END
    global _PAGEDOWN
    global _RIGHT
    global _LEFT
    global _DOWN
    global _UP

    global _KP_NUM_LOCK
    global _KP_DIVIDE
    global _KP_AT
    global _KP_MULTIPLY
    global _KP_MINUS
    global _KP_PLUS
    global _KP_ENTER
    global _KP_1
    global _KP_2
    global _KP_3
    global _KP_4
    global _KP_5
    global _KP_6
    global _KP_7
    global _KP_8
    global _KP_9
    global _KP_0

    global _LEFT_CTRL
    global _LEFT_SHIFT
    global _LEFT_ALT
    global _LEFT_UI
    global _RIGHT_CTRL
    global _RIGHT_SHIFT
    global _RIGHT_ALT
    global _RIGHT_UI
    
    if language == "FR":
        _A = kc.Q
        _B = kc.B
        _C = kc.C
        _D = kc.D
        _E = kc.E
        _F = kc.F
        _G = kc.G
        _H = kc.H
        _I = kc.I
        _J = kc.J
        _K = kc.K
        _L = kc.L
        _M = kc.SEMICOLON
        _N = kc.N
        _O = kc.O
        _P = kc.P
        _Q = kc.A
        _R = kc.R
        _S = kc.S
        _T = kc.T
        _U = kc.U
        _V = kc.V
        _W = kc.Z
        _X = kc.X
        _Y = kc.Y
        _Z = kc.W

        _N1 = kc.N1
        _N2 = kc.N2
        _N3 = kc.N3
        _N4 = kc.N4
        _N5 = kc.N5
        _N6 = kc.N6
        _N7 = kc.N7
        _N8 = kc.N8
        _N9 = kc.N9
        _N0 = kc.N0

        _ENTER = kc.ENTER
        _ESCAPE = kc.ESCAPE
        _BACKSPACE = kc.BACKSPACE
        _TAB = kc.TAB
        _SPACE = kc.SPACE
        _MINUS = kc.MINUS
        _EQUAL = kc.EQUAL
        _OPEN_BRACKET = kc.OPEN_BRACKET
        _CLOSE_BRACKET = kc.CLOSE_BRACKET
        _BACKSLASH = kc.BACKSLASH
        _HASH = kc.HASH
        _SEMICOLON = kc.SEMICOLON
        _QUOTE = kc.QUOTE
        _GRAVE = kc.GRAVE
        _COMMA = kc.COMMA
        _DOT = kc.DOT
        _SLASH = kc.SLASH

        _CAPS_LOCK = kc.CAPS_LOCK
        _F1 = kc.F1
        _F2 = kc.F2
        _F3 = kc.F3
        _F4 = kc.F4
        _F5 = kc.F5
        _F6 = kc.F6
        _F7 = kc.F7
        _F8 = kc.F8
        _F9 = kc.F9
        _F10 = kc.F10
        _F11 = kc.F11
        _F12 = kc.F12
        _PRINTSCREEN = kc.PRINTSCREEN
        _SCROLL_LOCK = kc.SCROLL_LOCK
        _PAUSE = kc.PAUSE
        _INSERT = kc.INSERT
        _HOME = kc.HOME
        _PAGEUP = kc.PAGEUP
        _DELETE = kc.DELETE
        _END = kc.END
        _PAGEDOWN = kc.PAGEDOWN
        _RIGHT = kc.RIGHT
        _LEFT = kc.LEFT
        _DOWN = kc.DOWN
        _UP = kc.UP

        _KP_NUM_LOCK = kc.KP_NUM_LOCK
        _KP_DIVIDE = kc.KP_DIVIDE
        _KP_AT = kc.KP_AT
        _KP_MULTIPLY = kc.KP_MULTIPLY
        _KP_MINUS = kc.KP_MINUS
        _KP_PLUS = kc.KP_PLUS
        _KP_ENTER = kc.KP_ENTER
        _KP_1 = kc.KP_1
        _KP_2 = kc.KP_2
        _KP_3 = kc.KP_3
        _KP_4 = kc.KP_4
        _KP_5 = kc.KP_5
        _KP_6 = kc.KP_6
        _KP_7 = kc.KP_7
        _KP_8 = kc.KP_8
        _KP_9 = kc.KP_9
        _KP_0 = kc.KP_0

        _LEFT_CTRL = kc.LEFT_CTRL
        _LEFT_SHIFT = kc.LEFT_SHIFT
        _LEFT_ALT = kc.LEFT_ALT
        _LEFT_UI = kc.LEFT_UI
        _RIGHT_CTRL = kc.RIGHT_CTRL
        _RIGHT_SHIFT = kc.RIGHT_SHIFT
        _RIGHT_ALT = kc.RIGHT_ALT
        _RIGHT_UI = kc.RIGHT_UI
    elif language == "US":
        _A = kc.A
        _B = kc.B
        _C = kc.C
        _D = kc.D
        _E = kc.E
        _F = kc.F
        _G = kc.G
        _H = kc.H
        _I = kc.I
        _J = kc.J
        _K = kc.K
        _L = kc.L
        _M = kc.M
        _N = kc.N
        _O = kc.O
        _P = kc.P
        _Q = kc.Q
        _R = kc.R
        _S = kc.S
        _T = kc.T
        _U = kc.U
        _V = kc.V
        _W = kc.W
        _X = kc.X
        _Y = kc.Y
        _Z = kc.Z
        _N1 = kc.N1
        _N2 = kc.N2
        _N3 = kc.N3
        _N4 = kc.N4
        _N5 = kc.N5
        _N6 = kc.N6
        _N7 = kc.N7
        _N8 = kc.N8
        _N9 = kc.N9
        _N0 = kc.N0
        _ENTER = kc.ENTER
        _ESCAPE = kc.ESCAPE
        _BACKSPACE = kc.BACKSPACE
        _TAB = kc.TAB
        _SPACE = kc.SPACE
        _MINUS = kc.MINUS
        _EQUAL = kc.EQUAL
        _OPEN_BRACKET = kc.OPEN_BRACKET
        _CLOSE_BRACKET = kc.CLOSE_BRACKET
        _BACKSLASH = kc.BACKSLASH
        _HASH = kc.HASH
        _SEMICOLON = kc.SEMICOLON
        _QUOTE = kc.QUOTE
        _GRAVE = kc.GRAVE
        _COMMA = kc.COMMA
        _DOT = kc.DOT
        _SLASH = kc.SLASH
        _CAPS_LOCK = kc.CAPS_LOCK
        _F1 = kc.F1
        _F2 = kc.F2
        _F3 = kc.F3
        _F4 = kc.F4
        _F5 = kc.F5
        _F6 = kc.F6
        _F7 = kc.F7
        _F8 = kc.F8
        _F9 = kc.F9
        _F10 = kc.F10
        _F11 = kc.F11
        _F12 = kc.F12
        _PRINTSCREEN = kc.PRINTSCREEN
        _SCROLL_LOCK = kc.SCROLL_LOCK
        _PAUSE = kc.PAUSE
        _INSERT = kc.INSERT
        _HOME = kc.HOME
        _PAGEUP = kc.PAGEUP
        _DELETE = kc.DELETE
        _END = kc.END
        _PAGEDOWN = kc.PAGEDOWN
        _RIGHT = kc.RIGHT
        _LEFT = kc.LEFT
        _DOWN = kc.DOWN
        _UP = kc.UP
        _KP_NUM_LOCK = kc.KP_NUM_LOCK
        _KP_DIVIDE = kc.KP_DIVIDE
        _KP_AT = kc.KP_AT
        _KP_MULTIPLY = kc.KP_MULTIPLY
        _KP_MINUS = kc.KP_MINUS
        _KP_PLUS = kc.KP_PLUS
        _KP_ENTER = kc.KP_ENTER
        _KP_1 = kc.KP_1
        _KP_2 = kc.KP_2
        _KP_3 = kc.KP_3
        _KP_4 = kc.KP_4
        _KP_5 = kc.KP_5
        _KP_6 = kc.KP_6
        _KP_7 = kc.KP_7
        _KP_8 = kc.KP_8
        _KP_9 = kc.KP_9
        _KP_0 = kc.KP_0

        _LEFT_CTRL = kc.LEFT_CTRL
        _LEFT_SHIFT = kc.LEFT_SHIFT
        _LEFT_ALT = kc.LEFT_ALT
        _LEFT_UI = kc.LEFT_UI
        _RIGHT_CTRL = kc.RIGHT_CTRL
        _RIGHT_SHIFT = kc.RIGHT_SHIFT
        _RIGHT_ALT = kc.RIGHT_ALT
        _RIGHT_UI = kc.RIGHT_UI


def userInputInlineTwo(vlue, languagezer):
    rootLang(languagezer)

    # Exemple d'entrées utilisateur (remplace par les valeurs dynamiques)
    inputted = {inputted_lines}
    
    sequence = []

    for line in inputted:
        if line.startswith("[[DELAY") and line.endswith("]]"):
            # Si un délai est rencontré
            try:
                # Envoyer la séquence actuelle avant le délai
                if sequence:
                    sendKeys(sequence, vlue, 0.01)
                
                # Réinitialiser la séquence après l'envoi
                sequence = []
                
                # Extraire le délai (en millisecondes) et le convertir en secondes
                delay_value = int(line[8:-2].strip()) / 100.0
                time.sleep(delay_value)  # Effectuer la pause
            except ValueError:
                raise ValueError(f"Format invalide pour DELAY")
        
        elif line.startswith("[") and line.endswith("]"):
            # Supprimer les crochets
            key_block = line[1:-1].strip()
            
            if key_block.startswith("(") and key_block.endswith(")"):
                # Gérer une séquence en tuple (ex : (kcLEFT_CTRL, kcLEFT_ALT, kcT))
                tuple_keys = key_block[1:-1].split(",")  # Supprime les parenthèses et sépare les clés
                tuple_sequence = []
                for key in tuple_keys:
                    key = key.strip()
                    try:
                        tuple_sequence.append(globals()[key])
                    except KeyError:
                        raise ValueError(f"Touche inconnue dans le tuple")
                sequence.append(tuple(tuple_sequence))  # Ajouter le tuple au sequence
            else:
                # Gérer une séquence normale (ex : kcA)
                keys = key_block.split("+")  # Extrait les touches séparées par '+'
                for key in keys:
                    key = key.strip()
                    try:
                        sequence.append(globals()[key])
                    except KeyError:
                        raise ValueError(f"Touche inconnue")
                sequence.append(ENTER)
        else:
            # Gérer une chaîne normale
            for i in stringSeq(line):
                sequence.append(i)
            sequence.append(ENTER)  # Ajouter 'ENTER' après chaque ligne normale

    # Envoyer les touches restantes après avoir traité toutes les lignes
    if sequence:
        sendKeys(sequence, vlue, 0.01)
        """

        # Save to Pico (simulated by an os system command)
        def save_task():
            try:
                pico_file_path = "myLibs/customKivy.py"
                command = f"mpremote exec \"with open('{pico_file_path}', 'w') as f: f.write('''{custom_content.replace(chr(10), '\\n').replace('\"', '\\\"')}''')\""
                os.system(command)
                self.show_popup("Success", "Custom Commands Saved ! ")
            except Exception as e:
                self.show_popup("Error", f"Error saving config file: {e}")

        threading.Thread(target=save_task).start()

    @mainthread
    def show_popup(self, title, message):
        popup = Popup(
            title=title,
            content=Label(text=message),
            size_hint=(0.8, 0.4),
        )
        popup.open()

    def showCustomNotice(self, instance):
        # Créer le label d'information
        popup_label = Label(text="""Here's How To Use Custom Entry : 
Custom Mode allows you to type your own sequences in a human-readable language (better than markdown lol)
Basically you can type 4 different things : Phrase, Single Keys, Sequence Keys, and DELAY. For these 4 things, you need to type them on separate lines.
                            
For a phrase, just type : echo Hello World. Type it on a new line and it will be executed

For a Single Key, you can type : [_A] which is 'a' or [_H+_E+_L+_L+_O] which is 'hello' on a new line and it will be executed

For Sequence Keys, just type : [(_LEFT_CTRL, _LEFT_ALT, _T)] it will type these 3 keys at the same time (CTRL ALT T(which opens a Linux Terminal)). Type it on a new line and it will be executed

For DELAY it's the easiest, you have to type : [[DELAY xxx]] where xxx is the number of miliseconds, [[DELAY 150]] wait 1.5s before continuing the sequence. Type it on a new line and it will be executed
                            """)
        popup_label.font_name = "OswaldBoldZer"

        

        # Créer le bouton de fermeture
        close_button = Button(text="Close", size_hint=(None, None), size=(100, 50))
        close_button.bind(on_press=self.close_popup)  # Lier le bouton de fermeture à la méthode close_popup

        # Créer un BoxLayout pour organiser les widgets verticalement
        content_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content_layout.add_widget(popup_label)  # Ajouter le label d'information
        content_layout.add_widget(close_button)  # Ajouter le bouton de fermeture

        # Créer le popup
        self.popup = Popup(title="NOTICE", content=content_layout, size_hint=(None, None), size=(1500, 800))

        # Ouvrir le popup
        self.popup.open()

    
    def showKeycodesSheet(self, instance):
    # Créer le label d'information avec un texte très long
        popup_label = Label(text="""
_A: A, _B: B, _C: C, _D: D, _E: E, _F: F, _G: G, _H: H, _I: I, _J: J, 
_K: K, _L: L, _M: M, _N: N, _O: O,

_P: P, _Q: Q, _R: R, _S: S, _T: T, _U: U, _V: V, _W: W, _X: X, _Y: Y, 
_Z: Z, _0: 0, _1: 1, _2: 2, _3: 3,

_4: 4, _5: 5, _6: 6, _7: 7, _8: 8, _9: 9, _ENTER: Enter, _ESC: Escape, _BACKSPACE: Backspace, 
_TAB: Tab, _SPACE: Space, _MINUS: Minus (-), _EQUAL: Equals (=), _LEFT_SHIFT: Left Shift, _RIGHT_SHIFT: Right Shift,

_LEFT_CTRL: Left Control, _RIGHT_CTRL: Right Control, _LEFT_ALT: Left Alt, _RIGHT_ALT: Right Alt, 
_LEFT_GUI: Left Windows Key (GUI) or Cmd if Mac, _RIGHT_GUI: Right Windows Key (GUI) or Cmd if Mac, 
_LEFT: Left Arrow, _RIGHT: Right Arrow, _UP: Up Arrow, _DOWN: Down Arrow,

_HOME: Home, _END: End, _PAGE_UP: Page Up, _PAGE_DOWN: Page Down, _INSERT: Insert, 
_DELETE: Delete, _F1: F1, _F2: F2, _F3: F3, _F4: F4,

_F5: F5, _F6: F6, _F7: F7, _F8: F8, _F9: F9, _F10: F10, _F11: F11, _F12: F12, 
_NUM_LOCK: Num Lock, _SCROLL_LOCK: Scroll Lock,

_PAUSE: Pause/Break, _PRINT_SCREEN: Print Screen, _MEDIA_PLAY_PAUSE: Media Play/Pause, _MEDIA_STOP: Media Stop, 
_MEDIA_PREV_TRACK: Previous Track, _MEDIA_NEXT_TRACK: Next Track, _MEDIA_VOLUME_UP: Volume Up, 
_MEDIA_VOLUME_DOWN: Volume Down, _MEDIA_MUTE: Mute, 

_NUMPAD0: NumPad 0, _NUMPAD1: NumPad 1, _NUMPAD2: NumPad 2, _NUMPAD3: NumPad 3, _NUMPAD4: NumPad 4, 
_NUMPAD5: NumPad 5, _NUMPAD6: NumPad 6, _NUMPAD7: NumPad 7, _NUMPAD8: NumPad 8, _NUMPAD9: NumPad 9,

_NUMPAD_PLUS: NumPad Plus (+), _NUMPAD_MINUS: NumPad Minus (-), _NUMPAD_DIVIDE: NumPad Divide (/), 
_NUMPAD_MULTIPLY: NumPad Multiply (*), _NUMPAD_ENTER: NumPad Enter, _NUMPAD_DECIMAL: NumPad Decimal (.), 
_NUMPAD_EQUAL: NumPad Equals (=),

_LEFT_BRACKET: Left Bracket ([), _RIGHT_BRACKET: Right Bracket (]), _BACKSLASH: Backslash (\), 
_SEMI_COLON: Semi Colon (;), _QUOTE: Single Quote ('), _COMMA: Comma (,), _PERIOD: Period (.),
_SLASH: Slash (/), _LESS_THAN: Less Than (<), _GREATER_THAN: Greater Than (>),

_TILDE: Tilde (~), _GRAVE_ACCENT: Grave Accent (`)
""")
        popup_label.font_name = "OswaldBoldZer"

    # Créer un ScrollView pour permettre le défilement du texte
        scrollview = ScrollView(size_hint=(1, None), height=800)  # Fixer une hauteur fixe pour le ScrollView
        scrollview.add_widget(popup_label)  # Ajouter le Label à l'intérieur du ScrollView

        # Créer le bouton de fermeture
        close_button = Button(text="Close", size_hint=(None, None), size=(100, 50))
        close_button.bind(on_press=self.close_popup)  # Lier le bouton de fermeture à la méthode close_popup

        # Créer un BoxLayout pour organiser les widgets verticalement
        content_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content_layout.add_widget(scrollview)  # Ajouter le ScrollView contenant le label d'information
        content_layout.add_widget(close_button)  # Ajouter le bouton de fermeture

        # Créer le popup avec des dimensions spécifiques et ajuster sa taille
        self.popup = Popup(title="Keycodes", content=content_layout, size_hint=(None, None), size=(1700, 1000))

        # Ouvrir le popup
        self.popup.open()

    def close_popup(self, instance):
        # Fermer le popup lorsque le bouton de fermeture est cliqué
        self.popup.dismiss()

class ChickenThiefApp(App):
    def build(self):
        Window.minimum_width = 1600
        Window.minimum_height = 900
        return ConfigEditor()


ChickenThiefApp().run()
