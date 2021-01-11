import PyQt5.QtWidgets as QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import sys
from PyQt5.QtCore import pyqtSlot
import pandas as pd

class App(QMainWindow):
	def __init__(self):
		super(App, self).__init__()
		self.title = "Label Comparison App"
		self.left = 500
		self.top = 200
		self.width = 1200
		self.height = 500
		self.initUI()


	def initUI(self):
		self.setWindowTitle(self.title)
		self.setGeometry(self.left, self.top, self.width, self.height)

		# Create textboxes
		# This textbox has the sentence to compare
		"""self.textbox1 = QLineEdit(self)
		self.textbox1.move(120, 130)

		# This textbox has the first option (original prompt)
		self.textbox2 = QLineEdit(self)
		self.textbox2.move(800, 130)

		# This textbox has the second option (descriptive prompt)
		self.textbox3 = QLineEdit(self)
		self.textbox3.move(1000, 130)"""


		self.label1 = QLabel(self)
		self.label1.setText("Phrase Text")
		self.label1.setFont(QFont('Times', 20))
		self.label1.adjustSize()
		self.label1.move(70, 70)

		self.label2 = QLabel(self)
		self.label2.setText("Label 1")
		self.label2.setFont(QFont("Times", 20))
		self.label2.adjustSize()
		self.label2.move(800, 70)

		self.label3 = QLabel(self)
		self.label3.setText("Label 2")
		self.label3.setFont(QFont("Times", 20))
		self.label3.adjustSize()
		self.label3.move(1000, 70)

		# Create 2 buttons for 2 click events in the window
		self.b1 = QPushButton(self)
		self.b1.setText("Correct")
		self.b1.move(800, 250)
		self.b1.clicked.connect(self.on_click)

		self.b2 = QPushButton(self)
		self.b2.setText("Correct")
		self.b2.move(1000, 250)
		self.b2.clicked.connect(self.on_click)
		#self.b1.move()
	def on_click(self):
		self.label1.setText("Pressed!")



if __name__ == '__main__':
	app = QApplication(sys.argv)
	ex = App()
	ex.show()
	sys.exit(app.exec_())

