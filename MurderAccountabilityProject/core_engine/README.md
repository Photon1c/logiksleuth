These scripts are solely for educational and research purposes.

The data sets that they user are 100% open-source, making this repository open-source too.

The PII screening layer is strictly set until more lax parameters are set by users, such as law enforcement agencies (LEAs).

Any limitations of this project is largely due to working outside of paywalls and gatekeeped data access points.

🕵 Instructions

First, ingest the proper data inputs. If you do not have any available, use ```mock_data_generator.py```.

Once input data has been created or saved in /data folder, run ```ucr_converter.py``` to convert incident codes.

Then, run ```python ingest_quickcheck.py data/ucr_incidents.jsonl```, this should give output similar to the output below:

```
Total ingested: 1047185
Research Lake:   1047185
Restricted Vault:0
Quarantine:      0

== Research Lake (showing up to 3) ==
1. status=closed, access=research, linkable=True, geo=county, keys=['access', 'case_status', 'conviction_status', 'county', 'date', 'geo_precision', 'linkable', 'mo_tags']...
2. status=closed, access=research, linkable=True, geo=county, keys=['access', 'case_status', 'conviction_status', 'county', 'date', 'geo_precision', 'linkable', 'mo_tags']...
3. status=closed, access=research, linkable=True, geo=county, keys=['access', 'case_status', 'conviction_status', 'county', 'date', 'geo_precision', 'linkable', 'mo_tags']...

== Restricted Vault (showing up to 3) ==

== Quarantine (showing up to 3) ==

```

These scripts essentially aim to "clean" and weed out PII from out data set. The UCR dataset candidates meet all requirements to proceed with analysis. Future entries can be flagged and discarded per the logic diagram in this project's start ([located here](../media/golden_sparrow.png))
