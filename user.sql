CREATE TABLE users (
    user_id BIGSERIAL NOT NULL PRIMARY KEY,
    full_name VARCHAR(50) NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(150),
    points INTEGER DEFAULT 0,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE admins (
    id_admin BIGSERIAL NOT NULL PRIMARY KEY,
    admin_username VARCHAR(50) NOT NULL,
    admin_email VARCHAR(100),
    admin_pass VARCHAR(255) NOT NULL
);

CREATE TABLE sampah (
    id_sampah BIGSERIAL NOT NULL PRIMARY KEY,
    nama_sampah VARCHAR(50) NOT NULL,
    ukuran VARCHAR(100),
    poin_sampah int NOT NULL
);

CREATE TABLE barang_tukar (
    barang_id BIGSERIAL NOT NULL PRIMARY KEY,
    barang_name VARCHAR(50) NOT NULL,
    barang_points INTEGER,
    barang_stok INTEGER
);

CREATE TABLE transaksi_ubah_botol (
    id_t_botol BIGSERIAL NOT NULL PRIMARY KEY,
    jumlah_botol INT,
    jumlah_poin INT,
    tanggal TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE transaksi_tukar_point (
    id_t_poin BIGSERIAL NOT NULL PRIMARY KEY,
    nama_barang VARCHAR(255),
    jumlah_poin INT,
    tanggal TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    user_id INT,
    barang_id INT,
    status VARCHAR(20) DEFAULT 'Belum Dikonfirmasi',
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (barang_id) REFERENCES barang_tukar(barang_id)
);


INSERT INTO barang_tukar (
    barang_name,
    barang_points,
    barang_stok
) VALUES (
    'Gula 1 Kg',
    100,
    10
);

INSERT INTO admin ( 
    admin_username,
    admin_email,
    admin_pass
) VALUES (
    'Minyak Goreng 1 Liter',
    100,
    10
);

INSERT INTO sampah ( 
    nama_sampah,
    ukuran,
    poin_sampah
) VALUES (
    'Botol Besar',
    'besar',
    6
);

ALTER TABLE barang_tukar
ADD COLUMN barang_image VARCHAR(255);

UPDATE barang_tukar SET barang_image = 'assets/gula.jpg' WHERE barang_id = 2;