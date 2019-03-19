import os

import intake
import pandas as pd
import pytest
import xarray as xr

from intake_esm import config
from intake_esm.core import ESMMetadataStoreCatalog

here = os.path.abspath(os.path.dirname(__file__))


def test_build_collection():
    with config.set({'database-directory': './tests/test_collections'}):
        collection_input_file = os.path.join(here, 'collection_input_test.yml')
        col = intake.open_esm_metadatastore(
            collection_input_file=collection_input_file, overwrite_existing=True
        )
        assert isinstance(col.df, pd.DataFrame)

        with pytest.raises(ValueError):
            col = intake.open_esm_metadatastore(
                collection_input_file=collection_input_file,
                collection_name='cesm_dple',
                collection_type='cesm',
            )


def test_build_collection_cesm1_le():
    with config.set({'database-directory': './tests/test_collections'}):
        collection_input_file = os.path.join(here, 'cesm1-le_collection-input.yml')
        col = intake.open_esm_metadatastore(
            collection_input_file=collection_input_file, overwrite_existing=True
        )
        assert isinstance(col.df, pd.DataFrame)

        with pytest.raises(ValueError):
            col = intake.open_esm_metadatastore(
                collection_input_file=collection_input_file,
                collection_name='cesm_dple',
                collection_type='cesm',
            )


@pytest.mark.parametrize('collection', ['cesm_dple_test_collection'])
def test_constructor(collection):
    with config.set({'database-directory': './tests/test_collections'}):
        c = intake.open_esm_metadatastore(collection_name=collection, collection_type='cesm')
        assert isinstance(c, ESMMetadataStoreCatalog)


def test_search():
    with config.set({'database-directory': './tests/test_collections'}):
        c = intake.open_esm_metadatastore(
            collection_name='cesm_dple_test_collection', collection_type='cesm'
        )
        cat = c.search(variable='O2', direct_access=True)

        assert isinstance(cat.query_results, pd.DataFrame)
        assert not cat.query_results.empty


def test_cat():
    with config.set({'database-directory': './tests/test_collections'}):
        cat = intake.open_catalog(os.path.join(here, 'cesm_catalog.yaml'))
        cat = cat['cesm_dple_test_collection_7afe8a3a-8d2f-40a8-9ede-899f48ce83b2']
        assert isinstance(cat.query_results, pd.DataFrame)


@pytest.mark.parametrize(
    'chunks, expected_chunks',
    [
        ({'member_id': 1, 'time': 100, 'nlat': 2, 'nlon': 2}, (1, 100, 2, 2)),
        ({'member_id': 1, 'time': 200, 'nlat': 1, 'nlon': 1}, (1, 200, 1, 1)),
    ],
)
def test_to_xarray_cesm(chunks, expected_chunks):
    with config.set({'database-directory': './tests/test_collections'}):
        c = intake.open_esm_metadatastore(collection_name='cesm1-le', collection_type='cesm')
        cat = c.search(
            variable=['STF_O2', 'SHF'],
            ensemble=[1, 3, 9],
            experiment=['20C', 'RCP85'],
            direct_access=True,
        )
        ds = cat.to_xarray(chunks=chunks)
        assert ds['SHF'].data.chunksize == expected_chunks
