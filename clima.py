import requests
import os
from datetime import datetime
import pytz

# Cidades e Coordenadas do seu documento
CIDADES = {
    "Jaqueira/PE": {"lat": -8.72, "lon": -35.80},
    "Flexeiras/AL": {"lat": -9.26, "lon": -35.71},
    "Palmeira dos Índios/AL": {"lat": -9.40, "lon": -36.62},
    "Ibateguara/AL": {"lat": -8.97, "lon": -35.93},
    "Maceió/AL": {"lat": -9.66, "lon": -35.73},
    "Capela/AL": {"lat": -9.40, "lon": -36.07}
}

def check_weather():
    # Configura fuso horário de Brasília
    fuso = pytz.timezone('America/Sao_Paulo')
    agora = datetime.now(fuso)
    
    # REGRA: Não enviar aos domingos (6 é domingo)
    if agora.weekday() == 6:
        print("Hoje é domingo, pulando envio.")
        return

    token = os.getenv('TELEGRAM_TOKEN')
    chat_id = os.getenv('CHAT_ID')
    hora_atual = agora.hour

    # Define o título conforme seu pedido
    if hora_atual == 19:
        titulo = "📝 *PREVISÃO PARA AMANHÃ (PLANEJAMENTO)*"
    elif hora_atual == 5:
        titulo = "🌅 *STATUS MATINAL DA OBRA*"
    else:
        titulo = f"🕒 *ATUALIZAÇÃO DE ROTINA ({hora_atual}h)*"

    mensagem = f"{titulo}\n\n"

    for cidade, coord in CIDADES.items():
        try:
            # URL do Open-Meteo (Melhor precisão para o Brasil)
            url = f"https://api.open-meteo.com/v1/forecast?latitude={coord['lat']}&longitude={coord['lon']}&current=temperature_2m,rain&hourly=precipitation_probability,rain&timezone=America%2FSao_Paulo&forecast_days=2"
            res = requests.get(url).json()

            if hora_atual == 19:
                # Previsão para amanhã (24h a frente da hora atual)
                indice = 24 + hora_atual
                temp = res['hourly']['temperature_2m'][indice] if 'temperature_2m' in res['hourly'] else "N/A"
                chuva_mm = res['hourly']['rain'][indice]
                prob = res['hourly']['precipitation_probability'][indice]
            else:
                # Tempo real agora
                temp = res['current']['temperature_2m']
                chuva_mm = res['current']['rain']
                prob = res['hourly']['precipitation_probability'][hora_atual]

            # Lógica do Asfalto: 20mm inviabiliza (conforme seu PDF)
            if chuva_mm >= 20:
                status = "🔴 ALERTA: CHUVA PESADA"
            elif chuva_mm > 0.2:
                status = "🟡 ATENÇÃO: CHUVA LEVE"
            else:
                status = "✅ LIBERADO"

            mensagem += f"📍 *{cidade}*\n"
            mensagem += f"🌡️ {temp}°C | 🌧️ {chuva_mm}mm | 📊 Prob: {prob}%\n"
            mensagem += f"📢 Status: {status}\n\n"
        
        except Exception as e:
            mensagem += f"📍 *{cidade}*: Erro ao obter dados.\n\n"

    # Enviar para o Telegram
    url_tel = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url_tel, data={"chat_id": chat_id, "text": mensagem, "parse_mode": "Markdown"})

if __name__ == "__main__":
    check_weather()
