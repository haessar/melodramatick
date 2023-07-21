# Quick start
1. Activate virtualenv from root directory: `source venv/bin/activate`
2. Manually add composers matching `compile_<composer>_operas.py` in the Composers admin panel, ensuring surname matches explicitly.
4. Manually import each `<composer>_operas.csv` using the Operas admin panel.
5. Run through cells in `compile_lists` notebook. Import the .csv files as instructed in [Output CSVs](#output-csvs).
6. Run through cells in `update_spotify_links` notebook. Import the .csv files as instructed in [Output CSVs](#output-csvs).

# Output CSVs

Each notebook outputs at least one csv. I will describe here what they are for. Each `_operas.csv` or `_composers.csv` can be imported via Operas or Composers admin panel, respectively, **but will first need to be manually filled in**:
* ``<composer>_operas.csv: `` From each `compile_<composer>_operas` notebook. Table of a given composer's complete operatic works.
* ``compile_lists_missing_composers.csv: `` From `compile_lists` notebook. Composers whose operas are found in any of the "top lists" who aren't contained in the database.
* ``misc_operas.csv: `` From `compile_lists` notebook. Operas found in any of the "top lists" that aren't contained in database. Any opera belonging to a composer not yet added (see previous point) will NOT be included here.
* ```update_spotify_links_missing_composers.csv: ``` From `update_spotify_links` notebook. Composers whose operas are found in any suitably formatted Spotify playlist who aren't contained in the database.
* ``playlist_operas.csv: `` From `update_spotify_links` notebook. Operas found in any suitably formatted Spotify playlist that aren't contained in the database. Any opera belonging to a composer not yet added (see previous point) will NOT be included here.
