try:
    from . import agent
except ImportError:
    # google-adk not installed yet; tools can still be imported directly
    pass
