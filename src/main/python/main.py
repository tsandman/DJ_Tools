from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtGui

from SpotifyGUI import SpotifyGUI

import sys

if __name__ == '__main__':
    appctxt = ApplicationContext()
    app = QApplication(sys.argv)
    ex = SpotifyGUI()
    ex.show()
    sys.exit( appctxt.app.exec_() )
