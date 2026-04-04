"""
generator.py — README generator using Jinja2 + LLM RAG.
"""
from __future__ import annotations

import os

from jinja2 import Environment, FileSystemLoader

from .analyzer import ProjectData
from .llm.base import LLMProvider

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")
DEFAULT_TEMPLATE = "README_template.md"


def _build_context_texts(data: ProjectData) -> list[str]:
    """Build a flat list of context snippets for RAG prompts."""
    texts = []
    for folder, files in data.folders_summary.items():
        for f in files:
            if f.get("error"):
                continue
            texts.append(
                f"{folder}/{os.path.basename(f['file'])} ({f.get('language','?')}):\n"
                f"  Funciones: {', '.join(f.get('functions', [])[:10])}\n"
                f"  Clases: {', '.join(f.get('classes', [])[:10])}\n"
                f"  Resumen: {f.get('narrative', '')[:300]}"
            )
    if data.dependencies:
        texts.append("Dependencias runtime: " + ", ".join(data.dependencies[:30]))
    if data.dev_dependencies:
        texts.append("Dependencias dev: " + ", ".join(data.dev_dependencies[:20]))
    if data.language_summary:
        lang_str = ", ".join(f"{lang}: {count} archivos" for lang, count in data.language_summary.items())
        texts.append(f"Lenguajes detectados: {lang_str}")
    return texts


def _generate_architecture_diagram(context_texts: list[str], project_name: str, llm: LLMProvider) -> str:
    prompt = (
        f"Analiza el proyecto '{project_name}' y genera un diagrama ASCII profesional "
        f"que represente su arquitectura: capas, módulos, dependencias y flujo de datos. "
        f"Usa solo caracteres ASCII. Sé conciso y claro."
    )
    return llm.rag_chat(prompt, context_texts)


def _enrich_routes(routes: list[dict], llm: LLMProvider) -> list[dict]:
    """Add LLM-generated description to each route."""
    enriched = []
    for route in routes:
        context = [
            f"Ruta: {route.get('method', '?')} {route.get('path', '?')}",
            f"Archivo: {route.get('file', '?')}",
        ]
        description = llm.rag_chat(
            f"Explica brevemente el propósito técnico de la ruta "
            f"{route.get('method', '?')} {route.get('path', '?')}.",
            context,
        )
        enriched.append({**route, "description": description})
    return enriched


def generate_readme(
    data: ProjectData,
    output_path: str,
    llm: LLMProvider,
    template_filename: str = DEFAULT_TEMPLATE,
    enrich_routes: bool = True,
) -> str:
    """
    Generate a README.md file from ProjectData using an LLM and Jinja2 template.

    Args:
        data: Structured project data from analyze_project().
        output_path: Where to write the final README.md.
        llm: An initialized LLMProvider instance.
        template_filename: Jinja2 template filename inside autoreadme/templates/.
        enrich_routes: Whether to generate LLM descriptions for each route.

    Returns:
        The rendered README string.
    """
    def _safe_basename(path) -> str:
        try:
            return os.path.basename(str(path))
        except Exception:
            return str(path) if path else ""

    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
    env.filters["basename"] = _safe_basename  # {{ f.file | basename }}
    template = env.get_template(template_filename)

    context_texts = _build_context_texts(data)

    # Architecture diagram
    architecture_ascii = _generate_architecture_diagram(context_texts, data.name, llm)

    # Elaborated intro
    elaborated_intro = llm.rag_chat(
        f"Genera un resumen técnico exhaustivo del proyecto '{data.name}' "
        f"detallando su arquitectura, propósito, módulos principales y dependencias clave.",
        context_texts,
    )

    # Route enrichment (optional, costs LLM calls)
    routes = _enrich_routes(data.routes, llm) if enrich_routes and data.routes else data.routes

    # Deduplicate connections
    seen_connections = set()
    unique_connections: list[dict] = []
    for c in data.connections:
        key = (c.get("type"), c.get("file"))
        if key not in seen_connections:
            seen_connections.add(key)
            unique_connections.append(c)

    readme_md = template.render(
        name=data.name,
        description=data.description,
        elaborated_intro=elaborated_intro,
        architecture_ascii=architecture_ascii,
        folders=data.folders_summary,
        dependencies=data.dependencies,
        dev_dependencies=data.dev_dependencies,
        routes=routes,
        connections=unique_connections,
        docker_section=data.docker,
        k8s_section=data.k8s,
        k8s_resources_explained={k: v for k, v in data.k8s.items()},
        language_summary=data.language_summary,
        db_analysis="",  # Reserved for future SQL-deep analysis
    )

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(readme_md)

    return readme_md


def generate_pr_companion_report(
    project_path: str,
    llm: LLMProvider,
    base_branch: str = "main",
) -> str:
    """Generate a Pull Request Companion report."""
    from .git_utils import get_git_diff, get_changed_files, get_file_content_at_rev
    from .differ import analyze_changes
    import os

    diff = get_git_diff(base_branch)
    changed_files = get_changed_files(base_branch)
    
    reports = []
    breaking_changes = []
    
    for fp in changed_files:
        full_path = os.path.join(project_path, fp)
        if not os.path.exists(full_path): continue
        
        with open(full_path, "r", encoding="utf-8") as f:
            new_content = f.read()
            
        old_content = get_file_content_at_rev(fp, base_branch)
        
        if old_content:
            report = analyze_changes(fp, old_content, new_content)
            reports.append(report)
            if report.is_breaking:
                for bc in report.signature_changes:
                    breaking_changes.append(f"Firma cambiada: {fp} -> {bc}")
                for func in report.removed_functions:
                    breaking_changes.append(f"Función ELIMINADA: {fp} -> {func}")

    # LLM summary
    summary = llm.rag_chat(
        "Actúa como un experto revisor de código. Analiza el siguiente DIFF y genera un resumen ejecutivo conciso. "
        "REGLAS CRÍTICAS: 1) Prohibido el uso de lenguaje especulativo o dubitativo (evita 'es posible', 'tal vez', 'seguramente'). "
        "2) Si el diff no contiene información suficiente para explicar un cambio, limítate a describir lo que ves sin inventar motivos. "
        "3) Sé directo, técnico y 100% factual.",
        [f"Diff:\n{diff[:3000]}"]
    )
    
    # LLM test suggestions
    test_suggestions = llm.rag_chat(
        "Eres un ingeniero de QA Senior experto en testing unitario y de integración. "
        "Analiza el DIFF y sugiere casos de prueba EXACTOS y con fundamentos lógicos claros. "
        "REGLAS CRÍTICAS: 1) No des consejos genéricos de testing. 2) Cada sugerencia debe estar vinculada directamente a una línea o función modificada. "
        "3) Si no hay suficiente información para sugerir un test útil y específico, responde 'No hay suficiente contexto en el diff para sugerencias específicas'. "
        "4) Elimina cualquier rastro de duda o lenguaje vago.",
        [f"Diff:\n{diff[:3000]}"]
    )
    
    # Build report
    report_md = [
        f"# 🤖 PR Companion\n",
        f"## 📋 Resumen del Pull Request\n",
        f"{summary}\n",
    ]
    
    if breaking_changes:
        report_md.append(f"## ⚠️ Detección de Breaking Changes\n")
        for bc in breaking_changes:
            report_md.append(f"- **ALERTA:** {bc}\n")
        report_md.append("\n")
        
    report_md.append(f"## 🧪 Sugerencias de Tests\n")
    report_md.append(f"{test_suggestions}\n")
    
    return "\n".join(report_md)
