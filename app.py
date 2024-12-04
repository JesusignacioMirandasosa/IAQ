from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import openai
import os
from google.cloud import bigquery

# Configurar Flask y CORS
app = Flask(__name__)
CORS(app)

# Configurar claves y clientes
openai.api_key = os.getenv("OPENAI_API_KEY")
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = './client_secret_539993514787-4g7ljptbpr1r0lreao4kb7itn1e88kia.apps.googleusercontent.com.json'
bigquery_client = bigquery.Client()

# Función para consultar Mimic-IV
def query_mimic(symptom):
    """
    Consulta BigQuery para buscar medicamentos relacionados con un síntoma.
    """
    query = f"""
        SELECT drug_name, dosage
        FROM `physionet-data.mimiciv_derived.prescriptions`
        WHERE LOWER(symptom) LIKE '%{symptom.lower()}%'
        LIMIT 3
    """
    query_job = bigquery_client.query(query)
    results = query_job.result()
    medications = []
    for row in results:
        medications.append(f"{row.drug_name} ({row.dosage})")
    return medications

# Ruta principal para el frontend
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para manejar solicitudes del chatbot
@app.route('/chatbot', methods=['POST'])
def chatbot():
    try:
        # Recibir mensaje del usuario
        data = request.get_json()
        user_message = data.get('message', '').strip()

        if not user_message:
            return jsonify({'reply': 'Por favor, envía un mensaje válido.'}), 400

        # Consultar Mimic-IV
        mimic_reply = "Aquí hay algunos medicamentos relacionados:\n"
        medications = query_mimic(user_message)
        if medications:
            mimic_reply += "\n".join(medications)
        else:
            mimic_reply += "No se encontraron medicamentos relacionados."

        # Llamada a OpenAI para completar la conversación
        openai_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un asistente médico experto que ayuda a diagnosticar síntomas."},
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": mimic_reply}
            ],
            max_tokens=150,
            temperature=0.7
        )
        reply = openai_response['choices'][0]['message']['content'].strip()

        return jsonify({'reply': reply}), 200

    except Exception as e:
        return jsonify({'reply': f'Error: {str(e)}'}), 500

# Ejecutar el servidor
if __name__ == '__main__':
    app.run(debug=True)
