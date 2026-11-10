CREATE DATABASE IF NOT EXISTS centro_cidadania_do_brasil;
USE centro_cidadania_do_brasil;
CREATE TABLE IF NOT EXISTS alunos (
  id INT AUTO_INCREMENT PRIMARY KEY,
  matricula VARCHAR(20) NOT NULL UNIQUE,
  nome VARCHAR(100) NOT NULL
);

INSERT INTO alunos (matricula, nome) VALUES
  ('2026001', 'Natália da Silva'),
  ('2026002', 'Rafael Oliveira Santos'),
  ('2026003', 'Beatriz Almeida Costa');
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,alunosalunos
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL
);

CREATE TABLE inscricoes (
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

  
    FOREIGN KEY (usuario_id)
    REFERENCES usuarios(id)
);

CREATE TABLE frequencias (
    id INT AUTO_INCREMENT PRIMARY KEY,

    inscricao_id INT NOT NULL,

    data_aula DATE NOT NULL,

    presente TINYINT(1) NOT NULL,

    FOREIGN KEY (inscricao_id)
    REFERENCES inscricoes(id)
);

CREATE TABLE arquivos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome_original VARCHAR(255) NOT NULL,
    nome_salvo VARCHAR(255) NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    data_upload DATETIME DEFAULT CURRENT_TIMESTAMP
);
