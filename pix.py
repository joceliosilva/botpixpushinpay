from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
import requests
import logging
import qrcode
from io import BytesIO

# Token do bot
TELEGRAM_BOT_TOKEN = "TOKEN DO SEU BOT"
API_PUSHINPAY = "https://api.pushinpay.com.br/api/pix/cashIn" #não modificar
PUSHINPAY_TOKEN = "TOKEN DA PUSHINPAY"

# Configuração do logging (pode remover depois) 
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Função para gerar o PIX
def gerar_pix(valor_em_centavos):
    headers = {
        "Authorization": f"Bearer {PUSHINPAY_TOKEN}",
        "Content-Type": "application/json"
    }
    body = {
        "value": valor_em_centavos,
        "webhook_url": "http://seu-endpoint.com"  # Coloque aqui o URL do seu webhook, se necessário
    }

    try:
        response = requests.post(API_PUSHINPAY, headers=headers, json=body)
        response.raise_for_status()
        
        # Log da resposta da API
        logger.info(f"Resposta da API PushinPay: {response.text}")
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Erro ao chamar a API PushinPay: {e}")
        raise Exception(f"Erro na API PushinPay: {e}")

# Função do comando /start
async def start(update, context):
    mensagem = (
        "👋 *OLÁ!*\n\n"
        "VI QUE VOCÊ SE INTERESSOU PELO MEU CONTEÚDO\n\n"
        "NÃO POSSO ENVIAR UMA PRÉVIA DIRETAMENTE AQUI PARA NÃO SER BANIDO, "
        "MAS SEGUE ABAIXO O LINK DA PRÉVIA NO MEGA:\n\n"
        "📥 [Visualizar no MEGA](LINK DO MEGA SE FOR FAZER ASSIM)\n\n"
        "AO VISUALIZAR, SE GOSTAR, CLIQUE NO BOTÃO COMPRAR ABAIXO PARA PROSSEGUIR COM A COMPRA!\n\n"
       
    )

    keyboard = [
        [InlineKeyboardButton("💳 Comprar Agora", callback_data="comprar_agora")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=mensagem,
        parse_mode="Markdown",
        reply_markup=reply_markup,
    )

# Função de callback para o botão "Comprar Agora"
async def handle_callback(update, context):
    query = update.callback_query
    await query.answer()

    if query.data == "comprar_agora":
        valor = 10.50  #digite o valor do seu produto, casas decimais com (.) e nao (,)
        valor_em_centavos = int(valor * 100)

        # Chamar a função para gerar o PIX
        pix_data = gerar_pix(valor_em_centavos)
        
        chave_copia_e_cola = pix_data.get("qr_code")

        if not chave_copia_e_cola:
            await query.message.reply_text("Erro ao gerar o PIX, tente novamente mais tarde.")
            return

        mensagem = f"""
        🧾 *Detalhes do pagamento:*\n\n
        💰 *Valor:* R$ {valor:.2f}\n
        📲 *Chave Copia e Cola (CLIQUE SOBRE O TEXTO E COLE NO SEU BANCO):* `{chave_copia_e_cola}\n`
        
        👉 Se preferir, clique no botão abaixo para visualizar o QR Code e realizar o pagamento:
        """

        keyboard = [
            [InlineKeyboardButton("👁️ Ver QR Code", callback_data="ver_qr_code")],
            [InlineKeyboardButton("💸 Já Fiz o Pagamento", callback_data="ja_fiz_pagamento")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Enviar a mensagem com os detalhes de pagamento e os botões
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=mensagem,
            parse_mode="Markdown",
            reply_markup=reply_markup,
        )

# Função de callback para exibir o QR Code
async def ver_qr_code(update, context):
    query = update.callback_query
    await query.answer()

    # Recuperar dados do pagamento
    valor = 10.50
    valor_em_centavos = int(valor * 100)
    pix_data = gerar_pix(valor_em_centavos)

    chave_copia_e_cola = pix_data.get("qr_code")

    if not chave_copia_e_cola:
        await query.message.reply_text("Erro ao gerar o QR Code, tente novamente mais tarde.")
        return

    # Gerar o QR Code a partir da chave Copia e Cola
    qr = qrcode.make(chave_copia_e_cola)
    qr_image_file = BytesIO()
    qr.save(qr_image_file)
    qr_image_file.seek(0)

    # Enviar o QR code como imagem
    await context.bot.send_photo(chat_id=query.message.chat_id, photo=InputFile(qr_image_file))

# Função de callback para o botão "Já Fiz o Pagamento"
async def ja_fiz_pagamento(update, context):
    query = update.callback_query
    await query.answer()

    # Enviar a mensagem de confirmação de pagamento
    await query.message.reply_text(
        "✅ Beleza! Envie o comprovante para o @(seu nick), e receba seu acesso! "
        "⚠️ Caso o bot falhe e não envie seu acesso, entre em contato com @(seu suporte)."
    )

# Função principal
def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_callback, pattern="comprar_agora"))
    application.add_handler(CallbackQueryHandler(ver_qr_code, pattern="ver_qr_code"))
    application.add_handler(CallbackQueryHandler(ja_fiz_pagamento, pattern="ja_fiz_pagamento"))

    application.run_polling()

if __name__ == "__main__":
    main()
