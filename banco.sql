CREATE DATABASE IF NOT EXISTS centro_cidadania_do_brasil;
USE centro_cidadania_do_brasil;

-- 1. Tabela de turmas
CREATE TABLE IF NOT EXISTS turmas (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nome VARCHAR(100) NOT NULL,
  modalidade VARCHAR(100) NOT NULL,
  dias VARCHAR(100) NOT NULL,
  horario VARCHAR(50) NOT NULL
);

-- 2. Tabela de alunos
CREATE TABLE IF NOT EXISTS alunos (
  id INT AUTO_INCREMENT PRIMARY KEY,
  matricula VARCHAR(20) NOT NULL UNIQUE,
  nome VARCHAR(100) NOT NULL,
  turma_id INT NULL,
  CONSTRAINT fk_aluno_turma
    FOREIGN KEY (turma_id) REFERENCES turmas(id)
    ON DELETE SET NULL
);

ALTER TABLE alunos
ADD COLUMN turma_id INT NULL,
ADD CONSTRAINT fk_aluno_turma
  FOREIGN KEY (turma_id) REFERENCES turmas(id)
  ON DELETE SET NULL;

-- 3. Tabela de histórico de chamadas dos alunos
CREATE TABLE IF NOT EXISTS chamadas_alunos (
  id INT AUTO_INCREMENT PRIMARY KEY,
  aluno_matricula VARCHAR(20) NOT NULL,
  data_aula DATE NOT NULL,
  presente TINYINT(1) NOT NULL,
  UNIQUE KEY uk_aluno_data (aluno_matricula, data_aula),
  CONSTRAINT fk_chamada_aluno
    FOREIGN KEY (aluno_matricula) REFERENCES alunos(matricula)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

-- Turma e alunos iniciais de exemplo
INSERT IGNORE INTO turmas (id, nome, modalidade, dias, horario) VALUES
  (1, 'Turma A - Manhã', 'Jiu-Jitsu', 'Seg / Qua / Sex', '09:00');

INSERT IGNORE INTO alunos (matricula, nome, turma_id) VALUES
  ('2026001', 'Natália da Silva', 1),
  ('2026002', 'Rafael Oliveira Santos', 1),
  ('2026003', 'Beatriz Almeida Costa', 1);

-- 4. Tabela de usuários
CREATE TABLE IF NOT EXISTS usuarios (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nome VARCHAR(100) NOT NULL,
  email VARCHAR(100) NOT NULL UNIQUE,
  senha VARCHAR(255) NOT NULL
);

-- 5. Tabela de inscrições
CREATE TABLE IF NOT EXISTS inscricoes (
  id INT AUTO_INCREMENT PRIMARY KEY,
  usuario_id INT NOT NULL,
  nome_aluno VARCHAR(100) NOT NULL,
  data_nascimento DATE NOT NULL,
  sexo VARCHAR(20) NOT NULL,
  rg VARCHAR(20) NOT NULL,
  cpf VARCHAR(20) NOT NULL,
  endereco VARCHAR(200) NOT NULL,
  bairro VARCHAR(100) NOT NULL,
  cep VARCHAR(20) NOT NULL,
  nome_mae VARCHAR(100) NOT NULL,
  nome_pai VARCHAR(100) NOT NULL,
  problema_cardiaco VARCHAR(10) NOT NULL,
  dor_peito_atividade VARCHAR(10) NOT NULL,
  dor_peito_recente VARCHAR(10) NOT NULL,
  tontura_ou_perda_consciencia VARCHAR(10) NOT NULL,
  problema_osseo_articular VARCHAR(10) NOT NULL,
  medicacao_continua VARCHAR(10) NOT NULL,
  tratamento_pressao VARCHAR(10) NOT NULL,
  outra_condicao_saude VARCHAR(10) NOT NULL,
  modalidade VARCHAR(100) NOT NULL,
  dias VARCHAR(100) NOT NULL,
  horario VARCHAR(50) NOT NULL,
  motivo_inscricao VARCHAR(100) NOT NULL,
  outro_motivo VARCHAR(200),
  recebe_auxilio VARCHAR(10) NOT NULL,
  participa_outro_projeto VARCHAR(10) NOT NULL,
  nome_projeto VARCHAR(100),
  numero_pessoas_casa INT,
  contato_emergencia VARCHAR(100) NOT NULL,
  parentesco VARCHAR(100) NOT NULL,
  telefone_emergencia VARCHAR(20) NOT NULL,
  nome_responsavel VARCHAR(100) NOT NULL,
  cpf_responsavel VARCHAR(20) NOT NULL,
  rg_responsavel VARCHAR(20) NOT NULL,
  data_autorizacao DATE NOT NULL,
  assinatura_responsavel VARCHAR(100) NOT NULL,
  FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

-- 6. Tabela de frequências (inscrições)
CREATE TABLE IF NOT EXISTS frequencias (
  id INT AUTO_INCREMENT PRIMARY KEY,
  inscricao_id INT NOT NULL,
  data_aula DATE NOT NULL,
  presente TINYINT(1) NOT NULL,
  FOREIGN KEY (inscricao_id) REFERENCES inscricoes(id)
);

-- 7. Tabela de arquivos
CREATE TABLE IF NOT EXISTS arquivos (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nome_original VARCHAR(255) NOT NULL,
  nome_salvo VARCHAR(255) NOT NULL,
  tipo VARCHAR(50) NOT NULL,
  data_upload DATETIME DEFAULT CURRENT_TIMESTAMP
);
