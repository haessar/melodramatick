# CSV import formats

Melodramatick provides admin CSV imports for composers and works. The importers
expect UTF-8 CSV files with a header row. Header names must match model field
names exactly.

## Composer CSV

Import composers from the Composer admin page using `Import CSV`.

Supported fields:

- `surname` (required): composer's family name.
- `first_name` (required): composer's given name or names.
- `nationality` (required): short nationality label.
- `gender` (required): `M` or `F`.
- `birth_date` (optional): date in `YYYY-MM-DD` format.

Example CSV with birth dates:

```csv
surname,first_name,nationality,gender,birth_date
Tchaikovsky,Pyotr Ilyich,Russian,M,1840-05-07
Prokofiev,Sergei,Russian,M,1891-04-23
```

Composer imports create global composer records. They do not automatically attach
the imported composers to the current site; works can still be imported against
those composers by surname.

## Work CSV

Import works from the generated work admin page, such as Ballets, using
`Import CSV`.

The composer must already exist. The `composer` column should contain the
composer's `surname` exactly as it appears in the composer table.

Required columns:

```csv
composer,title,year
Tchaikovsky,Swan Lake,1876
Prokofiev,Romeo and Juliet,1935
```

Supported base fields:

- `composer` (required): existing composer surname.
- `title` (required): work title.
- `year` (required): composition or publication year.
- `notes` (optional): free text.
- `sub_genre_id` (optional): database ID for an existing subgenre.

Generated tick apps may add their own fields. Include those fields using the
field names from the generated model. For example, if `balletick/models.py`
adds a `choreographer` field to `class Ballet`, include a `choreographer`
column:

```csv
composer,title,year,choreographer
Tchaikovsky,Swan Lake,1876,Marius Petipa
Prokofiev,Romeo and Juliet,1935,Leonid Lavrovsky
```

If every row in a work CSV belongs to the same composer, Melodramatick marks
that composer as `complete` for the current site.

## Notes

- Import composers before importing works.
- Unknown composer surnames cause the work import to stop without importing that
  file.
- Duplicate works are identified by composer and title.
- Related fields other than `composer`, such as `sub_genre`, should use the
  underlying ID column name, for example `sub_genre_id`.
