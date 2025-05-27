# QuantLink FREN Core Narrator - Demo Guide

## Demo Video Hazırlığı

Bu rehber, QuantLink FREN Core Narrator projesinin demo videosunu çekmek için gerekli adımları içerir.

## Özellikler

### ✅ Tamamlanan Özellikler

1. **Web Arayüzü**
   - Modern, responsive Bootstrap tasarımı
   - Real-time server status kontrolü
   - Loading spinners ve progress indicators
   - Audio controls (play, pause, volume)

2. **Cryptocurrency Price Narration**
   - 15+ popüler cryptocurrency desteği
   - Multiple currency support (USD, EUR, GBP, JPY, AUD, CAD)
   - 24h, 7d, 30d price change narration
   - Real-time price fetching from CoinGecko API

3. **Batch Mode**
   - Multiple cryptocurrency selection
   - Combined narration for selected cryptos
   - Grid view for multiple price display

4. **Custom Text Narration**
   - Multi-language support (EN, ES, FR, DE, IT, JA)
   - Speed control (normal/slow)
   - Pre-built demo text examples

5. **Backend API**
   - RESTful Flask API
   - CORS enabled for cross-origin requests
   - Automatic audio file cleanup
   - Error handling and logging

## Demo Senaryosu

### 1. Giriş (30 saniye)
- Projeyi tanıt
- Web arayüzünü göster
- Server status'ün "Connected" olduğunu göster

### 2. Single Crypto Narration (60 saniye)
- Bitcoin seçip price fetch et
- 24h change ile birlikte narrate et
- Audio player'ın çalıştığını göster
- Farklı bir crypto (Ethereum) ile tekrarla

### 3. Batch Mode Demo (90 saniye)
- Batch mode'u aktif et
- 3-4 crypto seç (Bitcoin, Ethereum, Solana, Cardano)
- Fetch prices ile grid view'i göster
- Batch narration'ı çalıştır

### 4. Custom Text Narration (60 saniye)
- Demo text örneklerinden birini seç
- Farklı dil seç (Spanish)
- Slow speed ile narrate et
- Kendi custom text'ini yaz ve narrate et

### 5. Advanced Features (30 saniye)
- 7d ve 30d price changes'i aktif et
- Farklı currency seç (EUR)
- Status messages'i göster

## Teknik Detaylar

### Kullanılan Teknolojiler
- **Backend**: Python Flask, gTTS (Google Text-to-Speech)
- **Frontend**: HTML5, CSS3, JavaScript (ES6+), Bootstrap 5
- **API**: CoinGecko API for cryptocurrency data
- **Audio**: HTML5 Audio API

### API Endpoints
- `GET /api/health` - Health check
- `GET /api/crypto/price` - Single crypto price
- `GET /api/crypto/prices` - Multiple crypto prices
- `POST /api/narrator/crypto` - Narrate crypto price
- `POST /api/narrator/text` - Narrate custom text

### Öne Çıkan Özellikler
1. **Real-time Data**: CoinGecko API ile güncel fiyat verileri
2. **Multi-language TTS**: 6 farklı dilde narration
3. **Batch Processing**: Birden fazla cryptocurrency'yi aynı anda işleme
4. **Responsive Design**: Mobil ve desktop uyumlu
5. **Error Handling**: Kapsamlı hata yönetimi ve kullanıcı bildirimleri

## Demo İpuçları

1. **Ses Kontrolü**: Demo öncesi ses seviyesini kontrol et
2. **Network**: İnternet bağlantısının stabil olduğundan emin ol
3. **Browser**: Chrome veya Firefox kullan (audio support için)
4. **Preparation**: Demo text'lerini önceden hazırla
5. **Timing**: Her feature için yeterli zaman ayır

## Troubleshooting

### Yaygın Sorunlar
1. **Server Connection Error**: Port 5001'in açık olduğunu kontrol et
2. **Audio Not Playing**: Browser'ın audio permission'ını kontrol et
3. **API Rate Limiting**: CoinGecko API rate limit'ine takılırsa bekle
4. **CORS Issues**: Server'ın CORS enabled olduğunu kontrol et

### Demo Sırasında Dikkat Edilecekler
- Status messages'i takip et
- Loading spinner'ların çalıştığını göster
- Audio player controls'ü kullan
- Error handling'i göstermek için kasıtlı hata yap (opsiyonel)

## Sonuç

Bu demo, QuantLink FREN Core Narrator'ın temel özelliklerini ve gelişmiş fonksiyonlarını kapsamlı bir şekilde gösterir. Proje, cryptocurrency verilerini AI-powered narration ile birleştiren modern bir web uygulaması olarak başarıyla tamamlanmıştır.
