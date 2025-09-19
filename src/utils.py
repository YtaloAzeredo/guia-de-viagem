"""
Utilitários para exibição e formatação no terminal.
"""

import os
from typing import Any

# Configuração para evitar warnings
os.environ["TOKENIZERS_PARALLELISM"] = "false"

try:
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.panel import Panel
    from rich.text import Text
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# Console global
console = Console() if RICH_AVAILABLE else None


def print_markdown(text: str, title: str = None) -> None:
    """
    Renderiza e exibe texto markdown no terminal de forma bonita.
    
    Args:
        text: Texto em formato markdown
        title: Título opcional para o painel
    """
    if not RICH_AVAILABLE:
        # Fallback para terminais sem Rich
        print(f"\n{'='*60}")
        if title:
            print(f"{title.upper()}")
            print("="*60)
        print(text)
        print("="*60)
        return
    
    # Renderiza com Rich
    try:
        md = Markdown(text)
        if title:
            panel = Panel(md, title=f"[bold blue]{title}[/bold blue]", 
                         border_style="bright_blue")
            console.print(panel)
        else:
            console.print(md)
    except Exception as e:
        # Fallback em caso de erro
        print(f"Erro ao renderizar markdown: {e}")
        print(text)


def print_info(message: str, style: str = "info") -> None:
    """
    Exibe mensagem informativa com estilo.
    
    Args:
        message: Mensagem a ser exibida
        style: Estilo da mensagem (info, success, warning, error)
    """
    if not RICH_AVAILABLE:
        print(f"[{style.upper()}] {message}")
        return
    
    styles = {
        "info": "blue",
        "success": "green", 
        "warning": "yellow",
        "error": "red"
    }
    
    style_color = styles.get(style, "white")
    console.print(f"[{style_color}]{message}[/{style_color}]")


def print_header(title: str) -> None:
    """Exibe cabeçalho estilizado."""
    if not RICH_AVAILABLE:
        print(f"\n{'='*60}")
        print(f"{title.center(60)}")
        print("="*60)
        return
    
    text = Text(title, style="bold magenta", justify="center")
    panel = Panel(text, border_style="magenta")
    console.print("\n", panel)


def print_separator() -> None:
    """Exibe separador visual."""
    if not RICH_AVAILABLE:
        print("-" * 60)
        return
    
    console.print("-" * 80, style="dim")


def display_response(response: dict, query: str) -> None:
    """
    Exibe a resposta do sistema de forma formatada.
    
    Args:
        response: Resposta do sistema
        query: Consulta original do usuário
    """
    print_separator()
    print_header("🤖 RESPOSTA DO GUIA DE VIAGEM")
    
    # Exibe a consulta
    print_info(f"📝 Sua pergunta: {query}", "info")
    print_separator()
    
    # Exibe o resultado
    if response.get("success"):
        # Determina o tipo de resposta
        if "itinerary" in response:
            print_markdown(response["itinerary"], "📅 Roteiro de Viagem")
        elif "logistics" in response:
            print_markdown(response["logistics"], "🚗 Informações de Logística")
        elif "local_info" in response:
            print_markdown(response["local_info"], "📍 Informações Locais")
        elif "translation" in response:
            print_markdown(response["translation"], "🗣️ Guia de Tradução")
        elif "response" in response:
            print_markdown(response["response"], "💬 Resposta")
        else:
            # Fallback para qualquer resposta
            content = str(response.get("content", response))
            print_markdown(content, "📋 Informações")
    else:
        # Exibe erro
        error_msg = response.get("error", "Erro desconhecido")
        print_info(f"❌ {error_msg}", "error")
    
    print_separator()