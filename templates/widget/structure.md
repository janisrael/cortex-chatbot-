The widget preview uses:
Main file:
templates/widget/preview.html — rendered by the /demo route
Route:
blueprints/widget.py — /demo route (line 97-126) renders preview.html
Fallback:
templates/widget/demo.html — used only if there's an error loading the preview
Actual widget embed:
templates/widget/widget_embed.html — the embeddable widget used by the /widget route