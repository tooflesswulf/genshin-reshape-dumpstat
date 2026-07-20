"""Build the final infographic page.

Inlines the six PNGs (light + dark variant per figure) into
infographic-template.html as base64 data URIs so reshape-infographic.html
is a single self-contained shareable file.

Run:  python build_infographic.py
(Regenerate the charts first with make_image1.py / make_image2.py /
make_image3.py.)
"""
import base64
import pathlib

HERE = pathlib.Path(__file__).parent
IMAGES = {
    '{{IMG1}}': 'Image1-reshape-probs.png',
    '{{IMG1D}}': 'Image1-reshape-probs-dark.png',
    '{{IMG2}}': 'Image2-guarantee-vs-thr.png',
    '{{IMG2D}}': 'Image2-guarantee-vs-thr-dark.png',
    '{{IMG3}}': 'Image3-guarantees-cmp.png',
    '{{IMG3D}}': 'Image3-guarantees-cmp-dark.png',
    '{{IMG-DUST}}': 'Item_Dust_of_Enlightenment.png',
}


def main():
    html = (HERE / 'infographic-template.html').read_text()
    for placeholder, fname in IMAGES.items():
        b64 = base64.b64encode((HERE / fname).read_bytes()).decode()
        html = html.replace(placeholder, f'data:image/png;base64,{b64}')
    out = HERE / 'reshape-infographic.html'
    out.write_text(html)
    print(f'wrote {out.name} ({out.stat().st_size:,} bytes)')


if __name__ == '__main__':
    main()
