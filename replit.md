# Bot de Sorteio Discord - Python

## Visão Geral
Bot do Discord em Python para gerenciamento de sorteios com sistema de fichas personalizável, desenvolvido para rodar no Render.

## Estrutura do Projeto
```
├── bot.py              # Arquivo principal com todos os comandos
├── database.py         # Sistema de database JSON
├── utils.py            # Funções utilitárias
├── requirements.txt    # Dependências Python
├── .env               # Variáveis de ambiente (não commitado)
└── database.json      # Armazenamento de dados (não commitado)
```

## Funcionalidades Principais

### Modal de Inscrição
- Formulário interativo ao usar `/inscrever`
- Validação de nomes reais
- Verificação de hashtag
- Prevenção de duplicatas

### Sistema de Fichas Personalizável
- Fichas base: 1 para todos
- Fichas por cargo: Configurável com sigla personalizada (ex: S.B, M.C)
- Fichas por TAG: Configurável qualquer tag e quantidade

### Listas Abreviadas
- Formato compacto: "Rafael Fe." ao invés de "Rafael Felipe"
- Lista detalhada mostra todas as fichas com siglas dos cargos
- Sem espaços entre participantes

### Comandos Admin Completos
- Gerenciamento de configurações
- Blacklist com motivo
- Exportação de listas
- Estatísticas detalhadas
- Limpeza seletiva ou total

## Configuração

### Variáveis de Ambiente Necessárias
- `BOT_TOKEN` - Token do bot do Discord

### Permissões do Bot Discord
- Server Members Intent (ativado)
- Message Content Intent (ativado)

## Mudanças Recentes
- 02/11/2025: Projeto criado em Python para deploy no Render
- Modal interativo de inscrição implementado
- Sistema de siglas personalizáveis para cargos
- Formato de lista abreviado e compacto
- TAG totalmente configurável pelo admin
