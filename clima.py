import requests
import os

# Dados das cidades do seu documento [cite: 37]
CIDADES = {
    "Jaqueira/PE": {"lat": -8.72, "lon": -35.80},
    "Flexeiras/AL": {"lat": -9.26, "lon": -35.71},
    "Palmeira dos Índios/AL": {"lat": -9.40, "lon": -36.62},
    "Ibateguara/AL": {"lat": -8.97, "lon": -35.93},
    "Maceió/AL": {"lat": -9.66, "lon": -35.73},
    "Capela/AL": {"lat": -9.40, "lon": -36.07}
}

def check_weather():
    token = os.getenv('TELEGRAM_TOKEN')
    chat_id = os.getenv('CHAT_ID')
    api_key = os.getenv('WEATHER_KEY')
    
    mensagem = "🚧 *RELATÓRIO CLIMÁTICO DIÁRIO* 🚧\n\n"
    
    for cidade, coord in CIDADES.items():
        # Busca previsão (Curto Prazo) [cite: 3, 39]
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={coord['lat']}&lon={coord['lon']}&appid={api_key}&units=metric&lang=pt_br"
        res = requests.get(url).json()
        
        temp_max = res['main']['temp_max']
        umidade = res['main']['humidity'] [cite: 10, 11]
        chuva_mm = res.get('rain', {}).get('1h', 0) [cite: 8]
        
        # Lógica de alerta do seu documento: 20mm inviabiliza asfalto [cite: 9]
        status = "🔴 ALERTA: CHUVA PESADA" if chuva_mm >= 20 else "✅ LIBERADO"
        if 0 < chuva_mm < 20: status = "🟡 ATENÇÃO: CHUVA LEVE"

        mensagem += f"📍 *{cidade}*\n"
        mensagem += f"🌡️ Max: {temp_max}°C | 💧 Umidade: {umidade}%\n"
        mensagem += f"🌧️ Chuva: {chuva_mm}mm\n"
        mensagem += f"📢 Status: {status}\n\n"

    # Envia para o Telegram
    url_tel = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url_tel, data={"chat_id": chat_id, "text": mensagem, "parse_mode": "Markdown"})

if __name__ == "__main__":
    check_weather()
