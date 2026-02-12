# 🤖 Telegram Python Paket Yöneticisi Botu

Otomatik paket yükleme ve Python dosyası çalıştırma özellikli Telegram botu.

## 🚀 Özellikler

- ✅ Python paketlerini otomatik yükleme
- 📦 Yüklü paketleri listeleme
- 🔄 Paket güncelleme/kaldırma
- 🐍 Python dosyası çalıştırma
- 📁 Otomatik bağımlılık yönetimi
- 🔍 Eksik paket kontrolü

## 📋 Komutlar

- `/start` - Botu başlat
- `/help` - Yardım menüsü
- `/packages` - Yüklü paketleri listele
- `/install [paket]` - Paket yükle
- `/uninstall [paket]` - Paket kaldır
- `/update [paket]` - Paket güncelle
- `/check` - Eksik paketleri kontrol et
- `/status` - Bot durumu

## 🛠️ Kurulum

### Render'a Deploy

1. Bu repoyu fork'layın
2. Render.com'da yeni Web Service oluşturun
3. Forkladığınız repoyu bağlayın
4. Environment variable'a `TELEGRAM_BOT_TOKEN` ekleyin
5. Deploy edin

### Local Kurulum

```bash
git clone https://github.com/username/telegram-python-bot
cd telegram-python-bot
pip install -r requirements.txt
echo "TELEGRAM_BOT_TOKEN=your_token_here" > .env
python main.py
