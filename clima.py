import requests
import os
from datetime import datetime
import pytz

# Configuração de Cidades
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
    hora = agora.hour
    dia_semana = agora.weekday() # 0=Segunda, 6=Domingo

    # REGRA: Não enviar aos domingos
    if dia_semana == 6:
        print("Hoje é domingo. Sem envios conforme solicitado.")
        return

    token = os.getenv('TELEGRAM_TOKEN')
    chat_id = os.getenv('CHAT_ID')
    api_key = os.getenv('WEATHER_KEY')

    # Define o Título da Mensagem
    if hora == 19:
        titulo = "📝 *PREVISÃO PARA AMANHÃ (PLANEJAMENTO)*"
    elif hora == 5:
        titulo = "🌅 *STATUS MATINAL DA OBRA*"
    else:
        titulo = f"🕒 *ATUALIZAÇÃO DE ROTINA ({hora}h)*"

    mensagem = f"{titulo}\n\n"

    for cidade, coord in CIDADES.items():
        if hora == 19:
            # Busca Previsão (Forecast) para amanhã
            url = f"https://api.openweathermap.org/data/2.5/forecast?lat={coord['lat']}&lon={coord['lon']}&appid={api_key}&units=metric&lang=pt_br"
            res = requests.get(url).json()
            item = res['list'][8] # Aproximadamente 24h à frente
            temp = item['main']['temp']
            chuva_prob = item.get('pop', 0) * 100
            chuva_mm = item.get('rain', {}).get('3h', 0)
        else:
            # Busca Tempo Atual
            url = f"https://api.openweathermap.org/data/2.5/weather?lat={coord['lat']}&lon={coord['lon']}&appid={api_key}&units=metric&lang=pt_br"
            res = requests.get(url).json()
            temp = res['main']['temp']
            chuva_mm = res.get('rain', {}).get('1h', 0)
            chuva_prob = "N/A"

        # Lógica de Status (Baseado no seu documento: 20mm inviabiliza)
        status = "🔴 ALERTA: CHUVA PESADA" if (isinstance(chuva_mm, (int, float)) and chuva_mm >= 20) else "✅ LIBERADO"

        mensagem += f"📍 *{cidade}*\n"
        mensagem += f"🌡️ Temp: {temp}°C | 🌧️ Chuva: {chuva_mm}mm\n"
        if hora == 19: mensagem += f"📊 Probabilidade: {chuva_prob:.0f}%\n"
        mensagem += f"📢 Status: {status}\n\n"

    # Envio
    url_tel = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url_tel, data={"chat_id": chat_id, "text": mensagem, "parse_mode": "Markdown"})

if __name__ == "__main__":
    check_weather()
