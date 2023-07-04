# For the GUI
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import messagebox
from tkinter import colorchooser
from PIL import Image, ImageTk

# For the Serial
import sys
import glob
import serial

# For the geometry inside teh canvas
from geometry import Geometry

# For the save file option
from tkinter import filedialog

# For the obj file conversion
import obj_handler

# For the, you guessed it, threads
from threading import *

# For sleep
import time

# For time measurement of functions
from timer import *

import math

MIN_WIDTH = 700
MIN_HEIGHT = 500


class App(ttk.Frame):

	def __init__(self, parent):
		ttk.Frame.__init__(self)

		# Make the app responsive
		self.columnconfigure(0, weight=0)
		self.columnconfigure(1, weight=8)
		self.columnconfigure(2, weight=0)
		self.rowconfigure(0, weight=1)

		self.connectedStatus = tk.BooleanVar(value=False)
		self.firstConnection = tk.BooleanVar(value=True)

		# Create value lists for the UI
		self.serial_port_menu_list  = ["", "Select Port"]
		self.baud_rate_menu_list    = ["" ,50, 75, 110, 134, 150, 200, 300, 600, 1200, 1800, 2400, 4800, 9600, 19200, 38400, 57600, 115200, 576000, 921600]
		self.data_bits_menu_list    = ["", 5, 6, 7, 8]
		self.parity_menu_list       = ["", "None", "Even", "Odd", "Mark", "Space"]
		self.stop_bits_menu_list    = ["", "One", "OnePointFive", "Two"]

		# Create control variables, also for the UI
		self.default_serial_port_option     = tk.StringVar(value=self.serial_port_menu_list[1])
		self.default_baud_rate_option       = tk.StringVar(value=self.baud_rate_menu_list[17])
		self.default_data_bits_option       = tk.StringVar(value=self.data_bits_menu_list[4])
		self.default_parity_option          = tk.StringVar(value=self.parity_menu_list[1])
		self.default_stop_bits_option       = tk.StringVar(value=self.stop_bits_menu_list[1])

		# Create Serial Control Variables
		self.serial_port_list   = [""];
		self.baud_rate_list     = [50, 75, 110, 134, 150, 200, 300, 600, 1200, 1800, 2400, 4800, 9600, 19200, 38400, 57600, 115200, 576000, 921600]
		self.data_bits_list     = [serial.FIVEBITS, serial.SIXBITS, serial.SEVENBITS, serial.EIGHTBITS]
		self.parity_list        = [serial.PARITY_NONE, serial.PARITY_EVEN, serial.PARITY_ODD, serial.PARITY_MARK, serial.PARITY_SPACE]
		self.stop_bits_list     = [serial.STOPBITS_ONE, serial.STOPBITS_ONE_POINT_FIVE, serial.STOPBITS_TWO]

		# Default values:
		self.selected_serial_port = ""
		self.selected_baud_rate = 115200
		self.selected_data_bits = serial.EIGHTBITS
		self.selected_parity = serial.PARITY_NONE
		self.selected_stop_bits = serial.STOPBITS_ONE


		self._fill_color_holder = "#000000"
		self._line_color_holder = "#0000FF"

		self._canvas_color = tk.StringVar()
		self._canvas_color.set("#505050")

		self.file_name = tk.StringVar() # Initiate a blank file name
		self._file_exists = False # A flag for whether the file has been loaded or not
		self._changed = True # A flag used to only redraw the object when a change occured

		self.current_zoom = 10
		self.MOVING_STEP = 50

		# Serial object:
		self.serialThingy = serial.Serial()

		# Create widgets :)
		self.setup_widgets()

	def setup_widgets(self):

		self.left_frame = ttk.Frame(self, padding=(5, 5))
		self.left_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")

		self.center_frame = ttk.Frame(self, padding=(5, 5))
		self.center_frame.grid(row=0, column=1, padx=0, pady=5, sticky="nsew")

		self.right_frame = ttk.Frame(self, padding=(5, 5))
		self.right_frame.grid(row=0, column=2, padx=10, pady=5, sticky="nsew")

		# Create a frame for the Configuration menu
		self.configuration_menu_frame = ttk.LabelFrame(self.left_frame, text="Configuration", padding=(15, 10))
		self.configuration_menu_frame.pack(fill="both", pady=10)
		# self.configuration_menu_frame.grid(
		# 	row=0, column=0, padx=(20, 10), pady=(10, 10), sticky="nsew"
		# )
		
		self.configuration_menu_frame.columnconfigure(0, weight=1)
		self.configuration_menu_frame.columnconfigure(1, weight=1)
		self.configuration_menu_frame.rowconfigure(0, weight=1)
		self.configuration_menu_frame.rowconfigure(1, weight=1)
		self.configuration_menu_frame.rowconfigure(2, weight=1)
		self.configuration_menu_frame.rowconfigure(3, weight=1)
		self.configuration_menu_frame.rowconfigure(4, weight=1)

		# Import Button
		self.import_model_button = ttk.Button(self.configuration_menu_frame, text="    Import Model    ", command=self.__read_file)
		self.import_model_button.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

		# FILL
		self._check_no_fill = tk.IntVar()
		self._check_no_fill_button = ttk.Checkbutton(self.configuration_menu_frame, text="No fill", variable=self._check_no_fill, command=self.changed, onvalue=True, offvalue=False)
		self._check_no_fill_button.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
		
		self.fill_color = tk.StringVar()
		self.fill_color.set("#000000")
		ttk.Label(self.configuration_menu_frame, text="Fill color:",font=("-size", 12, "-weight", "normal")).grid(row=2, column=0, padx=5, pady=5, sticky="nsew")
		self._fill_btn = tk.Button(self.configuration_menu_frame, text="      ", command=self.__pick_color_fill, relief='flat')
		self._fill_btn.grid(row=2, column=1, padx=5, pady=5, sticky="nsew")
		self._fill_btn['bg'] = self.fill_color.get()

		# LINE
		self.line_color = tk.StringVar()
		self.line_color.set("#5588FF")
		ttk.Label(self.configuration_menu_frame, text="Line color:",font=("-size", 12, "-weight", "normal")).grid(row=3, column=0, padx=5, pady=5, sticky="nsew")
		self._line_btn = tk.Button(self.configuration_menu_frame, text="      ", command=self.__pick_color_line, relief='flat')
		self._line_btn.grid(row=3, column=1, padx=5, pady=5, sticky="nsew")
		self._line_btn['bg'] = self.line_color.get()

		# CANVAS' BACKGROUND
		ttk.Label(self.configuration_menu_frame, text="Canvas color:",font=("-size", 12, "-weight", "normal")).grid(row=4, column=0, padx=5, pady=5, sticky="nsew")
		self._canvas_btn = tk.Button(self.configuration_menu_frame, text="      ", command=self.__pick_color_canvas, relief='flat')
		self._canvas_btn.grid(row=4, column=1, padx=5, pady=5, sticky="nsew")
		self._canvas_btn['bg'] = self._canvas_color.get()


		# Create a frame for the connection menu
		self.connection_menu_frame = ttk.LabelFrame(self.left_frame, text="Connection", padding=(15, 10))
		self.connection_menu_frame.pack(fill="both", pady=10)
		# self.connection_menu_frame.grid(
		# 	row=1, column=0, padx=(20, 10), pady=(10, 10), sticky="nsew"
		# )

		self.connection_menu_frame.columnconfigure(0, weight=3)
		self.connection_menu_frame.columnconfigure(1, weight=1)
		self.connection_menu_frame.rowconfigure(0, weight=1)
		self.connection_menu_frame.rowconfigure(1, weight=1)
		self.connection_menu_frame.rowconfigure(2, weight=1)
		self.connection_menu_frame.rowconfigure(3, weight=1)
		self.connection_menu_frame.rowconfigure(4, weight=1)
		self.connection_menu_frame.rowconfigure(5, weight=1)


		# Ports Menu
		self.ports_menu = ttk.OptionMenu(
			#self.connection_menu_frame, self.default_serial_port_option , *self.serial_port_menu_list
			self.connection_menu_frame, tk.StringVar(value="Select Port") , *self.serial_port_list, command=self.optionMenuSelectSerialPort
		)
		self.ports_menu.grid(row=0, column=0, padx=5, pady=2, sticky="nsew")

		# Refresh Button
		self.refresh_button = ttk.Button(self.connection_menu_frame, text="Refresh", command=self.refreshClick)
		self.refresh_button.grid(row=0, column=1, padx=5, pady=2, sticky="nsew")

		# Baud Rate Label
		self.bauds_label = ttk.Label(
			self.connection_menu_frame,
			text="Baud Rate:",
			justify="left",
			font=("-size", 11, "-weight", "normal"),
		)
		self.bauds_label.grid(row=1, column=0, pady=2)

		# Baud Rate Menu
		self.bauds_menu = ttk.OptionMenu(
			self.connection_menu_frame, self.default_baud_rate_option, *self.baud_rate_menu_list, command=self.optionMenuSelectBaudRate
		)
		self.bauds_menu.grid(row=1, column=1, padx=5, pady=2, sticky="nsew")

		# Data Bits Label
		self.data_bits_label = ttk.Label(
			self.connection_menu_frame,
			text="Data Bits:",
			justify="left",
			font=("-size", 11, "-weight", "normal"),
		)
		self.data_bits_label.grid(row=2, column=0, pady=2)

		# Data Bits Menu
		self.data_bits_menu = ttk.OptionMenu(
			self.connection_menu_frame, self.default_data_bits_option, *self.data_bits_menu_list, command=self.optionMenuSelectDataBits
		)
		self.data_bits_menu.grid(row=2, column=1, padx=5, pady=2, sticky="nsew")

		# Parity Label
		self.parity_label = ttk.Label(
			self.connection_menu_frame,
			text="Parity:",
			justify="left",
			font=("-size", 11, "-weight", "normal"),
		)
		self.parity_label.grid(row=3, column=0, pady=2)
		
		# Parity Menu
		self.parity_menu = ttk.OptionMenu(
			self.connection_menu_frame, self.default_parity_option, *self.parity_menu_list, command=self.optionMenuSelectParity
		)
		self.parity_menu.grid(row=3, column=1, padx=5, pady=2, sticky="nsew")
		
		# Stop Bits Label
		self.stop_bits_label = ttk.Label(
			self.connection_menu_frame,
			text="Stop Bits::",
			justify="left",
			font=("-size", 11, "-weight", "normal"),
		)
		self.stop_bits_label.grid(row=4, column=0, pady=2)

		# Stop Bits Menu
		self.stop_bits_menu = ttk.OptionMenu(
			self.connection_menu_frame, self.default_stop_bits_option, *self.stop_bits_menu_list, command=self.optionMenuSelectStopBits
		)
		self.stop_bits_menu.grid(row=4, column=1, padx=5, pady=2, sticky="nsew")

		# Connect Button
		#self.toggle_button = ttk.Checkbutton(
		#    self.connection_menu_frame, text="Connect", style="Toggle.TButton", command=self.connectClick
		#)
		self.connect_button = ttk.Button(self.connection_menu_frame, text="Connect", command=self.connectClick)
		self.connect_button.grid(row=5, column=0, columnspan=2 ,padx=5, pady=2, sticky="nsew")


		# Create a frame for the main view window canvas
		self.canvas_frame = ttk.LabelFrame(self.center_frame, text="Main viewport", padding=(15, 10))
		self.canvas_frame.pack(fill="both", expand=True, pady=10)
		# self.canvas_frame.grid(
		# 	row=0, rowspan=2, column=1, padx=(10, 10), pady=(10, 10), sticky="nsew"
		# )

		self.__create_canvas()
		self._canvas_w, self._canvas_h = self.get_canvas_shape()
		self._geometry_handler = Geometry(self._canvas_w, self._canvas_h)


		# Create a frame for the translation menu
		self.translation_frame = ttk.LabelFrame(self.right_frame, text="Translation", padding=(15, 10), width=150)
		self.translation_frame.pack(fill="both", pady=10)
		# self.translation_frame.grid(
		# 	row=0, column=2, padx=(10, 10), pady=(10, 10), sticky="nsew"
		# )

		self.translation_frame.columnconfigure(0, weight=1)
		self.translation_frame.columnconfigure(1, weight=1)
		self.translation_frame.columnconfigure(2, weight=1)
		self.translation_frame.rowconfigure(0, weight=1)
		self.translation_frame.rowconfigure(1, weight=1)
		self.translation_frame.rowconfigure(2, weight=1)

		# 🡄 🡆 🡅 🡇

		# Up Button
		self.up_button = ttk.Button(self.translation_frame, text="🡅", command=self.__move_up)
		self.up_button.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

		# Left Button
		self.left_button = ttk.Button(self.translation_frame, text="🡄", command=self.__move_left)
		self.left_button.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

		# Right Button
		self.right_button = ttk.Button(self.translation_frame, text="🡆", command=self.__move_right)
		self.right_button.grid(row=1, column=2, padx=5, pady=5, sticky="nsew")

		# Down Button
		self.down_button = ttk.Button(self.translation_frame, text="🡇", command=self.__move_down)
		self.down_button.grid(row=2, column=1, padx=5, pady=5, sticky="nsew")

		# Home Button
		self.home_button = ttk.Button(self.translation_frame, text="Home", command=self.__zero_position)
		self.home_button.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")


		# Create a frame for the rotation menu
		self.rotation_frame = ttk.LabelFrame(self.right_frame, text="Rotation", padding=(15, 10), width=150)
		self.rotation_frame.pack(fill="both", pady=10)

		# self.rotation_frame.grid(
		# 	row=1, column=2, padx=(10, 10), pady=(10, 10), sticky="nsew"
		# )

		self.rotation_frame.columnconfigure(0, weight=1)
		self.rotation_frame.columnconfigure(1, weight=1)
		self.rotation_frame.columnconfigure(2, weight=1)
		self.rotation_frame.rowconfigure(0, weight=1)
		self.rotation_frame.rowconfigure(1, weight=1)
		self.rotation_frame.rowconfigure(2, weight=1)
		self.rotation_frame.rowconfigure(3, weight=1)


		# X rotation Label
		self.x_rot_label = ttk.Label(
			self.rotation_frame,
			text="X: 0°",
			justify="center",
			font=("-size", 11, "-weight", "normal"),
		)
		self.x_rot_label.grid(row=0, column=1, pady=2)

		# Y rotation Label
		self.y_rot_label = ttk.Label(
			self.rotation_frame,
			text="Y: 0°",
			justify="center",
			font=("-size", 11, "-weight", "normal"),
		)
		self.y_rot_label.grid(row=1, column=1, pady=2)

		# Z rotation Label
		self.z_rot_label = ttk.Label(
			self.rotation_frame,
			text="Z: 0°",
			justify="center",
			font=("-size", 11, "-weight", "normal"),
		)
		self.z_rot_label.grid(row=2, column=1, pady=2)

		# X rotation -5°
		self.x_rot_minus = ttk.Button(self.rotation_frame, text="-5°", command= lambda: self.__rotate(-5,0,0))
		self.x_rot_minus.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

		# X rotation +5°
		self.x_rot_plus = ttk.Button(self.rotation_frame, text="+5°", command= lambda: self.__rotate(+5,0,0))
		self.x_rot_plus.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")

		# Y rotation -5°
		self.y_rot_minus = ttk.Button(self.rotation_frame, text="-5°", command= lambda: self.__rotate(0,-5,0))
		self.y_rot_minus.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

		# Y rotation +5°
		self.y_rot_plus = ttk.Button(self.rotation_frame, text="+5°", command= lambda: self.__rotate(0,+5,0))
		self.y_rot_plus.grid(row=1, column=2, padx=5, pady=5, sticky="nsew")

		# Z rotation -5°
		self.z_rot_minus = ttk.Button(self.rotation_frame, text="-5°", command= lambda: self.__rotate(0,0,-5))
		self.z_rot_minus.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")

		# Z rotation +5°
		self.z_rot_plus = ttk.Button(self.rotation_frame, text="+5°", command= lambda: self.__rotate(0,0,+5))
		self.z_rot_plus.grid(row=2, column=2, padx=5, pady=5, sticky="nsew")

		# Reset rotation
		self.reset_rotation_button = ttk.Button(self.rotation_frame, text="Reset", command=self.__reset_rotation)
		self.reset_rotation_button.grid(row=3, column=0, columnspan=3 ,padx=5, pady=5, sticky="nsew")


		# Sizegrip
		self.sizegrip = ttk.Sizegrip(self)
		self.sizegrip.grid(row=100, column=100, padx=(0, 5), pady=(0, 5))


	def __create_canvas(self):
		self._canvas = tk.Canvas(self.canvas_frame, bg=self._canvas_color.get(), height=MIN_HEIGHT, width=MIN_WIDTH)
		self._canvas.pack(fill="both", expand=True, pady=10)
		
		#self._canvas.place(relx=0.01, rely=0.01, relwidth=self.CANVAS_WIDTH/MIN_WIDTH, relheight=self.CANVAS_HEIGHT/MIN_HEIGHT)
		
		# Catch the canvas resize event
		self._canvas.bind("<Configure>", self.__resized)
	
		# Bind the scrolling on canvas event to zoom slider
		self._canvas.bind('<MouseWheel>', self.__zoom_handler)  # with Windows and MacOS, but not Linux
		#self.canvas.bind('<Button-5>',   self.wheel)  # only with Linux, wheel scroll down
		#self.canvas.bind('<Button-4>',   self.wheel)  # only with Linux, wheel scroll up


	def __read_file(self):
		#messagebox.showinfo(message='Only .obj files are compatible!', title="WARNING")

		file_path = filedialog.askopenfilename(defaultextension=".obj", filetypes=(("OBJ Files", "*.obj"), ("All Files", "*.*")))

		if len(file_path) and file_path[-4:] != ".obj":
			messagebox.showinfo(message="Incompatible file format", title="ERROR")

		elif len(file_path):
			self.file_name.set(file_path.split('/')[-1])
			self.__reset_rotation()
			with open(file_path) as file:
				self._geometry_handler.upload_object(*obj_handler.extract_data(file))
				self._file_exists = True
				self.canvas_frame.configure(text=f"Main viewport - Viewing: {file_path}")

	def __zoom_handler(self, *args):
		zoom_factor = 0.1  # Adjust this value as per your preference
		delta = args[0].delta # Returns -120 for scroll up and 120 for scrol down
		transformed_delta = math.copysign(1, delta) * math.log1p(abs(delta))  # Logarithmic transformation
		
		self.current_zoom += zoom_factor * transformed_delta

		print(f"current_zoom: {self.current_zoom}")
		self._geometry_handler.set_zoom(self.current_zoom)
		self.changed()

	def __set_zoom(self):
		self._geometry_handler.set_zoom(self._zoom_slider.get())


	def __move_up(self):
		self._geometry_handler.update_position(0, -1 * self.MOVING_STEP)
		self.changed()

	def __move_down(self):
		self._geometry_handler.update_position(0, self.MOVING_STEP)
		self.changed()

	def __move_left(self):
		self._geometry_handler.update_position(-1 * self.MOVING_STEP, 0)
		self.changed()

	def __move_right(self):
		self._geometry_handler.update_position(self.MOVING_STEP, 0)
		self.changed()

	def __zero_position(self):
		self._geometry_handler.set_position(round(self._canvas_w/2), round(self._canvas_h/2))
		self.changed()


	def __rotate(self, x, y, z):
		# print(f"x: {x}, y:{y}, z:{z}")

		# Convert to radians
		x = x*math.pi / 180
		y = y*math.pi / 180
		z = z*math.pi / 180
		self._geometry_handler.step_rotation(x, y, z)
		self.update_rot_labels()

		self.changed()


	def __reset_rotation(self):
		self._geometry_handler.reset_rotation()
		self.update_rot_labels()
		self.changed()

	def update_rot_labels(self):
		x, y, z = self._geometry_handler.orientation

		# Convert to degrees:
		x = round(x*180 / math.pi) 
		y = round(y*180 / math.pi) 
		z = round(z*180 / math.pi) 
		self.x_rot_label.configure(text=f"X: {x}°")
		self.y_rot_label.configure(text=f"Y: {y}°")
		self.z_rot_label.configure(text=f"Z: {z}°")

	def get_canvas_shape(self):
		"""returns the shape of the canvas holding the visualized frame"""
		self.update()
		return self._canvas.winfo_width(), self._canvas.winfo_height()


	def __resized(self, *args):
		#print("Resized!")
		'''Callback to the window resize events'''
		w, h = self.get_canvas_shape()
		if self._canvas_w != w or self._canvas_h != h:
			# Keep the object in the middle of the canvas
			self._geometry_handler.update_position((w-self._canvas_w)//2, (h-self._canvas_h)//2)
			self._canvas_w = w
			self._canvas_h = h
			self.changed()

		#print(f"_canvas_w: {self._canvas_w}, _canvas_h: {self._canvas_h}")


	def changed(self, *args):
		'''Signal to the rendering function that something has changed in the object'''
		self._changed = True

	def __draw_object(self):
		'''Draw the object on the canvas'''
		projected_points = self._geometry_handler.transform_object()
		self.__draw_faces(projected_points)
	
	#@time_me
	def __draw_faces(self, points: dict) -> None:
		''''''
		for face in self._geometry_handler.faces:
			# Grab the points that make up that specific face
			to_draw = [points[f] for f in face]
			
			#for point in to_draw:
			#	if(point[0] < 0 or
			#	   point[1] < 0 or
			#	   point[0] > self.CANVAS_WIDTH or
			#	   point[1] > self.CANVAS_HEIGHT
			#	):
			#		continue # Don't draw points that are out of the screen
			#	# This is the slowest part of the GUI
			#	self.__draw_point(point)

			self._canvas.create_polygon(to_draw, outline=self._line_color_holder, fill=self._fill_color_holder)
	

	def __update_colors(self):
		self.__change_fill_color(self.fill_color.get(), self._check_no_fill.get())
		self.__change_line_color(self.line_color.get())

	def __change_fill_color(self, color: str, no_fill: bool = False):
		'''Change the face fill color'''
		self._fill_color_holder = "" if no_fill else color

	def __change_line_color(self, color):
		''''''
		self._line_color_holder = color

#	@time_me
	def render(self):

		'''Render the object on the screen'''
		if self._file_exists and (self._changed):
			#Delete all the previous points and lines in order to draw new ones
			self._canvas.delete("all")
			self.__update_colors()
			self.__draw_object()
			self._changed = False



	def __pick_color_fill(self):
		self.__pick_color("f")

	def __pick_color_line(self):
		self.__pick_color("l")

	def __pick_color_canvas(self):
		self.__pick_color("c")

	def __pick_color(self, picker):
		if(picker == "f"):
			col = colorchooser.askcolor(initialcolor = self.fill_color.get())
			if(col[1]):
				self.fill_color.set(col[1])
				self._fill_btn['bg']  = col[1]
		
		elif(picker == "c"):
			col = colorchooser.askcolor(initialcolor = self._canvas_color.get())
			if(col[1]):
				self._canvas_color.set(col[1])
				self._canvas_btn['bg']  = col[1]
				self._canvas['bg'] = self._canvas_color.get()
		
		else:
			col = colorchooser.askcolor(initialcolor = self.line_color.get())
			if(col[1]):
				self.line_color.set(col[1])
				self._line_btn['bg']  = col[1]
		
		self.changed()



	## Serial Functions ##

	def refreshClick(self):
		""" Lists serial port names on Windows, Linux or Mac.
	
			:raises EnvironmentError:
				On unsupported or unknown platforms
			:returns:
				A list of the serial ports available on the system
		"""
		if sys.platform.startswith('win'):
			ports = ['COM%s' % (i + 1) for i in range(20)]
		elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
			# this excludes your current terminal "/dev/tty"
			ports = glob.glob('/dev/tty[A-Za-z]*')
		elif sys.platform.startswith('darwin'):
			ports = glob.glob('/dev/tty.*')
		else:
			raise EnvironmentError('Unsupported platform')
	
		result = [""]
		for port in ports:
			try:
				s = serial.Serial(port)
				s.close()
				result.append(port)
			except (OSError, serial.SerialException):
				pass

		print("result:")       
		print(result)

		# redo this later using (https://stackoverflow.com/questions/19794069/tkinter-gui-update-choices-of-an-option-menu-depending-on-a-choice-from-another)

		if(len(result) != 1):
			self.serial_port_list = result
			self.selected_serial_port = self.serial_port_list[1]

			self.ports_menu = ttk.OptionMenu(
				self.connection_menu_frame, tk.StringVar(value=self.serial_port_list[1]), *self.serial_port_list, command=self.optionMenuSelectSerialPort
			)
			self.ports_menu.grid(row=0, column=0, padx=5, pady=2, sticky="nsew")
		
		else:
			self.ports_menu = ttk.OptionMenu(
				self.connection_menu_frame, tk.StringVar(value="No ports found"), *[""]
			)
			self.ports_menu.grid(row=0, column=0, padx=5, pady=2, sticky="nsew")

	def connectClick(self):
		if (self.connectedStatus.get() == False and self.selected_serial_port != ""):
			SerialConnect(self)

			if(self.firstConnection.get() == True):
				# Start background thread
				Thread(target=SerialTerminal, args=(app,), daemon=True).start()
				self.firstConnection.set(False)

		else:
			SerialDisconnect(self)



	def updateConnectButton(self):
		if(self.connectedStatus.get() == True):
			self.connect_button.config(text="Disconnect", style="Accent.TButton")
		else:
			self.connect_button.config(text="Connect", style="")

	def optionMenuSelectSerialPort(self, value):
		self.selected_serial_port = value
		self.serialThingy.port = self.selected_serial_port

	def optionMenuSelectBaudRate(self, value):
		self.selected_baud_rate = self.baud_rate_list[self.baud_rate_menu_list.index(value) - 1]
		self.serialThingy.baudrate = self.selected_baud_rate

	def optionMenuSelectDataBits(self, value):
		self.selected_data_bits = self.data_bits_list[self.data_bits_menu_list.index(value) - 1]
		self.serialThingy.bytesize = self.selected_data_bits

	def optionMenuSelectParity(self, value):
		self.selected_parity = self.parity_list[self.parity_menu_list.index(value) - 1]
		self.serialThingy.parity = self.selected_parity

	def optionMenuSelectStopBits(self, value):
		self.selected_stop_bits = self.stop_bits_list[self.stop_bits_menu_list.index(value) - 1]
		self.serialThingy.stopbits = self.selected_stop_bits



def SerialTerminal(app):

	while True:
		if(app.connectedStatus.get() == True and app.serialThingy.is_open):
			try:
				chars = app.serialThingy.readline()
				if(len(chars) != 0):
					decoded = chars.decode("utf-8").rstrip()
					decoded = decoded.split(';')					
					
					try:
						#print(decoded)
						#print(f"Azimuth: {decoded[0]} Pitch: {decoded[1]} Roll: {decoded[2]}")
						# Convert to radians
						x = - int(decoded[1])*math.pi / 180
						y = int(decoded[0])*math.pi / 180
						z = int(decoded[2])*math.pi / 180
						
						app._geometry_handler.set_rotation(x, y, z)
						app.update_rot_labels()
						app.changed()
					except Exception as e:
						print("There was an error: ", e)
					
			except:
				print("Error reading from port. Perhaps it has been disconnected.")
				SerialDisconnect(app)


def SerialConnect(app):
	app.serialThingy.port = app.selected_serial_port
	app.serialThingy.baudrate = app.selected_baud_rate
	app.serialThingy.parity = app.selected_parity
	app.serialThingy.stopbits = app.selected_stop_bits
	app.serialThingy.bytesize = app.selected_data_bits

	try:
		app.serialThingy.open()
	except:
		print("Something went wrong when oppening the serial port")

	if(app.serialThingy.is_open):
		app.connectedStatus.set(True)
		app.updateConnectButton()        


def SerialDisconnect(app):
	app.serialThingy.close()

	if(not app.serialThingy.is_open):
		app.connectedStatus.set(False)
		app.updateConnectButton()
	else:
		print("Something went wrong when closing the serial port")

	

def on_close():

	action = tk.messagebox.askquestion(title="Goodbye", message="Any unsaved data will be lost.\nDo you wish to close?")
	if action == 'yes':
		  root.destroy()

def kill(event):
	root.destroy()
	print("Ctrl+C detected, bye")

def _update_display(app):
	while True:
		time.sleep(0.1)
		app.render()


if __name__ == "__main__":
	
	root = tk.Tk()
	root.title("RenderWorld")
	icon = Image.open('LogoRenderWorld.bmp')
	photo = ImageTk.PhotoImage(icon)
	root.wm_iconphoto(True, photo)

	# Set the theme
	root.tk.call("source", "azure.tcl")
	root.tk.call("set_theme", "dark")

	app = App(root)
	app.pack(fill="both", expand=True)

	# Set a minsize for the window, and place it in the middle
	root.update()
	root.minsize(MIN_WIDTH, MIN_HEIGHT)
	#x_cordinate = int((root.winfo_screenwidth() / 2) - (MIN_WIDTH / 2))
	#y_cordinate = int((root.winfo_screenheight() / 2) - (MIN_HEIGHT / 2))
	#root.geometry("+{}+{}".format(x_cordinate, y_cordinate-20))


	Thread(target=_update_display, args=(app, ), daemon=True).start()

	root.protocol("WM_DELETE_WINDOW",  on_close)
	root.bind('<Control-c>', kill)

	root.mainloop()


