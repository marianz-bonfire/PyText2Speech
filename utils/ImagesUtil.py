from PySide2.QtCore import Qt
from PySide2.QtGui import QPixmap

class ImagesUtil:
    def __init__(self):
        super(ImagesUtil, self).__init__()

    def scalePixmap(self, pixmap, width, height):
        # Convert QPixmap to QImage
        image = pixmap.toImage()

        # Scale the image smoothly
        scaleImage = image.scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        # Convert back to QPixmap
        return QPixmap.fromImage(scaleImage)