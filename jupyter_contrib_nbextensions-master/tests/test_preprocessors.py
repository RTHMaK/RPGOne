# -*- coding: utf-8 -*-

import os

import nbformat.v4 as nbf
from nbconvert import LatexExporter, RSTExporter
from nbconvert.utils.pandoc import PandocMissing
from nose.plugins.skip import SkipTest
from nose.tools import assert_in, assert_not_in, assert_true
from traitlets.config import Config


def path_in_data(rel_path):
    """Return an absolute path from a relative path in tests/data."""
    return os.path.join(os.path.dirname(__file__), 'data', rel_path)


def export_through_preprocessor(
        notebook_node, preproc_cls, exporter_class, export_format,
        customconfig=None):
    """Export a notebook through a given preprocessor."""
    config = Config(NbConvertApp={'export_format': export_format})
    if customconfig is not None:
        config.merge(customconfig)
    exporter = exporter_class(
        preprocessors=[preproc_cls.__module__ + '.' + preproc_cls.__name__],
        config=config)
    try:
        return exporter.from_notebook_node(notebook_node)
    except PandocMissing:
        raise SkipTest("Pandoc wasn't found")


def test_preprocessor_pymarkdown():
    """Test python markdown preprocessor."""
    # check import shortcut
    from jupyter_contrib_nbextensions.nbconvert_support import PyMarkdownPreprocessor  # noqa E501
    notebook_node = nbf.new_notebook(cells=[
        nbf.new_code_cell(source="a = 'world'"),
        nbf.new_markdown_cell(source="Hello {{ a }}",
                              metadata={"variables": {" a ": "world"}}),
    ])
    body, resources = export_through_preprocessor(
        notebook_node, PyMarkdownPreprocessor, RSTExporter, 'rst', )
    expected = 'Hello world'
    assert_in(expected, body, 'first cell should contain {}'.format(expected))


def test_preprocessor_codefolding():
    """Test codefolding preprocessor."""
    # check import shortcut
    from jupyter_contrib_nbextensions.nbconvert_support import CodeFoldingPreprocessor  # noqa: E501
    notebook_node = nbf.new_notebook(cells=[
        nbf.new_code_cell(source='\n'.join(["# Codefolding test 1",
                                            "'AXYZ12AXY'"]),
                          metadata={"code_folding": [0]}),
        nbf.new_code_cell(source='\n'.join(["# Codefolding test 2",
                                            "def myfun():",
                                            "    'GR4CX32ZT'"]),
                          metadata={"code_folding": [1]}),
    ])
    customconfig = Config(NbConvertApp={'codefolding': True})
    body, resources = export_through_preprocessor(
        notebook_node, CodeFoldingPreprocessor, RSTExporter, 'rst',
        customconfig)
    assert_not_in('AXYZ12AXY', body, 'check firstline fold has worked')
    assert_not_in('GR4CX32ZT', body, 'check function fold has worked')


def test_preprocessor_svg2pdf():
    """Test svg2pdf preprocessor for markdown cell svg images in latex/pdf."""
    # check import shortcut
    from jupyter_contrib_nbextensions.nbconvert_support import SVG2PDFPreprocessor  # noqa: E501
    from jupyter_contrib_nbextensions.nbconvert_support.pre_svg2pdf import (
        get_inkscape_executable_path)
    if not get_inkscape_executable_path():
        raise SkipTest('No inkscape executable found')

    notebook_node = nbf.new_notebook(cells=[
        nbf.new_markdown_cell(
            source='![This is a test]({})'.format(path_in_data('test.svg')))
    ])
    body, resources = export_through_preprocessor(
        notebook_node, SVG2PDFPreprocessor, LatexExporter, 'latex')

    pdf_path = path_in_data('test.pdf')
    pdf_existed = os.path.isfile(pdf_path)
    if pdf_existed:
        os.remove(pdf_path)
    assert_true(pdf_existed, 'exported pdf should exist')
    assert_in('test.pdf', body,
              'exported pdf should be referenced in exported notebook')
