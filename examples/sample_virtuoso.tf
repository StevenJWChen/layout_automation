;; Sample Virtuoso Technology File
;; Format: Cadence Virtuoso
;; Process: 180nm CMOS

;;=========================================================================
;; Layer Definitions
;;=========================================================================
layerDefinitions(
    techLayerPurposePriorities(
        "nwell"     "drawing"   1
        "pwell"     "drawing"   2
        "ndiff"     "drawing"   3
        "pdiff"     "drawing"   4
        "poly"      "drawing"   5
        "contact"   "drawing"   6
        "metal1"    "drawing"   7
        "via1"      "drawing"   8
        "metal2"    "drawing"   9
        "via2"      "drawing"   10
        "metal3"    "drawing"   11
    )
)

;;=========================================================================
;; Stream Layers (GDS Layer Mapping)
;;=========================================================================
streamLayers(
    ("nwell"    "drawing"   1   0)
    ("pwell"    "drawing"   2   0)
    ("ndiff"    "drawing"   3   0)
    ("pdiff"    "drawing"   4   0)
    ("poly"     "drawing"   10  0)
    ("contact"  "drawing"   20  0)
    ("metal1"   "drawing"   30  0)
    ("via1"     "drawing"   40  0)
    ("metal2"   "drawing"   50  0)
    ("via2"     "drawing"   60  0)
    ("metal3"   "drawing"   70  0)
)

;;=========================================================================
;; Display Resources (Colors)
;;=========================================================================
drDefineDisplay(
    techLayerProperties(
        "nwell"     "drawing"
        color "green"
        fillStyle "stipple"
    )
    techLayerProperties(
        "pwell"     "drawing"
        color "pink"
        fillStyle "stipple"
    )
    techLayerProperties(
        "ndiff"     "drawing"
        color "lime"
        fillStyle "solid"
    )
    techLayerProperties(
        "pdiff"     "drawing"
        color "tan"
        fillStyle "solid"
    )
    techLayerProperties(
        "poly"      "drawing"
        color "red"
        fillStyle "solid"
    )
    techLayerProperties(
        "contact"   "drawing"
        color "black"
        fillStyle "solid"
    )
    techLayerProperties(
        "metal1"    "drawing"
        color "blue"
        fillStyle "solid"
    )
    techLayerProperties(
        "via1"      "drawing"
        color "gray"
        fillStyle "solid"
    )
    techLayerProperties(
        "metal2"    "drawing"
        color "magenta"
        fillStyle "solid"
    )
    techLayerProperties(
        "via2"      "drawing"
        color "silver"
        fillStyle "solid"
    )
    techLayerProperties(
        "metal3"    "drawing"
        color "cyan"
        fillStyle "solid"
    )
)
