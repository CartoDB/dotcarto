# Replace datasets on a .carto file

## Usage:

Assuming there is a .carto file called `my_carto_file.carto` that came as the result of exporting a visualization with (at least) one layer that came from dataset `customers` and another layer that came from a `providers` dataset, you can replace those datasets with `customers_new` and `providers_new` as follows:

```python
from dotcarto import DotCartoFile

carto_file = DotCartoFile("my_carto_file.carto")

carto_file.replace_dataset("customers", "customers_new")
carto_file.replace_dataset("providers", "providers_new")

carto_file.get_new()
```

The new .carto file will be found in the same folder as `my_carto_file.carto`, with the name `NEW_my_carto_file.carto`.

## Caveats

* `customers_new` and `providers_new` must be existing datasets on the CARTO account at the time of generating the new .carto file
* `customers_new` and `providers_new` must have the same structure as `customers_new` and `providers_new`, otherwise the visualization will not render.
* When the new .carto file is uploaded, if `customers_new` and `providers_new` exist on the target CARTO account, they will be respected, if not, they will be created alongside with the visualization.
