# TSX-File-Downloader
Python script that allows searching and downloading of files from the TSX Supersites repository

Requires user to have made a free account with TSX Supersites at https://sso.eoc.dlr.de/supersites/

All search parameters are now contained with a file seperate to the code: config.json.
The following paramters need to be set there:

1. Specify the supersite you want to search. e.g. the Latin America supersite is found at https://download.geoservice.dlr.de/supersites/files/LatinAmerica/.
So set the parameter *url* to "https://download.geoservice.dlr.de/supersites/files/"
and the parameter *supersite* to "LatinAmerica"

2. Set the path to the directory you want to download to in the parameter *dir*.

3. Specify the Orbit Number and BeamID you want to search for in the parameters *orbit* and *beam_id*.

4. Set the date range you want to search over using the parameters *start* and *end*.

5. Specify your Username and Password for TSX Supersites in the variables *user* and *password*.

If there are files that match that search they will then be downloaded.
