"""
Audio to Video Converter - Main GUI Application
Converts audio files to MPEG video using a cover image.
All user-facing text in Brazilian Portuguese (PT-BR).
"""

import sys
from pathlib import Path
from typing import Optional, List
from dataclasses import dataclass, field

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFileDialog, QTableWidget, QTableWidgetItem,
    QProgressBar, QMessageBox, QHeaderView, QAbstractItemView,
    QGroupBox, QSizePolicy
)
from PySide6.QtCore import Qt, QThread, Signal, QSize
from PySide6.QtGui import QPixmap, QIcon

from converter import convert_audio_to_video, ConversionResult
from utils import (
    get_default_output_folder, ensure_output_folder, get_unique_output_path,
    is_supported_audio_file, is_supported_image_file
)


# Status constants (Portuguese)
STATUS_QUEUED = "Na fila"
STATUS_CONVERTING = "Convertendo"
STATUS_COMPLETED = "Concluído"
STATUS_ERROR = "Erro"
STATUS_CANCELLED = "Cancelado"


@dataclass
class AudioItem:
    """Represents an audio file in the conversion queue."""
    file_path: Path
    status: str = STATUS_QUEUED
    progress: float = 0.0
    output_path: Optional[Path] = None
    error_message: Optional[str] = None


class ConversionWorker(QThread):
    """Worker thread for running conversions without freezing the UI."""
    
    # Signals
    progress_updated = Signal(int, float)  # row, progress (0.0-1.0)
    status_updated = Signal(int, str)  # row, status
    conversion_completed = Signal(int, bool, str, str)  # row, success, output_path, error_message
    all_completed = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.items: List[tuple] = []  # List of (row, audio_path, cover_path, output_path)
        self.cancelled = False
        self.current_row = -1
    
    def set_items(self, items: List[tuple]):
        """Set the items to convert."""
        self.items = items
        self.cancelled = False
    
    def cancel(self):
        """Request cancellation of the current conversion."""
        self.cancelled = True
    
    def run(self):
        """Run the conversion process for all items."""
        for row, audio_path, cover_path, output_path in self.items:
            if self.cancelled:
                self.status_updated.emit(row, STATUS_CANCELLED)
                continue
            
            self.current_row = row
            self.status_updated.emit(row, STATUS_CONVERTING)
            
            def progress_callback(progress: float):
                self.progress_updated.emit(row, progress)
            
            def cancel_check() -> bool:
                return self.cancelled
            
            result = convert_audio_to_video(
                audio_path=audio_path,
                cover_image_path=cover_path,
                output_path=output_path,
                progress_callback=progress_callback,
                cancel_check=cancel_check
            )
            
            if self.cancelled:
                self.status_updated.emit(row, STATUS_CANCELLED)
                self.conversion_completed.emit(row, False, "", "Conversão cancelada")
            elif result.success:
                self.status_updated.emit(row, STATUS_COMPLETED)
                self.conversion_completed.emit(row, True, str(result.output_path), "")
            else:
                self.status_updated.emit(row, STATUS_ERROR)
                self.conversion_completed.emit(row, False, "", result.error_message or "Erro desconhecido")
        
        self.all_completed.emit()


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        
        self.cover_image_path: Optional[Path] = None
        self.output_folder: Path = get_default_output_folder()
        self.audio_items: List[AudioItem] = []
        self.worker: Optional[ConversionWorker] = None
        self.is_converting = False
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Conversor de Áudio para Vídeo")
        self.setMinimumSize(800, 600)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Cover image section
        cover_group = QGroupBox("Imagem de Capa (obrigatória)")
        cover_layout = QHBoxLayout(cover_group)
        
        self.cover_preview = QLabel()
        self.cover_preview.setFixedSize(120, 120)
        self.cover_preview.setAlignment(Qt.AlignCenter)
        self.cover_preview.setStyleSheet("""
            QLabel {
                border: 2px dashed #ccc;
                border-radius: 5px;
                background-color: #f9f9f9;
            }
        """)
        self.cover_preview.setText("Sem imagem")
        cover_layout.addWidget(self.cover_preview)
        
        cover_info_layout = QVBoxLayout()
        self.cover_label = QLabel("Nenhuma imagem selecionada")
        self.cover_label.setWordWrap(True)
        cover_info_layout.addWidget(self.cover_label)
        
        self.btn_select_cover = QPushButton("Selecionar imagem de capa...")
        self.btn_select_cover.clicked.connect(self.select_cover_image)
        cover_info_layout.addWidget(self.btn_select_cover)
        cover_info_layout.addStretch()
        
        cover_layout.addLayout(cover_info_layout, 1)
        main_layout.addWidget(cover_group)
        
        # Audio files section
        audio_group = QGroupBox("Arquivos de Áudio")
        audio_layout = QVBoxLayout(audio_group)
        
        # Audio buttons
        audio_buttons_layout = QHBoxLayout()
        
        self.btn_add_audio = QPushButton("Adicionar áudios...")
        self.btn_add_audio.clicked.connect(self.add_audio_files)
        audio_buttons_layout.addWidget(self.btn_add_audio)
        
        self.btn_remove_selected = QPushButton("Remover selecionados")
        self.btn_remove_selected.clicked.connect(self.remove_selected)
        self.btn_remove_selected.setEnabled(False)
        audio_buttons_layout.addWidget(self.btn_remove_selected)
        
        self.btn_clear_list = QPushButton("Limpar lista")
        self.btn_clear_list.clicked.connect(self.clear_list)
        self.btn_clear_list.setEnabled(False)
        audio_buttons_layout.addWidget(self.btn_clear_list)
        
        audio_buttons_layout.addStretch()
        audio_layout.addLayout(audio_buttons_layout)
        
        # Audio table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Arquivo", "Status", "Progresso", "Arquivo de saída"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.table.setColumnWidth(2, 150)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        audio_layout.addWidget(self.table)
        
        main_layout.addWidget(audio_group, 1)
        
        # Output folder section
        output_group = QGroupBox("Pasta de Saída")
        output_layout = QHBoxLayout(output_group)
        
        self.output_label = QLabel(str(self.output_folder))
        self.output_label.setWordWrap(True)
        output_layout.addWidget(self.output_label, 1)
        
        self.btn_select_output = QPushButton("Alterar pasta...")
        self.btn_select_output.clicked.connect(self.select_output_folder)
        output_layout.addWidget(self.btn_select_output)
        
        self.btn_open_output = QPushButton("Abrir pasta de saída")
        self.btn_open_output.clicked.connect(self.open_output_folder)
        output_layout.addWidget(self.btn_open_output)
        
        main_layout.addWidget(output_group)
        
        # Control buttons
        control_layout = QHBoxLayout()
        control_layout.addStretch()
        
        self.btn_start = QPushButton("Iniciar")
        self.btn_start.setMinimumWidth(120)
        self.btn_start.setEnabled(False)
        self.btn_start.clicked.connect(self.start_conversion)
        self.btn_start.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        control_layout.addWidget(self.btn_start)
        
        main_layout.addLayout(control_layout)
        
        # Status bar
        self.statusBar().showMessage("Pronto. Selecione uma imagem de capa e adicione arquivos de áudio.")
    
    def select_cover_image(self):
        """Open file dialog to select cover image."""
        file_filter = "Imagens (*.jpg *.jpeg *.png *.bmp *.gif *.webp *.tiff);;Todos os arquivos (*.*)"
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar imagem de capa",
            "",
            file_filter
        )
        
        if file_path:
            self.set_cover_image(Path(file_path))
    
    def set_cover_image(self, path: Path):
        """Set the cover image."""
        if not path.exists():
            QMessageBox.warning(
                self,
                "Erro",
                f"Arquivo não encontrado: {path}"
            )
            return
        
        if not is_supported_image_file(path):
            QMessageBox.warning(
                self,
                "Formato não suportado",
                "Por favor, selecione uma imagem nos formatos: JPG, PNG, BMP, GIF, WebP ou TIFF."
            )
            return
        
        self.cover_image_path = path
        self.cover_label.setText(path.name)
        
        # Update preview
        pixmap = QPixmap(str(path))
        if not pixmap.isNull():
            scaled = pixmap.scaled(
                self.cover_preview.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.cover_preview.setPixmap(scaled)
        
        self.update_start_button_state()
        self.statusBar().showMessage(f"Imagem de capa selecionada: {path.name}")
    
    def add_audio_files(self):
        """Open file dialog to add audio files."""
        file_filter = (
            "Arquivos de áudio (*.m4a *.mp3 *.wav *.aac *.flac *.ogg *.wma *.opus);;"
            "Todos os arquivos (*.*)"
        )
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Adicionar arquivos de áudio",
            "",
            file_filter
        )
        
        if files:
            added_count = 0
            for file_path in files:
                path = Path(file_path)
                if is_supported_audio_file(path):
                    self.add_audio_item(path)
                    added_count += 1
            
            if added_count > 0:
                self.statusBar().showMessage(f"{added_count} arquivo(s) de áudio adicionado(s).")
            
            self.update_buttons_state()
    
    def add_audio_item(self, path: Path):
        """Add an audio item to the table."""
        item = AudioItem(file_path=path)
        self.audio_items.append(item)
        
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        # File name
        name_item = QTableWidgetItem(path.name)
        name_item.setToolTip(str(path))
        name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
        self.table.setItem(row, 0, name_item)
        
        # Status
        status_item = QTableWidgetItem(STATUS_QUEUED)
        status_item.setFlags(status_item.flags() & ~Qt.ItemIsEditable)
        self.table.setItem(row, 1, status_item)
        
        # Progress bar
        progress_bar = QProgressBar()
        progress_bar.setMinimum(0)
        progress_bar.setMaximum(100)
        progress_bar.setValue(0)
        progress_bar.setTextVisible(True)
        progress_bar.setFormat("%p%")
        self.table.setCellWidget(row, 2, progress_bar)
        
        # Output file (empty initially)
        output_item = QTableWidgetItem("")
        output_item.setFlags(output_item.flags() & ~Qt.ItemIsEditable)
        self.table.setItem(row, 3, output_item)
    
    def remove_selected(self):
        """Remove selected items from the table."""
        if self.is_converting:
            QMessageBox.warning(
                self,
                "Conversão em andamento",
                "Não é possível remover itens durante a conversão."
            )
            return
        
        selected_rows = sorted(set(item.row() for item in self.table.selectedItems()), reverse=True)
        
        for row in selected_rows:
            self.table.removeRow(row)
            del self.audio_items[row]
        
        self.update_buttons_state()
        self.statusBar().showMessage(f"{len(selected_rows)} item(ns) removido(s).")
    
    def clear_list(self):
        """Clear all items from the table."""
        if self.is_converting:
            QMessageBox.warning(
                self,
                "Conversão em andamento",
                "Não é possível limpar a lista durante a conversão."
            )
            return
        
        reply = QMessageBox.question(
            self,
            "Confirmar",
            "Deseja remover todos os itens da lista?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.table.setRowCount(0)
            self.audio_items.clear()
            self.update_buttons_state()
            self.statusBar().showMessage("Lista limpa.")
    
    def select_output_folder(self):
        """Open dialog to select output folder."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Selecionar pasta de saída",
            str(self.output_folder)
        )
        
        if folder:
            self.output_folder = Path(folder)
            self.output_label.setText(str(self.output_folder))
            self.statusBar().showMessage(f"Pasta de saída alterada para: {self.output_folder}")
    
    def open_output_folder(self):
        """Open the output folder in file explorer."""
        import subprocess
        import platform
        
        folder = self.output_folder
        if not folder.exists():
            try:
                folder.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "Erro",
                    f"Não foi possível criar a pasta: {e}"
                )
                return
        
        try:
            if platform.system() == "Windows":
                subprocess.run(["explorer", str(folder)], check=False)
            elif platform.system() == "Darwin":
                subprocess.run(["open", str(folder)], check=False)
            else:
                subprocess.run(["xdg-open", str(folder)], check=False)
        except Exception as e:
            QMessageBox.warning(
                self,
                "Erro",
                f"Não foi possível abrir a pasta: {e}"
            )
    
    def on_selection_changed(self):
        """Handle table selection change."""
        has_selection = len(self.table.selectedItems()) > 0
        self.btn_remove_selected.setEnabled(has_selection and not self.is_converting)
    
    def update_buttons_state(self):
        """Update the enabled state of buttons."""
        has_items = len(self.audio_items) > 0
        has_selection = len(self.table.selectedItems()) > 0
        
        self.btn_remove_selected.setEnabled(has_selection and not self.is_converting)
        self.btn_clear_list.setEnabled(has_items and not self.is_converting)
        self.update_start_button_state()
    
    def update_start_button_state(self):
        """Update the enabled state of the start button."""
        can_start = (
            self.cover_image_path is not None and
            len(self.audio_items) > 0 and
            not self.is_converting
        )
        self.btn_start.setEnabled(can_start)
    
    def start_conversion(self):
        """Start the conversion process."""
        if not self.cover_image_path:
            QMessageBox.warning(
                self,
                "Imagem de capa necessária",
                "Por favor, selecione uma imagem de capa antes de iniciar."
            )
            return
        
        if len(self.audio_items) == 0:
            QMessageBox.warning(
                self,
                "Sem arquivos",
                "Por favor, adicione pelo menos um arquivo de áudio."
            )
            return
        
        # Ensure output folder exists
        try:
            ensure_output_folder(self.output_folder)
        except Exception as e:
            QMessageBox.critical(
                self,
                "Erro",
                f"Não foi possível criar a pasta de saída: {e}"
            )
            return
        
        # Prepare conversion items
        items_to_convert = []
        for row, item in enumerate(self.audio_items):
            if item.status in (STATUS_QUEUED, STATUS_ERROR, STATUS_CANCELLED):
                output_path = get_unique_output_path(
                    self.output_folder,
                    item.file_path.stem
                )
                items_to_convert.append((row, item.file_path, self.cover_image_path, output_path))
                
                # Reset item state
                item.status = STATUS_QUEUED
                item.progress = 0.0
                item.output_path = None
                item.error_message = None
                
                # Update table
                self.table.item(row, 1).setText(STATUS_QUEUED)
                self.table.item(row, 3).setText("")
                progress_bar = self.table.cellWidget(row, 2)
                if progress_bar:
                    progress_bar.setValue(0)
        
        if not items_to_convert:
            QMessageBox.information(
                self,
                "Nada a converter",
                "Todos os arquivos já foram convertidos."
            )
            return
        
        # Start conversion
        self.is_converting = True
        self.update_buttons_state()
        self.btn_add_audio.setEnabled(False)
        self.btn_select_cover.setEnabled(False)
        self.btn_select_output.setEnabled(False)
        self.statusBar().showMessage("Iniciando conversão...")
        
        # Create and start worker
        self.worker = ConversionWorker(self)
        self.worker.set_items(items_to_convert)
        self.worker.progress_updated.connect(self.on_progress_updated)
        self.worker.status_updated.connect(self.on_status_updated)
        self.worker.conversion_completed.connect(self.on_conversion_completed)
        self.worker.all_completed.connect(self.on_all_completed)
        self.worker.start()
    
    def on_progress_updated(self, row: int, progress: float):
        """Handle progress update from worker."""
        if 0 <= row < len(self.audio_items):
            self.audio_items[row].progress = progress
            progress_bar = self.table.cellWidget(row, 2)
            if progress_bar:
                progress_bar.setValue(int(progress * 100))
    
    def on_status_updated(self, row: int, status: str):
        """Handle status update from worker."""
        if 0 <= row < len(self.audio_items):
            self.audio_items[row].status = status
            self.table.item(row, 1).setText(status)
            
            # Update status color
            status_item = self.table.item(row, 1)
            if status == STATUS_COMPLETED:
                status_item.setForeground(Qt.darkGreen)
            elif status == STATUS_ERROR:
                status_item.setForeground(Qt.red)
            elif status == STATUS_CANCELLED:
                status_item.setForeground(Qt.darkYellow)
            elif status == STATUS_CONVERTING:
                status_item.setForeground(Qt.blue)
            else:
                status_item.setForeground(Qt.black)
    
    def on_conversion_completed(self, row: int, success: bool, output_path: str, error_message: str):
        """Handle conversion completion for a single item."""
        if 0 <= row < len(self.audio_items):
            item = self.audio_items[row]
            
            if success:
                item.output_path = Path(output_path)
                self.table.item(row, 3).setText(Path(output_path).name)
                self.statusBar().showMessage(f"Concluído: {item.file_path.name}")
            else:
                item.error_message = error_message
                if error_message and "cancelad" not in error_message.lower():
                    self.table.item(row, 3).setText(f"Erro: {error_message[:50]}...")
    
    def on_all_completed(self):
        """Handle completion of all conversions."""
        self.is_converting = False
        self.update_buttons_state()
        self.btn_add_audio.setEnabled(True)
        self.btn_select_cover.setEnabled(True)
        self.btn_select_output.setEnabled(True)
        
        # Count results
        completed = sum(1 for item in self.audio_items if item.status == STATUS_COMPLETED)
        errors = sum(1 for item in self.audio_items if item.status == STATUS_ERROR)
        cancelled = sum(1 for item in self.audio_items if item.status == STATUS_CANCELLED)
        
        message = f"Conversão finalizada. {completed} concluído(s)"
        if errors > 0:
            message += f", {errors} erro(s)"
        if cancelled > 0:
            message += f", {cancelled} cancelado(s)"
        
        self.statusBar().showMessage(message)
        
        if errors > 0:
            QMessageBox.warning(
                self,
                "Conversão concluída com erros",
                f"A conversão foi concluída.\n\n"
                f"• {completed} arquivo(s) convertido(s) com sucesso\n"
                f"• {errors} arquivo(s) com erro\n\n"
                f"Verifique a coluna 'Arquivo de saída' para mais detalhes."
            )
        elif completed > 0:
            QMessageBox.information(
                self,
                "Conversão concluída",
                f"Todos os {completed} arquivo(s) foram convertidos com sucesso!\n\n"
                f"Os vídeos foram salvos em:\n{self.output_folder}"
            )


def main():
    """Application entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("Conversor de Áudio para Vídeo")
    app.setOrganizationName("Audio2Video")
    
    # Set application style
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
