# jiajun-gao.github.io

Personal website of Jiajun Gao (高嘉骏), live at https://jiajun-gao.github.io.

Plain HTML, CSS, and JavaScript with no framework. The `.html` pages at the top level are
generated, so edit the sources in `_source/` and rebuild:

    python3 build.py _source .

- `_source/pages/` holds the content of each page
- `_source/nav.html` and `_source/footer.html` are shared by every page
- `_source/assets/` holds the stylesheet, script, and photo; the build copies them to `assets/`
