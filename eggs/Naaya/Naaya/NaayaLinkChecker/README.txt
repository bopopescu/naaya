This product checks if the links from a Naaya based site are (still) valid.
Both external (absolute) and internal links are checked.


Internal links checking
-----------------------

Only the part describing the path of the internal link is checked. The query
and the fragment are ignored. E.g.:
 - "subsections/water/victoria_lake" becomes "subsections/water/victoria_lake"
 - "/search?term=Naaya#results" becomes "/search"

The advantage of this kind of checking is speed, but on the other hand
some possible errors won't be cought. For example if the previous search
method has a bug and the server returns "500 Internal Server Error", this
error won't be cought.
