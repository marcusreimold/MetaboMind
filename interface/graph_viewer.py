from __future__ import annotations

import tkinter as tk
from typing import Any

import networkx as nx


class Tooltip:
    """Simple tooltip for canvas items."""

    def __init__(self, widget: tk.Widget) -> None:
        self.widget = widget
        self._tip: tk.Toplevel | None = None

    def show(self, text: str, x: int, y: int) -> None:
        self.hide()
        self._tip = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.geometry(f"+{x+10}+{y+10}")
        label = tk.Label(tw, text=text, background="lightyellow", relief=tk.SOLID, borderwidth=1)
        label.pack()

    def hide(self, _event: Any | None = None) -> None:
        if self._tip:
            self._tip.destroy()
            self._tip = None

    def bind(self, item: int, text: str) -> None:
        self.widget.tag_bind(item, "<Enter>", lambda e, t=text: self.show(t, e.x_root, e.y_root))
        self.widget.tag_bind(item, "<Leave>", self.hide)


class GraphViewer(tk.Frame):
    """Canvas widget to display a knowledge graph with zoom and scroll."""

    def __init__(self, parent: tk.Widget, graph: nx.MultiDiGraph) -> None:
        super().__init__(parent)
        self.graph = graph
        self.canvas = tk.Canvas(self, background="white")
        self.hbar = tk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.vbar = tk.Scrollbar(self, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=self.hbar.set, yscrollcommand=self.vbar.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.hbar.grid(row=1, column=0, sticky="ew")
        self.vbar.grid(row=0, column=1, sticky="ns")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.tooltip = Tooltip(self.canvas)
        self.canvas.bind("<MouseWheel>", self._on_zoom)
        self.canvas.bind("<ButtonPress-1>", self._on_drag_start)
        self.canvas.bind("<B1-Motion>", self._on_drag_move)
        self._scale = 1.0

        self._drag_start: tuple[int, int] | None = None

    def draw(self) -> None:
        self.canvas.delete("all")
        if len(self.graph) == 0:
            return
        pos = nx.spring_layout(self.graph, seed=42)
        for node, (x, y) in pos.items():
            r = 20
            item = self.canvas.create_oval(x * 300 - r, y * 300 - r, x * 300 + r, y * 300 + r, fill="lightblue")
            self.tooltip.bind(item, str(node))
            self.canvas.create_text(x * 300, y * 300, text=node)
        for u, v, data in self.graph.edges(data=True):
            x1, y1 = pos[u]
            x2, y2 = pos[v]
            item = self.canvas.create_line(x1 * 300, y1 * 300, x2 * 300, y2 * 300, arrow=tk.LAST)
            rel = data.get("relation", "")
            tip = f"{u} --{rel}--> {v}" if rel else f"{u} -> {v}"
            self.tooltip.bind(item, tip)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_zoom(self, event: tk.Event) -> None:
        factor = 1.1 if event.delta > 0 else 0.9
        self.canvas.scale("all", self.canvas.canvasx(event.x), self.canvas.canvasy(event.y), factor, factor)
        self._scale *= factor
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_drag_start(self, event: tk.Event) -> None:
        """Remember starting coordinates for panning."""
        self._drag_start = (event.x, event.y)
        self.canvas.scan_mark(event.x, event.y)

    def _on_drag_move(self, event: tk.Event) -> None:
        """Scroll canvas while mouse is dragged."""
        self.canvas.scan_dragto(event.x, event.y, gain=1)

