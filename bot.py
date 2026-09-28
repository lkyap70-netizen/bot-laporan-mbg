import os
import sys
from datetime import datetime
import locale
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

# Set locale bahasa Indonesia untuk tanggal
try:
    locale.setlocale(locale.LC_TIME, "id_ID.utf8")
except:
    try:
        locale.setlocale(locale.LC_TIME, "id_ID")
    except:
        locale.setlocale(locale.LC_TIME, "")

BOT_TOKEN = os.getenv("BOT_TOKEN")

def generate_pdf(photo_path, output_pdf_path):
    now = datetime.now()
    hari_tanggal = now.strftime("%A, %d %B %Y").upper()

    c = canvas.Canvas(output_pdf_path, pagesize=A4)
    width, height = A4

    # Header Laporan
    c.setFont("Helvetica-Bold", 11)
    c.drawString(40, height - 40, "KEPOLISIAN NEGARA REPUBLIK INDONESIA")
    c.drawString(40, height - 52, "DAERAH JAWA TIMUR")
    c.drawString(40, height - 64, "POLRES KOTA TUBAN")
    c.drawString(40, height - 76, "FORM PENGAWASAN PROGRAM MAKAN BERGIZI GRATIS POLRI")

    c.setFont("Helvetica", 10)
    c.drawString(40, height - 100, "Nama SPPG : SPPG POLRESTA TUBAN 2 JATIROGO")
    c.drawString(40, height - 114, "Pengelola   : YAYASAN KEMALA BHAYANGKARI")
    c.setFont("Helvetica-Bold", 10)
    c.drawString(40, height - 128, f"Hari/Tanggal: {hari_tanggal}")

    # Tempel Foto Dokumentasi
    if os.path.exists(photo_path):
        img = ImageReader(photo_path)
        c.drawImage(img, 40, height - 430, width=515, height=280, preserveAspectRatio=True)

    # Tanda Tangan
    c.setFont("Helvetica", 10)
    c.drawString(380, 150, f"Tuban, {now.strftime('%d %B %Y')}")
    c.drawString(380, 136, "Mengetahui,")
    c.drawString(380, 122, "Ps. KASI PROPAM POLRESTA TUBAN")
    
    c.setFont("Helvetica-Bold", 10)
    c.drawString(380, 60, "ABDUL LATIF, S.H., M.H.")
    c.drawString(380, 48, "IPTU NRP 81040175")

    c.drawString(60, 60, "SUWIGNYO")
    c.drawString(60, 48, "AIPTU NRP 83070036")

    c.save()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Selamat datang di Bot Laporan Pengawasan MBG Polresta Tuban.\n\n"
        "Silakan **kirimkan foto dokumentasi** kegiatan hari ini, bot akan otomatis membuatkan file PDF Laporan lengkap dengan tanggal hari ini."
    )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    msg = await update.message.reply_text("⏳ Sedang memproses foto & membuat laporan PDF...")

    photo_file = await update.message.photo[-1].get_file()
    temp_photo = f"photo_{user.id}.jpg"
    temp_pdf = f"Laporan_MBG_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

    await photo_file.download_to_drive(temp_photo)

    generate_pdf(temp_photo, temp_pdf)

    with open(temp_pdf, 'rb') as pdf_file:
        await update.message.reply_document(
            document=pdf_file,
            filename=temp_pdf,
            caption=f"✅ *Laporan Pengawasan MBG Selesai*\n📅 {datetime.now().strftime('%A, %d %B %Y').upper()}"
        )

    if os.path.exists(temp_photo): os.remove(temp_photo)
    if os.path.exists(temp_pdf): os.remove(temp_pdf)

if __name__ == "__main__":
    if not BOT_TOKEN:
        print("Error: BOT_TOKEN tidak ditemukan!")
        sys.exit(1)

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.run_polling()