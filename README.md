# Carteira Digital - Scrapper

Scrapper capaz de realizar login e extrair informações financeiras como valor alocado em ações e em fundos.

## Corretoras e softwares implementados:

- Smartt Bot
  - _Informações extraídas:_
  - Rendimento total de um robô
  - % de trades com sucesso de um robô
  - Drawndown máximos
- Rico
  - _Informações extraídas:_
  - Saldo em conta
  - Valor investido em Renda Fixa
  - Valor investido em Renda Variável
- Clear
  - _Informações extraídas:_
  - Valor bloqueado (Garantias)
  - Valor aplicado em Renda Variável
  - Valor aplicado em Renda Fixa
- GuiaBolso
  - _Informações extraídas:_
  - Saldo em cada banco integrado
  - Saldo em investimentos
  - Valor total em conta

## Requerimentos

- Python 3

## Instalação

- `pip install -r requirements.txt`
- `cp .env.example .env`
- Preencha as informações no arquivo `.env`
- `python main.py`

## Objetivo

O objetivo deste repositório é alimentar as informações para fornecer para o https://github.com/MaiaVinicius/carteira-digital.
