import base64
import io

import matplotlib.pyplot as plt


class EmptyFigure(Exception):
    pass


def to_bytes_fig(f):
    """
    Decorator to convert plot to bytes object
    """
    def wrapped(*args, **kwargs):
        fig, ax = plt.subplots(figsize=kwargs.pop("figsize", (8, 4)))
        try:
            f(ax, *args, **kwargs)
        except EmptyFigure:
            return
        flike = io.BytesIO()
        fig.savefig(flike, bbox_inches="tight")
        return base64.b64encode(flike.getvalue()).decode()

    return wrapped
