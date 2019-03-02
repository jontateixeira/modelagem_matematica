import os
import itertools

from ipykernel import kernelspec as ks
import nbformat
from nbformat.v4.nbbase import new_markdown_cell

from generate_contents import NOTEBOOK_DIR, REG, iter_notebooks, get_notebook_title


def prev_this_next(it):
    a, b, c = itertools.tee(it,3)
    next(c)
    return zip(itertools.chain([None], a), b, itertools.chain(c, [None]))


PREV_TEMPLATE = "[<- {title}]({url}) "
CONTENTS = "| [Índice](Indice.ipynb) | [Referências](99.00-Referencias.ipynb) |"
NEXT_TEMPLATE = " [{title} ->]({url})"
NAV_COMMENT = "<!--NAVIGATION-->\n"

COLAB_LINK = """

<a href="https://colab.research.google.com/github/rmsrosa/modelagem_matematica/blob/master/notebooks/{notebook_filename}"><img align="left" src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open in Colab" title="Open and Execute in Google Colaboratory"></a><br>
"""


def iter_navbars():
    for prev_nb, nb, next_nb in prev_this_next(iter_notebooks()):
        navbar = "" # NAV_COMMENT
        if prev_nb:
            navbar += PREV_TEMPLATE.format(title=get_notebook_title(prev_nb),
                                           url=prev_nb)
        navbar += CONTENTS
        if next_nb:
            navbar += NEXT_TEMPLATE.format(title=get_notebook_title(next_nb),
                                           url=next_nb)

        this_colab_link = COLAB_LINK.format(notebook_filename=os.path.basename(nb))
            
        yield os.path.join(NOTEBOOK_DIR, nb), navbar, this_colab_link


def write_navbars():
    for nb_name, navbar, this_colab_link in iter_navbars():
        nb = nbformat.read(nb_name, as_version=4)
        nb_file = os.path.basename(nb_name)
        is_comment = lambda cell: cell.source.startswith(NAV_COMMENT)

        navbar_top = NAV_COMMENT + this_colab_link + "\n" + navbar + "\n\n---\n"
        navbar_bottom = NAV_COMMENT + "\n---\n" + navbar + this_colab_link

        if is_comment(nb.cells[1]):
            print("- amending navbar for {0}".format(nb_file))
            nb.cells[1].source = navbar_top
        else:
            print("- inserting navbar for {0}".format(nb_file))
            nb.cells.insert(1, new_markdown_cell(source=navbar_top))

        if is_comment(nb.cells[-1]):
            nb.cells[-1].source = navbar_bottom
        else:
            nb.cells.append(new_markdown_cell(source=navbar_bottom))
        nbformat.write(nb, nb_name)


if __name__ == '__main__':
    write_navbars()
