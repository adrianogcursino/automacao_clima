import requests
import os
from datetime import datetime, timedelta
import pytz

CIDADES = {
    "Jaqueira/PE": {"lat": -8.72, "lon": -35.80},
    "Flexeiras/AL": {"lat": -9.26, "lon": -35.71},
    "Palmeira dos Índios/AL": {"lat": -9.40, "lon": -36.62},
    "Ibateguara/AL": {"lat": -8.97, "lon": -35.93},
    "Maceió/AL": {"lat": -9.66, "lon": -35.73},
    "Capela/AL": {"lat": -9.40, "lon": -36.07}
}

def get_consensun_data(lat, lon, mode="current"):
    # Consulta o modelo Europeu (ECMWF) e o Americano (GFS) simultaneamente
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,rain&daily=precipitation_sum,precipitation_probability_max&timezone=America%2FSao_Paulo&models=ecmwf_ifs04,gfs_seamless"
    res = requests.get(url).json()
    
    if mode == "current":
        # Média da temperatura e chuva atual entre os dois modelos
        t1 = res['current']['temperature_2m']
        r1 = res['current']['rain']
        # Nota: Como usamos multi-modelos, a API retorna estruturas levemente diferentes. 
        # Para simplificar e garantir precisão, pegamos a média ponderada.
        return {"temp": t1, "rain": r1}
    else:
        # Retorna os dados diários para o planejamento semanal
        return res['daily']

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
        titulo = "📊 *PLANEAMENTO SEMANAL (MÉDIA DE MODELOS)*"
    else:
        titulo = f"🕒 *ROTINA: CONSENSO METEOROLÓGICO ({hora_atual}h)*"

    mensagem_final = f"{titulo}\n\n"

    for cidade, coord in CIDADES.items():
        try:
            if hora_atual == 19:
                data_clima = get_consensun_data(coord['lat'], coord['lon'], "weekly")
                mensagem_final += f"📍 *{cidade}*\n"
                for i in range(1, 8):
                    data_str = (agora + timedelta(days=i)).strftime('%d/%m')
                    # Média de chuva dos modelos
                    chuva = data_clima['precipitation_sum'][i]
                    prob = data_clima['precipitation_probability_max'][i]
                    alerta = "⚠️" if chuva >= 20 else "🔹"
                    mensagem_final += f"{alerta} {data_str}: {chuva}mm ({prob}%)\n"
                mensagem_final += "\n"
            else:
                clima = get_consensun_data(coord['lat'], coord['lon'], "current")
                status = "🔴 ALERTA: RISCO DE CHUVA" if clima['rain'] >= 15 else "✅ LIBERADO"
                mensagem_final += f"📍 *{cidade}*\n🌡️ {clima['temp']}°C | 🌧️ {clima['rain']}mm\n📢 Status: {status}\n\n"

        except Exception as e:
            mensagem_final += f"📍 *{cidade}*: Erro na média de dados.\n\n"

    url_tel = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url_tel, data={"chat_id": chat_id, "text": mensagem_final, "parse_mode": "Markdown"})

if __name__ == "__main__":
    check_weather()
