# MoodShot

Gerenciador de perfis e filtros de câmera via prompt, desenvolvido para a Sprint 4 de Computational Thinking with Python.

## Requisitos

- Python 3.10 ou superior
- Biblioteca `requests` (usada na opção 5, recomendação pelo clima)

## Instalação

```bash
pip install -r requirements.txt
```

## Execução

```bash
python main.py
```

## Funcionalidades

O menu principal mostra, a cada iteração, o estado atual do dispositivo (foco, filtro, tema e modo).

| Opção | Funcionalidade |
| --- | --- |
| 1 | Alterar Foco (0 a 20, aceita decimais) |
| 2 | Filtros: 2.1 Filtros Default (Viagem, Estudo, Encontro, PopArt) e 2.2 Filtros Personalizados (criar ou usar um filtro com foco, saturação, vinheta e cor matiz) |
| 3 | Predefinições: tema da interface e modo claro/escuro |
| 4 | Histórico de ações |
| 5 | Recomendação de filtro, tema, modo e foco a partir do clima atual da cidade (API Open-Meteo) |
| 6 | Sair |

## Arquivos de dados

- `filtros_salvos.json`: filtros personalizados criados pelo usuário, recarregados ao iniciar.
- `historico.txt`: registro das ações, com data e hora.

Os dois arquivos são criados automaticamente na pasta do projeto, se não existirem.
