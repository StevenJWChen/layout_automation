;*******************************************************************
;* NCSU FreePDK45 Technology File (Sample)
;* 45nm CMOS Process
;*
;* This is a sample technology file in Cadence Virtuoso format
;* Based on FreePDK45 open-source PDK structure
;*******************************************************************

;; Technology Name
techParams(
    techVersion("FreePDK45_sample_v1.4")
    techName("FreePDK45")
    gridResolution(0.005)
    unitTimeName("ns")
    timePrecision(3)
    unitLengthName("micron")
    lengthPrecision(3)
    unitVoltageName("v")
    voltagePrecision(3)
    unitCurrentName("mA")
    currentPrecision(3)
    unitPowerName("pw")
    powerPrecision(3)
    unitResistanceName("ohm")
    resistancePrecision(3)
    unitCapacitanceName("pf")
    capacitancePrecision(3)
    unitInductanceName("nh")
    inductancePrecision(3)
)

;*******************************************************************
;* Layer Definitions
;*******************************************************************
layerDefinitions(
    techLayerPurposePriorities(
        "nwell"     "drawing"   1
        "nwell"     "pin"       2
        "nwell"     "label"     3

        "pwell"     "drawing"   1
        "pwell"     "pin"       2

        "active"    "drawing"   1
        "active"    "pin"       2

        "nimplant"  "drawing"   1
        "pimplant"  "drawing"   1

        "poly"      "drawing"   1
        "poly"      "pin"       2
        "poly"      "label"     3

        "contact"   "drawing"   1

        "metal1"    "drawing"   1
        "metal1"    "pin"       2
        "metal1"    "label"     3

        "via1"      "drawing"   1

        "metal2"    "drawing"   1
        "metal2"    "pin"       2
        "metal2"    "label"     3

        "via2"      "drawing"   1

        "metal3"    "drawing"   1
        "metal3"    "pin"       2
        "metal3"    "label"     3

        "via3"      "drawing"   1

        "metal4"    "drawing"   1
        "metal4"    "pin"       2
        "metal4"    "label"     3

        "via4"      "drawing"   1

        "metal5"    "drawing"   1
        "metal5"    "pin"       2
        "metal5"    "label"     3

        "via5"      "drawing"   1

        "metal6"    "drawing"   1
        "metal6"    "pin"       2
        "metal6"    "label"     3

        "via6"      "drawing"   1

        "metal7"    "drawing"   1
        "metal7"    "pin"       2
        "metal7"    "label"     3

        "via7"      "drawing"   1

        "metal8"    "drawing"   1
        "metal8"    "pin"       2
        "metal8"    "label"     3

        "via8"      "drawing"   1

        "metal9"    "drawing"   1
        "metal9"    "pin"       2
        "metal9"    "label"     3

        "via9"      "drawing"   1

        "metal10"   "drawing"   1
        "metal10"   "pin"       2
        "metal10"   "label"     3
    )
)

;*******************************************************************
;* Stream Layers (GDS-II Layer Numbers)
;*******************************************************************
streamLayers(
    ("nwell"     "drawing"   1   0)
    ("nwell"     "pin"       1   10)
    ("nwell"     "label"     1   5)

    ("pwell"     "drawing"   2   0)
    ("pwell"     "pin"       2   10)

    ("active"    "drawing"   6   0)
    ("active"    "pin"       6   10)

    ("nimplant"  "drawing"   7   0)
    ("pimplant"  "drawing"   8   0)

    ("poly"      "drawing"   9   0)
    ("poly"      "pin"       9   10)
    ("poly"      "label"     9   5)

    ("contact"   "drawing"   10  0)

    ("metal1"    "drawing"   11  0)
    ("metal1"    "pin"       11  10)
    ("metal1"    "label"     11  5)

    ("via1"      "drawing"   12  0)

    ("metal2"    "drawing"   13  0)
    ("metal2"    "pin"       13  10)
    ("metal2"    "label"     13  5)

    ("via2"      "drawing"   14  0)

    ("metal3"    "drawing"   15  0)
    ("metal3"    "pin"       15  10)
    ("metal3"    "label"     15  5)

    ("via3"      "drawing"   16  0)

    ("metal4"    "drawing"   17  0)
    ("metal4"    "pin"       17  10)
    ("metal4"    "label"     17  5)

    ("via4"      "drawing"   18  0)

    ("metal5"    "drawing"   19  0)
    ("metal5"    "pin"       19  10)
    ("metal5"    "label"     19  5)

    ("via5"      "drawing"   20  0)

    ("metal6"    "drawing"   21  0)
    ("metal6"    "pin"       21  10)
    ("metal6"    "label"     21  5)

    ("via6"      "drawing"   22  0)

    ("metal7"    "drawing"   23  0)
    ("metal7"    "pin"       23  10)
    ("metal7"    "label"     23  5)

    ("via7"      "drawing"   24  0)

    ("metal8"    "drawing"   25  0)
    ("metal8"    "pin"       25  10)
    ("metal8"    "label"     25  5)

    ("via8"      "drawing"   26  0)

    ("metal9"    "drawing"   27  0)
    ("metal9"    "pin"       27  10)
    ("metal9"    "label"     27  5)

    ("via9"      "drawing"   28  0)

    ("metal10"   "drawing"   29  0)
    ("metal10"   "pin"       29  10)
    ("metal10"   "label"     29  5)
)

;*******************************************************************
;* Display Resources (Layer Colors and Patterns)
;*******************************************************************
drDefineDisplay(
    techLayerProperties(
        "nwell"     "drawing"
        color       "green"
        fillStyle   "stipple"
        lineStyle   "solid"
        packet      "stipple10"
    )
    techLayerProperties(
        "nwell"     "pin"
        color       "green"
        fillStyle   "outline"
        lineStyle   "solid"
    )

    techLayerProperties(
        "pwell"     "drawing"
        color       "pink"
        fillStyle   "stipple"
        lineStyle   "solid"
        packet      "stipple10"
    )
    techLayerProperties(
        "pwell"     "pin"
        color       "pink"
        fillStyle   "outline"
        lineStyle   "solid"
    )

    techLayerProperties(
        "active"    "drawing"
        color       "brown"
        fillStyle   "solid"
        lineStyle   "solid"
    )
    techLayerProperties(
        "active"    "pin"
        color       "brown"
        fillStyle   "outline"
        lineStyle   "solid"
    )

    techLayerProperties(
        "nimplant"  "drawing"
        color       "lime"
        fillStyle   "dots"
        lineStyle   "solid"
    )
    techLayerProperties(
        "pimplant"  "drawing"
        color       "tan"
        fillStyle   "dots"
        lineStyle   "solid"
    )

    techLayerProperties(
        "poly"      "drawing"
        color       "red"
        fillStyle   "solid"
        lineStyle   "solid"
    )
    techLayerProperties(
        "poly"      "pin"
        color       "red"
        fillStyle   "outline"
        lineStyle   "solid"
    )

    techLayerProperties(
        "contact"   "drawing"
        color       "black"
        fillStyle   "X"
        lineStyle   "solid"
    )

    techLayerProperties(
        "metal1"    "drawing"
        color       "blue"
        fillStyle   "solid"
        lineStyle   "solid"
    )
    techLayerProperties(
        "metal1"    "pin"
        color       "blue"
        fillStyle   "outline"
        lineStyle   "solid"
    )

    techLayerProperties(
        "via1"      "drawing"
        color       "gray"
        fillStyle   "X"
        lineStyle   "solid"
    )

    techLayerProperties(
        "metal2"    "drawing"
        color       "magenta"
        fillStyle   "solid"
        lineStyle   "solid"
    )
    techLayerProperties(
        "metal2"    "pin"
        color       "magenta"
        fillStyle   "outline"
        lineStyle   "solid"
    )

    techLayerProperties(
        "via2"      "drawing"
        color       "silver"
        fillStyle   "X"
        lineStyle   "solid"
    )

    techLayerProperties(
        "metal3"    "drawing"
        color       "cyan"
        fillStyle   "solid"
        lineStyle   "solid"
    )
    techLayerProperties(
        "metal3"    "pin"
        color       "cyan"
        fillStyle   "outline"
        lineStyle   "solid"
    )

    techLayerProperties(
        "via3"      "drawing"
        color       "gray"
        fillStyle   "X"
        lineStyle   "solid"
    )

    techLayerProperties(
        "metal4"    "drawing"
        color       "orange"
        fillStyle   "solid"
        lineStyle   "solid"
    )
    techLayerProperties(
        "metal4"    "pin"
        color       "orange"
        fillStyle   "outline"
        lineStyle   "solid"
    )

    techLayerProperties(
        "via4"      "drawing"
        color       "silver"
        fillStyle   "X"
        lineStyle   "solid"
    )

    techLayerProperties(
        "metal5"    "drawing"
        color       "yellow"
        fillStyle   "solid"
        lineStyle   "solid"
    )
    techLayerProperties(
        "metal5"    "pin"
        color       "yellow"
        fillStyle   "outline"
        lineStyle   "solid"
    )

    techLayerProperties(
        "via5"      "drawing"
        color       "gray"
        fillStyle   "X"
        lineStyle   "solid"
    )

    techLayerProperties(
        "metal6"    "drawing"
        color       "purple"
        fillStyle   "solid"
        lineStyle   "solid"
    )
    techLayerProperties(
        "metal6"    "pin"
        color       "purple"
        fillStyle   "outline"
        lineStyle   "solid"
    )

    techLayerProperties(
        "via6"      "drawing"
        color       "silver"
        fillStyle   "X"
        lineStyle   "solid"
    )

    techLayerProperties(
        "metal7"    "drawing"
        color       "navy"
        fillStyle   "solid"
        lineStyle   "solid"
    )
    techLayerProperties(
        "metal7"    "pin"
        color       "navy"
        fillStyle   "outline"
        lineStyle   "solid"
    )

    techLayerProperties(
        "via7"      "drawing"
        color       "gray"
        fillStyle   "X"
        lineStyle   "solid"
    )

    techLayerProperties(
        "metal8"    "drawing"
        color       "maroon"
        fillStyle   "solid"
        lineStyle   "solid"
    )
    techLayerProperties(
        "metal8"    "pin"
        color       "maroon"
        fillStyle   "outline"
        lineStyle   "solid"
    )

    techLayerProperties(
        "via8"      "drawing"
        color       "silver"
        fillStyle   "X"
        lineStyle   "solid"
    )

    techLayerProperties(
        "metal9"    "drawing"
        color       "olive"
        fillStyle   "solid"
        lineStyle   "solid"
    )
    techLayerProperties(
        "metal9"    "pin"
        color       "olive"
        fillStyle   "outline"
        lineStyle   "solid"
    )

    techLayerProperties(
        "via9"      "drawing"
        color       "gray"
        fillStyle   "X"
        lineStyle   "solid"
    )

    techLayerProperties(
        "metal10"   "drawing"
        color       "gold"
        fillStyle   "solid"
        lineStyle   "solid"
    )
    techLayerProperties(
        "metal10"   "pin"
        color       "gold"
        fillStyle   "outline"
        lineStyle   "solid"
    )
)
