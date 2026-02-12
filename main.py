import os
import sys
import subprocess
import logging
from package_manager import PackageManager
from bot import BotManager

# Loglama ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_and_install_base_packages():
    """Temel paketleri kontrol et ve yükle"""
    required_packages = ['python-telegram-bot', 'requests', 'pipdeptree']
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            logger.info(f"✅ {package} zaten yüklü")
        except ImportError:
            logger.info(f"📦 {package} yükleniyor...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def main():
    """Ana uygulama başlangıcı"""
    try:
        # Temel paketleri kontrol et
        check_and_install_base_packages()
        
        # Bot token'ı kontrol et
        bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
        if not bot_token:
            logger.error("❌ TELEGRAM_BOT_TOKEN bulunamadı!")
            logger.info("Lütfen .env dosyası oluşturun veya environment variable ekleyin")
            sys.exit(1)
        
        # Paket yöneticisini başlat
        package_manager = PackageManager()
        
        # Bot'u başlat
        bot_manager = BotManager(bot_token, package_manager)
        bot_manager.start()
        
    except KeyboardInterrupt:
        logger.info("👋 Bot durduruldu")
    except Exception as e:
        logger.error(f"❌ Hata: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
