import os
import logging
from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from package_manager import PackageManager
from executor import PythonExecutor

logger = logging.getLogger(__name__)

class BotManager:
    def __init__(self, token: str, package_manager: PackageManager):
        self.token = token
        self.package_manager = package_manager
        self.executor = PythonExecutor(package_manager)
        self.updater = Updater(token=token, use_context=True)
        self.setup_handlers()
        
    def setup_handlers(self):
        """Bot komutlarını ayarla"""
        dp = self.updater.dispatcher
        
        # Komutlar
        dp.add_handler(CommandHandler("start", self.start_command))
        dp.add_handler(CommandHandler("help", self.help_command))
        dp.add_handler(CommandHandler("packages", self.list_packages))
        dp.add_handler(CommandHandler("install", self.install_package))
        dp.add_handler(CommandHandler("uninstall", self.uninstall_package))
        dp.add_handler(CommandHandler("update", self.update_package))
        dp.add_handler(CommandHandler("check", self.check_packages))
        dp.add_handler(CommandHandler("status", self.status))
        
        # Python dosyası çalıştırma
        dp.add_handler(MessageHandler(Filters.document.py, self.execute_python_file))
        
        # Hata yakalama
        dp.add_error_handler(self.error_handler)
        
    def start(self):
        """Bot'u başlat"""
        logger.info("🚀 Bot başlatılıyor...")
        self.updater.start_polling()
        self.updater.idle()
        
    def start_command(self, update: Update, context: CallbackContext):
        """Start komutu"""
        welcome_message = """
🤖 **Python Paket Yöneticisi Botu'na Hoş Geldiniz!**

Bu bot ile:
✅ Python paketlerini yükleyebilir
✅ Yüklü paketleri görüntüleyebilir
✅ Paketleri güncelleyebilir/kaldırabilir
✅ Python dosyalarını çalıştırabilirsiniz

**📋 Komutlar:**
/packages - Yüklü paketleri listele
/install [paket] - Yeni paket yükle
/uninstall [paket] - Paket kaldır
/update [paket] - Paket güncelle
/check - Eksik paketleri kontrol et
/status - Bot durumunu göster
/help - Yardım menüsü

📁 **Python dosyası çalıştırmak için:** .py dosyası gönderin
        """
        update.message.reply_text(welcome_message, parse_mode=ParseMode.MARKDOWN)
        
    def help_command(self, update: Update, context: CallbackContext):
        """Yardım komutu"""
        help_text = """
🔍 **Detaylı Yardım**

**Paket İşlemleri:**
• `/install requests` - requests paketini yükler
• `/install pandas numpy` - Birden fazla paket yükler
• `/uninstall requests` - Paket kaldırır
• `/update requests` - Paketi günceller
• `/packages` - Tüm paketleri listeler
• `/check` - Eksik paketleri kontrol eder

**Dosya İşlemleri:**
• `.py` dosyası gönderin - Otomatik çalıştırır
• Gereken paketler otomatik yüklenir

**Not:** Tüm işlemler otomatik olarak yapılır! 🚀
        """
        update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)
        
    def list_packages(self, update: Update, context: CallbackContext):
        """Yüklü paketleri listele"""
        try:
            packages = self.package_manager.get_installed_packages()
            
            if not packages:
                update.message.reply_text("📦 Hiç paket yüklü değil.")
                return
                
            message = "📦 **Yüklü Paketler:**\n\n"
            for pkg in packages[:20]:  # İlk 20 paket
                message += f"• `{pkg}`\n"
                
            if len(packages) > 20:
                message += f"\n...ve {len(packages) - 20} paket daha"
                
            update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            update.message.reply_text(f"❌ Hata: {str(e)}")
            
    def install_package(self, update: Update, context: CallbackContext):
        """Paket yükle"""
        if not context.args:
            update.message.reply_text("⚠️ Lütfen yüklenecek paket adını girin.\nÖrnek: `/install requests`", parse_mode=ParseMode.MARKDOWN)
            return
            
        packages = context.args
        update.message.reply_text(f"📦 `{', '.join(packages)}` yükleniyor...", parse_mode=ParseMode.MARKDOWN)
        
        try:
            results = self.package_manager.install_packages(packages)
            
            success_msg = "✅ **Başarıyla yüklenenler:**\n"
            failed_msg = "❌ **Yüklenemeyenler:**\n"
            
            for pkg, success in results.items():
                if success:
                    success_msg += f"• `{pkg}`\n"
                else:
                    failed_msg += f"• `{pkg}`\n"
                    
            response = success_msg
            if "❌" in failed_msg:
                response += f"\n{failed_msg}"
                
            update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            update.message.reply_text(f"❌ Yükleme hatası: {str(e)}")
            
    def uninstall_package(self, update: Update, context: CallbackContext):
        """Paket kaldır"""
        if not context.args:
            update.message.reply_text("⚠️ Lütfen kaldırılacak paket adını girin.")
            return
            
        package = context.args[0]
        update.message.reply_text(f"🗑️ `{package}` kaldırılıyor...", parse_mode=ParseMode.MARKDOWN)
        
        try:
            if self.package_manager.uninstall_package(package):
                update.message.reply_text(f"✅ `{package}` başarıyla kaldırıldı.", parse_mode=ParseMode.MARKDOWN)
            else:
                update.message.reply_text(f"❌ `{package}` kaldırılamadı.", parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            update.message.reply_text(f"❌ Hata: {str(e)}")
            
    def update_package(self, update: Update, context: CallbackContext):
        """Paket güncelle"""
        if not context.args:
            update.message.reply_text("⚠️ Lütfen güncellenecek paket adını girin.")
            return
            
        package = context.args[0]
        update.message.reply_text(f"🔄 `{package}` güncelleniyor...", parse_mode=ParseMode.MARKDOWN)
        
        try:
            if self.package_manager.update_package(package):
                update.message.reply_text(f"✅ `{package}` başarıyla güncellendi.", parse_mode=ParseMode.MARKDOWN)
            else:
                update.message.reply_text(f"❌ `{package}` güncellenemedi.", parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            update.message.reply_text(f"❌ Hata: {str(e)}")
            
    def check_packages(self, update: Update, context: CallbackContext):
        """Eksik paketleri kontrol et"""
        update.message.reply_text("🔍 Eksik paketler kontrol ediliyor...")
        
        try:
            missing_packages = self.package_manager.check_missing_packages()
            
            if not missing_packages:
                update.message.reply_text("✅ Tüm paketler güncel ve yüklü!")
                return
                
            message = "📦 **Eksik/Güncellenmesi Gereken Paketler:**\n\n"
            for pkg in missing_packages[:10]:
                message += f"• `{pkg}`\n"
                
            if len(missing_packages) > 10:
                message += f"\n...ve {len(missing_packages) - 10} paket daha"
                
            message += "\n\n📥 Yüklemek için: `/install paket_adi`"
            update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            update.message.reply_text(f"❌ Kontrol hatası: {str(e)}")
            
    def status(self, update: Update, context: CallbackContext):
        """Bot durumu"""
        status_text = """
🟢 **Bot Durumu: Aktif**

**Sistem Bilgileri:**
• Paket Sayısı: {}
• Python Versiyonu: {}
• Bot Versiyonu: 1.0.0

**Özellikler:**
✅ Paket Yükleme
✅ Paket Kaldırma
✅ Paket Güncelleme
✅ Python Dosyası Çalıştırma
✅ Otomatik Bağımlılık Yönetimi
        """
        
        package_count = len(self.package_manager.get_installed_packages())
        python_version = os.popen('python --version').read().strip()
        
        update.message.reply_text(
            status_text.format(package_count, python_version),
            parse_mode=ParseMode.MARKDOWN
        )
        
    def execute_python_file(self, update: Update, context: CallbackContext):
        """Python dosyasını çalıştır"""
        try:
            file = update.message.document
            file_name = file.file_name
            
            if not file_name.endswith('.py'):
                update.message.reply_text("⚠️ Lütfen sadece .py dosyası gönderin.")
                return
                
            update.message.reply_text(f"📁 `{file_name}` indiriliyor...", parse_mode=ParseMode.MARKDOWN)
            
            # Dosyayı indir
            file_path = f"/tmp/{file_name}"
            file.get_file().download(custom_path=file_path)
            
            update.message.reply_text("🔍 Python dosyası analiz ediliyor...")
            
            # Dosyayı çalıştır
            success, output, error = self.executor.execute_file(file_path)
            
            if success:
                message = f"✅ **Dosya başarıyla çalıştırıldı!**\n\n📤 **Çıktı:**\n```\n{output[:3000]}\n```"
                if len(output) > 3000:
                    message += "\n\n... (çıktı çok uzun, ilk 3000 karakter gösteriliyor)"
            else:
                message = f"❌ **Çalıştırma hatası!**\n\n```\n{error[:3000]}\n```"
                
            update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
            
            # Geçici dosyayı temizle
            os.remove(file_path)
            
        except Exception as e:
            update.message.reply_text(f"❌ Dosya işleme hatası: {str(e)}")
            
    def error_handler(self, update: Update, context: CallbackContext):
        """Hata yakalayıcı"""
        logger.error(f"Update {update} caused error {context.error}")
        if update:
            update.message.reply_text("❌ Bir hata oluştu. Lütfen tekrar deneyin.")
