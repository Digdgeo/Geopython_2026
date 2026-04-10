# Claude Code — Instalación y primeros pasos

[Claude Code](https://claude.ai/code) es el CLI oficial de Anthropic para usar Claude directamente desde la terminal o tu editor de código. Te permite chatear con Claude, editar archivos, ejecutar comandos y mucho más sin salir del entorno de trabajo.

---

## Requisitos previos

- Node.js 18 o superior ([descargar](https://nodejs.org/))
- Una cuenta en [claude.ai](https://claude.ai) o una API key de [Anthropic](https://console.anthropic.com/)

---

## Instalación

```bash
npm install -g @anthropic-ai/claude-code
```

Verifica que se instaló correctamente:

```bash
claude --version
```

---

## Autenticación

Lanza Claude Code por primera vez y sigue el flujo de login:

```bash
claude
```

Se abrirá el navegador para autenticarte con tu cuenta de Anthropic. Una vez autenticado, vuelves a la terminal y ya puedes usarlo.

---

## Uso básico

Desde cualquier directorio de tu proyecto, lanza:

```bash
claude
```

Algunos ejemplos de lo que puedes pedirle:

```
> Explícame qué hace este script
> Añade una función que lea un GeoJSON y devuelva el bounding box
> Arregla el error de la línea 42
> Haz un commit con los cambios de hoy
```

Claude tiene acceso a tus archivos y puede leerlos, editarlos y ejecutar comandos (siempre pidiéndote confirmación antes de acciones importantes).

---

## Integración con VS Code

Instala la extensión **Claude Code** desde el marketplace de VS Code, o lanza Claude Code desde la terminal integrada del editor. Verás los cambios aplicarse directamente en el editor.

---

## Más información

- Documentación oficial: [docs.anthropic.com/claude-code](https://docs.anthropic.com/en/docs/claude-code/overview)
- Repositorio y issues: [github.com/anthropics/claude-code](https://github.com/anthropics/claude-code)
