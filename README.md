# Telegram Bot para Geração de PIX

Este é um bot do Telegram que permite gerar um código PIX para pagamento utilizando a API da Pushinpay. Ao utilizar o bot, o usuário pode visualizar a chave copia-e-cola para pagar via PIX e receber um QR Code para facilitar o pagamento.

## Funcionalidades

- **/start**: Exibe uma mensagem inicial com um link de pré-visualização e um botão de compra.
- **Botão "Comprar Agora"**: Gera um código PIX para pagamento e exibe os detalhes do pagamento.
- **Botão "Ver QR Code"**: Exibe o QR Code do pagamento.
- **Botão "Já Fiz o Pagamento"**: Confirma o pagamento e instrui o usuário a enviar o comprovante.

## Pré-requisitos

Antes de rodar o bot, você precisa de:

1. **Token do Telegram**: Crie um bot no Telegram usando o [BotFather](https://core.telegram.org/bots#botfather) e obtenha o token.
2. **Token da PushinPay**: Você precisa de um token de acesso para a API da PushinPay.

## Instalação

1. Clone este repositório:
   ```bash
   git clone https://github.com/joceliosilva/botpixpushinpay.git
2. Acesse a pasta onde efetuou o clone
   ```bash
   cd botpixpushinpay
4. Instale as dependecias
   ```bash
   pip install -r requirements.txt
5. Execute
   ```bash
   python pix.py

## Adendo
O bot deve ficar rodando, então é interessante que você coloque em uma máquina servidor ou em uma VPS online.
   

   

