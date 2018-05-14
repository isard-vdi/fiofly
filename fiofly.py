#!/usr/bin/env python3
#
# Albeto Larraz Dalmases
# Néfix Estrada Campañá
# IsardVDI Project
# Escola del Treball de Barcelona


import matplotlib.pyplot as plt
from tabulate import tabulate

import os
import argparse
import numpy as np
from pprint import pprint
from matplotlib.font_manager import FontProperties

# Helpers imports
from helpers import files_helpers
from helpers import syntax_checkers


OPTIONS_FIO = '--output-format=json,normal'
FILENAME_TEST = 'fio_test'


def to_MB(s_formated):
    s_formated = s_formated.split('/')[0]
    unit = s_formated[-2:]
    num = float(s_formated[:-2])
    if unit == 'MB':
        return num
    if unit == 'KB':
        return num / 1000
    if unit == 'B ':
        return num / 1000000


def create_plot(x0,x1,title0,title1,title_y):
    font0 = FontProperties()
    font0.set_family('monospace')

    x0 = np.array(x0)
    x1 = np.array(x1)
    y = np.arange(x1.size)

    fig, axes = plt.subplots(ncols=2, sharey=True)

    axes[0].barh(y, x0, align='center', height=0.5,
                 color=['blue', 'green', 'green', 'blue', 'blue', 'blue'], zorder=10)
    axes[1].barh(y, x1, align='center', height=0.5, color='green', zorder=10)

    axes[0].set(title=title0)
    axes[1].set(title=title1)

    # axes[0].set_yticks(ind + width / 2)
    # axes[0].set_yticklabels([str(d) for d in x0], minor=False)

    axes[0].invert_xaxis()
    axes[0].set(yticks=y, yticklabels=title_y)
    axes[0].yaxis.tick_right()

    for ax in axes.flat:
        ax.margins(0.03)
        ax.grid(True)

    fig.tight_layout()
    fig.subplots_adjust(wspace=0.5)
    return


class FioFly(object):
    def __init__(self, args):
        self.conf = files_helpers.get_yaml_file_config(args)
        syntax_checkers.check_syntax(self.conf)
        self.jobs_fios = self.conf['jobs_fios']

    def create_fios_tests(self):
        tests = self.conf['tests']
        all_cmds=[]
        all_cmds.append('echo "### {} #######"'.format('create dir to fio logs'))
        all_cmds.append('echo "### Command: mkdir -p {}"'.format(self.conf['conf']['fios_logs']))
        all_cmds.append('mkdir -p {}'.format(self.conf['conf']['fios_logs']))
        for t in tests:
            title=list(t.keys())[0]
            options = t[title]
            if options.get('do_fio') is True:
                all_cmds.append('echo "##############################"')
                all_cmds.append('echo "####### {} #######"'.format(title))
                dir_to_fio = options['dir_to_fio']
                all_cmds += self.fios_in_path(title, dir_to_fio)

        self.all_cmds = all_cmds

    def run_fios_tests(self):
        self.create_fios_tests()
        for cmd in self.all_cmds:
            try:
                os.system(cmd)
            except Exception as e:
                print('ERROR LAUNCHING COMMAND')
                print('Exception: ' + e)
                print('Command: ' + cmd)    

    def fios_in_path(self,title,path):
        cmds = []
        cmds.append('rm -f {}*'.format(path + '/' + title))
        for i in range(len(self.jobs_fios)):
            title_fio = list(self.jobs_fios[i].keys())[0]
            d_jobs_fio = list(self.jobs_fios[i].values())[0]
            cmds.append('echo -e "\n*{}-{} ---\n"'.format(title,title_fio))
            cmds.append('rm -f {}*'.format(path + '/' + title))
            cmds.append(self.cmd_fio(title_fio, d_jobs_fio, path, title))

        return cmds

    def cmd_fio(self,title_fio,d_jobs_fio,dir_to_fio,title):

        job_fio_options = ' '.join(['--{}={}'.format(k,v) for k,v in d_jobs_fio.items()])

        test_name = title + '-' + title_fio

        dir_logs = self.conf['conf']['fios_logs']

        fio_cmd = ('fio {options_fio} --output={output} {job_fio_options} ' +
                   ' --directory={directory} --name={name}')\
                    .format(options_fio=OPTIONS_FIO,
                            job_fio_options=job_fio_options,
                            output= dir_logs + '/' + test_name + '.json',
                            name=test_name,
                            directory=dir_to_fio)
                            # filename=dir_to_fio + '/' + FILENAME_TEST)
        return fio_cmd

    def print_fios(self):
        self.create_fios_tests()
        print('\n'.join(self.all_cmds))


    def read_stats(self):
        d_tests = {}
        dir_logs = self.conf['conf']['graphs_from_logs']
        files = [name for name in os.listdir(dir_logs) if name[-5:] == '.json']
        for t in self.conf['tests']:
            title=list(t.keys())[0]
            d_tests[title] = {}
            for j in [list(i.keys())[0] for i in self.jobs_fios]:
                rw = j.split('_')[1]
                param = j.split('_')[0]
                filename = title + '-' + j + '.json'
                #print(filename)
                if filename in files:
                    f = open(dir_logs + '/' + filename)
                    s = f.read()
                    f.close()
                    log = s[s.rfind('}') + 1:]
                    if rw == 'read':
                        lines = [l for l in log.split('\n') if l.find(' {} :'.format(rw)) > 0]
                    else:
                        lines = [l for l in log.split('\n') if l.find(' {}:'.format(rw)) > 0]
                    try:
                        if param == 'bw':
                            d_tests[title][j] = to_MB(lines[0].split('{}='.format(param))[1].split(',')[0])
                        else:
                            total_iops = sum([int(line.split('{}='.format(param))[1].split(',')[0]) for line in lines])
                            d_tests[title][j] = total_iops
                    except:
                        print(filename)
                        print(param)
                        pprint(lines)

        self.results_tests = d_tests
        return True

    def print_stats(self):
        header = ['test', 'bw_read', 'bw_write', 'iops_read', 'iops_write']
        table = []
        self.read_stats()
        d_tests = self.results_tests
        for t, d_params in d_tests.items():
            row = []
            row.append(t)
            #pprint(d_params)
            if 'bw_read' in d_params.keys():
                row.append(d_params['bw_read'])
                row.append(d_params['bw_write'])
                row.append(d_params['iops_read'])
                row.append(d_params['iops_write'])
                table.append(row)

        print(tabulate(table, tablefmt="grid", headers=header))

    def print_test_dirs(self):
        rows = []
        header = ['test','dir','do fio test','graph']
        tests = self.conf['tests']
        for t in tests:
            title=list(t.keys())[0]
            options = t[title]

            do_fio = 'Yes' if options.get('do_fio') is True else 'No'
            graphs = options.get('do_fio','Not Defined')
            dir_to_fio = options.get('dir_to_fio','Not Defined')

            rows.append([title,dir_to_fio,do_fio,graphs])

        print(tabulate(rows, tablefmt="grid", headers=header))


    def create_plots(self,png=False,option_graph='A'):



        selected_tests = [list(t)[0] for t in self.conf['tests'] if list(t.values())[0]['graphs'] == option_graph]

        self.read_stats()

        #PARAMITRIZE PLOT
        # title_tests = selected_tests
        title0 = 'Sequential Read MB/s'
        title1 = 'Sequential Write MB/s'

        bw_r = []
        bw_w = []
        iops_r = []
        iops_w = []

        for test in selected_tests:
            bw_r.append(self.results_tests[test].get('bw_read',0))
            bw_w.append(self.results_tests[test].get('bw_write',0))
            iops_r.append(self.results_tests[test].get('iops_read',0))
            iops_w.append(self.results_tests[test].get('iops_write',0))

        # BW
        create_plot(bw_r,bw_w,title0,title1,selected_tests)
        if png is True:
            plt.savefig('fio_bw.png',dpi=300)

        #FIOS
        title0 = 'Read FIOs per second'
        title1 = 'Write FIOs per second'
        create_plot(iops_r,iops_w,title0,title1,selected_tests)
        if png is True:
            plt.savefig('fio_iops.png',dpi=300)


    def show_plots(self):
        plt.show()


def set_arguments():

    ag = argparse.ArgumentParser(description='Run multiple fios, \
        show results and make graphics fom yaml configuration')

    #ag = parser.add_argument_group(title="Conf Settings")
    ag.add_argument("-y", "--yaml-file-conf", help="file with yaml conf")



    ## ~/.config/fiofly/fiofly.yml
    ## /etc/fiofly/fiofly.conf.yml

    # lanzar un print de sample
    #ag.add_argument()
    # A la ajuda!!
    # Crear un man

    ag.add_argument("-f", "--fio-commands", action="store_true",
                    help="print fio-commands" )

    ag.add_argument("-r", "--run-commands", action="store_true",
                    help="run fio-commands" )

    ag.add_argument("-i", "--info-tests", action="store_true",
                    help="dirs where make tests" )


    ag.add_argument("-p", "--plots-png-file", action="store_true",
                    help="create png file with plots")

    ag.add_argument("-s", "--show-plots", action="store_true",
                    help="show plots in screen")

    ag.add_argument("-t", "--table-results", action="store_true",
                    help="print table with results")

    return ag


def main():

    parser = set_arguments()
    try:
        args = parser.parse_args()
    
    except OSError:
        parser.print_help()
        sys.exit(1)

    fiofly = FioFly(args)

    if args.run_commands:
        fiofly.run_fios_tests()

    if args.fio_commands:
        fiofly.print_fios()

    if args.table_results:
        fiofly.print_stats()

    if args.show_plots:
        fiofly.create_plots()
        fiofly.show_plots()

    if args.plots_png_file:
        fiofly.create_plots(png=True)

    if args.info_tests:
        fiofly.print_test_dirs()

    if not any(vars(args).values()):
        parser.print_help()


if __name__ == "__main__":
    main()
