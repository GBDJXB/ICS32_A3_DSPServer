'''
a3.py integrates temporary contact information storage,
connecting server using DirectMessenger and GUI.
'''
# a3_gui.py

# Starter code for assignment 3 in ICS 32 Programming with Software Libraries in Python

# Replace the following placeholders with your information.

# Xinrong Le
# xinrol5@uci.edu
# 14083389

import socket
import json
import time
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, simpledialog
from ds_messenger import DirectMessenger
import ds_protocol


PORT = 3001


def get_time(timestamp: str) -> str:
    '''Transform a float timestamp into readable time'''
    time_local = datetime.fromtimestamp(float(timestamp))
    format_time_local = time_local.strftime("%H:%M:%S")
    return format_time_local


class Profile:
    '''
    Profile temporarily saves the information extracted
    from either local json file or server,
    depending on whether the user is connected to the server yet.
    Profile the class will update contacts as long as
    there is a new message sent or received.
    However, Profile does not automatically save the contacts to
    local json file. This is done by the Save method.
    '''
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.recipients = set()
        self.contacts = []

    def get_all_retrieved_contacts(self, response: list) -> list:
        '''
        Gets all the contacts when being called
        (usually from direct_messneger.retrieve_all)
        and save them to user_profile.
        '''
        if 'response' in response and 'messages' in response['response']:
            for message in response['response']['messages']:
                if not any(existing['timestamp'] == message['timestamp'] and
                          existing['message'] == message['message']
                          for existing in self.contacts):
                    if 'recipient' in message:
                        self.recipients.add(message['recipient'])
                    elif 'from' in message:
                        self.recipients.add(message['from'])

                    self.contacts.append(message)
        return self.contacts

    def add_sent_message(self, message: str, recipient: str, timestamp: float = None) -> None:
        '''
        Add a single sent message to the contact list in Profile,
        so that there's no need to save everyting everytime.
        '''
        if timestamp is None:
            timestamp = time.time()

        message_entry = {
            'message': message,
            'recipient': recipient,
            'timestamp': timestamp
        }

        self.recipients.add(recipient)
        self.contacts.append(message_entry)

    def add_received_message(self, message: str, sender: str, timestamp: float = None) -> None:
        '''
        Add a single received message to the contact list in Profile,
        so that there's no need to save everyting everytime.
        '''
        if timestamp is None:
            timestamp = time.time()

        message_entry = {
            'message': message,
            'from': sender,
            'timestamp': timestamp
        }

        self.recipients.add(sender)
        self.contacts.append(message_entry)

    def get_messages_with_contact(self, contact: str) -> list:
        '''Get all messages with a specific contact.'''
        messages = []
        for msg in self.contacts:
            if ('recipient' in msg and msg['recipient'] == contact or
                'from' in msg and msg['from'] == contact):
                messages.append(msg)

        return messages

    def save_profile(self, filename: str = None) -> None:
        '''Save all the user information in profile to local file.'''
        if filename is None:
            filename = f"profile_{self.username}.json"

        try:
            data = {
                "username": self.username, 
                "password": self.password,
                "recipients": list(self.recipients),
                "messages": self.contacts

            }

            with open(filename, 'w', encoding='utf-8') as js:
                json.dump(data, js)
            return True
        except Exception as e:
            print(f"Error saving profile: {e}")
            return False

    def load_profile(self, filename: str):
        '''Load a json file to user_profile'''
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                data = json.load(file)

            if 'username' in data:
                self.username = data['username']
            if 'password' in data:
                self.password = data['password']
            if 'messages' in data:
                self.contacts = data['messages']
            if 'recipients' in data:
                self.recipients = set(data['recipients'])

            return True
        except Exception as e:
            print(f"Error loading profile: {e}")
            return False


class Body(tk.Frame):
    '''
    Class handles the textboxes,
    including posts, entry and recipient list.
    '''
    def __init__(self, root, recipient_selected_callback=None):
        tk.Frame.__init__(self, root)
        self.root = root
        self._contacts = [str]
        self._select_callback = recipient_selected_callback
        # After all initialization is complete,
        # call the _draw method to pack the widgets
        # into the Body instance
        self._draw()

    def node_select(self, event):
        index = int(self.posts_tree.selection()[0])
        entry = self._contacts[index]
        if self._select_callback is not None:
            self._select_callback(entry)

    def insert_contact(self, contact: str):
        '''Add a new contact to the contact tree.'''
        self._contacts.append(contact)
        _id = len(self._contacts) - 1
        self._insert_contact_tree(_id, contact)

    def _insert_contact_tree(self, id, contact: str):
        if len(contact) > 25:
            entry = contact[:24] + "..."
        id = self.posts_tree.insert('', id, id, text=contact)

    # New version of insert message methods.
    # Now newest messages are shown at the bottom of the chatbox.
    # Just like what many social media do.
    # Also, the chatbox will automatically scroll to the end.

    def insert_user_message(self, message:str):
        '''
        Insert the message sent by the user to
        the bottom right side of the posts box.
        '''
        self.entry_editor.insert(tk.END, str(message) + '\n', 'entry-right')
        self.entry_editor.see(tk.END)

    def insert_contact_message(self, message:str):
        '''
        Insert the message sent by the recipient to
        the bottom left side of the posts box.
        '''
        self.entry_editor.insert(tk.END, str(message) + '\n', 'entry-left')
        self.entry_editor.see(tk.END)

    def clear_chatbox(self):
        '''Wipe the chatbox for new contacts.'''
        self.entry_editor.delete(1.0, tk.END)

    def get_text_entry(self) -> str:
        return self.message_editor.get('1.0', 'end').rstrip()

    def set_text_entry(self, text:str):
        self.message_editor.delete(1.0, tk.END)
        self.message_editor.insert(1.0, text)

    def _draw(self):
        posts_frame = tk.Frame(master=self, width=250)
        posts_frame.pack(fill=tk.BOTH, side=tk.LEFT)

        self.posts_tree = ttk.Treeview(posts_frame)
        self.posts_tree.bind("<<TreeviewSelect>>", self.node_select)
        self.posts_tree.pack(fill=tk.BOTH, side=tk.TOP,
                             expand=True, padx=5, pady=5)

        entry_frame = tk.Frame(master=self, bg="")
        entry_frame.pack(fill=tk.BOTH, side=tk.TOP, expand=True)

        editor_frame = tk.Frame(master=entry_frame, bg="red")
        editor_frame.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)

        scroll_frame = tk.Frame(master=entry_frame, bg="blue", width=10)
        scroll_frame.pack(fill=tk.BOTH, side=tk.LEFT, expand=False)

        message_frame = tk.Frame(master=self, bg="yellow")
        message_frame.pack(fill=tk.BOTH, side=tk.TOP, expand=False)

        self.message_editor = tk.Text(message_frame, width=0, height=5)
        self.message_editor.pack(fill=tk.BOTH, side=tk.LEFT,
                                 expand=True, padx=0, pady=0)

        self.entry_editor = tk.Text(editor_frame, width=0, height=5)
        self.entry_editor.tag_configure('entry-right', justify='right')
        self.entry_editor.tag_configure('entry-left', justify='left')
        self.entry_editor.pack(fill=tk.BOTH, side=tk.LEFT,
                               expand=True, padx=0, pady=0)

        entry_editor_scrollbar = tk.Scrollbar(master=scroll_frame,
                                              command=self.entry_editor.yview)
        self.entry_editor['yscrollcommand'] = entry_editor_scrollbar.set
        entry_editor_scrollbar.pack(fill=tk.Y, side=tk.LEFT,
                                    expand=False, padx=0, pady=0)


class Footer(tk.Frame):
    '''Presents tips and alerts and create a send button.'''
    def __init__(self, root, send_callback=None):
        tk.Frame.__init__(self, root)
        self.root = root
        self._send_callback = send_callback
        self._draw()

    def send_click(self):
        if self._send_callback is not None:
            self._send_callback()

    def _draw(self):
        save_button = tk.Button(master=self, text="Send", width=20)
        # You must implement this.
        # Here you must configure the button to bind its click to
        # the send_click() function.
        save_button.config(command=self.send_click)

        save_button.pack(fill=tk.BOTH, side=tk.RIGHT, padx=5, pady=5)

        self.footer_label = tk.Label(master=self, text="Ready.")
        self.footer_label.pack(fill=tk.BOTH, side=tk.LEFT, padx=5)

class Header(tk.Frame):
    '''Clarifies the Identity of the Recipient.'''
    def __init__(self, root):
        tk.Frame.__init__(self, root)
        self.root = root
        self._draw()

    def _draw(self):
        self.header_label = tk.Label(master=self, text="Recipient: None")
        self.header_label.pack(side='right', fill=tk.BOTH, padx=5)


class NewContactDialog(tk.simpledialog.Dialog):
    def __init__(self, root, title=None, user=None, pwd=None, server=None):
        self.root = root
        self.server = server
        self.user = user
        self.pwd = pwd
        super().__init__(root, title)

    def body(self, _frame):
        self.server_label = tk.Label(_frame, width=30, text="DS Server Address")
        self.server_label.pack()
        self.server_entry = tk.Entry(_frame, width=30)
        self.server_entry.insert(tk.END, self.server)
        self.server_entry.pack()

        self.username_label = tk.Label(_frame, width=30, text="Username")
        self.username_label.pack()
        self.username_entry = tk.Entry(_frame, width=30)
        self.username_entry.insert(tk.END, self.user)
        self.username_entry.pack()

        # You need to implement also the region for the user to enter
        # the Password. The code is similar to the Username you see above
        # but you will want to add self.password_entry['show'] = '*'
        # such that when the user types, the only thing that appears are
        # * symbols.
        #self.password...

        self.password_label = tk.Label(_frame, width=30, text="Password")
        self.password_label.pack()
        self.password_entry = tk.Entry(_frame, width=30, show='*')
        self.password_entry.insert(tk.END, self.pwd or "")
        self.password_entry.pack()


    def apply(self):
        self.user = self.username_entry.get()
        self.pwd = self.password_entry.get()
        self.server = self.server_entry.get()


class MainApp(tk.Frame):
    def __init__(self, root):
        tk.Frame.__init__(self, root)
        self.root = root
        self.username = ''
        self.password = ''
        self.server = ''
        self.recipient = ''
        # You must implement this! You must configure and
        # instantiate your DirectMessenger instance after this line.
        #self.direct_messenger = ... continue!
        self.direct_messenger = None
        self.check_messages = None
        self.switch_flag = ''
        self.user_profile = None
        # After all initialization is complete,
        # call the _draw method to pack the widgets
        # into the root frame
        self._draw()
        # self.body.insert_contact("studentexw23") # adding one example student.

    def send_message(self):
        '''
        Get the message entered and send it.
        Display it on the bottom of the post box.
        '''
        message = str(self.body.get_text_entry().strip())
        if not message:
            self.footer.footer_label.config(text="Please enter a message.")
            return

        if not self.recipient:
            self.footer.footer_label.config(text="Please select a recipient.")
            return

        if self.direct_messenger is None:
            self.footer.footer_label.config(text="Not connected to DSUserver.")
            return

        try:
            flag = self.direct_messenger.send(message, self.recipient)

            if flag:
                if self.switch_flag == 'user':
                    self.body.insert_user_message('\n'+get_time(datetime.now().timestamp())+
                                                  '\n'+self.username+':')
                self.switch_flag = 'recipient'

                self.body.insert_user_message(message)
                self.body.set_text_entry("")
                self.footer.footer_label.config(text="Message sent.")
            else:
                self.footer.footer_label.config(text="Failed to send message.")

        except Exception as ex:
            self.footer.footer_label.config(text=f"Error sending message: {ex}")
            raise ex

    def save_new_message_to_profile(self):
        '''Request all contacts from the server and save them to user_profile'''
        if self.direct_messenger and self.user_profile:
            try:
                self.user_profile.get_all_retrieved_contacts(self.direct_messenger.retrieve_all())
                return True
            except Exception as ex:
                print(f"Error saving new messages to profile: {ex}")
                return False
        return False

    def new_profile(self):
        '''Save information in user_profile in local json file.'''
        if self.user_profile:
            try:
                self.user_profile.get_all_retrieved_contacts(self.direct_messenger.retrieve_all())

                filename = f"profile_{self.username}.json"
                if self.user_profile.save_profile(filename):
                    self.footer.footer_label.config(text="Profile saved.")
                else:
                    self.footer.footer_label.config(text="Failed to save profile.")
            except Exception as ex:
                self.footer.footer_label.config(text=f"Error saving profile: {ex}")
        else:
            self.footer.footer_label.config(text="No profile to save.")

    def load_profile_json(self):
        '''The user chooses a json file and try to load the information to Profile.'''
        file_path = filedialog.askopenfilename(
            title="Select Profile Json File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialdir="."
            )

        if file_path:
            temp = Profile("","")
            if temp.load_profile(file_path):

                self.username = temp.username
                self.password = temp.password
                self.user_profile = Profile(self.username, self.password)
                self.user_profile.contacts = temp.contacts
                self.user_profile.recipients = temp.recipients
                self.body._contacts.clear()
                for i in self.body.posts_tree.get_children():
                    self.body.posts_tree.delete(i)

                for i in temp.recipients:
                    if i != self.username:
                        self.body.insert_contact(i)

                self.footer.footer_label.config(text="Profile loaded.")
                print(self.user_profile.contacts)
            else:
                self.footer.footer_label.config(text="Failed to load profile.")



    def add_contact(self):
        '''
        Ask the user to input a new recipient.
        '''
        new_contact = simpledialog.askstring(title="Add contact",
                                             prompt="Enter contact ID:")
        if new_contact == self.username:
            self.footer.footer_label.config(text="Cannot add yourself as contact.")
        elif new_contact:
            self.body.insert_contact(new_contact.strip())

    def recipient_selected(self, recipient):
        '''
        Upon clicking a new recipient, replace the current messages
        in the chatbox with the messages between the user and the
        chosen recipient.
        '''
        self.recipient = recipient
        self.header.header_label.config(text=f"Recipient: {recipient}")

        self.body.clear_chatbox()

        if self.user_profile:
            messages = self.user_profile.get_messages_with_contact(recipient)
            first_time_flag = True
            for message in messages:
                if 'recipient' in message and message['recipient'] == recipient:
                    if self.switch_flag == 'user' or first_time_flag:
                        self.body.insert_user_message('\n'+get_time(message['timestamp'])+
                                                      '\n'+self.username+':')
                        first_time_flag = False
                    self.switch_flag = 'recipient'

                    self.body.insert_user_message(str(message['message']))

                if 'from' in message and message['from'] == recipient:
                    if self.switch_flag == 'recipient' or first_time_flag:
                        self.body.insert_contact_message('\n'+get_time(message['timestamp'])+
                                                         '\n'+recipient+':')
                        first_time_flag = False
                    self.switch_flag = 'user'

                    self.body.insert_contact_message(str(message['message']))

        if self.direct_messenger:
            try:
                self.body.clear_chatbox()
                response = self.direct_messenger.retrieve_all()
                pre_messages = response['response']['messages']

                if len(pre_messages) > 0:
                    for message in pre_messages:
                        if 'recipient' in message and message['recipient'] == recipient:
                            if self.switch_flag == 'user':
                                self.body.insert_user_message('\n'+get_time(message['timestamp'])+
                                                              '\n'+self.username+':')
                            self.switch_flag = 'recipient'

                            self.body.insert_user_message(str(message['message']))

                        if 'from' in message and message['from'] == recipient:
                            if self.switch_flag == 'recipient':
                                self.body.insert_contact_message('\n'+
                                                                 get_time(message['timestamp'])+
                                                                 '\n'+recipient+':')
                            self.switch_flag = 'user'

                            self.body.insert_contact_message(str(message['message']))

            except Exception as ex:
                self.footer.footer_label.config(text=f"Error retrieving message: {ex}")

    def configure_server(self):
        '''
        Get server address from the user and connect to the server.
        '''
        ud = NewContactDialog(self.root, "Configure Account",
                              self.username, self.password, self.server)
        self.username = ud.user
        self.password = ud.pwd
        self.server = ud.server
        # You must implement this!
        # You must configure and instantiate your
        # DirectMessenger instance after this line.
        if self.username and self.password and self.server:
            try:
                sock  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((self.server, PORT))
                conn = ds_protocol.init(sock)

                authen_message = ds_protocol.authenticate(conn,
                                                       self.username,
                                                       self.password)

                if authen_message.type == "ok":
                    self.direct_messenger = DirectMessenger(dsuserver=conn,
                                                            username=self.username,
                                                            password=self.password)
                    self.direct_messenger.token = authen_message.token
                    self.user_profile = Profile(self.username, self.password)
                    self.footer.footer_label.config(text=
                        f"Connected to server. Current token: {self.direct_messenger.token}")

                elif authen_message.message.startswith("Incorrect password"):
                    self.footer.footer_label.config(text="Incorrect password. Please try again.")

            except Exception as ex:
                self.footer.footer_label.config(text=f"Connection error: {ex}")
                raise ex
        else:
            self.footer.footer_label.config(text="Please fill in all fields.")

    def publish(self, message:str):
        '''Send the message to the server.'''
        if self.direct_messenger and self.recipient:
            return self.direct_messenger.send(message, self.recipient)
        return False

    def check_new(self):
        '''
        Check if there is new message from server.
        In __main__ this is done every 2 seconds.
        '''
        if self.direct_messenger:
            try:
                new_messages = self.direct_messenger.retrieve_new()

                if len(new_messages['response']['messages']) > 0:
                    print(new_messages)

                    for message in new_messages['response']['messages']:
                        if self.switch_flag == 'recipient':
                            self.body.insert_contact_message('\n')
                        self.switch_flag = 'user'
                        self.body.insert_contact_message(str(message['message']))

                    self.save_new_message_to_profile()
                    self.user_profile.save_profile()

            except Exception as ex:
                self.footer.footer_label.config(text=f"Error retrieving message: {ex}")

        self.check_messages = self.root.after(2000, self.check_new)

    def _draw(self):
        # Build a menu and add it to the root frame.
        menu_bar = tk.Menu(self.root)
        self.root['menu'] = menu_bar
        menu_file = tk.Menu(menu_bar)

        menu_bar.add_cascade(menu=menu_file, label='File')
        menu_file.add_command(label='Save', command=self.new_profile)
        menu_file.add_command(label='Open...', command=self.load_profile_json)

        settings_file = tk.Menu(menu_bar)
        menu_bar.add_cascade(menu=settings_file, label='Settings')
        settings_file.add_command(label='Add Contact',
                                  command=self.add_contact)
        settings_file.add_command(label='Configure DS Server',
                                  command=self.configure_server)

        # The Body and Footer classes must be initialized and
        # packed into the root window.
        self.body = Body(self.root,
                         recipient_selected_callback=self.recipient_selected)
        self.body.pack(fill=tk.BOTH, side=tk.TOP, expand=True)
        self.footer = Footer(self.root, send_callback=self.send_message)
        self.footer.pack(fill=tk.BOTH, side=tk.BOTTOM)
        self.header = Header(self.root)
        self.header.pack(fill=tk.BOTH, side=tk.TOP)


if __name__ == "__main__":
    # All Tkinter programs start with a root window. We will name ours 'main'.
    main = tk.Tk()

    # 'title' assigns a text value to the Title Bar area of a window.
    main.title("ICS 32 Distributed Social Messenger")

    # This is just an arbitrary starting point. You can change the value
    # around to see how the starting size of the window changes.
    main.geometry("720x480")

    # adding this option removes some legacy behavior with menus that
    # some modern OSes don't support. If you're curious, feel free to comment
    # out and see how the menu changes.
    main.option_add('*tearOff', False)

    # Initialize the MainApp class, which is the starting point for the
    # widgets used in the program. All of the classes that we use,
    # subclass Tk.Frame, since our root frame is main, we initialize
    # the class with it.
    app = MainApp(main)

    # When update is called, we finalize the states of all widgets that
    # have been configured within the root frame. Here, update ensures that
    # we get an accurate width and height reading based on the types of widgets
    # we have used. minsize prevents the root window from resizing too small.
    # Feel free to comment it out and see how the resizing
    # behavior of the window changes.
    main.update()
    main.minsize(main.winfo_width(), main.winfo_height())
    _id = main.after(2000, app.check_new)
    print(_id)
    # And finally, start up the event loop for the program (you can find
    # more on this in lectures of week 9 and 10).
    main.mainloop()
