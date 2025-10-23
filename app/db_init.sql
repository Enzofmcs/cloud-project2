CREATE TABLE IF NOT EXISTS jobs (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(128) NOT NULL,
  image VARCHAR(128) NOT NULL,
  cmd TEXT NOT NULL,
  cpus DECIMAL(3,1) NOT NULL,
  mem_mb INT NOT NULL,
  io_weight INT NOT NULL,         -- 10..1000 (peso de IO)
  log_path VARCHAR(255) NOT NULL,
  status VARCHAR(32) NOT NULL,    -- running|exited|error
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
