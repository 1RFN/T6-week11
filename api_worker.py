import requests
from PySide6.QtCore import QThread, Signal

class ApiWorker(QThread):
    success = Signal(dict, str) 
    error = Signal(str)        

    def __init__(self, method, url, data=None, action_type=""):
        super().__init__()
        self.method = method
        self.url = url
        self.data = data
        self.action_type = action_type 

    def run(self):
        try:
            if self.method == 'GET':
                response = requests.get(self.url, timeout=10)
            elif self.method == 'POST':
                response = requests.post(self.url, json=self.data, timeout=10)
            elif self.method == 'PUT':
                response = requests.put(self.url, json=self.data, timeout=10)
            elif self.method == 'DELETE':
                response = requests.delete(self.url, timeout=10)

            if response.status_code in [200, 201]:
                data = response.json() if response.text else {}
                self.success.emit(data, self.action_type)
            elif response.status_code == 422:
                self.error.emit(f"Validasi Gagal (422) dari Server:\n{response.text}")
            elif response.status_code == 404:
                self.error.emit("Data tidak ditemukan (404).")
            else:
                self.error.emit(f"Error {response.status_code}: {response.text}")
                
        except requests.exceptions.Timeout:
            self.error.emit("Request Timeout: Koneksi ke server terlalu lama.")
        except requests.exceptions.ConnectionError:
            self.error.emit("Connection Error: Gagal terhubung ke server. Cek koneksi internet.")
        except Exception as e:
            self.error.emit(f"Terjadi kesalahan: {str(e)}")