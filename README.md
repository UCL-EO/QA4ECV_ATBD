# QA4ECV Algorithm Theoretical Basis Document

P.Lewis UCL/NCEO

# Contents

- [Download and sort data](notebooks/Get%20data.ipynb)

In this section, we download the test dataset from the server as a set of `netcdf` files and harmonise most of the labelling across datasets. We also perform narrow to broadband conversion on the MODIS datasets, apply QA masks and do any scaling. 

The result of this is set of `pickle` (storage) `s1.0` (i.e. 'stage 1.0' of processing, which is really just a dump from the netcdf files for a single pixel in time) files containing the original data:

    notebooks/obj/bbdr.flags_s1.0_.pkl
    notebooks/obj/bbdr.meris_s1.0_.pkl
    notebooks/obj/bbdr.vgt_s1.0_.pkl
    notebooks/obj/ga.brdf.merge_s1.0_.pkl
    notebooks/obj/ga.brdf.nosnow_s1.0_.pkl
    notebooks/obj/ga.brdf.snow_s1.0_.pkl
    notebooks/obj/mod09_s1.0_.pkl
    notebooks/obj/myd09_s1.0_.pkl
    notebooks/obj/prior.v2.nosnow_s1.0_.pkl
    notebooks/obj/prior.v2.snow_s1.0_.pkl
    notebooks/obj/prior.v2.snownosnow_s1.0_.pkl
    
and a set of `s2.0` files containing the masked and organised datasets.

    notebooks/obj/bbdr.flags_s2.0_.pkl
    notebooks/obj/bbdr.meris_s2.0_.pkl
    notebooks/obj/bbdr.vgt_s2.0_.pkl
    notebooks/obj/ga.brdf.merge_s2.0_.pkl
    notebooks/obj/ga.brdf.nosnow_s2.0_.pkl
    notebooks/obj/ga.brdf.snow_s2.0_.pkl
    notebooks/obj/mod09_s2.0_.pkl
    notebooks/obj/myd09_s2.0_.pkl
    notebooks/obj/prior.v2.nosnow_s2.0_.pkl
    notebooks/obj/prior.v2.snow_s2.0_.pkl
    notebooks/obj/prior.v2.snownosnow_s2.0_.pkl


- [Load data and and prepare constraint matrices](notebooks/Load%20data.ipynb)

This section reads the data from the `s2.0` files and organises into `s3.0` files, with the data organised as matrices:

    notebooks/obj/bbdr.meris_s3.0_.pkl
    notebooks/obj/bbdr.vgt_s3.0_.pkl
    notebooks/obj/mod09_s3.0_.pkl
    notebooks/obj/myd09_s3.0_.pkl

The `s3.0` files are slimmed down sources of processed information. You can do all of the modelling and inversion with these files alone (other than e.g. comparison with original reflectance data for e.g. outlier detection). They contain *only* the following keys:

    ['kernels', 'weight', 'idoy', 'doy', 'refl', 'year', 'date']
    
which is the critical information for modelling organised appropriately.

In this section, we also prepare matrices for other constraints we might want and the `A` and `b` matrices (full size, sparse representations). At present, these (`Ab` files) are:

    notebooks/obj/D1_Ab_.pkl
    notebooks/obj/D365_Ab_.pkl
    notebooks/obj/bbdr.meris_Ab_.pkl
    notebooks/obj/bbdr.vgt_Ab_.pkl
    notebooks/obj/myd09_Ab_.pkl
    notebooks/obj/mod09_Ab_.pkl
    notebooks/obj/prior.v2.nosnow_Ab_.pkl
    notebooks/obj/prior.v2.snow_Ab_.pkl

The files `D1_Ab` and `D365_Ab` contain differential constraint (sparse) matrices for imposing smoothness in time.


