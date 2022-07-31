from tkinter import *
from PIL import ImageTk, Image
import pygame
import sys
import socket
import threading
import random
from cryptography.fernet import Fernet

if (len(sys.argv) != 3):
    print(f"Usage: {sys.argv[0]} IP PORT")
    print(f"Example: {sys.argv[0]} 192.168.163.128 8080")
    sys.exit(0)

KEY = b'Q9w1t3JpGXzGwTymwo1DhN6pX0H2CRWHhLPSNcv_U7I='
f = Fernet(KEY)

def give_me_unique_name():
    roman_numerals = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX"]
    decimal_number = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    decimal_4digits = random.choice(decimal_number)+random.choice(decimal_number)+random.choice(decimal_number)+random.choice(decimal_number)
    return "CHARON" + random.choice(roman_numerals) + "#" + decimal_4digits

client_name=give_me_unique_name()
ip = sys.argv[1]
port = sys.argv[2]

class Client():

    def __init__(self, client_name, ip, port, chatlogTK):

        self.chat_history = chatlogTK
        # Create a TCP/IP socket and connect the socket to the port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = (ip, port)
        self.socket.connect(self.server_address)
        self.socket.setblocking(1)

        self.client_name = client_name
        encrypted_name = f.encrypt(str.encode(self.client_name))
        self.socket.send(encrypted_name)  
        #send = threading.Thread(target=self._client_send)
        #send.start()
        receive = threading.Thread(target=self._client_receive)
        receive.start()

    def _client_send(self, message):
        #while True:
        global f
        try:
                #c = input()
                #sys.stdout.write("\x1b[1A\x1b[2K") # Delete previous line
            encrypted_mes = f.encrypt(str.encode(message))
            self.socket.send(encrypted_mes) 
        except:
            self.socket.close()
            return

    def _client_receive(self):
        global f
        while True:
            try:
                if int(float(self.chat_history.index('end'))) > 24:
                    self.chat_history.delete("1.0", "2.0")
                    self.chat_history.insert(END, f.decrypt(self.socket.recv(1024)).decode("utf-8").upper()+"\n")
                else:
                    self.chat_history.insert(END, f.decrypt(self.socket.recv(1024)).decode("utf-8").upper()+"\n")
                #print(self.socket.recv(1024).decode("utf-8"))
            except:
                self.socket.close()
                return


target = []
pygame.mixer.init()
pygame.mixer.music.load("resources\\lobby.mp3")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)
root = Tk()

root.geometry('1920x1080')
#root.attributes('-fullscreen',True)
root.title("WELCOME TO THE REDROOM")
for i in range(25):
    bgimg=ImageTk.PhotoImage(Image.open("resources\\Screenshot ("+str(i+462)+").png"))
    target.append(bgimg)
bg = Label( root, image=target[0], relief="solid")
bg.place(x=0, y=0)
def countdown(i, widget):
    if i>24:
        i=0
    widget.configure(image=target[i])
    root.after(60, countdown, i+1, widget)

def send(entry, chat_history, client):

    if int(float(chat_history.index('end'))) > 24:

        chat_history.delete("1.0", "2.0")
        chat_history.insert(END, f'<{client_name}>   {entry.get().upper()}\n')
        client._client_send(f'<{client_name}>   {entry.get().upper()}')
        entry.delete(0, END)
    else:
        chat_history.insert(END, f'<{client_name}>   {entry.get().upper()}\n')
        client._client_send(f'<{client_name}>   {entry.get().upper()}')
        entry.delete(0, END)


def openNewWindowChat():
    newWindowChat = Toplevel(root)
    newWindowChat.title("REDROOM CHAT")
    newWindowChat.geometry("1100x700")
    newWindowChat.configure(background="black")
    chatlog = Text(newWindowChat, bg="black", fg="green", font="Courier 15 bold", width=85, height=23)
    chatlog.place(relx=0.5,rely=0.5,anchor=CENTER)
    #chatlog.config(state=DISABLED)
    e = Entry(newWindowChat, bg="white", fg="black", font="Courier 15", width=85)
    e.place(relx=0.5,rely=0.9,anchor=CENTER)
    redroomchatTitle = Label(newWindowChat, bg="blue", fg="white", text="REDROOM CHAT", font="Courier 15 bold", width=85)
    redroomchatTitle.place(relx=0.5,rely=0.1,anchor=CENTER)
    clientConnection = Client(client_name, ip, int(port), chatlog)
    newWindowChat.bind('<Return>', lambda event:send(e, chatlog, clientConnection))
    


enterButton = Button(root, text="ENTER REDROOM", command=openNewWindowChat, relief='raised',bg='black', fg="red",borderwidth=6, font="Courier 12")
enterButton.place(relx=0.5,rely=0.7,anchor=CENTER)

title = Label(root, text="WELCOME TO THE REDROOM, "+client_name, bg='black', fg="red", font="Courier 20")
title.place(relx=0.5,rely=0.5,anchor=CENTER)

toQuit = Label(root, text="Press ESC to quit.", bg='black', fg="red", font="Courier 12")
toQuit.place(relx=0.5,rely=0.6,anchor=CENTER)

countdown(0, bg) # start count loop.

def on_closing():
    root.destroy()
def endit(event):
    on_closing()
root.bind('<Escape>', endit)
root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()