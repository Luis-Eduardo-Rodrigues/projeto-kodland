# Guerreiro Vs O Guardião

Jogo de plataforma medieval 2D criado em Python com Pygame Zero para o teste
pratico de tutoria da Kodland.

## Historia

Um guerreiro precisa atravessar o vilarejo de Arven, as muralhas de Eldoria e
a cripta onde o Selo das Sombras foi rompido. Em cada fase ele deve recolher
todas as moedas e derrotar os inimigos para abrir a porta de saida.

## Como executar

Requer Python 3 e Pygame Zero.

```bash
python3 -m pip install -r requirements.txt
./run_game.sh
```

O iniciador posiciona a janela no centro da tela e evita a janela temporaria
de 100 x 100 criada pelo comando `pgzrun`. No Windows, execute `run_game.bat`.
Para garantir a centralizacao, sempre use um desses dois iniciadores.

## Controles

- `A`/`D` ou setas: movimentar
- `W`, seta para cima ou `Espaco`: pular
- `Z` ou `X`: atacar com a espada
- `Shift` ou `C`: executar um dash
- `P`: pausar ou continuar
- `Esc`: voltar ao menu
- `R`: reiniciar depois da vitoria ou derrota

## Recursos implementados

- Tres fases com objetivos, pontuacao e dificuldade progressiva
- Menu moderno com botoes arredondados, personagens e guia compacto de teclas
- Controle conjunto de musica e efeitos sonoros
- Cavaleiro com animacoes alinhadas de idle, corrida, pulo, queda, dano e ataque
- Movimento mais suave, salto, dash com recarga e efeito visual
- Aranhas, morcegos e mumias com movimento, patrulha e animacoes corrigidas
- Morcegos com voo baixo e patrulha simples para facilitar o combate
- Pocoes de cura, pontuacao e porta com objetivo duplo
- Guardiao final com barra de vida e sete pontos de resistencia
- HUD alinhado, tela de pausa e mensagens com linguagem mais natural
- Classes proprias para personagens, movimento e animacao

Consulte [CREDITS.md](CREDITS.md) para as licencas dos recursos visuais e
sonoros utilizados.
