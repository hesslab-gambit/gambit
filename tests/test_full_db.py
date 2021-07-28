"""
Run a full set of queries using the testdb_210126 database.

Tests in this file will only be run when the --gambit-test-full-db option is passed to the pycharm
command.

Database files and query sequences are located in tests/data/testdb_210126, but only the genome
database file is included in version control. Other files need to be obtained separately. See the
Readme.md file in that directory for more information.
"""

import json
from csv import DictReader

import pytest

from gambit.io.seq import SequenceFile
from gambit.signatures.hdf5 import HDF5Signatures
from gambit.db.gambitdb import GAMBITDatabase
from gambit.db.models import ReferenceGenomeSet
from gambit.query import QueryParams, query_parse
from gambit.cli import cli
from gambit.util.misc import zip_strict
from gambit import __version__ as GAMBIT_VERSION


@pytest.fixture(autouse=True, scope='module')
def testdb_files(request, testdb_dir):
	"""Paths to testdb_210126 files.

	Skips all dependent tests if the --gambit-test-full-db command line option is not passed.

	Checks that the directory and required files/subdirectories exist and fails tests immediately
	if they do not.
	"""
	if not request.config.getoption('gambit_test_full_db'):
		pytest.skip('--gambit-test-full-db option not given')

	files = dict(
		root=testdb_dir,
		db=testdb_dir / 'testdb_210126-genomes.db',
		signatures=testdb_dir / 'testdb_210126-signatures.h5',
		queries=testdb_dir / 'query-seqs/queries.csv',
	)

	for k, v in files.items():
		assert v.exists(), f'Required testdb file not found: {v}'

	return files


@pytest.fixture(scope='module')
def signatures(testdb_files):
	"""K-mer signatures for test genomes."""
	return HDF5Signatures.open(testdb_files['signatures'])


@pytest.fixture(scope='module')
def testdb(testdb_session, signatures):
	"""Full GAMBITDatabase object for test db."""

	with testdb_session() as session:
		gset = session.query(ReferenceGenomeSet).one()
		yield GAMBITDatabase(gset, signatures)


@pytest.fixture(scope='module')
def query_data(testdb_files):
	"""Query files and their expected taxa."""
	table_path = testdb_files['queries']
	seqs_dir = table_path.parent

	files = []
	expected_taxa = []

	with open(table_path, newline='') as f:
		for row in DictReader(f):
			file = SequenceFile(
				path=seqs_dir / (row['name'] + '.fa'),
				format='fasta',
			)
			files.append(file)
			expected_taxa.append(row['expected_taxon'])

	return files, expected_taxa


@pytest.mark.parametrize('classify_strict', [False, True])
def test_query_python(testdb, query_data, classify_strict):
	"""Run a full query using the Python API."""

	query_files, expected_taxa = query_data
	params = QueryParams(classify_strict=classify_strict)

	results = query_parse(testdb, query_files, params)

	assert results.params == params
	assert results.genomeset == testdb.genomeset
	assert results.signaturesmeta == testdb.signatures.meta
	assert results.gambit_version == GAMBIT_VERSION

	for item, file, expected_key in zip_strict(results.items, query_files, expected_taxa):
		clsresult = item.classifier_result
		expected_taxon = testdb.genomeset.taxa.filter_by(key=expected_key).one() if expected_key else None

		assert item.input.file == file
		assert clsresult.success

		if expected_taxon is None:
			assert clsresult.predicted_taxon is None
			assert clsresult.primary_match is None
			assert item.report_taxon is None
		else:
			assert clsresult.predicted_taxon == expected_taxon
			assert item.report_taxon == expected_taxon
			assert clsresult.primary_match is not None
			assert clsresult.primary_match.matched_taxon == expected_taxon

			# In this database, closest match should be primary match
			assert clsresult.closest_match == clsresult.primary_match

		assert not clsresult.warnings
		assert clsresult.error is None


@pytest.mark.parametrize('out_fmt', ['json'])
@pytest.mark.parametrize('classify_strict', [False, True])
def test_query_cli(testdb_files, testdb, query_data, out_fmt, classify_strict, tmp_path):
	"""Run a full query using the command line interface."""
	results_file = tmp_path / 'results.json'
	query_files, expected_taxa = query_data

	args = [
		f'--db={testdb_files["root"]}',
		'query',
		f'--output={results_file}',
		f'--outfmt={out_fmt}',
		'--strict' if classify_strict else '--no-strict',
		*(str(f.path) for f in query_files),
	]

	cli.main(args, standalone_mode=False)

	if out_fmt == 'json':
		_check_results_json(results_file, testdb, query_files, expected_taxa)
	else:
		assert False

def _check_results_json(results_file, testdb, query_files, expected_taxa):
	with results_file.open() as f:
		results = json.load(f)

	assert results['genomeset']['key'] == testdb.genomeset.key
	assert results['signaturesmeta']['id'] == testdb.signatures.meta.id
	assert results['gambit_version'] == GAMBIT_VERSION

	items = results['items']
	assert isinstance(items, list)
	assert len(items) == len(query_files)

	for item, file, expected in zip_strict(items, query_files, expected_taxa):
		clsresult = item['classifier_result']
		assert item['input']['label'] == file.path.name
		assert clsresult['success'] is True

		if expected == '':
			assert clsresult['predicted_taxon'] is None
			assert item['report_taxon'] is None
			assert clsresult['primary_match'] is None
		else:
			predicted = clsresult['predicted_taxon']
			assert predicted is not None
			assert predicted['key'] == expected
			assert item['report_taxon'] == predicted
			assert clsresult['primary_match'] is not None
			assert clsresult['primary_match']['matched_taxon']['key'] == expected

			# In this database, closest match should be primary match
			assert clsresult['closest_match'] == clsresult['primary_match']

		assert clsresult['warnings'] == []
		assert clsresult['error'] is None
