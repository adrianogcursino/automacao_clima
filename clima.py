import requests
import os
from datetime import datetime, timedelta
import pytz
import json

CIDADES = {
    "Jaqueira/PE": {"lat": -8.72, "lon": -35.80},
    "Flexeiras/AL": {"lat": -9.26, "lon": -35.71},
    "Palmeira dos Índios/AL": {"lat": -9.40, "lon": -36.62},
    "Ibateguara/AL": {"lat": -8.97, "lon": -35.93},
    "Maceió/AL": {"lat": -9.66, "lon": -35.73},
    "Capela/AL": {"lat": -9.40, "lon": -36.07}
}

def get_weather_data(lat, lon):
    # Adicionamos humidade relativa (relative_humidity_2m) para o índice de cura
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,rain&daily=precipitation_sum,precipitation_probability_max&timezone=America%2FSao_Paulo&models=ecmwf_ifs04,gfs_seamless"
    return requests.get(url).json()

def check_weather():
    fuso = pytz.timezone('America/Sao_Paulo')
    agora = datetime.now(fuso)
    hora_atual = agora.hour
    dia_semana = agora.weekday()

    if dia_semana == 6 and hora_atual != 19:
        return

    if (hora_atual > 18 or hora_atual < 5) and hora_atual != 19:
        return

    token = os.getenv('TELEGRAM_TOKEN')
    chat_id = os.getenv('CHAT_ID')

    if hora_atual == 19:
        titulo = "📊 *PLANEAMENTO SEMANAL E RISCO*"
    else:
        titulo = f"🚦 *STATUS OPERACIONAL ({hora_atual}h)*"

    mensagem_final = f"{titulo}\n\n"

    for cidade, coord in CIDADES.items():
        try:
            res = get_weather_data(coord['lat'], coord['lon'])
            
            if hora_atual == 19:
                mensagem_final += f"📍 *{cidade}*\n"
                for i in range(1, 8):
                    data_str = (agora + timedelta(days=i)).strftime('%d/%m')
                    chuva = res['daily']['precipitation_sum'][i]
                    prob = res['daily']['precipitation_probability_max'][i]
                    
                    if chuva >= 15: icone = "🔴"
                    elif chuva > 0: icone = "🟡"
                    else: icone = "🟢"
                    
                    mensagem_final += f"{icone} {data_str}: {chuva}mm ({prob}%)\n"
                mensagem_final += "\n"
            else:
                temp = res['current']['temperature_2m']
                humidade = res['current']['relative_humidity_2m']
                chuva = res['current']['rain']
                
                # Lógica do Semáforo
                if chuva >= 15:
                    status = "🔴 *PARALISAR: CHUVA PESADA*"
                elif chuva > 0 or humidade > 85:
                    status = "🟡 *ATENÇÃO: CHUVA OU HUMIDADE ALTA*"
                else:
                    status = "🟢 *LIBERADO: CONDIÇÕES IDEAIS*"
                
                mensagem_final += f"📍 *{cidade}*\n🌡️ {temp}°C | 💧 Hum: {humidade}%\n🌧️ Chuva: {chuva}mm\n📢 {status}\n\n"

        except Exception as e:
            mensagem_final += f"📍 *{cidade}*: Erro na leitura.\n\n"

    # --- SUGESTÃO 4: BOTÕES DE RADAR ---
    # Criamos um botão que abre o radar focado na região das obras (Windy)
    radar_url = "https://www.windy.com/-9.400/-36.000?rain,-9.400,-36.000,9"
    
    keyboard = {
        "inline_keyboard": [[
            {"text": "📡 Ver Radar em Tempo Real", "url": radar_url}
        ]]
    }

    url_tel = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id, 
        "text": mensagem_final, 
        "parse_mode": "Markdown",
        "reply_markup": json.dumps(keyboard)
    }
    
    requests.post(url_tel, data=payload)

if __name__ == "__main__":
    check_weather()
