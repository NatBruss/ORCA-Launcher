from tkinter import *
from tkinter.ttk import *
from tkinter import filedialog as fd
from tkinter import messagebox as mbox
import subprocess as sp
import sys, os
from select import select
from threading import Thread


class App(Tk):
    def __init__(self):
        Tk.__init__(self)
        
        # set windows properties
        self.minsize(300,100)
        self.title("ORCA Runner (v0.01)")

        # configure widget layout
        self.columnconfigure(0,weight=1)
        self.rowconfigure(3,weight=1)

        # construct input entry box
        self.inEntry = Entry(self)
        self.inEntry.grid(column=0,row=0,sticky="nesw")

        # construct input "Browse" button
        self.inButton = Button(self,text="Browse...", \
            command=self.browseForInput)
        self.inButton.grid(column=1,row=0)

        # construct output entry box
        self.outEntry = Entry(self)
        self.outEntry.grid(column=0,row=1,sticky="news")

        # construct output "Browse" button
        self.outButton = Button(self,text="Browse...", \
            command=self.browseForOutput)
        self.outButton.grid(column=1,row=1)

        # construct the button to activate the "Calculate" button
        self.goButton = Button(self,text="Calculate!",command=self.runORCA)
        self.goButton.grid(column=0,row=2,columnspan=2,sticky="nesw")

        self.running = None

        # start the main window's loop
        self.mainloop()


    def browseForInput(self):
        """
        opens a "open file" file dialog to get the input file path
        """
        # pop open an "open file" dialog, and select an input file
        returnvalue = fd.askopenfilename(initialdir="./")
        self.inEntry.delete(0,END)
        self.inEntry.insert(END,returnvalue)


    def browseForOutput(self):
        """
        opens a "save as" file dialog to get the output file path
        """
        # pop open an "save file" dialog, and select an output file
        returnvalue = fd.asksaveasfilename(initialdir="./", \
                filetypes=(("output file","*.out"),))
        self.outEntry.delete(0,END)
        self.outEntry.insert(END,returnvalue+".out")
    
    def runORCA(self):
        """
        start the ORCA process
        """

        # disables the interface when running
        self.goButton.config(state=DISABLED)

        # launch the orca process
        self.running = sp.Popen(["./orca",self.inEntry.get()],stdout=sp.PIPE)

        # create a text window to show ORCA's output
        self.openText = Text(self)
        self.openText.grid(column=0,row=3,columnspan=2,sticky="nesw")

        # start the thread for piping ORCA's output to the text window
        self.readThread = Thread(target=self.readOutput)
        self.readThread.start()

        # call back every 100ms to check it orca's still running
        self.after(100,self.callback)
    
    def readOutput(self):
        """
        Reads ORCA's output into a text. Should be run in a seperate thread.
        """

        # read the running program's stdout line by line
        for read2 in self.running.stdout:
            
            # convert the line to a string
            buffer = str(read2,encoding="utf-8")

            # insert the buffer text to the text box
            self.openText.config(state="normal")
            self.openText.insert(END,buffer)
            self.openText.config(state=DISABLED)
            self.openText.see(END)
    
    def callback(self):
        """
        called every 100ms while ORCA is running
        """

        # get information from the ORCA process
        self.running.poll()

        # if the ORCA process has finished, do some finishing up stuff, and 
        # stop the callback loop
        if self.running.returncode != None:
            self.running.wait()
            self.goButton.config(state="normal")
            with open(self.outEntry.get(),"w") as file:
                file.write(self.openText.get("0.0",END))
            self.openText.destroy()
            return

        # continue the callback loop if the process continues.
        self.after(100,self.callback)
    
    def destroy(self):
        if self.running:
            if self.running.returncode == None:
                res = mbox.askyesno("Really Quit?","The ORCA process is still running, do you really want to exit?")
                if not res:
                    return 
        Tk.destroy(self)

if __name__ == "__main__":
    App()