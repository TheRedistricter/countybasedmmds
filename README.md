# countybasedmmds
Create optimal (hopefully) multi-member congressional districts using county-like entities.

Uses metis graph partitioning: https://metis.readthedocs.io/en/latest/ which was installed in Anaconda3 using "conda install metis".

Uses code from https://www.geeksforgeeks.org/find-all-combinations-that-adds-upto-given-number-2/ to find all numbers that sum to a given number.

Uses us_state_abbrev.py from https://gist.github.com/rogerallen/1583593.

Uses mdutils for Markdown generation: https://mdutils.readthedocs.io/en/latest/overview.html which was installed using "python3 -m pip install mdutils"

Uses the county adjacency, and county population files from the US Census Bureau. The county populations are estimates for 2019. The county adjaceny file was editted to remove a few inconsistencies.

Uses the current (2020) census reapportionment from the US Census Bureau.  
