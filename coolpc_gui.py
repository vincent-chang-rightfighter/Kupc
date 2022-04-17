from cProfile import label
from tkinter.tix import NoteBook
from bs4 import BeautifulSoup
import requests
import re
import base64
import sys
import os
import tkinter
import threading
# import webbrowser
from icon import img
# import emoji
import textwrap
import sqlite3
# import csv
from tkinter import *
from tkinter.ttk import Notebook, Treeview
from tkinter import END, Tk, Frame, ttk, messagebox, Text, Label
from tktooltip import ToolTip
program_directory = sys.path[0]
dir_path2 = os.path.join(os.environ['APPDATA'], 'KUPC')
if not os.path.exists(dir_path2):
    os.makedirs(dir_path2)
file_path = os.path.join(dir_path2, 'KUPC.db')

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36'}

total_regex = r"共有.*\n"
blank_regex = r"^\s*\n"
subst = ""
item_selected_name = ""
item_selected_class = ""
item_selected_price = ""
item_selected_date = ""


class NewWindow(Toplevel):
    def __init__(self, master=None):
        super().__init__(master=master)
        btn.config(state='disable')
        self.title("歷史資料庫")
        tmp = open("tmp.ico", "wb+")
        tmp.write(base64.b64decode(img))
        tmp.close()
        self.iconbitmap('tmp.ico')
        os.remove("tmp.ico")
        # self.geometry("200x200")
        self.resizable(False, False)
        window_height = 600
        window_width = 1200
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_cordinate = int((screen_width/2) - (window_width/2))
        y_cordinate = int((screen_height/2) - (window_height/2))
        self.geometry("{}x{}+{}+{}".format(window_width,
                                           window_height, x_cordinate, y_cordinate))

        new_db_selected_name = ""
        new_db_selected_price = ""
        new_db_selected_date = ""

        def quit_win():
            self.destroy()
            btn.config(state='normal')
        self.protocol("WM_DELETE_WINDOW", quit_win)

        def db_treeview():
            if new_tree.get_children():
                for i in new_tree.get_children():
                    new_tree.delete(i)
            con = sqlite3.connect(file_path)
            cur = con.cursor()
            cur.execute("VACUUM;")
            cur.execute("SELECT * FROM Stuff")
            rows = cur.fetchall()
            for row in rows:
                new_tree.insert("",  "end", values=(
                    row[0], row[1], row[2], row[3]))
            con.close()

        def new_item_selected(event):
            global new_db_selected_name
            global new_db_selected_price
            global new_db_selected_date
            for selected_item in new_tree.selection():
                item = new_tree.item(selected_item)
                record = item['values']
                new_db_selected_name = record[0]
                new_db_selected_price = record[2]
                new_db_selected_date = record[3]

        def db_delete():
            global new_db_selected_name
            global new_db_selected_price
            global new_db_selected_date
            con = sqlite3.connect(file_path)
            cur = con.cursor()
            # cur.execute(
            #     "DELETE FROM Stuff WHERE name =? AND price=? AND date=? LIMIT 1;", (new_db_selected_name, new_db_selected_price, new_db_selected_date))
            cur.execute(
                "DELETE FROM Stuff WHERE rowid IN(SELECT rowid FROM Stuff WHERE  name =? AND price=? AND date=? LIMIT 1)", (new_db_selected_name, new_db_selected_price, new_db_selected_date))

            # cur.execute(
            #     "DELETE FROM Stuff WHERE rowid NOT IN (SELECT MAX(rowid) FROM Stuff GROUP BY name,class,price,date)")
            con.commit()
            con.close()
            db_treeview()

        delete_btn = ttk.Button(self,
                                text="自此資料庫中刪除", command=lambda: db_delete(), style="Toggle.TButton")
        delete_btn.grid(row=1, column=0, padx=5,
                        pady=5, sticky=tkinter.E+tkinter.W)
        ToolTip(delete_btn, msg="點擊左側項目再點擊此按鈕", follow=True, delay=1)

        new_frame = Frame(self)
        new_frame.place(x=10, y=50, width=1050, height=500)
        scrollBar = ttk.Scrollbar(new_frame)
        scrollBar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        new_tree = Treeview(new_frame, columns=('c1', 'c2', 'c3', 'c4'),
                            show="headings", yscrollcommand=scrollBar.set)
        new_tree.column('c1', width=620, stretch=tkinter.NO)
        new_tree.column('c2', width=205, stretch=tkinter.NO)
        new_tree.column('c3', width=90, stretch=tkinter.NO)
        new_tree.column('c4', width=115, stretch=tkinter.NO)
        new_tree.heading('c1', text='品名', anchor='w')
        new_tree.heading('c2', text='類別', anchor='w')
        new_tree.heading('c3', text='價格', anchor='w')
        new_tree.heading('c4', text='時間', anchor='w')
        new_tree.pack(side=tkinter.LEFT, fill=tkinter.Y)
        new_tree.bind('<Button-1>', handle_click)
        # tree.bind('<ButtonRelease-1>', treeviewClick)
        scrollBar.config(command=new_tree.yview)
        new_tree.bind('<<TreeviewSelect>>', new_item_selected)
        db_treeview()


def exit_func():
    MsgBox = messagebox.askquestion('確認', '要離開程式了嗎?', icon='warning')
    if MsgBox == 'yes':
        root.destroy()
    else:
        tkinter.messagebox.showinfo('返回', '可愛的人類呢')


def time_crawler():
    res = requests.get(
        "https://coolpc.com.tw/evaluate.php", headers=headers)
    soup = BeautifulSoup(res.text, 'lxml')
    for time in soup.find_all(id="Mdy"):
        print(time.text[:-2])


def time_crawler_thread():
    t1 = threading.Thread(target=time_crawler)
    t1.start()


def wrap(string, lenght=90):
    return '\n'.join(textwrap.wrap(string, lenght))


def item_crawler(value, class_string):

    if tree.get_children():
        for i in tree.get_children():
            tree.delete(i)
    tree.yview_moveto(0)
    res = requests.get(
        "https://coolpc.com.tw/evaluate.php", headers=headers)
    soup = BeautifulSoup(res.text, 'lxml')
    time_string = ""
    name_string = ""
    price_int = ""

    for time in soup.find_all(id="Mdy"):
        time_string = time.text[:-2]
    for item in soup.select('#tbdy > tr:nth-child('+str(value)+')'):
        for opt in item.select('td:nth-child(3) > select'):
            for opt_item in opt.find_all(value=True, disabled=False):
                total_result = re.sub(total_regex, subst,
                                      opt_item.text, 0, re.MULTILINE)
                blank_result = re.sub(blank_regex, subst,
                                      total_result, 0, re.MULTILINE)
                if len(blank_result) != 0:
                    name_string = blank_result.split(',')[0]
                    price_int = blank_result.split("$").pop().split(" ")[0]
                    if price_int != '1':
                        tree.insert("",  "end", values=(
                            wrap(name_string), class_string, price_int, time_string))

    text.config(state=tkinter.NORMAL)
    text.insert(END, '取得 "'+str(class_string)+'" 項目 成功\n')
    text.config(state=tkinter.DISABLED)
    text.yview_moveto(1)


def item_crawler_thread(value, class_string):
    t2 = threading.Thread(
        target=item_crawler(value, class_string))
    t2.start()


def handle_click(event):
    if tree.identify_region(event.x, event.y) == "separator":
        return "break"


def item_selected(event):
    global item_selected_name
    global item_selected_class
    global item_selected_price
    global item_selected_date
    for selected_item in tree.selection():
        item = tree.item(selected_item)
        record = item['values']
        # show a message
        # print(record[0], record[1], record[2], record[3])
        item_selected_name = record[0]
        item_selected_class = record[1]
        item_selected_price = record[2]
        item_selected_date = record[3]


def db_insert_button():
    if item_selected_name != "" and item_selected_class != "" and item_selected_price != "" and item_selected_date != "":
        con = sqlite3.connect(file_path)
        cur = con.cursor()
        cur.execute(
            '''CREATE TABLE IF NOT EXISTS Stuff(name TEXT ,class TEXT,price INTEGER,date TEXT)''')
        cur.execute(
            "INSERT INTO Stuff (name, class, price, date)VALUES(?, ?, ?, ?)", (item_selected_name, item_selected_class, item_selected_price, item_selected_date))
        con.commit()
        con.close()
        text.config(state=tkinter.NORMAL)
        text.insert(END, '已將選中"'+str(item_selected_class)+'"項目\n新增歷史資料庫\n')
        text.config(state=tkinter.DISABLED)
        text.yview_moveto(1)


def db_insert_button_thread():
    t3 = threading.Thread(target=db_insert_button())
    t3.start()


root = Tk()
root.tk.call('source', os.path.join(dir_path2, 'sun-valley.tcl'))
root.tk.call("set_theme", "dark")
# root.tk.call("set_theme", "light")
tmp = open("tmp.ico", "wb+")
tmp.write(base64.b64decode(img))
tmp.close()
root.iconbitmap('tmp.ico')
os.remove("tmp.ico")

style = ttk.Style()
root.resizable(False, False)
window_height = 810
window_width = 1350
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x_cordinate = int((screen_width/2) - (window_width/2))
y_cordinate = int((screen_height/2) - (window_height/2))

root.geometry("{}x{}+{}+{}".format(window_width,
                                   window_height, x_cordinate, y_cordinate))

LARGE_FONT = 11
SMALL_FONT = 10
style.configure("Treeview.Heading", font=("Microsoft JhengHei", LARGE_FONT, "bold"),
                rowheight=int(LARGE_FONT*2.5))
style.configure("Treeview", font=("Microsoft JhengHei", SMALL_FONT),
                rowheight=int(SMALL_FONT*3.5))

root.title('庫 PC 查價')

tabcontrol = Notebook(root)
tabcontrol.place(x=10, y=5, width=1050, height=115)
tab_1 = ttk.Frame(tabcontrol)
tab_2 = ttk.Frame(tabcontrol)
tab_3 = ttk.Frame(tabcontrol)
for index in [0, 5]:
    tab_1.columnconfigure(index=index, weight=1)
    tab_1.rowconfigure(index=index, weight=1)
    tab_2.columnconfigure(index=index, weight=1)
    tab_2.rowconfigure(index=index, weight=1)

for index in [0, 2]:
    tab_3.columnconfigure(index=index, weight=1)
    tab_3.rowconfigure(index=index, weight=1)

tabcontrol.add(tab_1, text="零組件")
tabcontrol.add(tab_2, text="電腦周邊")
tabcontrol.add(tab_3, text="網通及其他")

btn1 = ttk.Button(tab_3, text="品牌小主機、AIO｜VR 虛擬", command=lambda: [
    item_crawler_thread(1, "品牌小主機、AIO｜VR 虛擬")])
btn1.grid(row=0, column=1, padx=2, pady=2, sticky=tkinter.E+tkinter.W)

btn2 = ttk.Button(tab_3, text="手機｜平板｜筆電｜穿戴", command=lambda: [
    item_crawler_thread(2, "手機｜平板｜筆電｜穿戴")])
btn2.grid(row=1, column=1, padx=2, pady=2, sticky=tkinter.E+tkinter.W)

# btn3 = ttk.Button(root, text="酷！PC 套裝產線")
# btn3.grid(row=0, column=2, padx=2,pady=2)

btn4 = ttk.Button(tab_1, text="處理器 CPU", command=lambda: [
    item_crawler_thread(4, "處理器 CPU")])
btn4.grid(row=0, column=0, padx=2, pady=2, sticky=tkinter.E+tkinter.W)

btn5 = ttk.Button(tab_1, text="主機板 MB", command=lambda: [
    item_crawler_thread(5, "主機板 MB")])
btn5.grid(row=0, column=1, padx=2, pady=2, sticky=tkinter.E+tkinter.W)

btn6 = ttk.Button(tab_1, text="記憶體 RAM", command=lambda: [
    item_crawler_thread(6, "記憶體 RAM")])
btn6.grid(row=0, column=2, padx=2, pady=2, sticky=tkinter.E+tkinter.W)

btn7 = ttk.Button(tab_1, text="固態硬碟 M.2｜SSD", command=lambda: [
    item_crawler_thread(7, "固態硬碟 M.2｜SSD")])
btn7.grid(row=0, column=3, padx=2, pady=2, sticky=tkinter.E+tkinter.W)

btn8 = ttk.Button(tab_1, text="傳統內接硬碟 HDD", command=lambda: [
    item_crawler_thread(8, "傳統內接硬碟 HDD")])
btn8.grid(row=0, column=4, padx=2, pady=2, sticky=tkinter.E+tkinter.W)

btn12 = ttk.Button(tab_1, text="顯示卡 VGA", command=lambda: [
    item_crawler_thread(12, "顯示卡 VGA")])
btn12.grid(row=0, column=5, padx=2, pady=2, sticky=tkinter.E+tkinter.W)

btn15 = ttk.Button(tab_1, text="電源供應器", command=lambda: [
    item_crawler_thread(15, "電源供應器")])
btn15.grid(row=1, column=0, padx=2, pady=2, sticky=tkinter.E+tkinter.W)

btn10 = ttk.Button(tab_1, text="散熱器｜散熱墊｜散熱膏", command=lambda: [
    item_crawler_thread(10, "散熱器｜散熱墊｜散熱膏")])
btn10.grid(row=1, column=1, padx=2, pady=2, sticky=tkinter.E+tkinter.W)

btn11 = ttk.Button(tab_1, text="封閉式｜開放式水冷", command=lambda: [
    item_crawler_thread(11, "封閉式｜開放式水冷")])
btn11.grid(row=1, column=2, padx=2, pady=2, sticky=tkinter.E+tkinter.W)

btn14 = ttk.Button(tab_1, text="機殼 CASE", command=lambda: [
    item_crawler_thread(14, "機殼 CASE")])
btn14.grid(row=1, column=3, padx=2, pady=2, sticky=tkinter.E+tkinter.W)

btn16 = ttk.Button(tab_1, text="機殼風扇｜機殼配件", command=lambda: [
    item_crawler_thread(16, "機殼風扇｜機殼配件")])
btn16.grid(row=1, column=4, padx=2, pady=2, sticky=tkinter.E+tkinter.W)

btn27 = ttk.Button(tab_1, text="介面擴充卡｜專業 Raid 卡", command=lambda: [
    item_crawler_thread(27, "介面擴充卡｜專業 Raid 卡")])
btn27.grid(row=1, column=5, padx=2, pady=2, sticky=tkinter.E+tkinter.W)

btn13 = ttk.Button(tab_2, text="螢幕｜投影機｜壁掛", command=lambda: [
    item_crawler_thread(13, "螢幕｜投影機｜壁掛")])
btn13.grid(row=0, column=1, padx=2, pady=2, sticky=tkinter.E+tkinter.W)

btn9 = ttk.Button(tab_2, text="外接硬碟｜隨身碟｜記憶卡", command=lambda: [
    item_crawler_thread(9, "外接硬碟｜隨身碟｜記憶卡")])
btn9.grid(row=0, column=0, padx=2, pady=2, sticky=tkinter.E+tkinter.W)

btn17 = ttk.Button(tab_2, text="鍵盤+鼠｜搖桿｜桌+椅", command=lambda: [
    item_crawler_thread(17, "鍵盤+鼠｜搖桿｜桌+椅")])
btn17.grid(row=0, column=2, padx=2, pady=2, sticky=tkinter.E+tkinter.W)

btn18 = ttk.Button(tab_2, text="滑鼠｜鼠墊｜數位板", command=lambda: [
    item_crawler_thread(18, "滑鼠｜鼠墊｜數位板")])
btn18.grid(row=0, column=3, padx=2, pady=2, sticky=tkinter.E+tkinter.W)

btn19 = ttk.Button(tab_3, text="IP 分享器｜網卡｜網通設備", command=lambda: [
    item_crawler_thread(19, "IP 分享器｜網卡｜網通設備")])
btn19.grid(row=0, column=0, padx=2, pady=2, sticky=tkinter.E+tkinter.W)

btn20 = ttk.Button(tab_3, text="網路 NAS｜網路 IPCAM", command=lambda: [
    item_crawler_thread(20, "網路 NAS｜網路 IPCAM")])
btn20.grid(row=1, column=0, padx=2, pady=2, sticky=tkinter.E+tkinter.W)

btn21 = ttk.Button(tab_2, text="音效卡｜電視卡(盒)｜影音", command=lambda: [
    item_crawler_thread(21, "音效卡｜電視卡(盒)｜影音")])
btn21.grid(row=1, column=4, padx=2, pady=2, sticky=tkinter.E+tkinter.W)

btn22 = ttk.Button(tab_2, text="喇叭｜耳機｜麥克風", command=lambda: [
    item_crawler_thread(22, "喇叭｜耳機｜麥克風")])
btn22.grid(row=1, column=3, padx=2, pady=2, sticky=tkinter.E+tkinter.W)

btn23 = ttk.Button(tab_2, text="燒錄器 CD / DVD / BD", command=lambda: [
    item_crawler_thread(23, "燒錄器 CD / DVD / BD")])
btn23.grid(row=1, column=2, padx=2, pady=2, sticky=tkinter.E+tkinter.W)

btn24 = ttk.Button(tab_2, text="USB 週邊｜硬碟座｜讀卡機", command=lambda: [
    item_crawler_thread(24, "USB 週邊｜硬碟座｜讀卡機")])
btn24.grid(row=1, column=1, padx=2, pady=2, sticky=tkinter.E+tkinter.W)

btn25 = ttk.Button(tab_2, text="行車紀錄器｜USB 視訊鏡頭", command=lambda: [
    item_crawler_thread(25, "行車紀錄器｜USB 視訊鏡頭")])
btn25.grid(row=0, column=4, padx=2, pady=2, sticky=tkinter.E+tkinter.W)

btn26 = ttk.Button(tab_2, text="UPS 不斷電｜印表機｜掃描", command=lambda: [
    item_crawler_thread(26, "UPS 不斷電｜印表機｜掃描")])
btn26.grid(row=1, column=0, padx=2, pady=2, sticky=tkinter.E+tkinter.W)

btn28 = ttk.Button(tab_2, text="網路、傳輸線、轉頭｜KVM", command=lambda: [
    item_crawler_thread(28, "網路、傳輸線、轉頭｜KVM")])
btn28.grid(row=0, column=6, padx=2, pady=2, sticky=tkinter.E+tkinter.W)

btn29 = ttk.Button(tab_3, text="OS + 應用軟體｜禮物卡", command=lambda: [
    item_crawler_thread(29, "OS + 應用軟體｜禮物卡")])
btn29.grid(row=0, column=2, padx=2, pady=2, sticky=tkinter.E+tkinter.W)

frame = Frame(root)
frame.place(x=10, y=180, width=1050, height=610)

scrollBar = ttk.Scrollbar(frame)
scrollBar.pack(side=tkinter.RIGHT, fill=tkinter.Y)

tree = Treeview(frame, columns=('c1', 'c2', 'c3', 'c4'),
                show="headings", yscrollcommand=scrollBar.set)
tree.column('c1', width=620, stretch=tkinter.NO)
tree.column('c2', width=205, stretch=tkinter.NO)
tree.column('c3', width=90, stretch=tkinter.NO)
tree.column('c4', width=115, stretch=tkinter.NO)
tree.heading('c1', text='品名', anchor='w')
tree.heading('c2', text='類別', anchor='w')
tree.heading('c3', text='價格', anchor='w')
tree.heading('c4', text='時間', anchor='w')
tree.pack(side=tkinter.LEFT, fill=tkinter.Y)

tree.bind('<Button-1>', handle_click)
# tree.bind('<ButtonRelease-1>', treeviewClick)
tree.bind('<<TreeviewSelect>>', item_selected)

scrollBar.config(command=tree.yview)

Log_label = Label(root, text="Log:",
                  font=("Microsoft JhengHei", LARGE_FONT, "bold"))
Log_label.place(x=1080, y=335)
frame2 = Frame(root)
frame2.place(x=1080, y=360, width=260, height=430)
scrollBar2 = ttk.Scrollbar(frame2)
scrollBar2.pack(side=tkinter.RIGHT, fill=tkinter.Y)
text = Text(frame2, state=tkinter.DISABLED,
            yscrollcommand=scrollBar2.set, relief=tkinter.FLAT, font=(
                "Microsoft JhengHei", 9, "bold"))
text.pack(side=tkinter.LEFT, fill=tkinter.Y)
scrollBar2.config(command=text.yview)

function_label = Label(root, text="功能:",
                       font=("Microsoft JhengHei", LARGE_FONT, "bold"))
function_label.place(x=1080, y=160)
frame3 = Frame(root)
frame3.place(x=1080, y=190, width=260, height=100)

btn_insert_to_database = ttk.Button(frame3, text="加入至歷史資料庫", command=lambda: [
    db_insert_button_thread()])
btn_insert_to_database.grid(row=0, column=0, padx=5,
                            pady=5, sticky=tkinter.E+tkinter.W)
btn = ttk.Button(frame3,
                 text="開啟歷史資料庫", command=lambda: NewWindow(root), style="Toggle.TButton")
btn.grid(row=1, column=0, padx=5,
         pady=5, sticky=tkinter.E+tkinter.W)
ToolTip(btn_insert_to_database, msg="點擊左側項目再點擊此按鈕", follow=True, delay=1)
ToolTip(btn, msg="查看歷史資料庫紀錄內容", follow=True, delay=1)
root.protocol("WM_DELETE_WINDOW", exit_func)

root.mainloop()
