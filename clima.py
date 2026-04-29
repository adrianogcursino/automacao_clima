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

def check_weather():
    fuso = pytz.timezone('America/Sao_Paulo')
    agora = datetime.now(fuso)
    hora = agora.hour
    dia_semana = agora.weekday()

    # Bloqueio de Domingo (exceto as mensagens de planejamento para segunda)
    if dia_semana == 6 and hora not in [19, 20]:
        return

    token = os.getenv('TELEGRAM_TOKEN')
    chat_id = os.getenv('CHAT_ID')

    # Definição do Tipo de Mensagem
    if hora == 19:
        titulo = "📊 *PLANEJAMENTO SEMANAL (7 DIAS)*"
    elif hora == 20:
        titulo = "🚀 *FOCO AMANHÃ: PREVISÃO DETALHADA*"
    else:
        titulo = f"🚦 *STATUS OPERACIONAL ({hora}h)*"

    mensagem_final = f"{titulo}\n\n"

    for cidade, coord in CIDADES.items():
        try:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={coord['lat']}&longitude={coord['lon']}&current=temperature_2m,relative_humidity_2m,rain&daily=precipitation_sum,precipitation_probability_max&timezone=America%2FSao_Paulo&forecast_days=8"
            res = requests.get(url).json()
            
            if hora == 19:
                # MODO 7 DIAS
                mensagem_final += f"📍 *{cidade}*\n"
                for i in range(1, 8):
                    d = (agora + timedelta(days=i)).strftime('%d/%m')
                    c = res['daily']['precipitation_sum'][i]
                    p = res['daily']['precipitation_probability_max'][i]
                    icone = "🔴" if c >= 15 else ("🟡" if c > 0.5 else "🟢")
                    mensagem_final += f"{icone} {d}: {c}mm ({p}%)\n"
                mensagem_final += "\n"
                
            elif hora == 20:
                # MODO DIA SEGUINTE
                c_amanha = res['daily']['precipitation_sum'][1]
                p_amanha = res['daily']['precipitation_probability_max'][1]
                status = "🔴 ALERTA" if c_amanha >= 15 else "🟢 LIBERADO"
                mensagem_final += f"📍 *{cidade}* (Amanhã)\n🌧️ {c_amanha}mm | 📊 Prob: {p_amanha}%\n📢 {status}\n\n"
                
            else:
                # MODO ROTINA (06h às 16h)
                temp = res['current']['temperature_2m']
                hum = res['current']['relative_humidity_2m']
                chuva = res['current']['rain']
                status = "🔴 *PARALISAR*" if chuva >= 15 else ("🟡 *RISCO*" if (chuva > 0.5 or hum > 85) else "🟢 *OK*")
                mensagem_final += f"📍 *{cidade}*\n🌡️ {temp}°C | 💧 Hum: {hum}%\n🌧️ {chuva}mm | 📢 {status}\n\n"

        except:
            mensagem_final += f"📍 *{cidade}*: Erro na leitura.\n\n"

    # Botão de Radar
    kb = {"inline_keyboard": [[{"text": "📡 Ver Radar Tempo Real", "url": "https://www.windy.com/-9.400/-36.000?rain,-9.400,-36.000,9"}]]}
    requests.post(f"https://api.telegram.org/bot{token}/sendMessage", 
                  data={"chat_id": chat_id, "text": mensagem_final, "parse_mode": "Markdown", "reply_markup": json.dumps(kb)})

if __name__ == "__main__":
    check_weather()
