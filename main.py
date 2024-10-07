import sys
from ui.MainWindow import *

import qdarktheme

if __name__ == '__main__':
    qdarktheme.enable_hi_dpi()
    app = QApplication(sys.argv)

    qdarktheme.setup_theme('light')

    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
