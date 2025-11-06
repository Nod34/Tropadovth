# Minimal stub to avoid ModuleNotFoundError on platforms where the C-extension audioop is missing.
# Only use this if your bot NÃO usa funcionalidades de voz/áudio em tempo de execução.
# Module-level __getattr__ (PEP 562) fornece mensagens de erro claras se alguma função for chamada.
def __getattr__(name):
    raise RuntimeError("audioop is not available in this environment. Voice/audio features are disabled.")

# Common audioop function names — raise clear errors if used
def rms(*args, **kwargs): raise RuntimeError("audioop.rms not available")
def add(*args, **kwargs): raise RuntimeError("audioop.add not available")
def bias(*args, **kwargs): raise RuntimeError("audioop.bias not available")
def max(*args, **kwargs): raise RuntimeError("audioop.max not available")
def min(*args, **kwargs): raise RuntimeError("audioop.min not available")
def avg(*args, **kwargs): raise RuntimeError("audioop.avg not available")
def find(*args, **kwargs): raise RuntimeError("audioop.find not available")
def reverse(*args, **kwargs): raise RuntimeError("audioop.reverse not available")
def lin2lin(*args, **kwargs): raise RuntimeError("audioop.lin2lin not available")
def ratecv(*args, **kwargs): raise RuntimeError("audioop.ratecv not available")

# Tentar importar audioop/voice sem crashar no startup
try:
    import audioop
except Exception:
    audioop = None  # ou deixar sem uso; comandos de voz devem checar isso antes de rodar

# Se tiver imports de discord.voice, proteja assim:
try:
    from discord import VoiceClient
except Exception:
    VoiceClient = None
