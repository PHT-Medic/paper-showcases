import os
from subprocess import PIPE, run


def run_hlatyping():
    #subprocess.call(['./nextflow', 'run', 'nf-core/hlatyping', '-profile', 'docker,test', '--outdir', './results'])
    command = ['nextflow', 'run', 'nf-core/hlatyping', '--reads',
            '/data/*_{1,2}.filt.fastq.gz',  '--out-dir', './results']
    result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    print(result.returncode, result.stdout, result.stderr)

    
if __name__ == '__main__':
    # run_hlatyping()
    run_hlatyping()
