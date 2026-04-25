import requests
import os
from datetime import datetime, timedelta
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
    hora_atual = agora.hour
    dia_semana = agora.weekday() # 6 é Domingo

    # --- REGRAS DE HORÁRIO ---
    
    # 1. Se for Domingo e NÃO for 19h, não envia nada.
    if dia_semana == 6 and hora_atual != 19:
        print("Domingo: Apenas o planeamento das 19h será enviado.")
        return

    # 2. Bloqueia atualizações de rotina após as 18h e antes das 05h
    # (Exceto o horário das 19h que é o planeamento)
    if (hora_atual > 18 or hora_atual < 5) and hora_atual != 19:
        print(f"Fora do horário de operação ({hora_atual}h).")
        return

    token = os.getenv('TELEGRAM_TOKEN')
    chat_id = os.getenv('CHAT_ID')

    if hora_atual == 19:
        titulo = "📅 *PLANEAMENTO SEMANAL (PRÓXIMOS 7 DIAS)*"
    elif hora_atual == 5:
        titulo = "🌅 *STATUS MATINAL DA OBRA*"
    else:
        titulo = f"🕒 *ATUALIZAÇÃO DE ROTINA ({hora_atual}h)*"

    mensagem_final = f"{titulo}\n\n"

    for cidade, coord in CIDADES.items():
        try:
            # Open-Meteo: Dados diários para os 7 dias e atuais para rotina
            url = f"https://api.open-meteo.com/v1/forecast?latitude={coord['lat']}&longitude={coord['lon']}&daily=precipitation_sum,precipitation_probability_max&current=temperature_2m,rain&timezone=America%2FSao_Paulo&forecast_days=8"
            res = requests.get(url).json()

            if hora_atual == 19:
                # MODO SEMANAL (7 dias à frente)
                mensagem_final += f"📍 *{cidade}*\n"
                for i in range(1, 8):
                    data = (agora + timedelta(days=i)).strftime('%d/%m')
                    chuva = res['daily']['precipitation_sum'][i]
                    prob = res['daily']['precipitation_probability_max'][i]
                    alerta = "⚠️" if chuva >= 20 else "🔹"
                    mensagem_final += f"{alerta} {data}: {chuva}mm ({prob}%)\n"
                mensagem_final += "\n"
            else:
                # MODO ROTINA (Das 05h às 18h)
                temp = res['current']['temperature_2m']
                chuva_mm = res['current']['rain']
                # Regra do PDF: 20mm inviabiliza asfalto
                status = "🔴 ALERTA: CHUVA" if chuva_mm >= 20 else "✅ LIBERADO"
                mensagem_final += f"📍 *{cidade}*\n🌡️ {temp}°C | 🌧️ {chuva_mm}mm\n📢 Status: {status}\n\n"

        except Exception as e:
            mensagem_final += f"📍 *{cidade}*: Erro nos dados.\n\n"

    # Enviar para o Telegram
    url_tel = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url_tel, data={"chat_id": chat_id, "text": mensagem_final, "parse_mode": "Markdown"})

if __name__ == "__main__":
    check_weather()
