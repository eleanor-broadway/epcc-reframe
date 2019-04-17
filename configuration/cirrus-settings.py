#
# ReFrame generic settings
#


class ReframeSettings:
    reframe_module = None
    job_poll_intervals = [1, 2, 3]
    job_submit_timeout = 60
    checks_path = ['checks/']
    checks_path_recurse = True

    site_configuration = {
        'systems': {
            'cirrus': {
                'descr': 'Cirrus',
                'hostnames': ['cirrus'],
                'modules_system': 'tmod',
                'partitions': {
                    'login': {
                        'scheduler': 'local',
                        'modules': [],
                        'access':  [],
                        'environs': ['PrgEnv-intel18-impi', 'PrgEnv-intel17-impi',
                                     'PrgEnv-gcc6-impi'],
                        'descr': 'Login nodes',
                        'max_jobs': 4
                    },
    
                    'compute': {
                        'scheduler': 'pbs+mpirun',
                        'modules': [],
                        'access':  [],
                        'environs': ['PrgEnv-intel18-impi', 'PrgEnv-intel17-impi',
                                     'PrgEnv-gcc6-impi'],
                        'descr': 'Compute nodes (Broadwell)',
                        'max_jobs': 10
                    }
                }
            }
        },
    
        'environments': {
            '*': {
                'PrgEnv-intel17-impi': {
                    'type': 'ProgEnvironment',
                    'modules': ['intel-tools-17', 'intel-mpi-17'],
                },
    
                'PrgEnv-intel18-impi': {
                    'type': 'ProgEnvironment',
                    'modules': ['intel-tools-18', 'intel-mpi-18'],
                },
    
                'PrgEnv-gcc6-impi': {
                    'type': 'ProgEnvironment',
                    'modules': ['gcc/6.3.0', 'intel-mpi-18'],
                }
            }
        }
    }


    logging_config = {
        'level': 'DEBUG',
        'handlers': [
            {
                'type': 'file',
                'name': 'reframe.log',
                'level': 'DEBUG',
                'format': '[%(asctime)s] %(levelname)s: '
                          '%(check_info)s: %(message)s',
                'append': False,
            },

            # Output handling
            {
                'type': 'stream',
                'name': 'stdout',
                'level': 'INFO',
                'format': '%(message)s'
            },
            {
                'type': 'file',
                'name': 'reframe.out',
                'level': 'INFO',
                'format': '%(message)s',
                'append': False,
            }
        ]
    }

    perf_logging_config = {
        'level': 'DEBUG',
        'handlers': [
            {
                'type': 'filelog',
                'prefix': '%(check_system)s/%(check_partition)s',
                'level': 'INFO',
                'format': (
                    '%(asctime)s|reframe %(version)s|'
                    '%(check_info)s|jobid=%(check_jobid)s|'
                    '%(check_perf_var)s=%(check_perf_value)s|'
                    'ref=%(check_perf_ref)s '
                    '(l=%(check_perf_lower_thres)s, '
                    'u=%(check_perf_upper_thres)s)|'
                    '%(check_perf_unit)s'
                ),
                'append': True
            }
        ]
    }


settings = ReframeSettings()