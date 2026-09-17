"""Record constructor shared by the Biblio-VSE v2 extension files."""


def A(id_muestra, meta_regla, tipo_artefacto, archivo, etiqueta, escenario, contenido,
      adv=None, note=None):
    rec = {
        "id_muestra": id_muestra,
        "meta_regla": meta_regla,
        "tipo_artefacto": tipo_artefacto,
        "archivo": archivo,
        "escenario": escenario,
        "origen": "extension_v2",
    }
    if adv:
        rec["adversarial"] = adv
        rec["adversarial_nota"] = note
    rec["contenido_texto"] = contenido
    rec["etiqueta_clase"] = etiqueta
    return rec
