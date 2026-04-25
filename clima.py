import requests
import os
from datetime import datetime
import pytz

# Cidades e Coordenadas
CIDADES = {
    "Jaqueira/PE": {"lat": -8.72, "lon": -35.80},
    "Flexeiras/AL": {"lat": -9.26, "lon": -35.71},
    "Palmeira dos Índios/AL": {"lat": -9.40, "lon": -36.62},
    "Ibateguara/AL": {"lat": -8.97, "lon": -35.93},
    "Maceió/AL": {"lat": -9.66, "lon": -35.73},
    "Capela/AL": {"lat": -9.40, "lon": -36.07}
}

def check_weather():
    fuso = pytz.timezone('America/Sao_Paulo')
    agora = datetime.now(fuso)
    
    if agora.weekday() == 6: # Domingo não envia
        return

    token = os.getenv('TELEGRAM_TOKEN')
    chat_id = os.getenv('CHAT_ID')
    hora = agora.hour

    # Títulos
    if hora == 19:
        titulo = "📝 *PREVISÃO PARA AMANHÃ (PLANEJAMENTO)*"
    elif hora == 5:
        titulo = "🌅 *STATUS MATINAL DA OBRA*"
    else:
        titulo = f"🕒 *ATUALIZAÇÃO DE ROTINA ({hora}h)*"

    mensagem = f"{titulo}\n\n"

    for cidade, coord in CIDADES.items():
        # Open-Meteo: Gratuito, sem chave e mais preciso para o Brasil
        url = f"https://api.open-meteo.com/v1/forecast?latitude={coord['lat']}&longitude={coord['lon']}&current=temperature_2m,relative_humidity_2m,rain&hourly=rain,precipitation_probability&timezone=America%2FSao_Paulo&forecast_days=2"
        
        res = requests.get(url).json()
        
        if hora == 19:
            # Pega a previsão para o dia seguinte (mesma hora de amanhã)
            chuva_mm = res['hourly']['rain'][24 + hora]
            prob = res['hourly']['precipitation_probability'][24 + hora]
            temp = res['hourly']['temperature_2m'][24 + hora]
        else:
            # Pega o tempo real agora
            chuva_mm = res['current']['rain']
            temp = res['current']['temperature_2m']
            prob = res['hourly']['precipitation_probability'][hora]

        # Lógica do Asfalto (Documento original: 20mm inviabiliza)
        if chuva_mm >= 20:
            status = "🔴 ALERTA: CHUVA PESADA"
        elif chuva_mm > 0.5:
            status = "🟡 ATENÇÃO: CHUVA LEVE/MODERADA"
        else:
            status = "✅ LIBERADO"

        mensagem += f"📍 *{cidade}*\n"
        mensagem += f"🌡️ {temp}°C | 🌧️ {chuva_mm}mm | 📊 Prob: {prob}%\n"
        mensagem += f"📢 Status: {status}\n\n"

    # Envio para Telegram
    url_tel = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url_tel, data={"chat_id": chat_id, "text": mensagem, "parse_mode": "Markdown"})

if __name__ == "__main__":
    check_weather()
