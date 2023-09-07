from tkinter import *
from tkinter import ttk
from subprocess import run
from bs4 import BeautifulSoup
from os import remove,getcwd
from tkinter.filedialog import asksaveasfilename
from tkinter.messagebox import showerror, showinfo
import psutil

class MainApp(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.title('Battery Health Check')
        self.iconbitmap('icon.ico')
        self.geometry('400x100+450+300')
        self.head = Label(self, text='Battery health check', font='Arial 21')
        self.head.pack(side=TOP)
        self.resizable(0,0)
        self.check = ttk.Button(self, text='Test your battery', command=self.check_battery)
        self.check.pack(pady=15)

    def check_battery(self):
        run(['powercfg', '/batteryreport', '-output', '.\\log.html'])
        self.root=Tk()
        self.root.title('Detailed Battery Report')
        self.root.iconbitmap('icon.ico')
        self.yscroll = ttk.Scrollbar(self.root, orient='vertical')
        self.yscroll.pack(side='right', fill=Y)
        self.t=Text(self.root, font=('Consolas', '18'), yscrollcommand=self.yscroll.set)
        self.yscroll.config(command=self.t.yview)
        self.html_parse()
        self.root.bind('<Control-s>', self.save_report)
        self.t.pack(expand=True, fill=BOTH)
        self.root.mainloop()

    def html_parse(self):
        global s
        with open('.\\log.html','r') as html:
            soup = BeautifulSoup(html)
            for script in soup(["script", "style"]):
                script.decompose()
            strips = list(soup.stripped_strings)
            info={}
            for i in range(3,34,2):
                info.setdefault(strips[i], strips[i+1])
        remove('.\\log.html')
        self.report='DETAILED BATTERY REPORT (Press Ctrl+S to save this report)\n\n'
        a=''
        for i in info:
            if i=='Information about each currently installed battery':
                self.report+='\n'+ i + '\n\n' + info[i].replace('\n\n                  ','-')+'\n'
                a='    '
            elif 'installed' in info[i].lower():
                self.report=self.report.rstrip('\n')+' '+i+'\n'
            else:
                self.report+= a+i.replace('\n',' ') + ' : ' + ' '*((23-len(i.replace('\n',' ')))) +info[i] +'\n'
        self.health = round((int(strips[3:35][-3].rstrip(' mWh').replace(',',''))/int(strips[3:35][-5].rstrip(' mWh').replace(',','')))*100, 2)
        if 85<self.health<100:
            if self.health>95:
                self.status='Excellent\n\nResult:\n    The Battery is in excellent condition with its full charge capacity.'
            else:
                self.status='Excellent\n\nResult:\n    The Battery is in good condition but might have lost some charging capacity due to ageing.'
        elif 70<self.health<85:
            self.status='Good\n\nResult:\n    It\'s recommended to take care of your battery by following certain tips.'
        elif 55<self.health<70:
            self.status='Average\n\nResult:\n    It\'s recommended to view the status of your battery regularly.'
        elif 40<self.health<55:
            self.status='Acceptable\n\nResult:\n    It\'s recommended to view the status of your battery regularly.'
        elif 25<self.health<40:
            self.status='Bad\n\nResult:\n    It\'s recommended to immediaitely replace your battery.'
        elif self.health<25:
            self.status='Critical\n\nResult:\n    It\'s recommended to immediaitely replace your battery.'
        self.report+=a+"AC POWER STATUS:"+' '*10+('DISCONNECTED','CONNECTED')[psutil.sensors_battery().power_plugged] + '\n'
        self.report+=a+'REMAINING CAPACITY:'+' '*7+str(psutil.sensors_battery().percent)+' % '+ '(' + str(round(int(psutil.sensors_battery().percent)*int(strips[3:35][-3].rstrip(' mWh').replace(',',''))/100, 2))+ ' mWh' + ')' + '\n'
        self.report+=a+"HEALTH :"+' '*18+str(self.health)+' %'+'\n'+\
            a+'STATUS:'+' '*19+self.status
        self.t.insert(INSERT, self.report)
        self.t.tag_add('status', 23.0, END)
        if 'Excellent' in self.status:
            self.t.tag_config('status', foreground='darkgreen')
        elif 'Good' in  self.status:
            self.t.tag_config('status', foreground='#85d06f')
        elif 'Average' in self.status:
            self.t.tag_config('status', foreground='#a5f24f') 
        elif 'Acceptable' in self.status:
            self.t.tag_config('status', foreground='#ffff00') 
        elif 'Bad' in self.status:
            self.t.tag_config('status', foreground='#f91104')  
        elif 'Critical' in self.status:
            self.t.tag_config('status', foreground='#d70428')  
        self.t.config(state=DISABLED)

    def save_report(self, key):
        file=asksaveasfilename(
        confirmoverwrite=True, filetypes=(('HTML file','*.html'), ('Text File', '*.txt')), initialdir=getcwd(),\
        initialfile='Batteryreport', title='Save Batteryreport', defaultextension=".*")

        if file:
            if '.html' in file:
                run(['powercfg', '/batteryreport', '-output', file])
            else:
                with open(file, 'w') as fh:
                    fh.write(self.report.replace(' (Press Ctrl+S to save this report)', ''))
                    fh.flush()
            showinfo('Battery Report', 
            'Battery report was saved successfully as '+file.split('/')[-1]+' in directory '+'/'.join(file.split('/')[:-1]))
        else:
            showerror('Error','Report saving operation was cancelled by the user.')


if __name__ == '__main__':
    MainApp().mainloop()
