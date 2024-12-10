import unittest

from llm_web_kit.input.datajson import DataJson
from llm_web_kit.pipeline.pipeline_suit import PipelineSuit


class TestPipelineSuite(unittest.TestCase):

    def test_pipeline_init(self):
        # Test pipeline
        pipesuit = PipelineSuit(f'{__file__}/../assets/html_pipe_normal.jsonc')
        self.assertIsNotNone(pipesuit)
        input_data = {'dataset_name': 'news', 'file_format': 'html'}
        pipesuit.format(input_data)
        data: DataJson = pipesuit.extract(input_data)
        assert data.get_content_list().length() == 0
