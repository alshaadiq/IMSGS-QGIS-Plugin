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
    <h3> Generate Multi-Scaled Grid System</h3>
</div>

Create a vector layer with a grid covering a given extent. The grid is fixed for the Indonesian region by defining Xmin, Xmax, Ymin, Ymax points based on the World Geodetic System 1984 (WGS84) reference system. The resolution can be chosen as required and can be extracted by the size of the input layer. Every grid contains a unique identifier that differentiates between grids.

| Input                                                    | Output                                                     |
| -------------------------------------------------------- | ---------------------------------------------------------- |
| ![Input Image](/icons/ToolExample/InputGenerateGrid.png) | ![Output Image](/icons/ToolExample/OutputGenerateGrid.png) |

<div style="display: flex; align-items: center;">
    <img src="/icons/populdist.png" alt="LOGO!" style="width: 100px; height: 100px; margin-right: 20px; scale : 0.75">
    <h3> Distribute Populations to Grid</h3>
</div>

Obtain the population distribution for each grid. The population distribution depends on the grid, road type, road length, land cover type, and administrative boundary data containing population information. The weighting of road and land cover data is filled in manually/freely by the user. The results of the population distribution calculation are then used to calculate the water and food demand for each grid.

<table>
  <tr>
    <th>Layer</th>
    <th>Attribute Table</th>
    <th>Output</th>
  </tr>
  <tr>
    <td>IMSGS</td>
    <td>IMGSID</td>
    <td rowspan="4"><img class="output-image" src="/icons/ToolExample/PopulOutput.png" alt="Output Image"></td>
  </tr>
  <tr>
    <td>Land Cover</td>
    <td>Land Cover Type’s Weight</td>
    <td></td>
  </tr>
  <tr>
    <td>Road</td>
    <td>Road Type’s Weight</td>
    <td></td>
  </tr>
  <tr>
    <td>Administrative Boundaries</td>
    <td>Population</td>
    <td></td>
  </tr>
</table>
