"""
Extract a minimal nav-graph JSON (nodes + edges) from a .vsdx file,
bypassing the vsdx library's verbose Shape/Cell object model.

Usage:
    python vsdx_to_navgraph.py wireframe.vsdx > navgraph.json
    python vsdx_to_navgraph.py wireframe.vsdx --page "Page-1"   # only one page
"""
import sys
import json
import zipfile
import re
from xml.etree import ElementTree as ET

NS = {"v": "http://schemas.microsoft.com/office/visio/2012/main"}


def load_page_xmls(vsdx_path):
    """Return {page_name: xml_bytes} for every page in the vsdx."""
    pages = {}
    with zipfile.ZipFile(vsdx_path) as z:
        # map page file -> friendly name via pages.xml (visio/pages/pages.xml)
        rel_names = {}
        try:
            pages_xml = z.read("visio/pages/pages.xml")
            root = ET.fromstring(pages_xml)
            for page in root.findall("v:Page", NS):
                name = page.get("Name")
                rel_id = page.get("RelID") or page.find("v:Rel", NS)
                # fallback: order-based mapping if RelID absent
            # Simpler: just enumerate pageN.xml files in order pages.xml lists them
        except KeyError:
            pass

        page_files = sorted(
            [n for n in z.namelist() if re.match(r"visio/pages/page\d+\.xml$", n)]
        )
        for i, pf in enumerate(page_files, start=1):
            pages[f"page{i}"] = z.read(pf)
    return pages


def extract_nodes_and_edges(page_xml_bytes):
    root = ET.fromstring(page_xml_bytes)

    # --- 1. shape id -> text label (only shapes that actually carry text) ---
    node_text = {}
    for shape in root.iter("{http://schemas.microsoft.com/office/visio/2012/main}Shape"):
        shape_id = shape.get("ID")
        text_el = shape.find("v:Text", NS)
        if text_el is not None:
            text = "".join(text_el.itertext()).strip()
            if text:
                node_text[shape_id] = text

    # --- 2. Connects section -> pair Begin/End rows per connector ---
    connects_el = root.find("v:Connects", NS)
    edges = []
    if connects_el is not None:
        by_connector = {}
        for c in connects_el.findall("v:Connect", NS):
            connector_id = c.get("FromSheet")   # the connector shape itself
            target_id = c.get("ToSheet")        # the node shape it's attached to
            from_cell = c.get("FromCell", "")    # "BeginX" or "EndX"
            by_connector.setdefault(connector_id, {})
            if from_cell.startswith("Begin"):
                by_connector[connector_id]["from"] = target_id
            elif from_cell.startswith("End"):
                by_connector[connector_id]["to"] = target_id

        for connector_id, ends in by_connector.items():
            src, dst = ends.get("from"), ends.get("to")
            if src and dst:
                edges.append(
                    {
                        "from": node_text.get(src, f"UNLABELED_{src}"),
                        "to": node_text.get(dst, f"UNLABELED_{dst}"),
                        "from_id": src,
                        "to_id": dst,
                    }
                )

    nodes = [{"id": sid, "label": txt} for sid, txt in node_text.items()]
    return nodes, edges


def main():
    if len(sys.argv) < 2:
        print("usage: python vsdx_to_navgraph.py file.vsdx [--page pageN]", file=sys.stderr)
        sys.exit(1)

    vsdx_path = sys.argv[1]
    want_page = None
    if "--page" in sys.argv:
        want_page = sys.argv[sys.argv.index("--page") + 1]

    pages = load_page_xmls(vsdx_path)

    result = {}
    for page_name, xml_bytes in pages.items():
        if want_page and page_name != want_page:
            continue
        nodes, edges = extract_nodes_and_edges(xml_bytes)
        result[page_name] = {"nodes": nodes, "edges": edges}

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
