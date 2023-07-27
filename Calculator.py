import tkinter as tk
import mysql.connector

#Koneksi dengan database
db = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="kalkulator"
)

cursor = db.cursor()
sql = "SELECT * FROM hasil_operasi"
cursor.execute(sql)

results = cursor.fetchall()

LARGE_FONT_STYLE = ('Squada One', 40)
SMALL_FONT_STYLE = ('Squada One', 16)
DIGIT_FONT_STYLE = ('Squada One', 24, 'bold')
DEFAULT_FONT_STYLE = ('Squada One', 20)

GREY_WHITE = '#d5ddf2'
LIGHT_GREY = '#F5F5F5'
LABEL_COLOR = '#25265E'
BLUE = '#abc0f5'
WHITE = '#FFFFFF'

class Calculator:
    # Class constructor
    def __init__(self):
        self.window = tk.Tk()
        self.window.geometry('375x667')
        self.window.resizable(0, 0)
        self.window.title('Calculator')
        self.total_expression = ''
        self.current_expression = ''
        self.display_frame = self.create_display_frame()
        
        self.total_label, self.current_label = self.create_label_display()
        
        self.digits = {
            7: (1, 1), 8: (1,2), 9: (1,3),
            4: (2,1), 5: (2,2), 6: (2,3),
            1: (3,1), 2: (3,2), 3: (3,3),
            '.': (4,1), 0: (4,2) 
        }
        
        self.operations = {'/' : '\u00F7', '*' : '\u00D7', '-' : '-', '+' : '+'}
        
        self.buttons_frame = self.create_button_frame()
        
        self.buttons_frame.rowconfigure(0, weight=1)
        
        for x in range(1, 5):
            self.buttons_frame.rowconfigure(x, weight=1)
            self.buttons_frame.columnconfigure(x, weight=1)
        
        self.create_digit_button()
        self.create_operator_buttons()
        self.create_clear_buttons()
        self.create_equal_buttons()
        self.create_square_buttons()
        self.create_sqrt_buttons()
        self.create_history_buttons()
        self.bind_keys()
    
    #Fungsi yang digunakan untuk membuat frame tampilan hasil operasi pada kalkulator
    def create_display_frame(self):
        frame = tk.Frame(self.window, height=221, bg = LIGHT_GREY)
        frame.pack(expand = True, fill='both')
        
        return frame
    
    #Fungsi yang digunakan untuk membyat frame tampilan button pada kalkulator
    def create_button_frame(self):
        frame = tk.Frame(self.window)
        frame.pack(expand = True, fill='both')
        return frame
    
    #Fungsi untuk binding key
    def bind_keys(self):
        self.window.bind('<Return>', lambda event: self.evaluate())
        for key in self.digits:
            self.window.bind(str(key), lambda event, digit = key: self.add_to_expression(digit))
            
        for key in self.operations:
            self.window.bind(str(key), lambda event, operator = key: self.append_operator(operator))
    
    #Fungsi untuk memunculkan button
    def create_operator_buttons(self):
        i = 0
        for operator, symbol in self.operations.items():
            button = tk.Button(self.buttons_frame, 
                               text = symbol, 
                               bg = GREY_WHITE, 
                               fg = LABEL_COLOR, 
                               font = DEFAULT_FONT_STYLE,
                               borderwidth=0,
                               command= lambda x = operator : self.append_operator(x))
            
            button.grid(row=i, column=4, sticky=tk.NSEW)
            
            i += 1
    
    #Untuk menghapus semua operasi pada tampilan kalkulator
    def clear(self):
        self.current_expression = ''
        self.total_expression = ''
        self.update_total_label()
        self.update_current_label()
    
    #Fungsi untuk menampilkan symbol operasi pada kalkulator
    def append_operator(self, operator):
        self.current_expression += operator
        self.total_expression += self.current_expression
        self.current_expression = ''
        self.update_total_label()
        self.update_current_label()
    
    #Fungsi untuk melakukan operasi pada kalkulator
    def evaluate(self):
        self.total_expression += self.current_expression
        self.update_total_label()
        
        try:
            self.current_expression =str(eval(self.total_expression))
            expression = self.total_expression
            for operator, symbol in self.operations.items():
                    expression = expression.replace(operator, f' {symbol} ')
            sql = "INSERT INTO hasil_operasi (total_label, current_label) VALUES (%s, %s)"
            val = (expression, self.current_expression)
            cursor.execute(sql, val)
            
            db.commit()
            
            self.total_expression = ''
            self.update_total_label()
        except Exception as e:
            self.current_expression = 'Value Error'
        finally:
            self.update_current_label()
    
    #Untuk mengkuadratkan angka pada kalkulator
    def square(self):
        self.current_expression = str(eval(f'{self.current_expression}**2'))
        self.update_current_label()
    
    #Untuk mengakarkan angka pada kalkulator
    def sqrt(self):
        self.current_expression = str(eval(f'{self.current_expression}**0.5'))
        self.update_current_label()
    
    #Untuk menambahkan angka pada current_label
    def add_to_expression(self, value):
        self.current_expression += str(value)
        self.update_current_label()
    
    #Untuk mengambil data pada database lalu ditampilkan pada kalkulator
    def take_history(self, index):
        sql = "SELECT * FROM hasil_operasi WHERE id =" + index
        cursor.execute(sql)

        results = cursor.fetchall()
        
        self.current_expression = results[0][2]
        self.update_current_label()
        self.update_total_label()
        
    #Untuk menampilkan semua data history pada database di kalkulator
    def show_history(self):
        
        sql = "SELECT * FROM hasil_operasi"
        cursor.execute(sql)

        results = cursor.fetchall()
        
        history_window = tk.Toplevel(self.window)
        history_window.title("History")
        history_window.geometry('375x300')

        history_frame = tk.Frame(history_window)
        history_frame.pack()
        
        scrollbar = tk.Scrollbar(history_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        history_canvas = tk.Canvas(
        history_frame,
        bg=LIGHT_GREY,
        yscrollcommand=scrollbar.set)
        history_canvas.pack(expand=True, fill='both')
        
        scrollbar.config(command=history_canvas.yview)
        
        history_frame_inner = tk.Frame(history_canvas)
        history_canvas.create_window((0, 0), window=history_frame_inner, anchor=tk.NW)

        for index, expression, result in results:
            button = tk.Button(
                history_frame_inner,
                text=f"{expression} = {result}",
                bg=GREY_WHITE,
                fg=LABEL_COLOR,
                font=SMALL_FONT_STYLE,
                command=lambda i=index: self.take_history(str(i))
            )
            button.pack(expand=True, fill='both')

        history_frame_inner.update_idletasks()

        history_canvas.config(scrollregion=history_canvas.bbox(tk.ALL))
        
        

    
    #Membuat tombol clear pada kalkulator
    def create_clear_buttons(self):
        button = tk.Button(self.buttons_frame, 
                               text = 'C', 
                               bg = GREY_WHITE, 
                               fg = LABEL_COLOR, 
                               font = DEFAULT_FONT_STYLE,
                               borderwidth=0,
                               command= lambda: self.clear())
            
        button.grid(row=0, column=1, sticky=tk.NSEW)

    #Membuat tombol '=' pada kalkulator
    def create_equal_buttons(self):
        button = tk.Button(self.buttons_frame, 
                               text = '=', 
                               bg = BLUE, 
                               fg = LABEL_COLOR, 
                               font = DEFAULT_FONT_STYLE,
                               borderwidth=0,
                               command= lambda: self.evaluate())
            
        button.grid(row=4, column=3, columnspan = 2, sticky=tk.NSEW)
    
    
    #Membuat tombol kuadrat pada kalkulator 
    def create_square_buttons(self):
        button = tk.Button(self.buttons_frame, 
                               text = 'x\u00b2', 
                               bg = GREY_WHITE, 
                               fg = LABEL_COLOR, 
                               font = DEFAULT_FONT_STYLE,
                               borderwidth=0,
                               command= lambda: self.square())
            
        button.grid(row=0, column=2, sticky=tk.NSEW)
    
    #Membuat button history pada kalkulator
    def create_history_buttons(self):
        button = tk.Button(self.buttons_frame, 
                               text = 'History', 
                               bg = GREY_WHITE, 
                               fg = LABEL_COLOR, 
                               font = DEFAULT_FONT_STYLE,
                               borderwidth=0,
                               command= lambda: self.show_history())
            
        button.grid(row=4, column=2, sticky=tk.NSEW)
    
    #Membuat tombol akar pada kalkulator
    def create_sqrt_buttons(self):
        button = tk.Button(self.buttons_frame, 
                               text = '\u221ax', 
                               bg = GREY_WHITE, 
                               fg = LABEL_COLOR, 
                               font = DEFAULT_FONT_STYLE,
                               borderwidth=0,
                               command= lambda: self.sqrt())
            
        button.grid(row=0, column=3, sticky=tk.NSEW)
    
    #Membuat tombol digit pada kalkulator
    def create_digit_button(self):
        for digit, grid in self.digits.items():
            button = tk.Button(self.buttons_frame, 
                               text = str(digit), 
                               bg = WHITE, 
                               fg = LABEL_COLOR, 
                               font=DIGIT_FONT_STYLE, 
                               borderwidth = 0,
                               command = lambda x = digit: self.add_to_expression(x))
            button.grid(row=grid[0], column=grid[1], sticky=tk.NSEW)
    
    #Membuat tampilan operasi pada kalkulator
    def create_label_display(self):
        total_label = tk.Label(self.display_frame, 
                         text = self.total_expression, 
                         anchor = tk.E, 
                         bg = LIGHT_GREY, 
                         fg = LABEL_COLOR, 
                         padx = 24, 
                         font=SMALL_FONT_STYLE)
        
        total_label.pack(expand=True, fill = 'both')
        
        current_label = tk.Label(self.display_frame, 
                         text = self.current_expression, 
                         anchor = tk.E, 
                         bg = LIGHT_GREY, 
                         fg = LABEL_COLOR, 
                         padx = 24, 
                         font=LARGE_FONT_STYLE)
        
        current_label.pack(expand=True, fill = 'both')
        
        return total_label, current_label
    
    #Untuk update perubahan pada operasi
    def update_total_label(self):
        expression = self.total_expression
        for operator, symbol in self.operations.items():
            expression = expression.replace(operator, f' {symbol} ')
        self.total_label.config(text = expression)
    
    #Untuk update perubahan pada operasi hasil
    def update_current_label(self):
        self.current_label.config(text = self.current_expression[:11])
    
    #looping aplikasi
    def run(self):
        self.window.mainloop()
    
    
if __name__ == '__main__':
    calc = Calculator()
    calc.run()