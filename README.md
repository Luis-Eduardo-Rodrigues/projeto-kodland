# O Cavaleiro de Valedouro

Jogo de plataforma medieval 2D criado em Python com Pygame Zero para o teste
pratico de tutoria da Kodland.

## Historia

O cavaleiro de Valedouro precisa atravessar a vila, as muralhas do norte e uma
masmorra esquecida. Em cada fase ele deve recolher todas as moedas antes de
abrir a porta de saida, enquanto enfrenta criaturas que patrulham o caminho.

## Como executar

Requer Python 3 e Pygame Zero.

```bash
python3 -m pip install -r requirements.txt
pgzrun main.py
```

## Controles

- `A`/`D` ou setas: movimentar
- `W`, seta para cima ou `Espaco`: pular
- `Z` ou `X`: atacar com a espada
- `Esc`: voltar ao menu
- `R`: reiniciar depois da vitoria ou derrota

## Recursos implementados

- Tres fases curtas com dificuldade progressiva
- Menu principal com botoes clicaveis
- Controle conjunto de musica e efeitos sonoros
- Cavaleiro com animacoes de idle, corrida, pulo, queda e ataque
- Aranhas, morcegos e mumias com movimento, patrulha e animacoes
- Combate, vidas, coleta de moedas e condicao de vitoria
- Classes proprias para personagens, movimento e animacao

Consulte [CREDITS.md](CREDITS.md) para as licencas dos recursos visuais e
sonoros utilizados.
