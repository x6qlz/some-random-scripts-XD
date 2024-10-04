import uuid
import time
import sys
import os
import shutil
import subprocess
import psutil
import tempfile
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QTabWidget, QTextEdit, QPushButton, QLineEdit, 
    QFileDialog, QMessageBox, QLabel, QHBoxLayout, QTreeView, QFileSystemModel, QSizePolicy, QSpacerItem, QFontDialog, QMenu, QInputDialog, QAbstractItemView
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QFileInfo, QStandardPaths
import zipfile

class FileViewer(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.layout = QVBoxLayout()
        
        self.model = QFileSystemModel()
        self.model.setRootPath(os.path.expanduser("~"))
        
        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(os.path.expanduser("~")))
        self.tree.clicked.connect(self.on_tree_clicked)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)

        
        self.tree.setSelectionMode(QAbstractItemView.ExtendedSelection)
        
        self.layout.addWidget(self.tree)
        
        self.searchLineEdit = QLineEdit()
        self.searchLineEdit.setPlaceholderText("Enter folder or program name")
        self.layout.addWidget(self.searchLineEdit)
        
        self.searchButton = QPushButton("Search")
        self.searchButton.clicked.connect(self.search_files)
        self.layout.addWidget(self.searchButton)
        
        self.infoLabel = QLabel()
        self.layout.addWidget(self.infoLabel)
        
        self.layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.compressButton = QPushButton("Compress Files")
        self.compressButton.clicked.connect(self.compress_files)  
        self.layout.addWidget(self.compressButton)

        self.setLayout(self.layout)
          
    def on_tree_clicked(self, index):
        path = self.model.filePath(index)
        info = self.get_file_info(path)
        self.infoLabel.setText(info)
    
    def get_file_info(self, path):
        info = ""
        file_info = QFileInfo(path)
        if file_info.exists():
            info += f"<b>Name:</b> {file_info.fileName()}<br>"
            info += f"<b>Path:</b> {file_info.absoluteFilePath()}<br>"
            if file_info.isDir():
                info += f"<b>Type:</b> Directory<br>"
            else:
                info += f"<b>Type:</b> {file_info.suffix()}<br>"
                info += f"<b>Size:</b> {file_info.size()} bytes<br>"
            info += f"<b>Creation Date:</b> {file_info.created().toString()}<br>"
            info += f"<b>Last Modified:</b> {file_info.lastModified().toString()}<br>"
            info += f"<b>Permissions:</b> {file_info.permissions()}<br>"
        return info
    
    def search_files(self):
        search_text = self.searchLineEdit.text()
        root_path = self.model.rootPath()
        search_index = self.model.index(root_path)
        matched_indexes = self.model.match(search_index, Qt.DisplayRole, search_text, -1, Qt.MatchContains | Qt.MatchRecursive)
        if matched_indexes:
            
            self.tree.clearSelection()
            
            self.tree.setCurrentIndex(matched_indexes[0])
            
            for index in matched_indexes:
                self.tree.expand(index)
            
            self.tree.setFocus()
        else:
            QMessageBox.information(self, "Search", "No matching files or folders found.")

    def show_context_menu(self, position):
        index = self.tree.indexAt(position)
        if index.isValid():
            menu = QMenu()
            menu.addAction("Rename", lambda: self.rename_file(index))
            menu.addAction("Delete", lambda: self.delete_file(index))
            menu.addAction("Open in File Editor", lambda: self.open_in_file_editor(index))  
            menu.exec_(self.tree.viewport().mapToGlobal(position))

    def open_in_file_editor(self, index):  
        path = self.model.filePath(index)
        try:
            with open(path, 'r') as file:
                content = file.read()
                
                file_editor = None
                for i in range(self.main_window.tabs.count()):
                    widget = self.main_window.tabs.widget(i)
                    if isinstance(widget, FileEditor):
                        file_editor = widget
                        break
                if file_editor:
                    file_editor.textEdit.setPlainText(content)
                else:
                    QMessageBox.critical(self, "Error", "File Editor not found.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open file in editor: {e}")

    def rename_file(self, index):
        old_path = self.model.filePath(index)
        new_name, ok = QInputDialog.getText(self, "Rename", "New Name:")
        if ok and new_name:
            new_path = os.path.join(os.path.dirname(old_path), new_name)
            try:
                os.rename(old_path, new_path)
                self.model.setRootPath("")  
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not rename file: {e}")

    def delete_file(self, index):
        path = self.model.filePath(index)
        if os.path.isdir(path):
            ok = QMessageBox.question(self, "Delete", "Are you sure you want to delete this folder and its contents?", QMessageBox.Yes | QMessageBox.No)
        else:
            ok = QMessageBox.question(self, "Delete", "Are you sure you want to delete this file?", QMessageBox.Yes | QMessageBox.No)
        if ok == QMessageBox.Yes:
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
                self.model.setRootPath("")  
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not delete file or folder: {e}")

    def compress_files(self):  
        selected_indexes = self.tree.selectionModel().selectedIndexes()
        if len(selected_indexes) < 2:
            QMessageBox.information(self, "Compression", "Please select at least two files to compress.")
            return

        
        file_paths = [self.model.filePath(index) for index in selected_indexes]

        
        destination_dir = QFileDialog.getExistingDirectory(self, "Select Destination Directory")
        if not destination_dir:
            return

        
        zip_name, ok = QInputDialog.getText(self, "ZIP Archive Name", "Enter the name of the ZIP archive:")
        if not ok or not zip_name:
            return

        
        try:
            zip_filename = os.path.join(destination_dir, f"{zip_name}.zip")
            with zipfile.ZipFile(zip_filename, 'w') as zipf:
                for file_path in file_paths:
                    
                    unique_id = str(uuid.uuid4())
                    
                    filename_without_ext = os.path.splitext(os.path.basename(file_path))[0]
                    
                    file_extension = os.path.splitext(file_path)[1]
                    
                    unique_filename = f"{filename_without_ext}_{unique_id}{file_extension}"
                    
                    zipf.write(file_path, arcname=unique_filename)
            QMessageBox.information(self, "Compression", "Files compressed successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Compression Error", f"Failed to compress files: {e}")


class FileEditor(QWidget):
    def __init__(self):
        super().__init__()
        
        self.layout = QVBoxLayout()
        
        self.textEdit = QTextEdit()
        self.layout.addWidget(self.textEdit)
        
        self.buttonLayout = QHBoxLayout()
        
        self.loadButton = QPushButton("Load File")
        self.loadButton.clicked.connect(self.load_file)
        self.buttonLayout.addWidget(self.loadButton)
        
        self.saveButton = QPushButton("Save File")
        self.saveButton.clicked.connect(self.save_file)
       
        self.buttonLayout.addWidget(self.saveButton)

        self.runButton = QPushButton("Run Script")
        self.runButton.clicked.connect(self.run_script)
        self.buttonLayout.addWidget(self.runButton)
        
        self.changeFontButton = QPushButton("Change Font")  
        self.changeFontButton.clicked.connect(self.change_font)  
        self.buttonLayout.addWidget(self.changeFontButton)  
        
        self.layout.addLayout(self.buttonLayout)

        self.setLayout(self.layout)
        
    def load_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*);;Text Files (*.txt)", options=options)
        if file_name:
            try:
                with open(file_name, 'r') as file:
                    content = file.read()
                    self.textEdit.setPlainText(content)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not load file: {e}")
    
    def save_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Save File", "", "All Files (*);;Text Files (*.txt)", options=options)
        if file_name:
            try:
                with open(file_name, 'w') as file:
                    content = self.textEdit.toPlainText()
                    file.write(content)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not save file: {e}")

    def run_script(self):
        script = self.textEdit.toPlainText()
        with open("temp_script.py", "w") as f:
            f.write(script)
        try:
            subprocess.run(["python", "temp_script.py"], check=True)
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "Error", f"Failed to run script: {e}")

    def change_font(self):
        font, ok = QFontDialog.getFont(self.textEdit.font())  
        if ok:
            self.textEdit.setFont(font)  # Set font to textEdit


class FileMover(QWidget):
    def __init__(self):
        super().__init__()
        
        self.layout = QVBoxLayout()
        
        self.sourceLabel = QLabel("Source File/Folder:")
        self.layout.addWidget(self.sourceLabel)
        
        self.sourceLineEdit = QLineEdit()
        self.layout.addWidget(self.sourceLineEdit)
        
        self.sourceButton = QPushButton("Browse")
        self.sourceButton.clicked.connect(self.browse_source)
        self.layout.addWidget(self.sourceButton)
        
        self.destinationLabel = QLabel("Destination Directory:")
        self.layout.addWidget(self.destinationLabel)
        
        self.destinationLineEdit = QLineEdit()
        self.layout.addWidget(self.destinationLineEdit)
        
        self.destinationButton = QPushButton("Browse")
        self.destinationButton.clicked.connect(self.browse_destination)
        self.layout.addWidget(self.destinationButton)
        
        self.moveButton = QPushButton("Move")
        self.moveButton.clicked.connect(self.move_file)
        self.layout.addWidget(self.moveButton)
        
        self.setLayout(self.layout)
    
    def browse_source(self):
        source_path, _ = QFileDialog.getOpenFileName(self, "Select Source File/Folder")
        if source_path:
            self.sourceLineEdit.setText(source_path)
    
    def browse_destination(self):
        destination_path = QFileDialog.getExistingDirectory(self, "Select Destination Directory")
        if destination_path:
            self.destinationLineEdit.setText(destination_path)
    
    def move_file(self):
        source_path = self.sourceLineEdit.text()
        destination_path = self.destinationLineEdit.text()
        if not os.path.exists(source_path):
            QMessageBox.critical(self, "Error", "Source does not exist.")
            return
        try:
            shutil.move(source_path, destination_path)
            QMessageBox.information(self, "Success", "File/Folder moved successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not move: {e}")

class SystemInfo(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()

        self.cpuLabel = QLabel()
        self.layout.addWidget(self.cpuLabel)

        self.memoryLabel = QLabel()
        self.layout.addWidget(self.memoryLabel)

        self.diskLabel = QLabel()
        self.layout.addWidget(self.diskLabel)

        self.networkLabel = QLabel()
        self.layout.addWidget(self.networkLabel)

        self.processesLabel = QLabel()
        self.layout.addWidget(self.processesLabel)

        self.refreshButton = QPushButton("Refresh")
        self.refreshButton.clicked.connect(self.display_system_info)
        self.layout.addWidget(self.refreshButton)

        self.setLayout(self.layout)

        
        self.display_system_info()

    def display_system_info(self):
        
        self.cpuLabel.clear()
        self.memoryLabel.clear()
        self.diskLabel.clear()
        self.networkLabel.clear()
        self.processesLabel.clear()

        
        cpu_info = psutil.cpu_percent(interval=1, percpu=True)
        cpu_text = "<b>CPU Usage:</b><br>"
        for i, cpu in enumerate(cpu_info):
            cpu_text += f"CPU {i}: {cpu}%<br>"
        self.cpuLabel.setText(cpu_text)

        
        mem_info = psutil.virtual_memory()
        mem_total = round(mem_info.total / (1024 * 1024 * 1024), 2)
        mem_used = round(mem_info.used / (1024 * 1024 * 1024), 2)
        mem_percent = mem_info.percent
        self.memoryLabel.setText(f"<b>Memory Usage:</b> {mem_used}GB / {mem_total}GB ({mem_percent}%)")

        
        disk_info = psutil.disk_usage('/')
        disk_total = round(disk_info.total / (1024 * 1024 * 1024), 2)
        disk_used = round(disk_info.used / (1024 * 1024 * 1024), 2)
        disk_percent = disk_info.percent
        self.diskLabel.setText(f"<b>Disk Usage:</b> {disk_used}GB / {disk_total}GB ({disk_percent}%)")

        
        network_info = psutil.net_io_counters()
        bytes_sent = round(network_info.bytes_sent / (1024 * 1024), 2)
        bytes_received = round(network_info.bytes_recv / (1024 * 1024), 2)
        self.networkLabel.setText(f"<b>Network Usage:</b> Sent: {bytes_sent}MB, Received: {bytes_received}MB")

        
        num_processes = len(psutil.pids())
        self.processesLabel.setText(f"<b>Number of Processes:</b> {num_processes}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Sys Manager")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: #f0f0f0; color: #333;")  

        self.tabs = QTabWidget()

        self.fileViewerTab = FileViewer(self)  
        self.tabs.addTab(self.fileViewerTab, "File Viewer")

        self.fileEditorTab = FileEditor()
        self.tabs.addTab(self.fileEditorTab, "File Editor")

        self.fileMoverTab = FileMover()
        self.tabs.addTab(self.fileMoverTab, "File Mover")

        self.systemInfoTab = SystemInfo()
        self.tabs.addTab(self.systemInfoTab, "System Info")
        
        
        self.tabs.currentChanged.connect(self.on_tab_changed)

        self.setCentralWidget(self.tabs)


    def on_tab_changed(self, index):
        if index == self.tabs.indexOf(self.systemInfoTab):
            self.systemInfoTab.display_system_info()

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Confirm Close', 
            "Are you sure you want to close the application?", 
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

def main():
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()