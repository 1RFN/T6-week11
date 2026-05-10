from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QTableWidget, QTableWidgetItem, 
                               QPushButton, QFormLayout, QLineEdit, QTextEdit, 
                               QComboBox, QMessageBox, QLabel, QHeaderView, QListWidget,
                               QAbstractItemView, QSplitter, QGroupBox)
from PySide6.QtCore import Qt
from api_worker import ApiWorker 

BASE_URL = "https://api.pahrul.my.id/api/posts"

class PostManagerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Post Manager API - Visual Programming")
        self.resize(1100, 700) 

        self.current_post_id = None
        self.current_mode = "VIEW" 
        self.active_workers = []

        self.setup_ui()
        self.load_posts()

    def setup_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)

        splitter = QSplitter(Qt.Horizontal)
        
        group_table = QGroupBox("Daftar Post")
        left_layout = QVBoxLayout(group_table)
        
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Title", "Author", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True) 
        self.table.itemSelectionChanged.connect(self.on_row_selected)
        left_layout.addWidget(self.table)

        btn_layout = QHBoxLayout()
        self.btn_refresh = QPushButton("Refresh Data")
        self.btn_add = QPushButton("Tambah Baru")
        self.btn_edit = QPushButton("Edit Terpilih")
        self.btn_delete = QPushButton("Hapus Terpilih")

        self.btn_refresh.clicked.connect(self.load_posts)
        self.btn_add.clicked.connect(self.prepare_add)
        self.btn_edit.clicked.connect(self.prepare_edit)
        self.btn_delete.clicked.connect(self.delete_post)

        self.btn_edit.setEnabled(False)
        self.btn_delete.setEnabled(False)

        btn_layout.addWidget(self.btn_refresh)
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
        left_layout.addLayout(btn_layout)

        group_form = QGroupBox("Detail & Form Post")
        right_layout = QVBoxLayout(group_form)

        self.lbl_title_form = QLabel("<h3>Memuat Data...</h3>")
        self.lbl_title_form.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(self.lbl_title_form)

        form_layout = QFormLayout()
        
        self.inp_title = QLineEdit()
        self.inp_author = QLineEdit()
        self.inp_slug = QLineEdit()
        
        self.inp_status = QComboBox()
        self.inp_status.addItems(["published", "draft"])

        self.inp_body = QTextEdit()
        self.inp_body.setMaximumHeight(120)

        form_layout.addRow("Title :", self.inp_title)
        form_layout.addRow("Author :", self.inp_author)
        form_layout.addRow("Slug :", self.inp_slug)
        form_layout.addRow("Status :", self.inp_status)
        form_layout.addRow("Body :", self.inp_body)
        right_layout.addLayout(form_layout)

        self.btn_save = QPushButton("Simpan Data")
        self.btn_save.setEnabled(False)
        self.btn_save.clicked.connect(self.save_post)
        right_layout.addWidget(self.btn_save)

        line = QLabel()
        line.setFrameShape(QLabel.HLine)
        line.setFrameShadow(QLabel.Sunken)
        right_layout.addWidget(line)

        self.lbl_comments = QLabel("<b>Komentar:</b>")
        right_layout.addWidget(self.lbl_comments)
        
        self.list_comments = QListWidget()
        right_layout.addWidget(self.list_comments)

        comment_input_layout = QHBoxLayout()
        self.inp_comment_name = QLineEdit()
        self.inp_comment_name.setPlaceholderText("Nama kamu...")
        
        self.inp_comment_body = QLineEdit()
        self.inp_comment_body.setPlaceholderText("Tulis komentar...")
        
        self.btn_send_comment = QPushButton("Kirim")
        self.btn_send_comment.setEnabled(False) 
        self.btn_send_comment.clicked.connect(self.send_comment)

        comment_input_layout.addWidget(self.inp_comment_name)
        comment_input_layout.addWidget(self.inp_comment_body)
        comment_input_layout.addWidget(self.btn_send_comment)
        
        right_layout.addLayout(comment_input_layout)

        splitter.addWidget(group_table)
        splitter.addWidget(group_form)
        splitter.setSizes([600, 400])
        main_layout.addWidget(splitter)

        self.lbl_status = QLabel("Ready")
        self.statusBar().addWidget(self.lbl_status)

        self.set_form_read_only(True)

    def set_form_read_only(self, is_readonly):
        self.inp_title.setReadOnly(is_readonly)
        self.inp_author.setReadOnly(is_readonly)
        self.inp_slug.setReadOnly(is_readonly)
        self.inp_body.setReadOnly(is_readonly)
        self.inp_status.setEnabled(not is_readonly)

    def clear_form(self):
        self.inp_title.clear()
        self.inp_author.clear()
        self.inp_slug.clear()
        self.inp_body.clear()
        self.inp_status.setCurrentIndex(0)
        self.list_comments.clear()
        self.current_post_id = None

        if hasattr(self, 'btn_send_comment'):
            self.btn_send_comment.setEnabled(False)
            self.inp_comment_name.clear()
            self.inp_comment_body.clear()

    def run_worker(self, method, url, data=None, action_type=""):
        self.lbl_status.setText(f"Sedang memproses... ({action_type})")
        self.btn_refresh.setEnabled(False)
        self.btn_save.setEnabled(False)
        
        worker = ApiWorker(method, url, data, action_type)
        worker.success.connect(self.on_api_success)
        worker.error.connect(self.on_api_error)
        
        self.active_workers.append(worker)
        
        def cleanup_thread():
            if worker in self.active_workers:
                self.active_workers.remove(worker)
            worker.deleteLater() 
            
        worker.finished.connect(cleanup_thread)
        
        worker.start()

    def on_api_error(self, error_msg):
        self.lbl_status.setText("Error!")
        QMessageBox.critical(self, "API Error", error_msg)
        self.reset_ui_state()

    def on_api_success(self, data, action_type):
        self.lbl_status.setText("Ready")
        
        if action_type == "GET_ALL":
            posts = data.get('data', data) if isinstance(data, dict) else data
            self.table.setRowCount(0)
            for row_idx, post in enumerate(posts):
                self.table.insertRow(row_idx)
                self.table.setItem(row_idx, 0, QTableWidgetItem(str(post.get('id', ''))))
                self.table.setItem(row_idx, 1, QTableWidgetItem(post.get('title', '')))
                self.table.setItem(row_idx, 2, QTableWidgetItem(post.get('author', '')))
                self.table.setItem(row_idx, 3, QTableWidgetItem(post.get('status', '')))
                
        elif action_type == "GET_DETAIL":
            post = data.get('data', data) if isinstance(data, dict) else data
            self.current_post_id = post.get('id')
            self.inp_title.setText(post.get('title', ''))
            self.inp_author.setText(post.get('author', ''))
            self.inp_slug.setText(post.get('slug', ''))
            self.inp_body.setText(post.get('body', ''))
            status = post.get('status', 'published')
            self.inp_status.setCurrentText(status)

            self.list_comments.clear()
            comments = post.get('comments', [])
            if comments:
                for comment in comments:
                    self.list_comments.addItem(f"{comment.get('name', 'User')}: {comment.get('body', '')}")
            else:
                self.list_comments.addItem("Belum ada komentar.")

        elif action_type == "POST":
            post_id = data.get('data', data).get('id', 'Unknown')
            QMessageBox.information(self, "Sukses", f"Post berhasil ditambahkan!\nID Server: {post_id}")
            self.load_posts()
            
        elif action_type == "PUT":
            QMessageBox.information(self, "Sukses", "Post berhasil diupdate!")
            self.load_posts()
            
        elif action_type == "DELETE":
            QMessageBox.information(self, "Sukses", "Post dan semua komentarnya berhasil dihapus!")
            self.clear_form()
            self.load_posts()

        elif action_type == "POST_COMMENT":
            QMessageBox.information(self, "Sukses", "Komentar berhasil ditambahkan!")
            self.inp_comment_name.clear()
            self.inp_comment_body.clear()
            self.run_worker('GET', f"{BASE_URL}/{self.current_post_id}", action_type="GET_DETAIL")

        self.reset_ui_state()

    def reset_ui_state(self):
        self.btn_refresh.setEnabled(True)
        if self.current_mode in ["ADD", "EDIT"]:
            self.btn_save.setEnabled(True)

    def load_posts(self):
        self.current_mode = "VIEW"
        self.clear_form()
        self.set_form_read_only(True)
        self.btn_save.setEnabled(False)
        self.lbl_title_form.setText("<h3>Mode: Lihat Detail</h3>")
        self.run_worker('GET', BASE_URL, action_type="GET_ALL")

    def on_row_selected(self):
        selected_rows = self.table.selectedItems()
        if selected_rows:
            self.btn_edit.setEnabled(True)
            self.btn_delete.setEnabled(True)
            self.btn_send_comment.setEnabled(True)
            row = selected_rows[0].row()
            post_id = self.table.item(row, 0).text()
            
            self.current_mode = "VIEW"
            self.set_form_read_only(True)
            self.btn_save.setEnabled(False)
            self.lbl_title_form.setText(f"<h3>Mode: Lihat Detail (ID: {post_id})</h3>")
            self.run_worker('GET', f"{BASE_URL}/{post_id}", action_type="GET_DETAIL")
        else:
            self.btn_edit.setEnabled(False)
            self.btn_delete.setEnabled(False)

    def prepare_add(self):
        self.current_mode = "ADD"
        self.clear_form()
        self.set_form_read_only(False)
        self.btn_save.setEnabled(True)
        self.table.clearSelection()
        self.lbl_title_form.setText("<h3>Mode: Tambah Post Baru</h3>")

    def prepare_edit(self):
        if not self.current_post_id:
            return
        self.current_mode = "EDIT"
        self.set_form_read_only(False)
        self.btn_save.setEnabled(True)
        self.lbl_title_form.setText(f"<h3>Mode: Edit Post (ID: {self.current_post_id})</h3>")

    def save_post(self):
        payload = {
            "title": self.inp_title.text(),
            "author": self.inp_author.text(),
            "slug": self.inp_slug.text(),
            "status": self.inp_status.currentText(),
            "body": self.inp_body.toPlainText()
        }

        if not payload["title"] or not payload["author"] or not payload["slug"] or not payload["body"]:
            QMessageBox.warning(self, "Peringatan", "Semua field (Title, Author, Slug, Body) harus diisi!")
            return

        if self.current_mode == "ADD":
            self.run_worker('POST', BASE_URL, data=payload, action_type="POST")
        elif self.current_mode == "EDIT":
            self.run_worker('PUT', f"{BASE_URL}/{self.current_post_id}", data=payload, action_type="PUT")

    def delete_post(self):
        if not self.current_post_id:
            return
            
        reply = QMessageBox.question(self, 'Konfirmasi Hapus',
                                     f"Apakah kamu yakin ingin menghapus Post ID {self.current_post_id}?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.run_worker('DELETE', f"{BASE_URL}/{self.current_post_id}", action_type="DELETE")

    def send_comment(self):
        if not self.current_post_id:
            return
            
        name = self.inp_comment_name.text()
        body = self.inp_comment_body.text()

        if not name or not body:
            QMessageBox.warning(self, "Peringatan", "Nama dan isi komentar harus diisi!")
            return

        comment_url = "https://api.pahrul.my.id/api/comments"
        
        payload = {
            "post_id": self.current_post_id,
            "name": name,
            "email": "irfan@unram.ac.id",  
            "body": body,
            "status": "published"         
        }
        
        self.run_worker('POST', comment_url, data=payload, action_type="POST_COMMENT")