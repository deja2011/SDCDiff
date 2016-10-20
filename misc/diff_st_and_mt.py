#!/depot/Python-2.7.8/bin/python -B

from extractor import Extractor, sdcflat
from comparator import Comparator
# from Consumer import consumer
import sys, time, linecache, timeit, multiprocessing
from subprocess import check_output, check_call, CalledProcessError


def main(*nkwargs, **kwargs):

    print 'Launched main.py at ', time.ctime()
    print 'sdcfile_1:', sdcfile_1
    print 'sdcfile_2:', sdcfile_2
    print 'cmd:    ', cmd

    print time.ctime()
    mt(sdcfile_1, sdcfile_2, cmd)
    # st(sdcfile_1, sdcfile_2, cmd)
    print time.ctime()

    return 0

    print "*" * 128
    print timeit.timeit(stmt = 'st(sdcfile_1, sdcfile_2, cmd)', setup = 'from __main__ import st, sdcfile_1, sdcfile_2, cmd', number = 2)
    print "*" * 128
    print timeit.timeit(stmt = 'mt(sdcfile_1, sdcfile_2, cmd)', setup = 'from __main__ import mt, sdcfile_1, sdcfile_2, cmd', number = 2)
    print "*" * 128

    # for ii in range(10):
    #     print '*' * 128
    #     mt(sdcfile_1, sdcfile_2, cmd)

    # print '\n\n\n'


def st(f_1, f_2, cmd):

    linecache.clearcache()

    errlog = open('error.st.log', 'w')
    tmpid_1 = open("tmp_1.tcl", "w")
    tmpid_2 = open("tmp_2.tcl", "w")

    try:
        check_call((sdcflat, f_1, cmd), stdout = tmpid_1, stderr = errlog)
    except CalledProcessError as e:
        errlog.write("Missing configuration of %s.(SDCFLAT-000)\n" % cmd)
        tmpid_1.close()
        return
    tmpid_1.close()

    try:
        check_call((sdcflat, f_2, cmd), stdout = tmpid_2, stderr = errlog)
    except CalledProcessError as e:
        errlog.write("Missing configuration of %s.(SDCFLAT-000)\n" % cmd)
        tmpid_2.close()
        return
    tmpid_2.close()
    
    # print "Building hash table of %s in file 1 ..." % cmd
    hash2nu_1 = dict()
    nu = 1
    while(True):
        line = linecache.getline("tmp_1.tcl", nu)
        if not line: break
        hash2nu_1[hash(line)] = nu
        nu += 1

    # print "Building hash table of %s in file 2 ..." % cmd
    hash2nu_2 = dict()
    nu = 1
    while(True):
        line = linecache.getline("tmp_2.tcl", nu)
        if not line: break
        hash2nu_2[hash(line)] = nu
        nu += 1

    hash1m2 = set(hash2nu_1.keys()) - set(hash2nu_2.keys())
    hash2m1 = set(hash2nu_2.keys()) - set(hash2nu_1.keys())

    if len(hash1m2) == 0 and len(hash2m1) == 0:
        print "--Two files have equivalent content on %s" % cmd
    else:
        print "--There are %d flattened commands exist only in file 1:" % len(hash1m2)
        for eachhash in hash1m2:
            print linecache.getline("tmp_1.tcl", hash2nu_1[eachhash]),

        print "--There are %d flattened commands exist only in file 2:" % len(hash2m1)
        for eachhash in hash2m1:
            print linecache.getline("tmp_2.tcl", hash2nu_2[eachhash]),


def mt(sdcfile_1, sdcfile_2, cmd):
    pool_1, pool_2 = set(), set()
    lock_1, lock_2 = multiprocessing.Lock(), multiprocessing.Lock()
    all_done = multiprocessing.Event()
    all_done.clear()
    errlog = open('error.mt.log', 'w')

    p_parser_1 = Extractor(sdcfile_1, pool_1, cmd, errlog, lock_1)
    p_parser_2 = Extractor(sdcfile_2, pool_2, cmd, errlog, lock_2)
    p_comparator = Comparator(pool_1, pool_2, lock_1, lock_2, all_done)

    p_parser_1.start()
    p_parser_2.start()
    p_comparator.start()

    p_parser_1.join()
    p_parser_2.join()
    all_done.set()
    p_comparator.join()

    errlog.close()

    print p_comparator.pool_1, id(p_comparator.pool_1)
    print p_comparator.pool_2, id(p_comparator.pool_2)

    for i, pool in enumerate((p_comparator.pool_1, p_comparator.pool_2)):
        print 'Following command exists only in pool_%d' % i
        for cmd in pool:
            print '   ', cmd

    print 'all.done'


if __name__ == '__main__':
    nkwargs = sys.argv[1:]
    sdcfile_1 = nkwargs[0]
    sdcfile_2 = nkwargs[1]
    cmd = nkwargs[2]
    main()
