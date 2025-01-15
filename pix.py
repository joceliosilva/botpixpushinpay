from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
import requests
import logging
import qrcode
from io import BytesIO

# Configuração do Token do bot e da PushinPay
TELEGRAM_BOT_TOKEN = "TOKEN DO BOT TELEGRAN"
API_PUSHINPAY_PIX = "https://api.pushinpay.com.br/api/pix/cashIn" #NÃO MUDAR
API_PUSHINPAY_STATUS = "https://api.pushinpay.com.br/api/transactions/" #NÃO MUDAR
PUSHINPAY_TOKEN = "TOKEN PUSHINPAY"

# Configuração do logging
logging.basicConfig(level=logging.WARNING, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Função para gerar o PIX
def gerar_pix(valor_em_centavos):
    headers = {
        "Authorization": f"Bearer {PUSHINPAY_TOKEN}",
        "Content-Type": "application/json"
    }
    body = {
        "value": valor_em_centavos,
        "webhook_url": "http://seu-endpoint.com"  # Substitua pelo URL do webhook se necessário
    }

    try:
        response = requests.post(API_PUSHINPAY_PIX, headers=headers, json=body)
        response.raise_for_status()
       
        return response.json()
    except requests.RequestException as e:
       
        raise Exception(f"Erro na API PushinPay: {e}")

# Função para consultar o status do PIX
def consultar_status_pix(transacao_id):
    url = f"{API_PUSHINPAY_STATUS}{transacao_id}"
    headers = {
        "Authorization": f"Bearer {PUSHINPAY_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        logger.info(f"Status do PIX: {response.json()}")
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Erro ao consultar o status do PIX: {e}")
        return None

# Funções do bot
async def start(update, context):
    mensagem = (
         "👋 *OLÁ!*\n\n"
        "EU SOU O BOT DE TESTES DE PAGAMENTO\n\n"
        "VOCÊ PODE USAR MEU CÓDIGO FONTE PARA DESENVOLVER SEU BOT! "
        "SEGUE ABAIXO MEU CÓDIGO NO GITHUB:\n\n"
        "📥 [Visualizar](https://github.com/joceliosilva/botpixpushinpay)\n\n"
        "SE LHE AJUDAR VOCÊ PODE AJUDAR MEU CRIADOR PAGANDO O PIX QUE SERÁ GERADO, É APENAS R$ 1,30!\n\n"
        
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

async def handle_callback(update, context):
    query = update.callback_query
    await query.answer()

    if query.data == "comprar_agora":
        valor = 1.30
        valor_em_centavos = int(valor * 100)

        try:
            pix_data = gerar_pix(valor_em_centavos)
            chave_copia_e_cola = pix_data.get("qr_code")
            transacao_id = pix_data.get("id")

            if not chave_copia_e_cola or not transacao_id:
                await query.message.reply_text("Erro ao gerar o PIX, tente novamente mais tarde.")
                return

            context.user_data["transacao_id"] = transacao_id

            mensagem = f"""
            🧾 *Detalhes do pagamento:*\n\n
        💰 *Valor:* R$ {valor:.2f}\n
        📲 *Chave Copia e Cola (CLIQUE SOBRE O TEXTO E COLE NO SEU BANCO):\n\n* `{chave_copia_e_cola}\n`
        
        👉 Se preferir, clique no botão abaixo para visualizar o QR Code e realizar o pagamento:
        """

            keyboard = [
                [InlineKeyboardButton("👁️ Ver QR Code", callback_data="ver_qr_code")],
                [InlineKeyboardButton("💸 Já Fiz o Pagamento", callback_data="ja_fiz_pagamento")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=mensagem,
                parse_mode="Markdown",
                reply_markup=reply_markup,
            )
        except Exception as e:
            await query.message.reply_text(f"Erro ao gerar o PIX: {e}")

async def ver_qr_code(update, context):
    query = update.callback_query
    await query.answer()

    transacao_id = context.user_data.get("transacao_id")
    if not transacao_id:
        await query.message.reply_text("Erro: ID da transação não encontrado.")
        return

    pix_data = consultar_status_pix(transacao_id)
    chave_copia_e_cola = pix_data.get("qr_code") if pix_data else None

    if not chave_copia_e_cola:
        await query.message.reply_text("Erro ao gerar o QR Code.")
        return

    qr = qrcode.make(chave_copia_e_cola)
    qr_image_file = BytesIO()
    qr.save(qr_image_file)
    qr_image_file.seek(0)

    await context.bot.send_photo(chat_id=query.message.chat_id, photo=InputFile(qr_image_file))

async def ja_fiz_pagamento(update, context):
    query = update.callback_query
    await query.answer()

    transacao_id = context.user_data.get("transacao_id")
    if not transacao_id:
        await query.message.reply_text("Erro: ID da transação não encontrado.")
        return

    status_pix = consultar_status_pix(transacao_id)
    if not status_pix:
        await query.message.reply_text("Erro ao verificar o pagamento.")
        return

    status = status_pix.get("status")
    link = "https://github.com/joceliosilva/botpixpushinpay"
    if status == "paid":
        await query.message.reply_text(f"✅ Pagamento confirmado! Aqui está seu link de acesso: {link}\n Se tiver algum problema, envie uma mensagem para o @jsbr06.")
    else:
        await query.message.reply_text(f"⚠️ O pagamento ainda não foi concluído. Clique novamente em 'JÁ FIZ O PAGAMENTO'")

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
