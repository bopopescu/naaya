# zope imports
from BTrees.IIBTree import weightedIntersection

# naaya imports
from Products.NaayaCore.GeoMapTool import clusters
from Products.NaayaCore.GeoMapTool.clusters_catalog import (
        _apply_index_with_range_dict_results, getObjectFromCatalog)

def filter_rids(catalog_tool, filters):
    ret = None

    for index_id in catalog_tool._catalog.indexes.keys():
        index = catalog_tool._catalog.getIndex(index_id)
        r = index._apply_index(filters)
        if r is not None:
            r, _ = r
            _, ret = weightedIntersection(ret, r)

    return ret



