# Public input provenance

Retrieved/checked 2026-11-10. Saved edge lists suffice for every experiment;
no download is required to repeat the analysis. All fixtures are simple,
undirected and unweighted. No edges were dropped from Florentine or dolphins,
and neither has isolates. Numeric relabeling is bijective; see `manifest.json`.
These small historical examples are convenience cases, not a representative sample.

| Fixture | Definition and primary attribution | Processing |
| --- | --- | --- |
| `karate.edgelist` | Zachary, *An Information Flow Model for Conflict and Fission in Small Groups*, J. Anthropological Research 33 (1977), 452–473. [NetworkX social generator](https://networkx.org/documentation/networkx-3.5/_modules/networkx/generators/social.html). | Existing project fixture; all 34 nodes and 78 edges; interaction weights omitted. 45 triangles. |
| `florentine.edgelist` | Marriage ties, 15 families and 20 ties. [NetworkX 3.5 generator](https://networkx.org/documentation/networkx-3.5/reference/generated/networkx.generators.social.florentine_families_graph.html), citing Padgett & Ansell, *Robust Action and the Rise of the Medici, 1400–1434*, American Journal of Sociology 98 (1993), 1259–1319. | Generated with pinned NetworkX 3.5; uses its 15-node subset, not a claim that no other families existed. 3 triangles. |
| `dolphins.edgelist` | Lusseau et al., *The bottlenose dolphin community of Doubtful Sound features a large proportion of long-lasting associations*, Behavioral Ecology and Sociobiology 54 (2003), 396–405. [Newman data page](https://websites.umich.edu/~mejn/netdata/), [source archive](https://websites.umich.edu/~mejn/netdata/dolphins.zip). | Parse `dolphins.gml`, retain all 62 nodes and 159 association edges. No further thresholding or symmetrizing. 95 triangles. The association criterion belongs to the original study. |

The Newman page offers its datasets for scientific use and requests original
citations; it is not a general-purpose software license. That permission and
scientific attribution apply to the dolphin fixture. No broader rights are
asserted. NetworkX is BSD-3-Clause; its notice is in `NETWORKX_LICENSE.txt`.

`manifest.json` records the downloaded archive SHA-256, derived file hashes,
original label map, retrieval date and NetworkX version. The manifest was made
by `prepare_data.py`. To recreate the derived inputs from source, from
`graph-sampling/`:

```sh
mkdir -p work
curl -L --fail https://websites.umich.edu/~mejn/netdata/dolphins.zip -o work/dolphins.zip
work/venv/bin/python prepare_data.py work/dolphins.zip
```

Compare the archive hash with the saved manifest BEFORE regeneration if the
upstream file changes. The data-preparation command intentionally replaces the
two derived edge lists and manifest; it does not touch karate.
