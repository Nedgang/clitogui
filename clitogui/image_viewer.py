"""Implementation of a generalist image viewer"""

try:
    from PIL import Image
    from PIL import ImageQt
except ImportError:
    Image = None

try:
    from PySide2.QtWidgets import *
    from PySide2.QtCore import *
    from PySide2.QtGui import *
except ImportError:
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *


class ImageView(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.setScene(QGraphicsScene())
        self.setBackgroundBrush(QBrush(Qt.white))
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

    def wheelEvent(self, event):
        zoomInFactor = 1.25
        zoomOutFactor = 1 / zoomInFactor

        # Save the scene pos
        oldPos = self.mapToScene(event.pos())

        # Zoom
        if event.angleDelta().y() > 0:
            zoomFactor = zoomInFactor
        else:
            zoomFactor = zoomOutFactor
        self.scale(zoomFactor, zoomFactor)

        # Get the new position
        newPos = self.mapToScene(event.pos())

        # Move scene to old position
        delta = newPos - oldPos
        self.translate(delta.x(), delta.y())

    def set_image(self, image: Image):
        # self.png_item = QGraphicsSvgItem('tmp.svg')
        self.image = image
        self.qimage = ImageQt.ImageQt(self.image)
        self.qpixmap = QPixmap.fromImage(self.qimage)
        self.png_item = QGraphicsPixmapItem(self.qpixmap)
        self.scene().clear()
        self.scene().addItem(self.png_item)
        self.scene().setSceneRect(self.png_item.sceneBoundingRect())


class ImageViewer(QWidget):
    def __init__(self, image: Image = None, parent=None):
        super().__init__(parent=parent)
        self.setWindowTitle("Image viewer")
        self.tool_bar = QToolBar()
        self.view = ImageView()

        _layout = QVBoxLayout()
        _layout.addWidget(self.tool_bar)
        _layout.addWidget(self.view)
        _layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(_layout)
        self.set_image(image)

    def set_image(self, image: Image):
        self.view.set_image(image)
