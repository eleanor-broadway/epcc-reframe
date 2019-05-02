import reframe as rfm
import reframe.utility.sanity as sn

class IO500BaseTest(rfm.RunOnlyRegressionTest):
    def __init__(self, test_version):
        super().__init__()
        self.descr = 'IO-500: %s' % test_version
        self.valid_systems = ['*']

        self.executable = './io500_%s.sh' % test_version

        self.num_tasks = 80
        self.num_tasks_per_node = 8
        self.num_cpus_per_task = 1
        self.time_limit = (2, 0, 0)
        self.variables = {
            'OMP_NUM_THREADS': str(self.num_cpus_per_task)
        }

        output_file = 'io-500-summary.txt'

        score = sn.extractsingle(r'TOTAL\s+(?P<score>\S+)',
                                     output_file, 'score', float)

        self.sanity_patterns = sn.all([
            sn.assert_found('TOTAL', output_file),
        ])

        self.perf_patterns = {
            'perf': sn.extractsingle(r'TOTAL\s+(?P<score>\S+)',
                                     output_file, 'score', float)
        }

        self.reference = {
            'cirrus:compute_mptloc': {
                'perf': (8.8, -0.1, 0.1),
            }
        }

        self.maintainers = ['a.turner@epcc.ed.ac.uk']
        self.tags = {'basic', 'production'}

@rfm.simple_test
class IO500MPTTest(IO500BaseTest):
    def __init__(self):
        super().__init__('mpt')
        self.valid_systems = ['cirrus:compute_mptloc']
        self.valid_prog_environs = ['PrgEnv-gcc6-mpt']

