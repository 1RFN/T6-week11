# Post Manager Desktop Application

Aplikasi desktop **"Post Manager"** ini dibangun menggunakan **Python** dan antarmuka **PySide6** untuk mengelola data artikel beserta komentarnya secara terpusat melalui integrasi **RESTful API**.

Sistem ini berhasil mengeksekusi operasi **CRUD (Create, Read, Update, Delete)** secara penuh dengan keunggulan teknis pada penerapan arsitektur **multithreading (`QThread`)**, yang memastikan antarmuka aplikasi tetap responsif dan bebas *freeze* saat menunggu balasan jaringan dari server.

Selain itu, aplikasi ini juga dirancang dengan penanganan status dan error yang komprehensif, mulai dari:

- indikator loading,
- perlindungan keamanan memori (*thread management*),
- hingga penanganan validasi duplikasi data langsung dari server.
