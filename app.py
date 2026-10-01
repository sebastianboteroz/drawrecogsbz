import os
import base64
import numpy as np
import streamlit as st
from PIL import Image
from openai import OpenAI

# ==========================================
# CONFIGURACIÓN DE PÁGINA Y ESTILOS PASTEL
# ==========================================
st.set_page_config(
    page_title="Diario Mágico de Princesas 👑✨",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados (Pastel Pink Minimalista)
st.markdown("""
<style>
    /* Fondo general rosado crema tenue */
    .stApp {
        background-color: #FFF9FA;
    }
    
    /* Banner Principal */
    .princess-header {
        background: linear-gradient(135deg, #FDE2E4 0%, #FFCAD4 50%, #B5E2FA 100%);
        padding: 2.2rem 2.5rem;
        border-radius: 20px;
        color: #4A4A4A;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 20px rgba(255, 202, 212, 0.35);
    }
    
    .princess-header h1 {
        color: #6D597A !important;
        font-weight: 800;
        font-size: 2.3rem;
        margin-bottom: 0.4rem;
    }
    
    .princess-header p {
        color: #7A6C7D;
        font-size: 1.1rem;
        margin: 0;
    }

    /* Barra lateral */
    div[data-testid="stSidebar"] {
        background-color: #FFF0F3 !important;
        border-right: 1px solid #FFCCD5;
    }

    /* Contenedor de la historia */
    .story-card {
        background-color: #FFFFFF;
        border: 1px solid #FFCCD5;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 12px rgba(255, 182, 193, 0.15);
    }

    /* Botón Mágico Rosa */
    .stButton>button {
        background: linear-gradient(90deg, #FFB3C1 0%, #FF8FA3 100%);
        color: #FFFFFF !important;
        font-weight: 700;
        font-size: 1rem;
        padding: 0.65rem 2rem;
        border-radius: 12px;
        border: none;
        width: 100%;
        transition: all 0.2s ease;
        box-shadow: 0 4px 10px rgba(255, 143, 163, 0.3);
    }
    
    .stButton>button:hover {
        opacity: 0.95;
        transform: translateY(-1px);
        box-shadow: 0 6px 14px rgba(255, 143, 163, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# Intento de importación segura para el Canvas
try:
    from streamlit_drawable_canvas import st_canvas
except ImportError:
    st.error("Por favor instala 'streamlit-drawable-canvas' en tu archivo requirements.txt")

# ==========================================
# BARRA LATERAL (HERRAMIENTAS DE DIBUJO)
# ==========================================
with st.sidebar:
    st.markdown("## 🏰 El Reino Encantado")
    st.caption("Configura tu varita mágica para empezar a crear.")
    
    st.markdown("---")
    
    st.subheader("🔑 Autenticación")
    ke = st.text_input(
        "Clave de API de OpenAI", 
        type="password",
        placeholder="sk-...",
        help="Tu API Key es necesaria para redactar el cuento."
    )
    
    if ke:
        os.environ['OPENAI_API_KEY'] = ke
        st.success("¡Varita Vinculada!", icon="✨")
    else:
        st.warning("Ingresa tu API Key para continuar.", icon="👑")

    st.markdown("---")
    
    st.subheader("🎨 Pinceles Reales")
    stroke_width = st.slider('Ancho de línea:', 1, 20, 4)
    stroke_color = st.color_picker("Color de trazo", "#6D597A")  # Morado pastel suave
    bg_color = st.color_picker("Color de lienzo", "#FFFFFF")     # Blanco limpio

# ==========================================
# CUERPO PRINCIPAL
# ==========================================
st.markdown("""
<div class="princess-header">
    <h1>El Lienzo Mágico de las Princesas 👑🌸</h1>
    <p>Dibuja una corona, una princesa, un castillo o un amuleto secreto... ¡y la IA escribirá su historia!</p>
</div>
""", unsafe_allow_html=True)

col_canvas, col_story = st.columns([1, 1.2], gap="large")

with col_canvas:
    st.subheader("🖼️ Tu Boceto Real")
    
    # Lienzo de dibujo con dimensiones controladas
    canvas_result = st_canvas(
        fill_color="rgba(255, 182, 193, 0.2)",
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        background_color=bg_color,
        height=320,
        width=420,
        drawing_mode="freedraw",
        key="princess_canvas",
    )
    
    st.caption("✍️ Dibuja libremente en el panel blanco superior.")
    analyze_button = st.button("✨ Crear Cuento de Hadas")

with col_story:
    st.subheader("📖 La Fábula de tu Dibujo")
    
    if analyze_button:
        if not ke:
            st.warning("⚠️ Por favor ingresa tu API Key en la barra lateral.")
        elif canvas_result.image_data is None:
            st.warning("⚠️ Dibuja algo en el panel antes de presionar el botón.")
        else:
            try:
                with st.spinner("✨ Los duendes mágicos están redactando la historia..."):
                    # Procesar imagen del Canvas
                    input_numpy_array = np.array(canvas_result.image_data)
                    input_image = Image.fromarray(input_numpy_array.astype('uint8'), 'RGBA')
                    
                    # Convertir a RGB para guardar como PNG limpio
                    rgb_image = Image.new("RGB", input_image.size, (255, 255, 255))
                    rgb_image.paste(input_image, mask=input_image.split()[3])
                    rgb_image.save('princess_img.png')

                    # Codificar imagen a Base64
                    with open('princess_img.png', "rb") as img_file:
                        base64_image = base64.b64encode(img_file.read()).decode("utf-8")

                    # Inicializar cliente de OpenAI
                    client = OpenAI(api_key=ke)

                    prompt_text = (
                        "Eres un escritor talentoso de cuentos infantiles de princesas y fantasía. "
                        "Observa detenidamente el dibujo en la imagen (que es un boceto hecho por un niño o niña). "
                        "Identifica qué elementos se dibujaron (una princesa, un castillo, una corona, un animal mágico, etc.) "
                        "y escribe un cuento mágico, dulce y fascinante en español. "
                        "Usa emojis de fantasía (👑, 🦄, ✨, 🌸) y dale un título hermoso al cuento."
                    )

                    messages = [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt_text},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/png;base64,{base64_image}"
                                    }
                                },
                            ],
                        }
                    ]

                    # Generación en tiempo real (Streaming)
                    message_placeholder = st.empty()
                    full_response = ""

                    stream = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=messages,
                        max_tokens=700,
                        stream=True
                    )

                    for chunk in stream:
                        if chunk.choices[0].delta.content is not None:
                            full_response += chunk.choices[0].delta.content
                            message_placeholder.markdown(full_response + "▌")

                    # Presentación final en tarjeta estilizada
                    message_placeholder.markdown(f'<div class="story-card">{full_response}</div>', unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Ocurrió un error al generar la historia: {e}")
    else:
        st.info("🌸 Haz un dibujo en el lienzo y presiona **'Crear Cuento de Hadas'** para ver la magia.")
