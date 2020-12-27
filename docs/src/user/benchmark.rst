**********
Benchmark
**********

You can benchmark the performance of search algorithms with different tasks at different
assessment levels.


Benchmark can be created as below, refer :doc:`/code/benchmark/benchmark_client`
for how to create and :doc:`/code/benchmark` for how to use benchmark.

.. code-block:: python

  from orion.benchmark.benchmark_client import get_or_create_benchmark
  from orion.benchmark.assessment import AverageResult, AverageRank
  from orion.benchmark.task import RosenBrock, EggHolder, CarromTable

  benchmark = get_or_create_benchmark(name='benchmark',
          algorithms=['random', 'tpe'],
          targets=[
              {
                  'assess': [AverageResult(2), AverageRank(2)],
                  'task': [RosenBrock(25, dim=3), EggHolder(20, dim=4), CarromTable(20)]
              }
          ])


Beside out of box :doc:`/code/benchmark/task` and :doc:`/code/benchmark/assessment`,
you can also extend benchmark to add new ``Tasks`` and ``Assessments`` by referring
:doc:`/code/benchmark/base`,