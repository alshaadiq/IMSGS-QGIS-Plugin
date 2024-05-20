<div style="display: flex; align-items: center;">
    <img src="/icons/15.png" alt="LOGO!" style="width: 100px; height: 100px; margin-right: 20px;">
    <h1>Indonesian Multi-scaled Grid System QGIS Plugin</h1>
</div>

---

**IMSGS** is a QGIS plugin that provides comprehensive support for calculating, mapping, and analyzing in a data-driven framework. The main objective of IMSGS is to provide automation of the determination of Indonesia's Environmental Support and Capacity in compliance with the national guidelines of the Ministry of Environment and Forestry.

## List Of Tools

---

<div style="display: flex; align-items: center;">
    <img src="/icons/generategrid.png" alt="LOGO!" style="width: 100px; height: 100px; margin-right: 20px; scale : 0.75">
    <h2> Generate Multi-Scaled Grid System</h2>
</div>

Create a vector layer with a grid covering a given extent. The grid is fixed for the Indonesian region by defining Xmin, Xmax, Ymin, Ymax points based on the World Geodetic System 1984 (WGS84) reference system. The resolution can be chosen as required and can be extracted by the size of the input layer. Every grid contains a unique identifier that differentiates between grids.

| Input                                                    | Output                                                     |
| -------------------------------------------------------- | ---------------------------------------------------------- |
| ![Input Image](/icons/ToolExample/InputGenerateGrid.png) | ![Output Image](/icons/ToolExample/OutputGenerateGrid.png) |

<div style="display: flex; align-items: center;">
    <img src="/icons/populdist.png" alt="LOGO!" style="width: 100px; height: 100px; margin-right: 20px; scale : 0.75">
    <h2> Distribute Populations to Grid</h2>
</div>

Obtain the population distribution for each grid. The population distribution depends on the grid, road type, road length, land cover type, and administrative boundary data containing population information. The weighting of road and land cover data is filled in manually/freely by the user. The results of the population distribution calculation are then used to calculate the water and food demand for each grid.

![Popul](/icons/ToolExample/Popul.png)

## Environmental Carrying Capacity (Water)

<div style="display: flex; align-items: center;">
    <img src="/icons/waterneed.png" alt="LOGO!" style="width: 100px; height: 100px; margin-right: 20px; scale : 0.75">
    <h3>Generate Water Needs Distribution </h3>
</div>

The distribution of water needs in each grid is based on land cover factors based on population and accessibility of a location based on the availability of roads.

<div style="display: flex; align-items: center;">
    <img src="/icons/wateravail.png" alt="LOGO!" style="width: 100px; height: 100px; margin-right: 20px; scale : 0.75">
    <h3>Generate Water Availability Distribution</h3>
</div>

The value of environmental services is determined as a function of the combination of weights and scores of three parameters, namely landscape, land cover, and vegetation type. The value of environmental services in each region will differ based on the determination of the scoring value.

<div style="display: flex; align-items: center;">
    <img src="/icons/waterstatus.png" alt="LOGO!" style="width: 100px; height: 100px; margin-right: 20px; scale : 0.75">
    <h3>Generate Water Need and Capacity Difference and Status </h3>
</div>

Analyze how much of the maximum population can be supported with existing water availability. The threshold determination is carried out with information on the need, availability, and need for water for a decent life (KHL) in the form of a constant. Threshold results were conducted without considering water needs for livestock and industrial activities.

## Environmental Carrying Capacity (Food)

<div style="display: flex; align-items: center;">
    <img src="/icons/enerneed.png" alt="LOGO!" style="width: 100px; height: 100px; margin-right: 20px; scale : 0.75">
    <h3>Generate Energy Needs Distribution </h3>
</div>

The energy needs distribution is determined based on the calculation of the Energy Adequacy Rate (AKE) of the population of each grid for a year.

<div style="display: flex; align-items: center;">
    <img src="/icons/eneravai.png" alt="LOGO!" style="width: 100px; height: 100px; margin-right: 20px; scale : 0.75">
    <h3>Generate Energy Availability Distribution </h3>
</div>

The energy availability distribution is determined with the principle of disagregation with the calculation of distributed Environmental Performance Index.

<div style="display: flex; align-items: center;">
    <img src="/icons/enerstatus.png" alt="LOGO!" style="width: 100px; height: 100px; margin-right: 20px; scale : 0.75">
    <h3>Generate Energy Need and Availability Distribution and Status</h3>
</div>

Analyze how much of the maximum population can be supported with existing food availability. The threshold determination is carried out with information on the need, availability, and need for food for a decent life (KHL) in the form of a constant.
