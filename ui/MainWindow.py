import os
import sys
import time

from PySide2.QtCore import Qt, QThread, Signal, QSize
from PySide2.QtWidgets import (QApplication, QComboBox, QFormLayout,
    QHBoxLayout, QLineEdit, QPlainTextEdit, QTextEdit, QMainWindow, QPushButton, QSlider, QWidget, QLabel)

from PySide2.QtTextToSpeech import QTextToSpeech, QVoice
from PySide2.QtGui import QMovie, QPixmap, QIcon

#from utils.ImagesUtil import *

class SpeechThread(QThread):
    # Signal to indicate that speech has finished
    speechFinished = Signal()
    speechStatus = Signal(bool)

    def __init__(self, text, speechEngine):
        super().__init__()
        self.text = text
        self.speechEngine = speechEngine
        self.speechEngine.stateChanged.connect(self.stateChanged)
        print("Intitialize thread.")

    def run(self):
        print('Thread started')
        self.speechEngine.say(self.text)
        # Wait until the speech is finished, as `say()` is asynchronous
        '''
        while self.speechEngine.state() == QTextToSpeech.Speaking:
            time.sleep(0.1)  # Sleep briefly to avoid UI block
        self.speechFinished.emit()  # Emit the signal when done
        '''

    def stateChanged(self, state):
        if state == QTextToSpeech.Speaking:
            print('Thread speaking...')
            self.speechStatus.emit(True)
        elif state == QTextToSpeech.Ready:
            print('Thread finished')
            self.speechFinished.emit(False)
        elif state == QTextToSpeech.Paused:
            print("Speech is paused.")

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.initResources()

        #self.imageUtil = ImagesUtil()
        self.appIcon = QIcon()
        self.appIcon.addFile(self.appPng)
        self.setWindowIcon(self.appIcon)
        self.setWindowTitle('Tarsier Text to Speech')

        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)
        layout = QFormLayout(centralWidget)

        self.imageLabel = QLabel()
        pixmap = QPixmap(self.speakingPng)
        self.imageLabel.setPixmap(self.scalePixmap(pixmap, 80, 80))
        self.imageLabel.setAlignment(Qt.AlignCenter)
        layout.addRow(self.imageLabel)

        textLayout = QHBoxLayout()

        self.text = QTextEdit()
        self.text.setPlaceholderText('Type...')
        textLayout.addWidget(self.text)

        self.sayButton = QPushButton('Play')
        textLayout.addWidget(self.sayButton, alignment=Qt.AlignBottom)

        self.loadingLabel = QLabel()
        self.loadingLabel.setAlignment(Qt.AlignCenter)
        layout.addRow(self.loadingLabel)
        self.loadingLabel.hide()

        # Use QMovie to play the loading GIF
        self.loadingMovie = QMovie(self.speakingGif)
        self.loadingMovie.setScaledSize(QSize(100, 100))  # Scale the movie
        self.loadingLabel.setMovie(self.loadingMovie)
        self.loadingMovie.start()

        self.sayButton.clicked.connect(self.say)
        layout.addRow('Text:', textLayout)

        self.voiceCombo = QComboBox()
        layout.addRow('Voice:', self.voiceCombo)

        self.volumeSlider = QSlider(Qt.Horizontal)
        self.volumeSlider.setMinimum(0)
        self.volumeSlider.setMaximum(100)
        self.volumeSlider.setValue(100)
        layout.addRow('Volume:', self.volumeSlider)

        self.engineLabel = QLabel('Engine...', self)
        layout.addRow('Synthesis Engine:', self.engineLabel)

        # Initialize QTextToSpeech
        self.speechEngine = QTextToSpeech()
        engineNames = QTextToSpeech.availableEngines()
        if len(engineNames) > 0:
            engineName = engineNames[0]
            self.speechEngine = QTextToSpeech(engineName)
            self.speechEngine.stateChanged.connect(self.stateChanged)
            self.engineLabel.setText('TextToSpeech({})'.format(engineName))
            self.voices = []
            for voice in self.speechEngine.availableVoices():
                self.voices.append(voice)
                self.voiceCombo.addItem(voice.name())
        else:
            self.engineLabel.setText('TextToSpeech (no engines available)')
            self.sayButton.setEnabled(False)

    def initResources(self):
        scriptDir = os.path.dirname(__file__)
        self.speakPng = os.path.join(scriptDir, '../resources/speak.png')
        self.speakGif = os.path.join(scriptDir, '../resources/speak.gif')
        self.speakingPng = os.path.join(scriptDir, '../resources/speaking.png')
        self.speakingGif = os.path.join(scriptDir, '../resources/speaking.gif')
        self.appPng = os.path.join(scriptDir, '../resources/speaking.png')

    def say(self):
        # Show the loading GIF
        self.imageLabel.hide();
        self.loadingLabel.show()
        self.loadingMovie.start()

        # Update the UI immediately
        QApplication.processEvents()

        self.sayButton.setText('Speaking...')
        self.sayButton.setEnabled(False)

        self.speechEngine.setVoice(self.voices[self.voiceCombo.currentIndex()])
        self.speechEngine.setVolume(float(self.volumeSlider.value()) / 100)
        self.speechEngine.say(self.text.toPlainText())

        # Create and start the speech thread
        '''
        self.speechThread = SpeechThread(self.text.toPlainText(), self.speechEngine)
        self.speechThread.speechFinished.connect(self.onSpeechFinished)
        self.speechThread.speechStatus.connect(self.onSpeechStatusChanged)
        self.speechThread.start()
        '''

    def onSpeechStatusChanged(self, status):
        if status == false:
            print("[onSpeechStatusChanged] Speech in a thread has finished.")
        else:
            print("[onSpeechStatusChanged] Speech in a thread is running.")


    def onSpeechFinished(self):
        # Stop the loading GIF when the speech finishes
        print("Speech in a thread has finished.")

        self.sayButton.setText('Play')
        self.sayButton.setEnabled(True)
        self.loadingMovie.stop()
        self.loadingLabel.hide()
        self.imageLabel.show()

    def stateChanged(self, state):
        if state == QTextToSpeech.Speaking:
            print("Speech is running...")
            self.sayButton.setEnabled(False)
        elif state == QTextToSpeech.Ready:
            print("Speech has finished.")
            self.sayButton.setText('Play')
            self.sayButton.setEnabled(True)
            # Stop the loading GIF when speech finishes
            self.loadingMovie.stop()
            self.loadingLabel.hide()
            self.imageLabel.show()
        elif state == QTextToSpeech.Paused:
            print("Speech is paused.")


    def scalePixmap(self, pixmap, width, height):
        # Convert QPixmap to QImage
        image = pixmap.toImage()

        # Scale the image smoothly
        scaled_image = image.scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        # Convert back to QPixmap
        return QPixmap.fromImage(scaled_image)

