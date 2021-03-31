import os
import datetime
import logging
#from tfx.components.evaluator.component import Evaluator
#from tfx.components.example_gen.csv_example_gen.component import CsvExampleGen
from tfx.components.example_validator.component import ExampleValidator
from tfx.components.model_validator.component import ModelValidator
from tfx.components.pusher.component import Pusher
from tfx.components.schema_gen.component import SchemaGen
from tfx.components.statistics_gen.component import StatisticsGen
from tfx.components.trainer.component import Trainer
from tfx.components.transform.component import Transform
from tfx.orchestration import pipeline
from tfx.orchestration.airflow.airflow_runner import AirflowDAGRunner
from tfx.proto import trainer_pb2, pusher_pb2
from tfx.utils.dsl_utils import csv_input
from tfx.proto import example_gen_pb2
from tfx.utils.dsl_utils import tfrecord_input
from tfx.components.example_gen.import_example_gen.component import ImportExampleGen
import tensorflow as tf

# Airflow config parameters
PIPELINE_NAME = 'exampleGen'
SCHEDULE_INTERVAL = '15 * * * *' # every 15 minutes
DAGS_DIR = '/root/airflow/dags/'
METADATA_DIR = '/root/airflow/data/'
LOGS_DIR = '/root/airflow/logs/'

AIRFLOW_CONFIG = {
    'schedule_interval': None,
    'start_date': datetime.datetime(2018, 1, 1)
}

def create_pipeline():
	path_to_tfrecord_dir = '/tensorflow/workspace/tfx/components/exampleGen/examples/all.record'
	# Output 2 splits: train:eval=3:1.
	output = example_gen_pb2.Output(
	             split_config=example_gen_pb2.SplitConfig(splits=[
	                 example_gen_pb2.SplitConfig.Split(name='train', hash_buckets=3),
	                 example_gen_pb2.SplitConfig.Split(name='eval', hash_buckets=1)
	             ]))
	examples = tfrecord_input(path_to_tfrecord_dir)
	example_gen = ImportExampleGen(input_base=examples, output_config=output)
	statistics_gen = StatisticsGen(input_data=example_gen.outputs.examples)
	infer_schema = SchemaGen(stats=statistics_gen.outputs.output)
	validate_stats = ExampleValidator(stats=statistics_gen.outputs.output, schema=infer_schema.outputs.output)
	#module_file = tf.train.latest_checkpoint(checkpoint_dir)
	#transform = Transform(
    #  input_data=example_gen.outputs.examples,
    #  schema=infer_schema.outputs.output,
    #  module_file=module_file)

    #trainer = Trainer(
    #  module_file=module_file,
    #  transformed_examples=transform.outputs.transformed_examples,
    #  schema=infer_schema.outputs.output,
    #  transform_output=transform.outputs.transform_output,
    #  train_args=trainer_pb2.TrainArgs(num_steps=10000),
    #  eval_args=trainer_pb2.EvalArgs(num_steps=5000))


	return pipeline.Pipeline(
		pipeline_name=PIPELINE_NAME,
        pipeline_root=DAGS_DIR,
        components=[example_gen, statistics_gen, infer_schema, validate_stats],
        enable_cache=True,
        metadata_db_root=METADATA_DIR,
        additional_pipeline_args={
            'logger_args': {
                'log_root': LOGS_DIR,
                'log_level': logging.INFO
            }
        }
		)

airflow_pipeline = AirflowDAGRunner(AIRFLOW_CONFIG).run(create_pipeline())
#pipeline = Pipeline().run(create_pipeline())
#pipeline = AirflowDAGRunner(_airflow_config).run(_create_pipeline())
#pipeline = TfxRunner().run(_create_pipeline())
#pipeline = AirflowDAGRunner(_airflow_config).run(_create_pipeline())
