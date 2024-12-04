from flask import Flask, request, jsonify, render_template
import openai
import os
from dotenv import load_dotenv
from flask_cors import CORS

# Cargar las variables de entorno
load_dotenv()

# Configuración de Flask
app = Flask(__name__)
CORS(app)

# Configurar la clave API de OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Ruta para servir el frontend
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para el chatbot
@app.route('/chatbot', methods=['POST'])
def chatbot():
    try:
        # Obtener el mensaje del usuario desde el frontend
        data = request.get_json()
        user_message = data.get('message', '').strip()

        if not user_message:
            return jsonify({'reply': 'Por favor, envía un mensaje válido.'}), 400

        # Llamar a OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Puedes cambiar a gpt-4 si está disponible
            messages=[
                {"role": "system", "content": "Eres un asistente médico experto en diagnosticar síntomas."},
                {"role": "user", "content": user_message}
            ],
            max_tokens=150,
            temperature=0.7
        )

        # Obtener la respuesta del modelo
        reply = response['choices'][0]['message']['content'].strip()
        return jsonify({'reply': reply}), 200

    except Exception as e:
        return jsonify({'reply': f'Error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
