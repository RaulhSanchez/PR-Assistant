import os
from autoreadme.llm import get_provider

def test_gemini():
    print("Testing Gemini Provider...")
    # La API key ya está en el .env, get_provider la pillará
    try:
        llm = get_provider(provider="gemini")
        response = llm.chat("Dí hola en una línea para probar que funcionas.")
        print(f"Respuesta de Gemini: {response}")
    except Exception as e:
        print(f"Error con Gemini: {e}")

if __name__ == "__main__":
    test_gemini()
